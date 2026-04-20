"""
Aggregation helpers for router endpoints.

All aggregation logic lives here to keep routers thin and testable.
"""
import hashlib
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from backend.models.schemas import (
    AlertEvent,
    AspectTrend,
    BrandShare,
    Brand,
    ComparativeTopicResponse,
    Mention,
    OverviewKPIs,
    PlatformAspectCell,
    PlatformComparisonResponse,
    ShareOfAspect,
    ShareOfVoiceResponse,
    TimeseriesPoint,
    TimeseriesResponse,
    TopicCluster,
    TopicExplorerResponse,
)


def _week_bucket(dt: datetime) -> str:
    """Return ISO date string for the Monday of the week containing dt."""
    monday = dt - timedelta(days=dt.weekday())
    return monday.strftime("%Y-%m-%d")


def _day_bucket(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Overview KPIs
# ---------------------------------------------------------------------------

def compute_overview_kpis(mentions: List[Mention], all_mentions: List[Mention]) -> OverviewKPIs:
    """Compute top-line KPIs from a filtered mention list."""
    total = len(mentions)
    if not mentions:
        return OverviewKPIs(
            total_mentions=0,
            overall_score=0.0,
            wow_delta=0.0,
            top_rising_negative=[],
            top_rising_positive=[],
        )

    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    this_week = [m for m in mentions if m.posted_at >= one_week_ago]
    last_week = [m for m in mentions if two_weeks_ago <= m.posted_at < one_week_ago]

    overall_score = sum(m.derived.compound_score for m in mentions) / total if total else 0.0

    tw_score = sum(m.derived.compound_score for m in this_week) / len(this_week) if this_week else 0.0
    lw_score = sum(m.derived.compound_score for m in last_week) / len(last_week) if last_week else 0.0
    wow_delta = round(tw_score - lw_score, 4)

    # Aspect trend analysis
    aspect_scores_this: Dict[str, List[float]] = defaultdict(list)
    aspect_scores_last: Dict[str, List[float]] = defaultdict(list)

    for m in this_week:
        for a in m.derived.aspects:
            aspect_scores_this[a.name].append(a.score)

    for m in last_week:
        for a in m.derived.aspects:
            aspect_scores_last[a.name].append(a.score)

    all_aspects = set(aspect_scores_this.keys()) | set(aspect_scores_last.keys())
    aspect_deltas: Dict[str, float] = {}
    for asp in all_aspects:
        tw_avg = sum(aspect_scores_this[asp]) / len(aspect_scores_this[asp]) if aspect_scores_this[asp] else 0.0
        lw_avg = sum(aspect_scores_last[asp]) / len(aspect_scores_last[asp]) if aspect_scores_last[asp] else 0.0
        aspect_deltas[asp] = tw_avg - lw_avg

    sorted_deltas = sorted(aspect_deltas.items(), key=lambda x: x[1])
    top_rising_negative = [a for a, _ in sorted_deltas[:3]]
    top_rising_positive = [a for a, _ in reversed(sorted_deltas[-3:])]

    return OverviewKPIs(
        total_mentions=total,
        overall_score=round(overall_score, 4),
        wow_delta=wow_delta,
        top_rising_negative=top_rising_negative,
        top_rising_positive=top_rising_positive,
    )


# ---------------------------------------------------------------------------
# Timeseries
# ---------------------------------------------------------------------------

def compute_timeseries(
    mentions: List[Mention],
    brand: Optional[Brand] = None,
    category=None,
) -> TimeseriesResponse:
    """Build daily sentiment timeseries from mentions."""
    by_day: Dict[str, List[float]] = defaultdict(list)
    for m in mentions:
        day = _day_bucket(m.posted_at)
        by_day[day].append(m.derived.compound_score)

    series = []
    for day in sorted(by_day.keys()):
        scores = by_day[day]
        series.append(TimeseriesPoint(
            date=day,
            score=round(sum(scores) / len(scores), 4),
            mention_count=len(scores),
        ))

    return TimeseriesResponse(series=series, brand=brand, category=category)


# ---------------------------------------------------------------------------
# Share of Voice
# ---------------------------------------------------------------------------

def compute_share_of_voice(mentions: List[Mention]) -> ShareOfVoiceResponse:
    brand_counts: Dict[str, int] = defaultdict(int)
    for m in mentions:
        brand_counts[m.brand.value] += 1

    total = len(mentions)
    brands = []
    for brand_val, count in sorted(brand_counts.items(), key=lambda x: -x[1]):
        try:
            b = Brand(brand_val)
        except ValueError:
            b = Brand.other
        brands.append(BrandShare(
            brand=b,
            mention_count=count,
            share=round(count / total, 4) if total else 0.0,
        ))

    return ShareOfVoiceResponse(total_mentions=total, brands=brands)


# ---------------------------------------------------------------------------
# Product aspects
# ---------------------------------------------------------------------------

def compute_product_aspects(mentions: List[Mention]) -> List[dict]:
    """
    Compute aspect-level stats from mentions for a single product.
    Returns list of dicts compatible with AspectTrend.
    """
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    aspect_all: Dict[str, List[Tuple[float, datetime]]] = defaultdict(list)
    for m in mentions:
        for a in m.derived.aspects:
            aspect_all[a.name].append((a.score, m.posted_at))

    results = []
    for asp, entries in aspect_all.items():
        entries_sorted = sorted(entries, key=lambda x: x[1])
        all_scores = [s for s, _ in entries_sorted]
        avg_score = sum(all_scores) / len(all_scores)

        recent = [s for s, dt in entries if dt >= thirty_days_ago]
        older = [s for s, dt in entries if sixty_days_ago <= dt < thirty_days_ago]

        r_avg = sum(recent) / len(recent) if recent else avg_score
        o_avg = sum(older) / len(older) if older else avg_score
        trend_delta = round(r_avg - o_avg, 4)

        # Severity: volume * magnitude * recency_weight
        recency_weight = len(recent) / max(len(all_scores), 1)
        severity = round(len(all_scores) * abs(avg_score) * (1 + recency_weight), 3)

        # Weekly sparkline (last 8 weeks)
        week_scores: Dict[str, List[float]] = defaultdict(list)
        for s, dt in entries_sorted:
            week_scores[_week_bucket(dt)].append(s)
        sparkline_weeks = sorted(week_scores.keys())[-8:]
        sparkline = [round(sum(week_scores[w]) / len(week_scores[w]), 4) for w in sparkline_weeks]

        results.append({
            "aspect": asp,
            "mention_count": len(all_scores),
            "avg_score": round(avg_score, 4),
            "trend_delta": trend_delta,
            "severity": severity,
            "sparkline": sparkline,
        })

    return sorted(results, key=lambda x: x["severity"], reverse=True)


# ---------------------------------------------------------------------------
# Platform comparison
# ---------------------------------------------------------------------------

def compute_platform_comparison(mentions: List[Mention]) -> PlatformComparisonResponse:
    # aspect x platform -> scores
    grid_data: Dict[Tuple[str, str], List[float]] = defaultdict(list)
    platform_topics: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for m in mentions:
        plat = m.source_platform.value
        for a in m.derived.aspects:
            grid_data[(plat, a.name)].append(a.score)
            platform_topics[plat][a.name] += 1

    grid = []
    from backend.models.schemas import SourcePlatform
    for (plat, asp), scores in grid_data.items():
        try:
            sp = SourcePlatform(plat)
        except ValueError:
            sp = SourcePlatform.other
        grid.append(PlatformAspectCell(
            platform=sp,
            aspect=asp,
            sentiment_score=round(sum(scores) / len(scores), 4),
            mention_count=len(scores),
        ))

    top_topics_by_platform = {}
    for plat, topic_counts in platform_topics.items():
        top_topics_by_platform[plat] = [
            t for t, _ in sorted(topic_counts.items(), key=lambda x: -x[1])[:5]
        ]

    return PlatformComparisonResponse(grid=grid, top_topics_by_platform=top_topics_by_platform)


# ---------------------------------------------------------------------------
# Topic Explorer
# ---------------------------------------------------------------------------

def compute_topics(mentions: List[Mention]) -> TopicExplorerResponse:
    """Cluster mentions by their top aspect and compute topic stats."""
    topic_mentions: Dict[str, List[Mention]] = defaultdict(list)

    for m in mentions:
        if m.derived.aspects:
            # Use the highest-confidence aspect as the primary topic
            top_asp = max(m.derived.aspects, key=lambda a: a.confidence)
            topic_mentions[top_asp.name].append(m)
        else:
            topic_mentions["general"].append(m)

    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    clusters = []
    for topic_name, topic_ments in topic_mentions.items():
        if len(topic_ments) < 1:
            continue

        # Deterministic topic_id from name
        topic_id = hashlib.md5(topic_name.encode()).hexdigest()[:8]

        scores = [m.derived.compound_score for m in topic_ments]
        avg_score = sum(scores) / len(scores)

        this_week = [m for m in topic_ments if m.posted_at >= one_week_ago]
        last_week = [m for m in topic_ments if two_weeks_ago <= m.posted_at < one_week_ago]
        momentum = len(this_week) - len(last_week)

        # Sample exemplar quotes
        exemplars = [m.text[:200] for m in sorted(
            topic_ments, key=lambda m: abs(m.derived.compound_score), reverse=True
        )[:3]]

        # Trend timeseries
        trend_by_day: Dict[str, List[float]] = defaultdict(list)
        for m in topic_ments:
            trend_by_day[_day_bucket(m.posted_at)].append(m.derived.compound_score)
        trend = [
            TimeseriesPoint(
                date=d,
                score=round(sum(s) / len(s), 4),
                mention_count=len(s),
            )
            for d, s in sorted(trend_by_day.items())
        ]

        # Novelty detection: new cluster with rising momentum and limited history
        fourteen_days_ago = now - timedelta(days=14)
        first_seen_at = min(m.posted_at for m in topic_ments)
        is_novel = (
            momentum > 0.3
            and len(topic_ments) < 25
            and first_seen_at >= fourteen_days_ago
        )

        clusters.append(TopicCluster(
            topic_id=topic_id,
            label=topic_name.replace("_", " ").title(),
            mention_count=len(topic_ments),
            avg_score=round(avg_score, 4),
            momentum=float(momentum),
            exemplar_quotes=exemplars,
            trend=trend,
            is_novel=is_novel,
        ))

    clusters.sort(key=lambda c: c.momentum, reverse=True)
    return TopicExplorerResponse(topics=clusters)


def compute_comparative_topics(
    mentions: List[Mention],
    brand_a: Brand,
    brand_b: Brand,
) -> ComparativeTopicResponse:
    """Share-of-aspect comparison between two brands."""
    a_mentions = [m for m in mentions if m.brand == brand_a]
    b_mentions = [m for m in mentions if m.brand == brand_b]

    a_aspect_counts: Dict[str, List[float]] = defaultdict(list)
    b_aspect_counts: Dict[str, List[float]] = defaultdict(list)

    for m in a_mentions:
        for a in m.derived.aspects:
            a_aspect_counts[a.name].append(a.score)

    for m in b_mentions:
        for a in m.derived.aspects:
            b_aspect_counts[a.name].append(a.score)

    all_aspects = set(a_aspect_counts.keys()) | set(b_aspect_counts.keys())
    total_a = sum(len(v) for v in a_aspect_counts.values()) or 1
    total_b = sum(len(v) for v in b_aspect_counts.values()) or 1

    share_of_aspect = []
    for asp in sorted(all_aspects):
        a_scores = a_aspect_counts[asp]
        b_scores = b_aspect_counts[asp]

        if a_scores:
            share_of_aspect.append(ShareOfAspect(
                brand=brand_a,
                aspect=asp,
                mention_share=round(len(a_scores) / total_a, 4),
                avg_score=round(sum(a_scores) / len(a_scores), 4),
            ))
        if b_scores:
            share_of_aspect.append(ShareOfAspect(
                brand=brand_b,
                aspect=asp,
                mention_share=round(len(b_scores) / total_b, 4),
                avg_score=round(sum(b_scores) / len(b_scores), 4),
            ))

    return ComparativeTopicResponse(
        brand_a=brand_a,
        brand_b=brand_b,
        share_of_aspect=share_of_aspect,
    )


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

def compute_alerts(mentions: List[Mention]) -> List[AlertEvent]:
    """
    Generate alerts for rising negative aspects.
    Severity = mention_count * |score_drop| * recency_weight
              * cross_platform_multiplier (1 + 0.5 * (platform_count - 1))
              * novelty_multiplier (2x if cluster is novel)
    """
    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)
    fourteen_days_ago = now - timedelta(days=14)

    # Group by (product_model, brand, aspect)
    key_to_recent: Dict[tuple, List[float]] = defaultdict(list)
    key_to_older: Dict[tuple, List[float]] = defaultdict(list)
    key_to_ments: Dict[tuple, List[Mention]] = defaultdict(list)
    key_to_brand: Dict[tuple, Brand] = {}
    # Track distinct platforms contributing to each key
    key_to_platforms: Dict[tuple, set] = defaultdict(set)
    # Track first_seen_at and mention count per aspect (for novelty check)
    aspect_first_seen: Dict[str, datetime] = {}
    aspect_all_counts: Dict[str, int] = defaultdict(int)

    for m in mentions:
        for a in m.derived.aspects:
            key = (m.product_model or "unknown", m.brand.value, a.name)
            key_to_brand[key] = m.brand
            key_to_platforms[key].add(m.source_platform.value)
            aspect_all_counts[a.name] += 1
            if a.name not in aspect_first_seen or m.posted_at < aspect_first_seen[a.name]:
                aspect_first_seen[a.name] = m.posted_at
            if m.posted_at >= one_week_ago:
                key_to_recent[key].append(a.score)
                key_to_ments[key].append(m)
            elif m.posted_at >= two_weeks_ago:
                key_to_older[key].append(a.score)

    # Pre-compute novelty per aspect: momentum > 0.3, mention_count < 25, first_seen within 14 days
    # Approximate momentum as (recent_count - prev_count) for aspect globally
    aspect_recent_counts: Dict[str, int] = defaultdict(int)
    aspect_prev_counts: Dict[str, int] = defaultdict(int)
    for m in mentions:
        for a in m.derived.aspects:
            if m.posted_at >= one_week_ago:
                aspect_recent_counts[a.name] += 1
            elif m.posted_at >= two_weeks_ago:
                aspect_prev_counts[a.name] += 1

    novel_aspects: set = set()
    for asp, total_count in aspect_all_counts.items():
        recent_c = aspect_recent_counts.get(asp, 0)
        prev_c = aspect_prev_counts.get(asp, 0)
        momentum = float(recent_c - prev_c)
        first_seen = aspect_first_seen.get(asp)
        if (
            momentum > 0.3
            and total_count < 25
            and first_seen is not None
            and first_seen >= fourteen_days_ago
        ):
            novel_aspects.add(asp)

    alerts = []
    seen_keys = set()

    for key, recent_scores in key_to_recent.items():
        if not recent_scores:
            continue
        older_scores = key_to_older.get(key, [])

        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores) if older_scores else 0.0
        score_drop = recent_avg - older_avg

        # Only fire if sentiment worsened
        if score_drop >= -0.05:
            continue

        product_model, brand_val, aspect = key

        # Cross-platform confirmation multiplier: (1 + 0.5 * (platform_count - 1))
        platform_count = len(key_to_platforms.get(key, set()))
        cross_platform_multiplier = 1.0 + 0.5 * (platform_count - 1)

        # Novelty multiplier: 2x if this aspect is novel
        novelty_multiplier = 2.0 if aspect in novel_aspects else 1.0

        severity = round(
            len(recent_scores) * abs(score_drop) * 2.0
            * cross_platform_multiplier
            * novelty_multiplier,
            3,
        )

        if severity < 0.1:
            continue

        alert_id = hashlib.md5(f"{key}".encode()).hexdigest()[:12]
        if alert_id in seen_keys:
            continue
        seen_keys.add(alert_id)

        try:
            brand = Brand(brand_val)
        except ValueError:
            brand = Brand.other

        exemplars = key_to_ments[key][:3]

        # Populate distinct platforms from all mentions for this key (not just exemplars)
        from backend.models.schemas import SourcePlatform as _SP
        raw_platforms = key_to_platforms.get(key, set())
        platform_list = []
        for p in sorted(raw_platforms):
            try:
                platform_list.append(_SP(p))
            except ValueError:
                platform_list.append(_SP.other)

        alerts.append(AlertEvent(
            alert_id=alert_id,
            product_model=product_model if product_model != "unknown" else None,
            brand=brand,
            aspect=aspect,
            severity=severity,
            score_drop=round(score_drop, 4),
            triggered_at=now,
            acknowledged=False,
            exemplar_mentions=exemplars,
            platforms=platform_list,
        ))

    # Safety recall alerts — CPSC-sourced mentions (record_type == "recall")
    # Each recall fires at maximum severity (10.0), overriding all multiplier ceilings.
    from backend.models.schemas import SourcePlatform as _SP2
    recall_mentions = [m for m in mentions if getattr(m, "record_type", "review") == "recall"]
    recall_seen_ids: set = set()
    for m in recall_mentions:
        recall_alert_id = hashlib.md5(f"safety_recall_{m.mention_id}".encode()).hexdigest()[:12]
        if recall_alert_id in recall_seen_ids:
            continue
        recall_seen_ids.add(recall_alert_id)
        alerts.append(AlertEvent(
            alert_id=recall_alert_id,
            product_model=m.product_model,
            brand=m.brand,
            aspect="safety_recall",
            severity=10.0,  # Maximum — overrides all multiplier ceilings per charter §6.3
            score_drop=-1.0,
            triggered_at=now,
            acknowledged=False,
            exemplar_mentions=[m],
            platforms=[m.source_platform],
        ))

    return sorted(alerts, key=lambda a: a.severity, reverse=True)
