"""
SharkNinja Dashboard - Topic Explorer Page
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import ast as _ast
import re
from collections import Counter

from utils.data_loader import load_data
from config import PRODUCT_CATEGORIES, BRANDS, PLATFORMS, COLOR_SCHEME

try:
    from analysis.topics import get_topic_frequency, get_topic_sentiment, get_topic_trends, get_top_phrases, get_emerging_topics
except ImportError:
    get_topic_frequency = None
    get_topic_sentiment = None
    get_topic_trends = None
    get_top_phrases = None
    get_emerging_topics = None

st.set_page_config(page_title="Topic Explorer - SharkNinja", page_icon="\U0001f4ac", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, h4 { color: #FAFAFA !important; }
    .stPlotlyChart { background: #1A1F2E; border-radius: 12px; padding: 8px; border: 1px solid #2A2F3E; }
    .phrase-chip {
        display: inline-block; background: #232839; border: 1px solid #2A2F3E;
        border-radius: 20px; padding: 6px 14px; margin: 4px;
        color: #FAFAFA; font-size: 0.85rem;
    }
    .emerging-tag {
        display: inline-block; background: linear-gradient(135deg, #E63946 0%, #c92a37 100%);
        border-radius: 4px; padding: 2px 8px; margin-left: 8px;
        color: white; font-size: 0.7rem; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def styled_layout(fig, height=400):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLOR_SCHEME["text"], family="Inter, sans-serif"),
        height=height, margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(gridcolor=COLOR_SCHEME["grid"], showline=False),
        yaxis=dict(gridcolor=COLOR_SCHEME["grid"], showline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


def parse_topics(series):
    all_topics = []
    for t in series.dropna():
        if isinstance(t, str):
            try:
                parsed = _ast.literal_eval(t)
                if isinstance(parsed, list):
                    all_topics.extend(parsed)
                    continue
            except (ValueError, SyntaxError):
                pass
            all_topics.extend([x.strip() for x in t.split(",") if x.strip()])
        elif isinstance(t, list):
            all_topics.extend(t)
    return all_topics


def compute_topic_freq(df_in, top_n=20):
    topics = parse_topics(df_in["topics"])
    if not topics:
        return pd.DataFrame(columns=["topic", "count"])
    freq = pd.Series(topics).value_counts().head(top_n).reset_index()
    freq.columns = ["topic", "count"]
    return freq


def compute_topic_sentiment(df_in):
    rows = []
    for _, row in df_in.iterrows():
        topics = []
        t = row.get("topics", "")
        if isinstance(t, str):
            try:
                parsed = _ast.literal_eval(t)
                if isinstance(parsed, list):
                    topics = parsed
            except (ValueError, SyntaxError):
                topics = [x.strip() for x in t.split(",") if x.strip()]
        elif isinstance(t, list):
            topics = t
        for topic in topics:
            rows.append({"topic": topic, "sentiment_score": row["sentiment_score"]})
    if not rows:
        return pd.DataFrame(columns=["topic", "avg_sentiment", "count"])
    tdf = pd.DataFrame(rows)
    result = tdf.groupby("topic").agg(avg_sentiment=("sentiment_score", "mean"), count=("sentiment_score", "count")).reset_index()
    return result


# --- Data ---
if "filtered_df" in st.session_state:
    df = st.session_state["filtered_df"]
else:
    @st.cache_data(ttl=300)
    def _load():
        return load_data()
    df = _load()

st.markdown("## \U0001f4ac Topic Explorer")
st.markdown("Discover what consumers are talking about and how they feel about each topic.")
st.markdown("---")

if len(df) == 0:
    st.warning("No data available. Please adjust filters on the main page.")
    st.stop()

# --- Word Cloud ---
st.markdown("#### Word Cloud")
all_topics = parse_topics(df["topics"])

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.use("Agg")

    if all_topics:
        topic_freq = Counter(all_topics)
        wc = WordCloud(
            width=1200, height=500,
            background_color="#0E1117",
            colormap="cool",
            max_words=100,
            prefer_horizontal=0.7,
            min_font_size=10,
        ).generate_from_frequencies(topic_freq)

        fig_wc, ax = plt.subplots(figsize=(14, 6))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        fig_wc.patch.set_facecolor("#0E1117")
        st.pyplot(fig_wc)
        plt.close(fig_wc)
    else:
        st.info("No topics found for word cloud.")
except ImportError:
    st.info("Install wordcloud package for word cloud visualization: pip install wordcloud")

# --- Topic Frequency Bar Chart ---
st.markdown("#### Top Topics by Frequency")
if get_topic_frequency:
    topic_freq_df = get_topic_frequency(df).head(20)
else:
    topic_freq_df = compute_topic_freq(df, 20)

if len(topic_freq_df) > 0:
    fig = px.bar(topic_freq_df, x="count", y="topic", orientation="h",
                 color_discrete_sequence=[COLOR_SCHEME["primary"]])
    fig = styled_layout(fig, height=500)
    fig.update_layout(yaxis=dict(categoryorder="total ascending"), xaxis_title="Mentions", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No topic frequency data available.")

# --- Topic-Sentiment Scatter ---
st.markdown("#### Topic Sentiment Landscape")
st.caption("X = frequency, Y = average sentiment, size = mention count")

if get_topic_sentiment:
    ts_df = get_topic_sentiment(df)
else:
    ts_df = compute_topic_sentiment(df)

if len(ts_df) > 0:
    ts_df = ts_df[ts_df["count"] >= 3]  # filter noise
    if len(ts_df) > 0:
        fig = px.scatter(ts_df, x="count", y="mean_sentiment", size="count",
                         hover_name="topic", text="topic",
                         color="mean_sentiment",
                         color_continuous_scale=[[0, COLOR_SCHEME["negative"]], [0.5, COLOR_SCHEME["neutral"]], [1, COLOR_SCHEME["positive"]]])
        fig.update_traces(textposition="top center", textfont=dict(size=9))
        fig = styled_layout(fig, height=500)
        fig.update_layout(xaxis_title="Frequency (mentions)", yaxis_title="Avg Sentiment Score", coloraxis_showscale=False)
        # Add reference line at neutral
        fig.add_hline(y=0, line_dash="dash", line_color=COLOR_SCHEME["neutral"], opacity=0.5)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough topic data for scatter plot.")
else:
    st.info("No topic sentiment data available.")

# --- Topic Trends ---
st.markdown("#### Topic Trends Over Time")

top_topics = parse_topics(df["topics"])
if top_topics:
    top_5 = pd.Series(top_topics).value_counts().head(5).index.tolist()

    trend_rows = []
    for _, row in df.iterrows():
        topics = []
        t = row.get("topics", "")
        if isinstance(t, str):
            try:
                parsed = _ast.literal_eval(t)
                if isinstance(parsed, list):
                    topics = parsed
            except (ValueError, SyntaxError):
                topics = [x.strip() for x in t.split(",") if x.strip()]
        elif isinstance(t, list):
            topics = t
        for topic in topics:
            if topic in top_5:
                trend_rows.append({"date": row["date"], "topic": topic})

    if trend_rows:
        trend_df = pd.DataFrame(trend_rows)
        trend_df["date"] = pd.to_datetime(trend_df["date"])
        weekly = trend_df.set_index("date").groupby("topic").resample("W").size().reset_index(name="count")

        fig = px.line(weekly, x="date", y="count", color="topic",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(line=dict(width=2.5))
        fig = styled_layout(fig, height=400)
        fig.update_layout(xaxis_title="", yaxis_title="Weekly Mentions")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough trend data.")
else:
    st.info("No topics found for trend analysis.")

# --- Emerging Topics ---
st.markdown("#### Emerging Topics")
st.caption("Topics with significant recent growth in mentions.")

if get_emerging_topics:
    emerging = get_emerging_topics(df)
    if emerging is not None and len(emerging) > 0:
        for item in emerging[:10]:
            st.markdown(f'<span class="phrase-chip">{item.get("topic", "N/A")}</span>'
                        f'<span class="emerging-tag">EMERGING</span>', unsafe_allow_html=True)
    else:
        st.info("No emerging topics detected.")
else:
    # Fallback: compare recent vs older period
    if len(df) > 0 and "date" in df.columns:
        median_date = df["date"].median()
        recent = df[df["date"] >= median_date]
        older = df[df["date"] < median_date]
        recent_topics = Counter(parse_topics(recent["topics"]))
        older_topics = Counter(parse_topics(older["topics"]))

        emerging_list = []
        for topic, count in recent_topics.items():
            old_count = older_topics.get(topic, 0)
            if count >= 3 and (old_count == 0 or count / max(old_count, 1) >= 1.5):
                emerging_list.append({"topic": topic, "recent": count, "older": old_count,
                                      "growth": count / max(old_count, 1)})

        if emerging_list:
            em_df = pd.DataFrame(emerging_list).sort_values("growth", ascending=False).head(10)
            for _, row in em_df.iterrows():
                growth_pct = (row["growth"] - 1) * 100
                st.markdown(f'<span class="phrase-chip">{row["topic"]} ({row["recent"]} mentions)</span>'
                            f'<span class="emerging-tag">+{growth_pct:.0f}%</span>', unsafe_allow_html=True)
        else:
            st.info("No significant emerging topics detected.")
    else:
        st.info("Insufficient data for emerging topic analysis.")

# --- Common Phrases ---
st.markdown("---")
st.markdown("#### Common Phrases")

if get_top_phrases:
    texts_list = df["text"].dropna().tolist()
    phrases = get_top_phrases(texts_list, n=20)
    if phrases is not None and len(phrases) > 0:
        for phrase, count in phrases:
            st.markdown(f'<span class="phrase-chip">{phrase} ({count})</span>',
                        unsafe_allow_html=True)
    else:
        st.info("No phrase data available.")
else:
    # Fallback: extract bigrams
    from collections import Counter as _Counter
    texts = df["text"].dropna().str.lower().tolist()
    bigrams = []
    stop_words = {"the", "a", "an", "is", "it", "to", "in", "for", "and", "of", "on", "i", "my", "this", "that", "with", "was", "but", "have", "has", "had", "not", "are", "be", "so", "very", "just", "from", "at", "by", "or", "as", "if", "they", "we", "you", "its", "been", "no", "do", "did", "can", "will", "would", "could", "should", "than", "then", "them", "their", "there", "these", "those", "which", "what", "when", "where", "who", "how", "all", "each", "every", "both", "few", "more", "most", "other", "some", "such", "only", "own", "same", "too", "also", "about", "after", "again", "any", "because", "before", "between", "does", "during", "even", "get", "got", "here", "him", "her", "into", "like", "made", "make", "many", "may", "me", "might", "much", "must", "now", "off", "once", "one", "our", "out", "over", "own", "said", "she", "he", "still", "take", "tell", "thing", "think", "through", "time", "under", "until", "up", "us", "use", "used", "using", "want", "way", "well", "went", "were", "while", "work", "year"}
    for text in texts[:2000]:
        words = re.findall(r"\b[a-z]{3,}\b", text)
        words = [w for w in words if w not in stop_words]
        for j in range(len(words) - 1):
            bigrams.append(f"{words[j]} {words[j+1]}")

    if bigrams:
        top_bigrams = _Counter(bigrams).most_common(20)
        for phrase, count in top_bigrams:
            st.markdown(f'<span class="phrase-chip">{phrase} ({count})</span>', unsafe_allow_html=True)
    else:
        st.info("No phrase data could be extracted.")

# --- Topic Drill-Down ---
st.markdown("---")
st.markdown("#### Topic Drill-Down")

all_topic_list = sorted(set(parse_topics(df["topics"])))
if all_topic_list:
    selected_topic = st.selectbox("Select a topic to view related reviews", all_topic_list)

    if selected_topic:
        # Filter reviews containing this topic
        mask = df["topics"].apply(lambda x: selected_topic in str(x) if pd.notna(x) else False)
        topic_reviews = df[mask].sort_values("sentiment_score", ascending=True)

        st.markdown(f"**{len(topic_reviews)} reviews** mention *{selected_topic}*")
        if len(topic_reviews) > 0:
            avg_s = topic_reviews["sentiment_score"].mean()
            color = COLOR_SCHEME["positive"] if avg_s > 0.2 else (COLOR_SCHEME["negative"] if avg_s < -0.2 else COLOR_SCHEME["neutral"])
            st.markdown(f'Average sentiment: <strong style="color:{color};">{avg_s:.3f}</strong>', unsafe_allow_html=True)

            for _, row in topic_reviews.head(15).iterrows():
                s = row["sentiment_score"]
                sc = COLOR_SCHEME["positive"] if s > 0.2 else (COLOR_SCHEME["negative"] if s < -0.2 else COLOR_SCHEME["neutral"])
                with st.expander(f'{row["product_name"]} | {row["platform"]} | Score: {s:.3f}'):
                    st.write(row["text"])
else:
    st.info("No topics available for drill-down.")
