"""
Topic extraction module using keyword matching and phrase analysis.
"""

import re
from collections import Counter
from datetime import timedelta

import pandas as pd
import nltk

# Ensure stopwords are available
try:
    from nltk.corpus import stopwords
    _STOP_WORDS = set(stopwords.words("english"))
except Exception:
    nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords
    _STOP_WORDS = set(stopwords.words("english"))


TOPIC_KEYWORDS = {
    "Suction Power": ["suction", "vacuum power", "picks up", "cleaning power"],
    "Battery Life": ["battery", "charge", "runtime", "dies", "lasts"],
    "Noise Level": ["noise", "loud", "quiet", "silent", "noisy", "sound"],
    "Build Quality": ["build", "quality", "durable", "broke", "flimsy", "sturdy", "cheap"],
    "Ease of Use": ["easy", "simple", "intuitive", "complicated", "confusing", "user-friendly"],
    "Value for Money": ["price", "value", "worth", "expensive", "affordable", "overpriced"],
    "Customer Service": ["customer service", "support", "warranty", "return", "replacement"],
    "App Experience": ["app", "wifi", "connect", "smart", "alexa", "google"],
    "Cleaning Performance": ["clean", "spotless", "streak", "residue", "thorough"],
    "Design": ["design", "look", "aesthetic", "sleek", "bulky", "compact", "lightweight"],
    "Cooking Quality": ["cook", "crispy", "tender", "burnt", "evenly", "delicious", "taste"],
    "Capacity": ["capacity", "size", "fit", "small", "large", "family"],
    "Pet Hair": ["pet", "hair", "fur", "dog", "cat", "shedding"],
    "Maintenance": ["filter", "maintenance", "clean the", "wash", "replace", "clog"],
}
# Pre-compile patterns
_COMPILED_PATTERNS = {}
for _topic, _keywords in TOPIC_KEYWORDS.items():
    patterns = []
    for kw in sorted(_keywords, key=len, reverse=True):
        if " " in kw:
            patterns.append(re.compile(re.escape(kw), re.IGNORECASE))
        else:
            patterns.append(re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE))
    _COMPILED_PATTERNS[_topic] = patterns


def extract_topics(text: str) -> list:
    """
    Extract topics from a single text string using keyword matching.

    Args:
        text: Input text.

    Returns:
        List of topic names found in the text.
    """
    if not text or not isinstance(text, str) or text.strip() == "":
        return []

    found = []
    for topic, patterns in _COMPILED_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                found.append(topic)
                break
    return found


def batch_extract_topics(texts: list) -> list:
    """
    Extract topics for a list of texts.

    Args:
        texts: List of text strings.

    Returns:
        List of lists of topic names.
    """
    if not texts:
        return []
    return [extract_topics(t) for t in texts]

def get_topic_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get frequency of each topic across all reviews.

    Args:
        df: DataFrame with a topics column (lists of topic strings).

    Returns:
        DataFrame with topic, count, percentage columns sorted by count descending.
    """
    if df is None or df.empty or "topics" not in df.columns:
        return pd.DataFrame(columns=["topic", "count", "percentage"])

    exploded = df["topics"].explode().dropna()
    exploded = exploded[exploded.astype(str).str.strip() != ""]

    if exploded.empty:
        return pd.DataFrame(columns=["topic", "count", "percentage"])

    counts = exploded.value_counts().reset_index()
    counts.columns = ["topic", "count"]

    total = len(df)
    counts["percentage"] = (counts["count"] / total * 100).round(2)
    counts = counts.sort_values("count", ascending=False).reset_index(drop=True)

    return counts

def get_topic_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get average sentiment per topic.

    Args:
        df: DataFrame with topics (list), sentiment_score, and sentiment_label columns.

    Returns:
        DataFrame with topic, mean_sentiment, count, and label distribution columns.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["topic", "mean_sentiment", "count", "positive_pct", "neutral_pct", "negative_pct"])

    required = {"topics", "sentiment_score", "sentiment_label"}
    if not required.issubset(df.columns):
        return pd.DataFrame(columns=["topic", "mean_sentiment", "count", "positive_pct", "neutral_pct", "negative_pct"])

    rows = []
    for _, row in df.iterrows():
        topics = row.get("topics", [])
        if not isinstance(topics, list):
            continue
        for topic in topics:
            rows.append({
                "topic": topic,
                "sentiment_score": row["sentiment_score"],
                "sentiment_label": row["sentiment_label"],
            })

    if not rows:
        return pd.DataFrame(columns=["topic", "mean_sentiment", "count", "positive_pct", "neutral_pct", "negative_pct"])

    exploded = pd.DataFrame(rows)

    grouped = exploded.groupby("topic").agg(
        mean_sentiment=("sentiment_score", "mean"),
        count=("sentiment_score", "count"),
    ).reset_index()

    # Calculate label distribution per topic
    label_dist = exploded.groupby(["topic", "sentiment_label"]).size().unstack(fill_value=0)
    label_totals = label_dist.sum(axis=1)

    for label in ["positive", "neutral", "negative"]:
        col = f"{label}_pct"
        if label in label_dist.columns:
            grouped[col] = grouped["topic"].map(
                lambda t, lb=label: round(
                    label_dist.loc[t, lb] / label_totals.loc[t] * 100, 2
                ) if t in label_dist.index and lb in label_dist.columns else 0.0
            )
        else:
            grouped[col] = 0.0

    grouped["mean_sentiment"] = grouped["mean_sentiment"].round(4)
    grouped = grouped.sort_values("mean_sentiment", ascending=False).reset_index(drop=True)

    return grouped

def get_topic_trends(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """
    Get topic frequency over time periods.

    Args:
        df: DataFrame with date (datetime) and topics (list) columns.
        freq: Pandas frequency string.

    Returns:
        DataFrame with period, topic, and count columns.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["period", "topic", "count"])

    required = {"date", "topics"}
    if not required.issubset(df.columns):
        return pd.DataFrame(columns=["period", "topic", "count"])

    temp = df.copy()
    temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
    temp = temp.dropna(subset=["date"])

    if temp.empty:
        return pd.DataFrame(columns=["period", "topic", "count"])

    rows = []
    for _, row in temp.iterrows():
        topics = row.get("topics", [])
        if not isinstance(topics, list):
            continue
        for topic in topics:
            rows.append({"date": row["date"], "topic": topic})

    if not rows:
        return pd.DataFrame(columns=["period", "topic", "count"])

    exploded = pd.DataFrame(rows)
    exploded["period"] = exploded["date"].dt.to_period(freq)

    result = exploded.groupby(["period", "topic"]).size().reset_index(name="count")
    result = result.sort_values(["period", "count"], ascending=[True, False]).reset_index(drop=True)

    return result

