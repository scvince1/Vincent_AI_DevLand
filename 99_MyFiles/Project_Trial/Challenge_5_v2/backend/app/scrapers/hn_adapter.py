"""
Hacker News scraper — HackerNewsScraper(BaseScraper)

Data source: HN Algolia Search API (no auth required, free)
  Search: https://hn.algolia.com/api/v1/search?query={brand}
  Items:  https://hacker-news.firebaseio.com/v0/item/{id}.json

Legal posture: GREEN — public API, explicitly designed for programmatic access.
Rate limits: Best-effort, no published hard limit. We add brief sleeps.

Strategy:
  - Query Algolia for each brand keyword → top stories + comments
  - Fetch HN item detail via Firebase REST for comment threading
  - Concatenate story title + top-level comment body as Mention.text
  - source_platform = SourcePlatform.other (no HN enum value in R4 — R5 cleanup)
"""
import time
from datetime import datetime, timezone
from typing import List, Optional

import requests

from backend.app.nlp.pipeline import analyze
from backend.app.scrapers.base import BaseScraper
from backend.models.schemas import (
    Brand,
    Category,
    DerivedSentiment,
    Mention,
    SourcePlatform,
)

HN_ALGOLIA_SEARCH = "https://hn.algolia.com/api/v1/search"
HN_FIREBASE_ITEM = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

BRAND_QUERIES = [
    "SharkNinja",
    "Shark vacuum",
    "Ninja air fryer",
    "Ninja coffee",
    "Dyson vacuum",
    "iRobot Roomba",
    "Roborock",
    "KitchenAid",
]

_BRAND_MAP = {
    "shark": Brand.shark,
    "ninja": Brand.ninja,
    "sharkninja": Brand.shark,
    "dyson": Brand.dyson,
    "irobot": Brand.irobot,
    "roborock": Brand.roborock,
    "kitchenaid": Brand.kitchenaid,
}

BRAND_KEYWORDS = list(_BRAND_MAP.keys())


def _detect_brand(text: str) -> Brand:
    lower = text.lower()
    for keyword, brand in _BRAND_MAP.items():
        if keyword in lower:
            return brand
    return Brand.other


def _detect_category(text: str) -> Category:
    lower = text.lower()
    if any(w in lower for w in ("robot vacuum", "roomba", "roborock", "robovac")):
        return Category.robot_vacuum
    if any(w in lower for w in ("cordless", "stick vac")):
        return Category.cordless_stick
    if "vacuum" in lower:
        return Category.upright
    if "air fryer" in lower or "airfryer" in lower:
        return Category.air_fryer
    if "coffee" in lower or "espresso" in lower:
        return Category.coffee
    if "pressure" in lower:
        return Category.pressure_cooker
    if "blender" in lower:
        return Category.blender
    if "ice cream" in lower:
        return Category.ice_cream_maker
    return Category.other


def _fetch_item_comments(item_id: int, max_comments: int = 5) -> List[str]:
    """Fetch top-level comments for an HN story via Firebase REST API."""
    try:
        resp = requests.get(
            HN_FIREBASE_ITEM.format(id=item_id),
            timeout=5,
        )
        resp.raise_for_status()
        item = resp.json()
        kids = (item or {}).get("kids") or []

        comments: List[str] = []
        for kid_id in kids[:max_comments]:
            try:
                c_resp = requests.get(
                    HN_FIREBASE_ITEM.format(id=kid_id),
                    timeout=5,
                )
                c_resp.raise_for_status()
                comment = c_resp.json() or {}
                text = comment.get("text") or ""
                # Strip HTML tags (HN uses basic HTML)
                import re
                text = re.sub(r"<[^>]+>", " ", text).strip()
                if text:
                    comments.append(text)
            except Exception:
                continue
            time.sleep(0.05)

        return comments
    except Exception:
        return []


