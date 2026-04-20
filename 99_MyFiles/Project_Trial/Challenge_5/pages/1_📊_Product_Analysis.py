"""
SharkNinja Dashboard - Product Analysis Page
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast as _ast

from utils.data_loader import load_data, filter_data
from config import PRODUCT_CATEGORIES, BRANDS, PLATFORMS, COLOR_SCHEME, BRAND_CATEGORY_MAP

try:
    from analysis.sentiment import get_sentiment_distribution, get_sentiment_by_group
except ImportError:
    get_sentiment_distribution = None
    get_sentiment_by_group = None

st.set_page_config(page_title="Product Analysis - SharkNinja", page_icon="\U0001f4ca", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, h4 { color: #FAFAFA !important; }
    .stPlotlyChart { background: #1A1F2E; border-radius: 12px; padding: 8px; border: 1px solid #2A2F3E; }
    .product-card {
        background: linear-gradient(135deg, #1A1F2E 0%, #232839 100%);
        border: 1px solid #2A2F3E; border-radius: 12px; padding: 20px;
        margin-bottom: 10px;
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


# --- Data ---
if "filtered_df" in st.session_state:
    df = st.session_state["filtered_df"]
else:
    @st.cache_data(ttl=300)
    def _load():
        return load_data()
    df = _load()

st.markdown("## \U0001f4ca Product Analysis")
st.markdown("Deep-dive into product-level sentiment and performance metrics.")
st.markdown("---")

if len(df) == 0:
    st.warning("No data available. Please adjust filters on the main page.")
    st.stop()

# --- Category selector ---
cat_display = list(PRODUCT_CATEGORIES.values())
selected_cat_display = st.selectbox("Select Product Category", ["All Categories"] + cat_display)

if selected_cat_display == "All Categories":
    df_cat = df
else:
    cat_key = {v: k for k, v in PRODUCT_CATEGORIES.items()}.get(selected_cat_display, "")
    df_cat = df[df["product_category"].str.lower() == cat_key.lower()]

if len(df_cat) == 0:
    st.info("No data for the selected category.")
    st.stop()

# --- Sentiment by Category ---
st.markdown("#### Sentiment by Product Category")
cat_sent = df.groupby("product_category").agg(
    avg_sentiment=("sentiment_score", "mean"),
    review_count=("id", "count")
).reset_index()
cat_sent["category_label"] = cat_sent["product_category"].map(PRODUCT_CATEGORIES).fillna(cat_sent["product_category"])

fig = px.bar(cat_sent.sort_values("avg_sentiment", ascending=True),
             x="avg_sentiment", y="category_label", orientation="h",
             color="avg_sentiment",
             color_continuous_scale=[[0, COLOR_SCHEME["negative"]], [0.5, COLOR_SCHEME["neutral"]], [1, COLOR_SCHEME["positive"]]],
             text="review_count")
fig.update_traces(texttemplate="%{text} reviews", textposition="outside")
fig = styled_layout(fig, height=350)
fig.update_layout(xaxis_title="Average Sentiment Score", yaxis_title="", coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)

# --- Product Ranking ---
st.markdown("#### Product Ranking by Sentiment")
prod_sent = df_cat.groupby("product_name").agg(
    avg_sentiment=("sentiment_score", "mean"),
    review_count=("id", "count"),
    avg_rating=("rating", "mean")
).reset_index().sort_values("avg_sentiment", ascending=False)

if len(prod_sent) > 0:
    fig = px.bar(prod_sent, x="product_name", y="avg_sentiment",
                 color="avg_sentiment",
                 color_continuous_scale=[[0, COLOR_SCHEME["negative"]], [0.5, COLOR_SCHEME["neutral"]], [1, COLOR_SCHEME["positive"]]],
                 text="review_count", hover_data=["avg_rating"])
    fig.update_traces(texttemplate="%{text} reviews", textposition="outside")
    fig = styled_layout(fig, height=400)
    fig.update_layout(xaxis_title="", yaxis_title="Avg Sentiment", xaxis_tickangle=-30, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# --- Sentiment Distribution Box Plot ---
st.markdown("#### Sentiment Distribution per Product")
if len(df_cat["product_name"].unique()) > 1:
    fig = px.box(df_cat, x="product_name", y="sentiment_score",
                 color_discrete_sequence=[COLOR_SCHEME["primary"]])
    fig = styled_layout(fig, height=400)
    fig.update_layout(xaxis_title="", yaxis_title="Sentiment Score", xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
else:
    fig = px.histogram(df_cat, x="sentiment_score", nbins=30,
                       color_discrete_sequence=[COLOR_SCHEME["primary"]])
    fig = styled_layout(fig, height=350)
    fig.update_layout(xaxis_title="Sentiment Score", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

# --- Top Positive / Negative Reviews ---
st.markdown("#### Top Reviews")
pos_tab, neg_tab = st.tabs(["\u2705 Most Positive", "\u274c Most Negative"])

with pos_tab:
    top_pos = df_cat.nlargest(10, "sentiment_score")
    for _, row in top_pos.iterrows():
        with st.expander(f"{row['product_name']} | Score: {row['sentiment_score']:.3f} | {row['platform']}"):
            st.write(row["text"])

with neg_tab:
    top_neg = df_cat.nsmallest(10, "sentiment_score")
    for _, row in top_neg.iterrows():
        with st.expander(f"{row['product_name']} | Score: {row['sentiment_score']:.3f} | {row['platform']}"):
            st.write(row["text"])

# --- Comparison Mode ---
st.markdown("---")
st.markdown("#### \U0001f50d Product Comparison")

products_available = sorted(df_cat["product_name"].unique().tolist())
if len(products_available) >= 2:
    comp_col1, comp_col2 = st.columns(2)
    with comp_col1:
        prod_a = st.selectbox("Product A", products_available, index=0)
    with comp_col2:
        default_b = 1 if len(products_available) > 1 else 0
        prod_b = st.selectbox("Product B", products_available, index=default_b)

    if prod_a and prod_b and prod_a != prod_b:
        df_a = df_cat[df_cat["product_name"] == prod_a]
        df_b = df_cat[df_cat["product_name"] == prod_b]

        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown(f'<div class="product-card"><h4 style="color:#00B4D8;">{prod_a}</h4>'
                        f'<p>Reviews: {len(df_a)} | Avg Sentiment: {df_a["sentiment_score"].mean():.3f} | '
                        f'Avg Rating: {df_a["rating"].mean():.1f}</p></div>', unsafe_allow_html=True)
        with mc2:
            st.markdown(f'<div class="product-card"><h4 style="color:#F4A261;">{prod_b}</h4>'
                        f'<p>Reviews: {len(df_b)} | Avg Sentiment: {df_b["sentiment_score"].mean():.3f} | '
                        f'Avg Rating: {df_b["rating"].mean():.1f}</p></div>', unsafe_allow_html=True)

        # Comparison chart
        comp_data = pd.DataFrame({
            "Product": [prod_a, prod_b],
            "Avg Sentiment": [df_a["sentiment_score"].mean(), df_b["sentiment_score"].mean()],
            "Avg Rating": [df_a["rating"].mean(), df_b["rating"].mean()],
            "Review Count": [len(df_a), len(df_b)],
            "Positive %": [
                (df_a["sentiment_label"].str.lower() == "positive").mean() * 100,
                (df_b["sentiment_label"].str.lower() == "positive").mean() * 100,
            ]
        })

        fig = go.Figure()
        fig.add_trace(go.Bar(name=prod_a, x=["Avg Sentiment", "Positive %"],
                             y=[comp_data.iloc[0]["Avg Sentiment"], comp_data.iloc[0]["Positive %"]],
                             marker_color=COLOR_SCHEME["primary"]))
        fig.add_trace(go.Bar(name=prod_b, x=["Avg Sentiment", "Positive %"],
                             y=[comp_data.iloc[1]["Avg Sentiment"], comp_data.iloc[1]["Positive %"]],
                             marker_color=COLOR_SCHEME["ninja"]))
        fig.update_layout(barmode="group")
        fig = styled_layout(fig, height=350)
        st.plotly_chart(fig, use_container_width=True)

        # Sentiment over time comparison
        st.markdown("##### Sentiment Trend Comparison")
        trend_a = df_a.set_index("date").resample("W")["sentiment_score"].mean().reset_index()
        trend_a["product"] = prod_a
        trend_b = df_b.set_index("date").resample("W")["sentiment_score"].mean().reset_index()
        trend_b["product"] = prod_b
        trend_comp = pd.concat([trend_a, trend_b])

        fig = px.line(trend_comp, x="date", y="sentiment_score", color="product",
                      color_discrete_map={prod_a: COLOR_SCHEME["primary"], prod_b: COLOR_SCHEME["ninja"]})
        fig = styled_layout(fig, height=350)
        fig.update_layout(xaxis_title="", yaxis_title="Avg Sentiment")
        st.plotly_chart(fig, use_container_width=True)
    elif prod_a == prod_b:
        st.info("Please select two different products to compare.")
else:
    st.info("Need at least 2 products in this category for comparison.")
