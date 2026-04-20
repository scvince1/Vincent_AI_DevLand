"""
SharkNinja Dashboard - Alerts & Insights Page
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import ast as _ast
from collections import Counter
from datetime import timedelta

from utils.data_loader import load_data
from config import PRODUCT_CATEGORIES, BRANDS, PLATFORMS, COLOR_SCHEME

st.set_page_config(page_title="Alerts & Insights - SharkNinja", page_icon="\U0001f6a8", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, h4 { color: #FAFAFA !important; }
    .stPlotlyChart { background: #1A1F2E; border-radius: 12px; padding: 8px; border: 1px solid #2A2F3E; }
    .alert-card {
        background: #1A1F2E; border-radius: 12px; padding: 20px; margin-bottom: 16px;
        border-left: 5px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .alert-red { border-left-color: #E63946; }
    .alert-yellow { border-left-color: #F4A261; }
    .alert-green { border-left-color: #2EC4B6; }
    .alert-card h4 { margin: 0 0 8px 0; }
    .alert-card p { margin: 0; color: #FAFAFA; font-size: 0.9rem; }
    .alert-badge {
        display: inline-block; border-radius: 4px; padding: 2px 10px;
        font-size: 0.75rem; font-weight: 700; margin-right: 8px;
    }
    .badge-critical { background: #E63946; color: white; }
    .badge-warning { background: #F4A261; color: #1A1F2E; }
    .badge-info { background: #2EC4B6; color: #1A1F2E; }
    .exec-summary {
        background: linear-gradient(135deg, #1A2332 0%, #1A1F2E 100%);
        border: 1px solid #2A2F3E; border-radius: 12px; padding: 24px;
        margin-bottom: 24px;
    }
    .exec-summary h3 { margin-top: 0; }
    .exec-summary ul { color: #FAFAFA; }
    .exec-summary li { margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)


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

st.markdown("## \U0001f6a8 Alerts & Insights")
st.markdown("Auto-generated intelligence for proactive brand management.")
st.markdown("---")

if len(df) == 0:
    st.warning("No data available. Please adjust filters on the main page.")
    st.stop()

alerts = []  # collect all alerts: (severity, title, body, category)

# =====================================================
# Detection: Products with Declining Sentiment
# =====================================================
if "date" in df.columns and len(df) > 10:
    median_date = df["date"].median()
    recent = df[df["date"] >= median_date]
    older = df[df["date"] < median_date]

    for product in df["product_name"].unique():
        recent_prod = recent[recent["product_name"] == product]
        older_prod = older[older["product_name"] == product]
        if len(recent_prod) >= 3 and len(older_prod) >= 3:
            recent_avg = recent_prod["sentiment_score"].mean()
            older_avg = older_prod["sentiment_score"].mean()
            decline = older_avg - recent_avg
            if decline > 0.1:
                severity = "critical" if decline > 0.2 else "warning"
                alerts.append((
                    severity,
                    f"Declining Sentiment: {product}",
                    f"Sentiment dropped by {decline:.3f} (from {older_avg:.3f} to {recent_avg:.3f}). "
                    f"Based on {len(recent_prod)} recent vs {len(older_prod)} older reviews.",
                    "sentiment_decline"
                ))

# =====================================================
# Detection: Emerging Negative Themes
# =====================================================
neg_df = df[df["sentiment_label"].str.lower() == "negative"]
if len(neg_df) >= 5:
    neg_topics = parse_topics(neg_df["topics"])
    all_topics = parse_topics(df["topics"])
    neg_freq = Counter(neg_topics)
    all_freq = Counter(all_topics)

    for topic, neg_count in neg_freq.most_common(20):
        total = all_freq.get(topic, neg_count)
        neg_ratio = neg_count / max(total, 1)
        if neg_ratio > 0.5 and neg_count >= 5:
            severity = "critical" if neg_ratio > 0.7 else "warning"
            alerts.append((
                severity,
                f"Negative Theme: {topic}",
                f"{neg_ratio*100:.0f}% of mentions for '{topic}' are negative ({neg_count}/{total} reviews).",
                "negative_theme"
            ))

# =====================================================
# Detection: Competitive Mentions
# =====================================================
competitors = ["dyson", "irobot", "kitchenaid", "roomba", "vitamix", "cuisinart", "keurig", "breville"]
comp_mentions = {}
for _, row in df.iterrows():
    text = str(row.get("text", "")).lower()
    for comp in competitors:
        if comp in text:
            if comp not in comp_mentions:
                comp_mentions[comp] = {"count": 0, "total_sentiment": 0.0}
            comp_mentions[comp]["count"] += 1
            comp_mentions[comp]["total_sentiment"] += row.get("sentiment_score", 0)

for comp, data in comp_mentions.items():
    if data["count"] >= 3:
        avg_sent = data["total_sentiment"] / data["count"]
        sentiment_desc = "positive" if avg_sent > 0.1 else ("negative" if avg_sent < -0.1 else "neutral")
        severity = "warning" if sentiment_desc == "positive" else "info"
        alerts.append((
            severity,
            f"Competitive Mention: {comp.title()}",
            f"{comp.title()} mentioned in {data['count']} reviews with {sentiment_desc} sentiment (avg: {avg_sent:.3f}). "
            f"Consumers are comparing SharkNinja products to {comp.title()}.",
            "competitor"
        ))

# =====================================================
# Detection: Platform Sentiment Gaps
# =====================================================
plat_sent = df.groupby("platform")["sentiment_score"].mean()
if len(plat_sent) >= 2:
    gap = plat_sent.max() - plat_sent.min()
    if gap > 0.15:
        best = plat_sent.idxmax()
        worst = plat_sent.idxmin()
        severity = "warning" if gap > 0.25 else "info"
        alerts.append((
            severity,
            f"Platform Sentiment Gap: {gap:.3f}",
            f"{best.title()} ({plat_sent.max():.3f}) significantly outperforms "
            f"{worst.title()} ({plat_sent.min():.3f}). "
            f"Consider investigating why sentiment differs across platforms.",
            "platform_gap"
        ))

# =====================================================
# Detection: Rating-Sentiment Mismatch
# =====================================================
for product in df["product_name"].unique():
    prod_df = df[df["product_name"] == product]
    if len(prod_df) >= 5:
        avg_rating = prod_df["rating"].mean()
        avg_sent = prod_df["sentiment_score"].mean()
        # High rating but low sentiment (or vice versa)
        if avg_rating >= 4.0 and avg_sent < -0.05:
            alerts.append((
                "warning",
                f"Rating-Sentiment Mismatch: {product}",
                f"High avg rating ({avg_rating:.1f}) but low sentiment ({avg_sent:.3f}). "
                f"Possible fake reviews or nuanced complaints.",
                "mismatch"
            ))
        elif avg_rating <= 2.5 and avg_sent > 0.1:
            alerts.append((
                "info",
                f"Rating-Sentiment Mismatch: {product}",
                f"Low avg rating ({avg_rating:.1f}) but positive sentiment ({avg_sent:.3f}). "
                f"Consumers may like the product but have specific issues.",
                "mismatch"
            ))

# =====================================================
# Executive Summary
# =====================================================
st.markdown('<div class="exec-summary">', unsafe_allow_html=True)
st.markdown("### Executive Summary")

total = len(df)
avg_s = df["sentiment_score"].mean()
pos_pct = (df["sentiment_label"].str.lower() == "positive").mean() * 100
neg_pct = (df["sentiment_label"].str.lower() == "negative").mean() * 100
critical_count = sum(1 for a in alerts if a[0] == "critical")
warning_count = sum(1 for a in alerts if a[0] == "warning")

summary_bullets = f"""
<ul>
    <li>Analyzed <strong>{total:,}</strong> reviews across {len(df["platform"].unique())} platforms.</li>
    <li>Overall sentiment is <strong>{"positive" if avg_s > 0.1 else ("negative" if avg_s < -0.1 else "neutral")}</strong>
        with an average score of <strong>{avg_s:.3f}</strong>.</li>
    <li><strong>{pos_pct:.1f}%</strong> positive reviews, <strong>{neg_pct:.1f}%</strong> negative reviews.</li>
    <li><strong>{critical_count}</strong> critical alerts and <strong>{warning_count}</strong> warnings require attention.</li>
