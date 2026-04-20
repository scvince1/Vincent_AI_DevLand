"""
SharkNinja Consumer Sentiment Dashboard - Main Page
"""

import sys
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast as _ast
from datetime import datetime, timedelta

from utils.data_loader import load_data, filter_data
from config import PRODUCT_CATEGORIES, BRANDS, PLATFORMS, COLOR_SCHEME

try:
    from analysis.sentiment import get_sentiment_distribution, get_sentiment_over_time, get_sentiment_by_group
    from analysis.topics import get_topic_frequency
except ImportError:
    get_sentiment_distribution = None
    get_sentiment_over_time = None
    get_sentiment_by_group = None
    get_topic_frequency = None

st.set_page_config(
    page_title="SharkNinja Sentiment Dashboard",
    page_icon="\U0001f988",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .stApp { background-color: #0E1117; }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1A1F2E 0%, #232839 100%);
        border: 1px solid #2A2F3E; border-radius: 12px;
        padding: 20px 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetric"] label {
        color: #8D99AE !important; font-size: 0.85rem !important;
        font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #FAFAFA !important; font-size: 2rem !important; font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #141824; border-right: 1px solid #2A2F3E;
    }
    h1, h2, h3 { color: #FAFAFA !important; }
    .stPlotlyChart {
        background: #1A1F2E; border-radius: 12px; padding: 8px; border: 1px solid #2A2F3E;
    }
    hr { border-color: #2A2F3E; }
    .banner-title {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #00B4D8, #0077B6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;
    }
    .banner-sub { color: #8D99AE; font-size: 1rem; margin-top: 0; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=300)
def get_data():
    return load_data()


df_all = get_data()

# --- Sidebar ---
with st.sidebar:
    st.markdown("### \U0001f988 SharkNinja Filters")
    st.markdown("---")
    if len(df_all) > 0 and "date" in df_all.columns:
        min_date = df_all["date"].min()
        max_date = df_all["date"].max()
        if pd.isna(min_date):
            min_date = datetime.now() - timedelta(days=90)
        if pd.isna(max_date):
            max_date = datetime.now()
        min_date = pd.Timestamp(min_date).date()
        max_date = pd.Timestamp(max_date).date()
    else:
        min_date = (datetime.now() - timedelta(days=90)).date()
        max_date = datetime.now().date()

    date_range = st.date_input("Date Range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)
    platform_options = list(PLATFORMS.values())
    selected_platforms = st.multiselect("Platforms", platform_options, default=platform_options)
    brand_options = list(BRANDS.values())
    selected_brands = st.multiselect("Brands", brand_options, default=brand_options)
    category_options = list(PRODUCT_CATEGORIES.values())
    selected_categories = st.multiselect("Categories", category_options, default=category_options)
    st.markdown("---")
    apply_clicked = st.button("\U0001f50d Apply Filters", use_container_width=True, type="primary")

# --- Filter logic ---
platform_key_map = {v: k for k, v in PLATFORMS.items()}
brand_key_map = {v: k for k, v in BRANDS.items()}
category_key_map = {v: k for k, v in PRODUCT_CATEGORIES.items()}


def apply_filters(source_df):
    filt = source_df.copy()
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        s, e = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        filt = filt[(filt["date"] >= s) & (filt["date"] <= e + pd.Timedelta(days=1))]
    if selected_platforms and len(selected_platforms) < len(PLATFORMS):
        keys = [platform_key_map[p] for p in selected_platforms if p in platform_key_map]
        filt = filt[filt["platform"].str.lower().isin(keys)]
    if selected_brands and len(selected_brands) < len(BRANDS):
        keys = [brand_key_map[b] for b in selected_brands if b in brand_key_map]
        filt = filt[filt["brand"].str.lower().isin(keys)]
    if selected_categories and len(selected_categories) < len(PRODUCT_CATEGORIES):
        keys = [category_key_map[c] for c in selected_categories if c in category_key_map]
        filt = filt[filt["product_category"].str.lower().isin(keys)]
    return filt.reset_index(drop=True)


df = apply_filters(df_all)
st.session_state["filtered_df"] = df


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


def compute_topic_freq(df_in, top_n=10):
    topics = parse_topics(df_in["topics"])
    if not topics:
        return pd.DataFrame(columns=["topic", "count"])
    freq = pd.Series(topics).value_counts().head(top_n).reset_index()
    freq.columns = ["topic", "count"]
    return freq


st.markdown('<p class="banner-title">\U0001f988 SharkNinja Sentiment Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="banner-sub">Real-time consumer sentiment intelligence across Reddit, Amazon & TikTok</p>', unsafe_allow_html=True)
st.markdown("---")

if len(df) == 0:
    st.warning("No data matches the current filters. Adjust your selections in the sidebar.")
    st.stop()

total_reviews = len(df)
avg_sentiment = df["sentiment_score"].mean()
positive_pct = (df["sentiment_label"].str.lower() == "positive").sum() / max(len(df), 1) * 100

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    period_days = (pd.Timestamp(date_range[1]) - pd.Timestamp(date_range[0])).days
    if period_days > 0:
        prev_start = pd.Timestamp(date_range[0]) - pd.Timedelta(days=period_days)
        prev_end = pd.Timestamp(date_range[0]) - pd.Timedelta(days=1)
        df_prev = df_all[(df_all["date"] >= prev_start) & (df_all["date"] <= prev_end)]
    else:
        df_prev = pd.DataFrame()
else:
    df_prev = pd.DataFrame()

review_delta = total_reviews - len(df_prev) if len(df_prev) > 0 else None
sent_delta = round(avg_sentiment - df_prev["sentiment_score"].mean(), 3) if len(df_prev) > 0 else None

topics_list = parse_topics(df["topics"])
top_topic = pd.Series(topics_list).value_counts().index[0] if topics_list else "N/A"

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Reviews", f"{total_reviews:,}", delta=f"{review_delta:+,}" if review_delta is not None else None)
with c2:
    st.metric("Avg Sentiment", f"{avg_sentiment:.3f}", delta=f"{sent_delta:+.3f}" if sent_delta is not None else None)
with c3:
    st.metric("Positive %", f"{positive_pct:.1f}%")
with c4:
    st.metric("Most Discussed Topic", top_topic)

st.markdown("")

r2l, r2r = st.columns([3, 2])

with r2l:
    st.markdown("#### Sentiment Trend Over Time")
    if get_sentiment_over_time:
        trend_data = get_sentiment_over_time(df)
    else:
        trend_data = df.set_index("date").resample("W")["sentiment_score"].mean().reset_index()
        trend_data.columns = ["period", "avg_sentiment"]
        trend_data["count"] = 0
    if len(trend_data) > 0:
        fig = px.line(trend_data, x="period", y="avg_sentiment", color_discrete_sequence=[COLOR_SCHEME["primary"]])
        fig.update_traces(line=dict(width=3), fill="tozeroy", fillcolor="rgba(0,180,216,0.1)")
        fig = styled_layout(fig)
        fig.update_layout(xaxis_title="", yaxis_title="Avg Sentiment Score")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for trend chart.")

with r2r:
    st.markdown("#### Review Volume by Platform")
    pc = df["platform"].value_counts().reset_index()
    pc.columns = ["platform", "count"]
    pcmap = {"reddit": COLOR_SCHEME["reddit"], "amazon": COLOR_SCHEME["amazon"], "tiktok": COLOR_SCHEME["tiktok"]}
    fig = px.bar(pc, x="platform", y="count", color="platform",
                 color_discrete_map={r["platform"]: pcmap.get(r["platform"].lower(), COLOR_SCHEME["primary"]) for _, r in pc.iterrows()})
    fig = styled_layout(fig)
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Reviews")
    st.plotly_chart(fig, use_container_width=True)

r3l, r3r = st.columns(2)

with r3l:
    st.markdown("#### Sentiment by Brand")
    if get_sentiment_by_group:
        bs = get_sentiment_by_group(df, "brand")
    else:
        bs = df.groupby("brand")["sentiment_score"].mean().reset_index()
    if len(bs) > 0:
        fig = px.bar(bs, x="brand", y="mean_sentiment", color="brand",
                     color_discrete_map={"shark": COLOR_SCHEME["shark"], "ninja": COLOR_SCHEME["ninja"]}, text="mean_sentiment")
        fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig = styled_layout(fig, height=380)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Avg Sentiment")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No brand data available.")

with r3r:
    st.markdown("#### Top 10 Topics")
    if get_topic_frequency:
        tf = get_topic_frequency(df).head(10)
    else:
        tf = compute_topic_freq(df, 10)
    if len(tf) > 0:
        fig = px.bar(tf, x="count", y="topic", orientation="h", color_discrete_sequence=[COLOR_SCHEME["secondary"]])
        fig = styled_layout(fig, height=380)
        fig.update_layout(yaxis=dict(categoryorder="total ascending"), xaxis_title="Mentions", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No topic data available.")

st.markdown("---")
st.markdown("#### Recent Reviews")

disp = df.sort_values("date", ascending=False).head(50).copy()
disp["date_str"] = disp["date"].dt.strftime("%Y-%m-%d")


def sentiment_color(label):
    la = str(label).lower()
    pos_color = COLOR_SCHEME["positive"]
    neg_color = COLOR_SCHEME["negative"]
    neu_color = COLOR_SCHEME["neutral"]
    if la == "positive":
        return f'<span style="color:{pos_color};font-weight:600;">Positive</span>'
    elif la == "negative":
        return f'<span style="color:{neg_color};font-weight:600;">Negative</span>'
    return f'<span style="color:{neu_color};">Neutral</span>'


disp["Sentiment"] = disp["sentiment_label"].apply(sentiment_color)
disp["Score"] = disp["sentiment_score"].round(3)
disp["Review"] = disp["text"].str[:120] + "..."

tbl = disp[["date_str", "platform", "brand", "product_name", "Review", "Score", "Sentiment"]].rename(
    columns={"date_str": "Date", "platform": "Platform", "brand": "Brand", "product_name": "Product"}
).to_html(escape=False, index=False, classes="review-table")

TABLE_CSS = """<style>
    .review-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; color: #FAFAFA; }
    .review-table th { background: #1A1F2E; color: #8D99AE; padding: 10px 12px; text-align: left; border-bottom: 2px solid #2A2F3E; text-transform: uppercase; font-size: 0.75rem; }
    .review-table td { padding: 8px 12px; border-bottom: 1px solid #2A2F3E; max-width: 300px; overflow: hidden; text-overflow: ellipsis; }
    .review-table tr:hover { background: #232839; }
</style>"""
st.markdown(TABLE_CSS + tbl, unsafe_allow_html=True)

st.markdown("---")
footer_text = (
    '<div style="text-align:center;color:#8D99AE;font-size:0.8rem;">'
    + "SharkNinja Sentiment Dashboard | " + f"{total_reviews:,}" + " reviews analyzed | "
    + "Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "</div>"
)
st.markdown(footer_text, unsafe_allow_html=True)