def get_top_phrases(texts: list, n: int = 20) -> list:
    """
    Extract most common bigrams and trigrams from texts, filtering stopwords.

    Args:
        texts: List of text strings.
        n: Number of top phrases to return.

    Returns:
        List of (phrase, count) tuples sorted by count descending.
    """
    if not texts:
        return []

    # Tokenize and clean
    all_tokens = []
    for text in texts:
        if not text or not isinstance(text, str):
            continue
        cleaned = re.sub(r"[^a-zA-Z\s]", " ", text.lower())
        tokens = [t for t in cleaned.split() if t and t not in _STOP_WORDS and len(t) > 1]
        all_tokens.append(tokens)

    if not all_tokens:
        return []

    phrase_counter = Counter()

    for tokens in all_tokens:
        # Bigrams
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i+1]}"
            phrase_counter[bigram] += 1

        # Trigrams
        for i in range(len(tokens) - 2):
            trigram = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
            phrase_counter[trigram] += 1

    return phrase_counter.most_common(n)

def get_emerging_topics(df: pd.DataFrame, lookback_days: int = 30) -> list:
    """
    Identify topics with significant frequency increase in the recent period
    compared to the prior period of equal length.

    Args:
        df: DataFrame with date (datetime) and topics (list) columns.
        lookback_days: Number of days for the recent window.

    Returns:
        List of dicts with topic, recent_count, prior_count, and growth_rate.
    """
    if df is None or df.empty:
        return []

    required = {"date", "topics"}
    if not required.issubset(df.columns):
        return []

    temp = df.copy()
    temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
    temp = temp.dropna(subset=["date"])

    if temp.empty:
        return []

    max_date = temp["date"].max()
    recent_start = max_date - timedelta(days=lookback_days)
    prior_start = recent_start - timedelta(days=lookback_days)

    recent_df = temp[temp["date"] > recent_start]
    prior_df = temp[(temp["date"] > prior_start) & (temp["date"] <= recent_start)]

    def count_topics(subset):
        counter = Counter()
        for topics_list in subset["topics"]:
            if isinstance(topics_list, list):
                for t in topics_list:
                    counter[t] += 1
        return counter

    recent_counts = count_topics(recent_df)
    prior_counts = count_topics(prior_df)

    all_topics = set(recent_counts.keys()) | set(prior_counts.keys())

    results = []
    for topic in all_topics:
        recent_c = recent_counts.get(topic, 0)
        prior_c = prior_counts.get(topic, 0)

        if prior_c == 0 and recent_c > 0:
            growth_rate = float("inf")
        elif prior_c == 0:
            continue
        else:
            growth_rate = (recent_c - prior_c) / prior_c

        # Only include topics with positive growth
        if growth_rate > 0:
            results.append({
                "topic": topic,
                "recent_count": recent_c,
                "prior_count": prior_c,
                "growth_rate": round(growth_rate, 4) if growth_rate != float("inf") else float("inf"),
            })

    results.sort(key=lambda x: x["growth_rate"], reverse=True)

    return results
