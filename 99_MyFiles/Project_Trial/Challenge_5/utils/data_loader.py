"""
Data loading and filtering utilities for the SharkNinja Sentiment Dashboard.

DataFrame schema (all modules must conform):
    id, platform, product_category, product_name, brand, text, rating,
    date, sentiment_score, sentiment_label, topics, engagement_score, author
"""

import os
import glob
import logging

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema enforcement
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = [
    "id", "platform", "product_category", "product_name", "brand",
    "text", "rating", "date", "sentiment_score", "sentiment_label",
    "topics", "engagement_score", "author",
]


def _enforce_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Add any missing columns with sensible defaults and cast types."""
    defaults = {
        "id": lambda n: range(n),
        "platform": "unknown",
        "product_category": "unknown",
        "product_name": "Unknown Product",
        "brand": "unknown",
        "text": "",
        "rating": 0.0,
        "date": pd.Timestamp.now(),
        "sentiment_score": 0.0,
        "sentiment_label": "neutral",
        "topics": "[]",
        "engagement_score": 0,
        "author": "anonymous",
    }
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            val = defaults.get(col, "")
            df[col] = val(len(df)) if callable(val) else val

    # Parse topics from string to list
    import ast
    def _parse_topics(val):
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            try:
                parsed = ast.literal_eval(val)
                return parsed if isinstance(parsed, list) else []
            except (ValueError, SyntaxError):
                return []
        return []
    df["topics"] = df["topics"].apply(_parse_topics)

    # Type coercions
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0.0)
    df["sentiment_score"] = pd.to_numeric(df["sentiment_score"], errors="coerce").fillna(0.0)
    df["engagement_score"] = pd.to_numeric(df["engagement_score"], errors="coerce").fillna(0)
    return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_data() -> pd.DataFrame:
    """
    Load all CSV files from data/sample/ and return a combined DataFrame.

    If no CSV files are present, generate_sample_data() is called automatically
    so the dashboard works immediately on a fresh checkout.
    """
    from config import DATA_DIR  # lazy import to avoid circular deps

    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

    if not csv_files:
        logger.info("No CSV files found in %s — generating sample data.", DATA_DIR)
        from utils.generate_sample_data import generate_sample_data
        return generate_sample_data()

    frames = []
    for path in csv_files:
        try:
            df = pd.read_csv(path, low_memory=False)
            frames.append(df)
            logger.info("Loaded %d rows from %s", len(df), path)
        except Exception as exc:
            logger.warning("Could not load %s: %s", path, exc)

    if not frames:
        logger.warning("All CSV files failed to load — generating sample data.")
        from utils.generate_sample_data import generate_sample_data
        return generate_sample_data()

    combined = pd.concat(frames, ignore_index=True)
    combined = _enforce_schema(combined)
    logger.info("Total loaded: %d rows", len(combined))
    return combined


def filter_data(
    df: pd.DataFrame,
    platform: str | None = None,
    brand: str | None = None,
    category: str | None = None,
    date_range: tuple | None = None,
) -> pd.DataFrame:
    """
    Filter a DataFrame by any combination of criteria.

    Parameters
    ----------
    df : pd.DataFrame
        Source data conforming to the standard schema.
    platform : str, optional
        One of 'reddit', 'amazon', 'tiktok'.
    brand : str, optional
        One of 'shark', 'ninja'.
    category : str, optional
        One of the keys in PRODUCT_CATEGORIES.
    date_range : tuple of (start, end), optional
        Both values should be parseable by pd.Timestamp.
        Inclusive on both ends.

    Returns
    -------
    pd.DataFrame
        Filtered copy of the input DataFrame.
    """
    result = df.copy()

    if platform:
        result = result[result["platform"].str.lower() == platform.lower()]

    if brand:
        result = result[result["brand"].str.lower() == brand.lower()]

    if category:
        result = result[result["product_category"].str.lower() == category.lower()]

    if date_range:
        start, end = date_range
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)
        result = result[
            (result["date"] >= start) & (result["date"] <= end)
        ]

    return result.reset_index(drop=True)
