"""
SharkNinja Dashboard - Platform Comparison Page
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

from utils.data_loader import load_data
from config import PRODUCT_CATEGORIES, BRANDS, PLATFORMS, COLOR_SCHEME

try:
    from analysis.sentiment import get_sentiment_over_time, get_sentiment_by_group
    from analysis.topics import get_topic_frequency
except ImportError:
    get_sentiment_over_time = None
    get_sentiment_by_group = None
    get_topic_frequency = None

st.set_page_config(page_title="Platform Comparison - SharkNinja", page_icon="\U0001f310", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, h4 { color: #FAFAFA !important; }
    .stPlotlyChart { background: #1A1F2E; border-radius: 12px; padding: 8px; border: 1px solid #2A2F3E; }
    .insight-box {
        background: linear-gradient(135deg, #1A2332 0%, #1A1F2E 100%);
        border-left: 4px solid #00B4D8; border-radius: 8px;
        padding: 16px 20px; margin-bottom: 20px;
    }
    .insight-box h4 { margin: 0 0 8px 0; color: #00B4D8 !important; }
    .insight-box p { margin: 0; color: #FAFAFA; }
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


# --- Data ---
if "filtered_df" in st.session_state:
    df = st.session_state["filtered_df"]
else:
    @st.cache_data(ttl=300)
    def _load():
        return load_data()
    df = _load()

st.markdown("## \U0001f310 Platform Comparison")
st.markdown("Cross-platform analysis of consumer sentiment across Reddit, Amazon & TikTok.")
st.markdown("---")

if len(df) == 0:
    st.warning("No data available. Please adjust filters on the main page.")
    st.stop()

platforms_in_data = df["platform"].unique().tolist()
platform_color_map = {"reddit": COLOR_SCHEME["reddit"], "amazon": COLOR_SCHEME["amazon"], "tiktok": COLOR_SCHEME["tiktok"]}

# --- Key Insight Callout ---
plat_sent = df.groupby("platform")["sentiment_score"].mean()
best_plat = plat_sent.idxmax()
worst_plat = plat_sent.idxmin()
gap = plat_sent.max() - plat_sent.min()

insight_html = f"""<div class="insight-box">
    <h4>\U0001f4a1 Key Insight</h4>
    <p><strong>{best_plat.title()}</strong> has the highest average sentiment ({plat_sent.max():.3f}),
    while <strong>{worst_plat.title()}</strong> has the lowest ({plat_sent.min():.3f}).
    The cross-platform sentiment gap is <strong>{gap:.3f}</strong>.</p>
</div>"""
st.markdown(insight_html, unsafe_allow_html=True)

# --- Sentiment Comparison Bar Chart ---
st.markdown("#### Sentiment Comparison by Platform")
plat_stats = df.groupby("platform").agg(
    avg_sentiment=("sentiment_score", "mean"),
    review_count=("id", "count"),
    positive_pct=("sentiment_label", lambda x: (x.str.lower() == "positive").mean() * 100)
).reset_index()

fig = px.bar(plat_stats, x="platform", y="avg_sentiment",
             color="platform", color_discrete_map=platform_color_map,
             text="avg_sentiment", hover_data=["review_count", "positive_pct"])
fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
fig = styled_layout(fig, height=380)
fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Average Sentiment Score")
st.plotly_chart(fig, use_container_width=True)

# --- Volume Over Time Stacked Area ---
st.markdown("#### Review Volume Over Time by Platform")
vol_time = df.set_index("date").groupby("platform").resample("W").size().reset_index(name="count")

fig = px.area(vol_time, x="date", y="count", color="platform",
              color_discrete_map=platform_color_map)
fig = styled_layout(fig, height=380)
fig.update_layout(xaxis_title="", yaxis_title="Weekly Review Count")
st.plotly_chart(fig, use_container_width=True)

# --- Topic-Platform Heatmap ---
st.markdown("#### Topic-Platform Heatmap")

# Build topic-platform matrix
topic_plat_data = []
for plat in platforms_in_data:
    plat_df = df[df["platform"] == plat]
    topics = parse_topics(plat_df["topics"])
    if topics:
        freq = pd.Series(topics).value_counts().head(15)
        for topic, count in freq.items():
            topic_plat_data.append({"platform": plat, "topic": topic, "count": count})

if topic_plat_data:
    tp_df = pd.DataFrame(topic_plat_data)
    pivot = tp_df.pivot_table(index="topic", columns="platform", values="count", fill_value=0)
    # Keep top 15 topics by total mentions
    pivot["total"] = pivot.sum(axis=1)
    pivot = pivot.nlargest(15, "total").drop(columns=["total"])

    fig = px.imshow(pivot.values,
                    x=pivot.columns.tolist(),
                    y=pivot.index.tolist(),
                    color_continuous_scale="Viridis",
                    aspect="auto")
    fig = styled_layout(fig, height=500)
    fig.update_layout(xaxis_title="Platform", yaxis_title="Topic")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No topic data available for heatmap.")

# --- Sentiment Trends Per Platform ---
st.markdown("#### Sentiment Trends by Platform")
trend_data = []
for plat in platforms_in_data:
    plat_df = df[df["platform"] == plat]
    if len(plat_df) > 0:
        weekly = plat_df.set_index("date").resample("W")["sentiment_score"].mean().reset_index()
        weekly["platform"] = plat
        trend_data.append(weekly)

if trend_data:
    all_trends = pd.concat(trend_data)
    fig = px.line(all_trends, x="date", y="sentiment_score", color="platform",
                  color_discrete_map=platform_color_map)
    fig.update_traces(line=dict(width=2.5))
    fig = styled_layout(fig, height=400)
    fig.update_layout(xaxis_title="", yaxis_title="Avg Sentiment Score")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Not enough data for trend analysis.")

# --- Platform Detail Metrics ---
st.markdown("---")
st.markdown("#### Platform Detail Metrics")
cols = st.columns(len(platforms_in_data))
for i, plat in enumerate(platforms_in_data):
    plat_df = df[df["platform"] == plat]
    with cols[i]:
        color = platform_color_map.get(plat.lower(), COLOR_SCHEME["primary"])
        st.markdown(f'<div style="background:#1A1F2E;border-top:3px solid {color};border-radius:8px;padding:16px;">'
                    f'<h4 style="color:{color};margin:0;">{plat.title()}</h4>'
                    f'<p style="color:#8D99AE;margin:4px 0;">Reviews: <strong style="color:#FAFAFA;">{len(plat_df):,}</strong></p>'
                    f'<p style="color:#8D99AE;margin:4px 0;">Avg Sentiment: <strong style="color:#FAFAFA;">{plat_df["sentiment_score"].mean():.3f}</strong></p>'
                    f'<p style="color:#8D99AE;margin:4px 0;">Avg Rating: <strong style="color:#FAFAFA;">{plat_df["rating"].mean():.1f}</strong></p>'
                    f'<p style="color:#8D99AE;margin:4px 0;">Positive: <strong style="color:{COLOR_SCHEME["positive"]};">'
                    f'{(plat_df["sentiment_label"].str.lower() == "positive").mean() * 100:.1f}%</strong></p>'
                    f'</div>', unsafe_allow_html=True)
