"""
LAYER 1 — VADER baseline sentiment.

This is the baseline only. The enhanced pipeline in pipeline.py overrides
these results when LAYER 2 detects sarcasm, comparative claims, or aspects.
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def get_vader_scores(text: str) -> dict:
    """Return VADER polarity scores dict: neg, neu, pos, compound."""
    return _analyzer.polarity_scores(text)


def vader_label(compound: float) -> str:
    """Convert compound score to sentiment label."""
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"