class HackerNewsScraper(BaseScraper):
    """
    Fetches HN stories and comments mentioning SharkNinja brands via Algolia API.
    source_platform = SourcePlatform.other (no HN enum value until R5 cleanup).
    """

    def __init__(self, queries: Optional[List[str]] = None):
        self._queries = queries or BRAND_QUERIES
        self._cached_mentions: Optional[List[Mention]] = None

    def _search_algolia(self, query: str) -> List[dict]:
        """Search HN via Algolia. Returns list of hit dicts."""
        try:
            resp = requests.get(
                HN_ALGOLIA_SEARCH,
                params={
                    "query": query,
                    "tags": "story",
                    "hitsPerPage": 20,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("hits") or []
        except Exception:
            return []

    def _hit_to_mention(self, hit: dict) -> Optional[Mention]:
        """Convert an Algolia search hit to a Mention."""
        try:
            title = (hit.get("title") or "").strip()
            story_text = (hit.get("story_text") or "").strip()
            combined = f"{title}\n\n{story_text}".strip() if story_text else title

            if not combined:
                return None

            # Fetch top comments from Firebase
            object_id = hit.get("objectID")
            if object_id:
                try:
                    story_id = int(object_id)
                    comments = _fetch_item_comments(story_id)
                    if comments:
                        combined += "\n\n" + "\n\n".join(comments)
                except (ValueError, TypeError):
                    pass

            # Run NLP
            result = analyze(combined[:2000])
            derived: DerivedSentiment = result.to_derived_sentiment()

            # Parse timestamp
            created_at = hit.get("created_at")
            if created_at:
                try:
                    posted_at = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )
                    if posted_at.tzinfo is None:
                        posted_at = posted_at.replace(tzinfo=timezone.utc)
                except (ValueError, AttributeError):
                    posted_at = datetime.now(timezone.utc)
            else:
                posted_at = datetime.now(timezone.utc)

            story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
            brand = _detect_brand(combined)
            category = _detect_category(combined)
            author = hit.get("author")

            return Mention(
                mention_id=f"hn-{object_id}",
                source_platform=SourcePlatform.other,
                source_url=story_url,
                author_handle=author,
                posted_at=posted_at,
                ingested_at=datetime.now(timezone.utc),
                brand=brand,
                category=category,
                product_model=None,
                text=combined[:5000],
                rating=None,
                language="en",
                derived=derived,
                record_type="review",
            )
        except Exception:
            return None

    def _load_all(self) -> List[Mention]:
        if self._cached_mentions is not None:
            return self._cached_mentions

        seen_ids: set = set()
        all_mentions: List[Mention] = []

        for query in self._queries:
            hits = self._search_algolia(query)
            for hit in hits:
                oid = hit.get("objectID")
                if oid in seen_ids:
                    continue
                seen_ids.add(oid)
                mention = self._hit_to_mention(hit)
                if mention:
                    all_mentions.append(mention)
            time.sleep(0.1)  # brief pause between brand queries

        self._cached_mentions = all_mentions
        return all_mentions

    def fetch(
        self,
        platform: Optional[str] = None,
        brand=None,
        category=None,
        product_model: Optional[str] = None,
        date_from=None,
        date_to=None,
        limit: int = 100,
        offset: int = 0,
        topic_id: Optional[str] = None,
        **kwargs,
    ) -> List[Mention]:
        all_mentions = self._load_all()

        result = all_mentions
        if brand:
            result = [m for m in result if m.brand == brand]
        if category:
            result = [m for m in result if m.category == category]
        if date_from:
            result = [m for m in result if m.posted_at >= date_from]
        if date_to:
            result = [m for m in result if m.posted_at <= date_to]

        return result[offset: offset + limit]

    def count(
        self,
        platform: Optional[str] = None,
        brand=None,
        category=None,
        product_model: Optional[str] = None,
        date_from=None,
        date_to=None,
        topic_id: Optional[str] = None,
        **kwargs,
    ) -> int:
        return len(self.fetch(
            platform=platform, brand=brand, category=category,
            product_model=product_model, date_from=date_from, date_to=date_to,
            limit=100000, offset=0,
        ))
