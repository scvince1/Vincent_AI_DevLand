"""
CPSC Recalls scraper — CPSCScraper(BaseScraper)

Data source: SaferProducts.gov REST API (no auth, no rate limit published)
Endpoint: https://www.saferproducts.gov/RestWebServices/Recall
Legal posture: GREEN — US government public data, no ToS concerns.

Verified 2026-04-11: endpoint accepts RecallTitle filter, returns JSON array.
Response fields used: RecallID, RecallNumber, RecallDate, Title, Description, URL,
  Manufacturers[*].Name, Importers[*].Name, Products[*].Name

CPSC mentions emit record_type="recall" on the Mention schema.
All CPSC-sourced mentions trigger safety_recall alerts at max severity in compute_alerts.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

import requests

from backend.app.scrapers.base import BaseScraper
from backend.models.schemas import (
    Brand,
    Category,
    DerivedSentiment,
    Mention,
    Polarity,
    SourcePlatform,
    SentimentLabel,
    AspectSentiment,
)

# Firms to filter for — checked against Manufacturers + Importers + Distributors
FIRM_KEYWORDS = [
    "shark",
    "ninja",
    "sharkninja",
    "dyson",
    "irobot",
    "roborock",
    "kitchenaid",
]

SAFERPRODUCTS_RECALL_URL = "https://www.saferproducts.gov/RestWebServices/Recall"

# Brand keyword → Brand enum mapping
_BRAND_MAP = {
    "shark": Brand.shark,
    "ninja": Brand.ninja,
    "sharkninja": Brand.shark,  # SharkNinja parent → shark
    "dyson": Brand.dyson,
    "irobot": Brand.irobot,
    "roborock": Brand.roborock,
    "kitchenaid": Brand.kitchenaid,
}


def _detect_brand(text: str) -> Brand:
    """Infer brand from recall title/firm text."""
    lower = text.lower()
    for keyword, brand in _BRAND_MAP.items():
        if keyword in lower:
            return brand
    return Brand.other


def _detect_category(text: str) -> Category:
    """Best-effort category inference from recall text."""
    lower = text.lower()
    if any(w in lower for w in ("vacuum", "roomba", "roborock", "robot")):
        return Category.robot_vacuum
    if any(w in lower for w in ("cordless", "stick", "handheld")):
        return Category.cordless_stick
    if "air fryer" in lower or "airfryer" in lower or "foodi" in lower:
        return Category.air_fryer
    if "pressure" in lower or "multi-cooker" in lower:
        return Category.pressure_cooker
    if "coffee" in lower or "espresso" in lower:
        return Category.coffee
    if "blender" in lower or "smoothie" in lower:
        return Category.blender
    if "hair" in lower or "dryer" in lower or "straightener" in lower:
        return Category.hair_tool
    if "purifier" in lower or "air clean" in lower:
        return Category.air_purifier
    return Category.other


def _firm_matches(recall: dict) -> bool:
    """Return True if any Manufacturers/Importers/Distributors match our keywords."""
    name_sources = (
        recall.get("Manufacturers") or [],
        recall.get("Importers") or [],
        recall.get("Distributors") or [],
    )
    for source in name_sources:
        for entry in source:
            name = (entry.get("Name") or "").lower()
            if any(kw in name for kw in FIRM_KEYWORDS):
                return True
    # Also check title as a fallback
    title = (recall.get("Title") or "").lower()
    return any(kw in title for kw in FIRM_KEYWORDS)


def _get_source_url(recall: dict) -> Optional[str]:
    return recall.get("URL") or None


class CPSCScraper(BaseScraper):
    """
    Fetches CPSC recall records via SaferProducts.gov REST API and maps them
    to Mention objects with record_type="recall".

    Recall records have no free-text aspect sentiment — derived.aspects is empty,
    compound_score is -1.0 (a recall is always a severe negative signal).
    """

    def __init__(self, firm_keywords: Optional[List[str]] = None):
        self._firm_keywords = firm_keywords or FIRM_KEYWORDS
        self._cached_mentions: Optional[List[Mention]] = None

    def _fetch_recalls(self) -> List[dict]:
        """
        Fetch recall records for all monitored firms.
        Makes one request per firm keyword with RecallTitle filter.
        Deduplicates by RecallID.
        """
        seen_ids: set = set()
        records: List[dict] = []

        for keyword in self._firm_keywords:
            try:
                resp = requests.get(
                    SAFERPRODUCTS_RECALL_URL,
                    params={"RecallTitle": keyword, "format": "json"},
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()
                for record in data:
                    rid = record.get("RecallID")
                    if rid and rid not in seen_ids:
                        if _firm_matches(record):
                            seen_ids.add(rid)
                            records.append(record)
            except requests.RequestException:
                # Non-fatal: if one keyword query fails, continue with others
                continue

        return records

    def _recall_to_mention(self, recall: dict) -> Mention:
        """Map a CPSC recall record to a Mention schema object."""
        title = recall.get("Title") or "CPSC Recall"
        description = recall.get("Description") or ""
        text = f"{title}\n\n{description}".strip()

        # Parse recall date
        raw_date = recall.get("RecallDate") or recall.get("LastPublishDate")
        if raw_date:
            try:
                posted_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                if posted_at.tzinfo is None:
                    posted_at = posted_at.replace(tzinfo=timezone.utc)
            except (ValueError, AttributeError):
                posted_at = datetime.now(timezone.utc)
        else:
            posted_at = datetime.now(timezone.utc)

        brand = _detect_brand(title)
        category = _detect_category(title + " " + description)
        source_url = _get_source_url(recall)

        # Product model from Products array if available
        products = recall.get("Products") or []
        product_model: Optional[str] = None
        if products:
            product_model = (products[0].get("Name") or "").strip() or None

        # Recall ID for stable mention_id
        recall_number = recall.get("RecallNumber") or str(recall.get("RecallID", uuid.uuid4()))
        mention_id = f"cpsc-{recall_number}"

        # Recalls carry maximum negative sentiment — no aspect-level breakdown
        derived = DerivedSentiment(
            overall_sentiment=SentimentLabel.negative,
            compound_score=-1.0,
            confidence=1.0,
            sarcasm_flag=False,
            aspects=[],
            comparative_pairs=None,
        )

        return Mention(
            mention_id=mention_id,
            source_platform=SourcePlatform.other,
            source_url=source_url,
            author_handle=None,
            posted_at=posted_at,
            ingested_at=datetime.now(timezone.utc),
            brand=brand,
            category=category,
            product_model=product_model,
            text=text,
            rating=None,
            language="en",
            derived=derived,
            record_type="recall",
        )

    def fetch(self, limit: int = 100, offset: int = 0, **filters) -> List[Mention]:
        """Fetch CPSC recall mentions. Results are cached for the lifetime of the instance."""
        if self._cached_mentions is None:
            records = self._fetch_recalls()
            self._cached_mentions = [self._recall_to_mention(r) for r in records]

        result = self._cached_mentions
        # Apply basic filters if provided
        brand = filters.get("brand")
        if brand:
            result = [m for m in result if m.brand == brand]

        return result[offset: offset + limit]

    def count(
        self,
        platform=None,
        brand=None,
        category=None,
        product_model=None,
        date_from=None,
        date_to=None,
        topic_id=None,
    ) -> int:
        return len(self.fetch(brand=brand, limit=100000, offset=0))
