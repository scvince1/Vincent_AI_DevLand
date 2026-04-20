"""
CSVAdapter — BaseScraper implementation that reads from local CSV fixture files.

Loads all *.csv files from `backend/data/` at init, runs the NLP pipeline on
each row's `text` field, and returns fully-derived Mention objects.
"""
import glob
import uuid
from datetime import datetime, timezone
from typing import List, Optional

import pandas as pd

from backend.app.nlp.pipeline import analyze
from backend.app.scrapers.base import BaseScraper
from backend.models.schemas import (
    Brand,
    Category,
    DerivedSentiment,
    Mention,
    SourcePlatform,
)


def _safe_enum(enum_cls, value, default):
    """Parse an enum value, falling back to default on unknown strings."""
    try:
        return enum_cls(str(value).lower().strip())
    except (ValueError, KeyError):
        return default


def _parse_dt(value) -> datetime:
    """Parse an ISO-8601 datetime string to a timezone-aware datetime."""
    if pd.isna(value):
        return datetime.now(timezone.utc)
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    s = str(value).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return datetime.now(timezone.utc)


def _row_to_mention(row: pd.Series) -> Optional[Mention]:
    """Convert a DataFrame row to a fully-derived Mention object."""
    try:
        text = str(row.get("text", "")).strip()
        if not text:
            return None

        # Run NLP pipeline
        result = analyze(text)
        derived: DerivedSentiment = result.to_derived_sentiment()

        mention = Mention(
            mention_id=str(row.get("mention_id", str(uuid.uuid4()))),
            source_platform=_safe_enum(SourcePlatform, row.get("source_platform", "other"), SourcePlatform.other),
            source_url=str(row["source_url"]) if pd.notna(row.get("source_url")) else None,
            author_handle=str(row["author_handle"]) if pd.notna(row.get("author_handle")) else None,
            posted_at=_parse_dt(row.get("posted_at")),
            ingested_at=_parse_dt(row.get("ingested_at")),
            brand=_safe_enum(Brand, row.get("brand", "other"), Brand.other),
            category=_safe_enum(Category, row.get("category", "other"), Category.other),
            product_model=str(row["product_model"]) if pd.notna(row.get("product_model")) else None,
            text=text,
            rating=float(row["rating"]) if pd.notna(row.get("rating")) else None,
            language=str(row.get("language", "en")).strip(),
            derived=derived,
        )
        return mention
    except Exception:
        return None


class CSVAdapter(BaseScraper):
    """
    Reads all *.csv files from the given data directory, applies the NLP pipeline,
    and serves mentions via in-memory filtering.
    """

    def __init__(self, data_dir: str = "backend/data/"):
        self._data_dir = data_dir
        self._mentions: List[Mention] = []
        self._topic_map: dict = {}  # mention_id -> topic_id
        self._load()

    def _load(self) -> None:
        csv_files = glob.glob(f"{self._data_dir}/*.csv")
        rows = []
        for path in csv_files:
            try:
                df = pd.read_csv(path, dtype=str, keep_default_na=False)
                # Replace empty strings with pd.NA for nullable handling
                df = df.replace("", pd.NA)
                rows.append(df)
            except Exception:
                pass

        if not rows:
            return

        combined = pd.concat(rows, ignore_index=True)
        for _, row in combined.iterrows():
            mention = _row_to_mention(row)
            if mention is not None:
                self._mentions.append(mention)
                # Store topic_id mapping if present
                topic_id = row.get("topic_id")
                if pd.notna(topic_id) and str(topic_id).strip():
                    self._topic_map[mention.mention_id] = str(topic_id).strip()

    def _filter(
        self,
        platform: Optional[str],
        brand: Optional[str],
        category: Optional[str],
        product_model: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        topic_id: Optional[str],
    ) -> List[Mention]:
        results = self._mentions

        if platform:
            results = [m for m in results if m.source_platform.value == platform]
        if brand:
            results = [m for m in results if m.brand.value == brand]
        if category:
            results = [m for m in results if m.category.value == category]
        if product_model:
            results = [m for m in results
                       if m.product_model and product_model.lower() in m.product_model.lower()]
        if date_from:
            df_aware = date_from if date_from.tzinfo else date_from.replace(tzinfo=timezone.utc)
            results = [m for m in results if m.posted_at >= df_aware]
        if date_to:
            dt_aware = date_to if date_to.tzinfo else date_to.replace(tzinfo=timezone.utc)
            results = [m for m in results if m.posted_at <= dt_aware]
        if topic_id:
            results = [m for m in results if self._topic_map.get(m.mention_id) == topic_id]

        return results

    def fetch(
        self,
        platform: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        product_model: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        topic_id: Optional[str] = None,
    ) -> List[Mention]:
        filtered = self._filter(platform, brand, category, product_model, date_from, date_to, topic_id)
        return filtered[offset: offset + limit]

    def count(
        self,
        platform: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        product_model: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        topic_id: Optional[str] = None,
    ) -> int:
        return len(self._filter(platform, brand, category, product_model, date_from, date_to, topic_id))