"""

if comp_mentions:
    top_comp = max(comp_mentions.items(), key=lambda x: x[1]["count"])
    summary_bullets += f'    <li>Top competitor mention: <strong>{top_comp[0].title()}</strong> ({top_comp[1]["count"]} mentions).</li>\n'

# Top performing product
prod_rank = df.groupby("product_name")["sentiment_score"].mean()
if len(prod_rank) > 0:
    best_prod = prod_rank.idxmax()
    summary_bullets += f'    <li>Best performing product: <strong>{best_prod}</strong> (avg sentiment: {prod_rank.max():.3f}).</li>\n'

summary_bullets += "</ul>"
st.markdown(summary_bullets, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# Alert Cards Display
# =====================================================
st.markdown("### Alert Feed")

# Sort: critical first, then warning, then info
severity_order = {"critical": 0, "warning": 1, "info": 2}
alerts.sort(key=lambda x: severity_order.get(x[0], 3))

if not alerts:
    st.markdown('<div class="alert-card alert-green">'
                '<h4><span class="alert-badge badge-info">ALL CLEAR</span> No alerts detected</h4>'
                '<p>All products and platforms are performing within normal parameters.</p>'
                '</div>', unsafe_allow_html=True)
else:
    # Filter controls
    cat_filter = st.multiselect("Filter by Alert Type",
                                ["sentiment_decline", "negative_theme", "competitor", "platform_gap", "mismatch"],
                                default=["sentiment_decline", "negative_theme", "competitor", "platform_gap", "mismatch"])

    for severity, title, body, category in alerts:
        if category not in cat_filter:
            continue
        if severity == "critical":
            card_class = "alert-red"
            badge_class = "badge-critical"
            badge_text = "CRITICAL"
        elif severity == "warning":
            card_class = "alert-yellow"
            badge_class = "badge-warning"
            badge_text = "WARNING"
        else:
            card_class = "alert-green"
            badge_class = "badge-info"
            badge_text = "INFO"

        st.markdown(
            f'<div class="alert-card {card_class}">'
            f'<h4><span class="alert-badge {badge_class}">{badge_text}</span> {title}</h4>'
            f'<p>{body}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

# =====================================================
# Trending Section
# =====================================================
st.markdown("---")
st.markdown("### Trending")

tcol1, tcol2 = st.columns(2)

with tcol1:
    st.markdown("#### Trending Up \u2B06\uFE0F")
    if "date" in df.columns:
        median_date = df["date"].median()
        recent = df[df["date"] >= median_date]
        older = df[df["date"] < median_date]
        recent_topics = Counter(parse_topics(recent["topics"]))
        older_topics = Counter(parse_topics(older["topics"]))

        trending_up = []
        for topic, count in recent_topics.items():
            old_count = older_topics.get(topic, 0)
            if count >= 3 and old_count > 0:
                growth = (count - old_count) / old_count
                if growth > 0.3:
                    trending_up.append({"topic": topic, "recent": count, "growth": growth})
            elif count >= 3 and old_count == 0:
                trending_up.append({"topic": topic, "recent": count, "growth": float("inf")})

        if trending_up:
            trending_up.sort(key=lambda x: x["growth"], reverse=True)
            for item in trending_up[:8]:
                growth_str = "NEW" if item["growth"] == float("inf") else f"+{item['growth']*100:.0f}%"
                st.markdown(f'<span style="color:#2EC4B6;font-weight:600;">\u25B2</span> '
                            f'**{item["topic"]}** ({item["recent"]} mentions, {growth_str})',
                            unsafe_allow_html=True)
        else:
            st.info("No significant upward trends detected.")

with tcol2:
    st.markdown("#### Trending Down \u2B07\uFE0F")
    if "date" in df.columns:
        trending_down = []
        for topic, count in older_topics.items():
            new_count = recent_topics.get(topic, 0)
            if count >= 3 and new_count < count:
                decline = (count - new_count) / count
                if decline > 0.3:
                    trending_down.append({"topic": topic, "older": count, "recent": new_count, "decline": decline})

        if trending_down:
            trending_down.sort(key=lambda x: x["decline"], reverse=True)
            for item in trending_down[:8]:
                st.markdown(f'<span style="color:#E63946;font-weight:600;">\u25BC</span> '
                            f'**{item["topic"]}** ({item["older"]} -> {item["recent"]} mentions, '
                            f'-{item["decline"]*100:.0f}%)',
                            unsafe_allow_html=True)
        else:
            st.info("No significant downward trends detected.")

# --- Alert Summary Metrics ---
st.markdown("---")
mcol1, mcol2, mcol3 = st.columns(3)
with mcol1:
    st.metric("Critical Alerts", critical_count)
with mcol2:
    st.metric("Warnings", warning_count)
with mcol3:
    info_count = sum(1 for a in alerts if a[0] == "info")
    st.metric("Info Alerts", info_count)
