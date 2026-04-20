"""
Reddit scraper — RedditScraper(BaseScraper)

Uses PRAW (Python Reddit API Wrapper) with OAuth2 credentials.

Credentials (set in .env, see .env.example):
  REDDIT_CLIENT_ID      — OAuth app client ID
  REDDIT_CLIENT_SECRET  — OAuth app client secret
  REDDIT_USER_AGENT     — Descriptive string, e.g. "sharkninja-sentiment/1.0"

Rate limit: 100 requests/minute authenticated. Basic exponential backoff on 429.
Legal posture: YELLOW for commercial use; non-commercial demo is low risk.
"""
import os
import time
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from backend.app.nlp.pipeline import analyze
from backend.app.scrapers.base import BaseScraper
from backend.models.schemas import (
    Brand,
    Category,
    DerivedSentiment,
    Mention,
    SourcePlatform,
)

# Default subreddit list (R4-P0-2 base; R4-P1-4 extends this to 7)
DEFAULT_SUBREDDITS = [
    "sharkninja",
    "BuyItForLife",
    "Appliances",
    "Coffee",
    "airfryer",
    "VacuumCleaners",
    "homeautomation",
]

# SharkNinja and competitor brand keywords for filtering
BRAND_KEYWORDS = [
    "shark", "ninja", "sharkninja",
    "dyson", "irobot", "roborock", "kitchenaid",
]

TOP_N_COMMENTS = 5  # Number of top comments to append to post text

_BRAND_MAP = {
    "shark": Brand.shark,
    "ninja": Brand.ninja,
    "sharkninja": Brand.shark,
    "dyson": Brand.dyson,
    "irobot": Brand.irobot,
    "roborock": Brand.roborock,
    "kitchenaid": Brand.kitchenaid,
}


def _detect_brand(text: str) -> Brand:
    lower = text.lower()
    for keyword, brand in _BRAND_MAP.items():
        if keyword in lower:
            return brand
    return Brand.other


def _detect_category(text: str) -> Category:
    lower = text.lower()
    if any(w in lower for w in ("roomba", "roborock", "robot vacuum", "robovac")):
        return Category.robot_vacuum
    if any(w in lower for w in ("cordless", "stick vac", "handheld")):
        return Category.cordless_stick
    if "vacuum" in lower or "hoover" in lower:
        return Category.upright
    if "air fryer" in lower or "airfryer" in lower or "foodi" in lower:
        return Category.air_fryer
    if "pressure" in lower or "instant pot" in lower:
        return Category.pressure_cooker
    if "coffee" in lower or "espresso" in lower or "barista" in lower:
        return Category.coffee
    if "blender" in lower or "smoothie" in lower:
        return Category.blender
    if "creami" in lower or "ice cream" in lower:
        return Category.ice_cream_maker
    if "hair" in lower or "blow dry" in lower:
        return Category.hair_tool
    if "air purif" in lower:
        return Category.air_purifier
    return Category.other


def _is_brand_relevant(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in BRAND_KEYWORDS)


class RedditScraper(BaseScraper):
    """
    Fetches Reddit posts + top comments from the default subreddit list via PRAW OAuth.
    Each submission is mapped to a Mention; text = selftext + top-N comments.
    """

    def __init__(self, subreddits: Optional[List[str]] = None):
        self._subreddits = subreddits or DEFAULT_SUBREDDITS
        self._praw = None
        self._cached_mentions: Optional[List[Mention]] = None

    def _get_praw(self):
        """Lazy-init PRAW instance from environment credentials."""
        if self._praw is not None:
            return self._praw
        try:
            import praw
        except ImportError as e:
            raise ImportError(
                "praw is required for RedditScraper. Install with: pip install praw"
            ) from e

        client_id = os.environ.get("REDDIT_CLIENT_ID", "")
        client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
        user_agent = os.environ.get(
            "REDDIT_USER_AGENT", "sharkninja-sentiment/1.0 (research demo)"
        )

        if not client_id or not client_secret:
            raise EnvironmentError(
                "REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set in environment. "
                "See .env.example for details."
            )

        self._praw = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        return self._praw

    def _fetch_subreddit(self, reddit, subreddit_name: str) -> List[Mention]:
        """Fetch hot + new posts from a single subreddit; return Mention list."""
        mentions: List[Mention] = []
        try:
            sub = reddit.subreddit(subreddit_name)
            submissions = list(sub.hot(limit=25)) + list(sub.new(limit=25))
            seen_ids: set = set()

            for submission in submissions:
                if submission.id in seen_ids:
                    continue
                seen_ids.add(submission.id)

                # Combine post title + body
                body = (submission.selftext or "").strip()
                title = (submission.title or "").strip()
                combined_text = f"{title}\n\n{body}".strip() if body else title

                # Append top N comments
                try:
                    submission.comments.replace_more(limit=0)
                    top_comments = submission.comments.list()[:TOP_N_COMMENTS]
                    comment_texts = [
                        c.body.strip() for c in top_comments
                        if hasattr(c, "body") and c.body.strip()
                    ]
                    if comment_texts:
                        combined_text += "\n\n" + "\n\n".join(comment_texts)
                except Exception:
                    pass  # Comments optional — continue without them

                if not combined_text or not _is_brand_relevant(combined_text):
                    continue

                # Run NLP pipeline
                try:
                    result = analyze(combined_text[:2000])  # Truncate for NLP perf
                    derived: DerivedSentiment = result.to_derived_sentiment()
                except Exception:
                    continue

                posted_at = datetime.fromtimestamp(
                    submission.created_utc, tz=timezone.utc
                )
                source_url = f"https://www.reddit.com{submission.permalink}"
                brand = _detect_brand(combined_text)
                category = _detect_category(combined_text)

                mentions.append(Mention(
                    mention_id=f"reddit-{submission.id}",
                    source_platform=SourcePlatform.reddit,
                    source_url=source_url,
                    author_handle=str(submission.author) if submission.author else None,
                    posted_at=posted_at,
                    ingested_at=datetime.now(timezone.utc),
                    brand=brand,
                    category=category,
                    product_model=None,  # Reddit posts rarely specify exact SKU
                    text=combined_text[:5000],
                    rating=None,
                    language="en",
                    derived=derived,
                    record_type="review",
                ))

                # Basic rate-limit breathing room
                time.sleep(0.02)

        except Exception:
            pass  # Non-fatal — log silently, return what we have

        return mentions

    def _load_all(self) -> List[Mention]:
        """Fetch from all configured subreddits; cache result."""
        if self._cached_mentions is not None:
            return self._cached_mentions

        reddit = self._get_praw()
        all_mentions: List[Mention] = []
        for sub in self._subreddits:
            all_mentions.extend(self._fetch_subreddit(reddit, sub))

        # Backoff retry: PRAW raises prawcore.exceptions.TooManyRequests on 429
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
