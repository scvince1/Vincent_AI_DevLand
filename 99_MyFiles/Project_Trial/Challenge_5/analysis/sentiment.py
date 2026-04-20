"""
Sentiment analysis module using NLTK's VADER sentiment analyzer.
"""

import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

_analyzer = None


def initialize():
    """Download VADER lexicon and initialize the analyzer."""
    global _analyzer
    nltk.download('vader_lexicon', quiet=True)
    _analyzer = SentimentIntensityAnalyzer()


def _get_analyzer():
    """Lazy-initialize and return the VADER analyzer."""
    global _analyzer
    if _analyzer is None:
        initialize()
    return _analyzer


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of a single text string.

    Args:
        text: Input text to analyze.

    Returns:
        dict with keys: score (float -1 to 1), label (str), compound (float),
        details (dict with pos, neg, neu).
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return {
            "score": 0.0,
            "label": "neutral",
            "compound": 0.0,
            "details": {"pos": 0.0, "neg": 0.0, "neu": 1.0},
        }

    analyzer = _get_analyzer()
    scores = analyzer.polarity_scores(text)

    compound = scores["compound"]

    if compound > 0.2:
        label = "positive"
    elif compound < -0.2:
        label = "negative"
    else:
        label = "neutral"

    return {
        "score": compound,
        "label": label,
        "compound": compound,
        "details": {
            "pos": scores["pos"],
            "neg": scores["neg"],
            "neu": scores["neu"],
        },
    }


def batch_analyze(texts: list) -> list:
    """
    Analyze sentiment for a list of texts.

    Args:
        texts: List of text strings.

    Returns:
        List of sentiment result dicts.
    """
    if not texts:
        return []
    return [analyze_sentiment(t) for t in texts]


def get_sentiment_distribution(df: pd.DataFrame) -> dict:
    """
    Get distribution of sentiment labels from a DataFrame.

    Args:
        df: DataFrame with a 'sentiment_label' column.

    Returns:
        dict with 'counts' (dict) and 'percentages' (dict) per label.
    """
    if df is None or df.empty or "sentiment_label" not in df.columns:
        return {"counts": {}, "percentages": {}}

    counts = df["sentiment_label"].value_counts().to_dict()
    total = sum(counts.values())

    percentages = {}
    if total > 0:
        percentages = {k: round(v / total * 100, 2) for k, v in counts.items()}

    return {"counts": counts, "percentages": percentages}


def get_sentiment_over_time(df: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """
    Aggregate sentiment scores over time periods.

    Args:
        df: DataFrame with 'date' (datetime) and 'sentiment_score' columns.
        freq: Pandas frequency string (e.g. 'W', 'M', 'D').

    Returns:
        DataFrame with period, avg_sentiment, and count columns.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["period", "avg_sentiment", "count"])

    required = {"date", "sentiment_score"}
    if not required.issubset(df.columns):
        return pd.DataFrame(columns=["period", "avg_sentiment", "count"])

    temp = df.copy()
    temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
    temp = temp.dropna(subset=["date", "sentiment_score"])

    if temp.empty:
        return pd.DataFrame(columns=["period", "avg_sentiment", "count"])

    grouped = temp.set_index("date").resample(freq)["sentiment_score"]
    result = grouped.agg(["mean", "count"]).reset_index()
    result.columns = ["period", "avg_sentiment", "count"]
    result["avg_sentiment"] = result["avg_sentiment"].round(4)

    return result


def get_sentiment_by_group(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """
    Aggregate sentiment by a grouping column.

    Args:
        df: DataFrame with 'sentiment_score' and the specified group column.
        group_col: Column name to group by.

    Returns:
        DataFrame with group, mean_sentiment, count, and std columns.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=[group_col, "mean_sentiment", "count", "std"])

    if group_col not in df.columns or "sentiment_score" not in df.columns:
        return pd.DataFrame(columns=[group_col, "mean_sentiment", "count", "std"])

    temp = df.dropna(subset=[group_col, "sentiment_score"])

    if temp.empty:
        return pd.DataFrame(columns=[group_col, "mean_sentiment", "count", "std"])

    grouped = temp.groupby(group_col)["sentiment_score"].agg(
        mean_sentiment="mean", count="count", std="std"
    ).reset_index()

    grouped["mean_sentiment"] = grouped["mean_sentiment"].round(4)
    grouped["std"] = grouped["std"].round(4).fillna(0.0)
    grouped = grouped.sort_values("mean_sentiment", ascending=False).reset_index(drop=True)

    return grouped
