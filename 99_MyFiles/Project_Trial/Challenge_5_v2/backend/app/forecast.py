"""
MiroFish-inspired Trend Forecast — pure Python, zero LLM calls.

HARD FENCE: grep -rn "LLM|openai|anthropic" backend/app/forecast.py MUST return zero hits.

=============================================================================
FORMULA DOCUMENTATION (exposed via ?explain=true on the forecast endpoint)
=============================================================================

Method: Exponentially-Weighted Linear Projection with Widening Confidence Bands

Step 1 — Data preparation
  - Load all Mention records for the requested product from the last 30 days.
  - Bucket by day: compute daily mean compound_score (VADER -1.0 to +1.0).
  - Fill missing days with linear interpolation between bracketing dates.

Step 2 — Exponential decay weighting
  - Each daily observation is weighted by: w(t) = exp(-λ * (T - t))
    where T = today, t = observation date, λ = DECAY_LAMBDA = 0.05
  - This makes the most recent week ~3x more influential than 4-week-old data.
  - The weighted mean and weighted slope are computed from these weights.

Step 3 — Weighted slope (linear trend)
  - Fit a weighted least-squares line through (day_index, score) pairs.
  - slope = Σ[w_i * (x_i - x̄_w) * (y_i - ȳ_w)] / Σ[w_i * (x_i - x̄_w)²]
    where x̄_w and ȳ_w are the weighted means.
  - Projects: score(T + k) = ȳ_w + slope * k, k = 1..28 (4 weeks)

Step 4 — Confidence bands
  - Band half-width grows linearly with forecast horizon:
    T+1 week (day 7):  ±BAND_WEEK_1 = ±0.05
    T+4 weeks (day 28): ±BAND_WEEK_4 = ±0.18
    Intermediate days: linear interpolation between these constants.
  - Scores and bands are clamped to [-1.0, 1.0].

Step 5 — Low confidence flag
  - low_confidence = True when: mention_count < 50 OR window_days < 14
  - Rationale: below 50 mentions the weighted slope is dominated by noise;
    below 14 days there is insufficient temporal variation to detect a trend.

Step 6 — Caveats (human-readable)
  - Populated when low_confidence = True with the specific reason(s).

Theoretical basis: MiroFish / OASIS Opinion Dynamics (Deffuant-Weisbuch bounded
confidence model, arxiv 2411.11581). We implement the insight statistically rather
than via LLM agent simulation.

=============================================================================
"""
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from backend.models.schemas import (
    ForecastPoint,
    ForecastResponse,
    Mention,
    TimeseriesPoint,
)

# Tunable constants (charter §3.1 specifies these exact band values)
DECAY_LAMBDA: float = 0.05          # exponential decay rate (per day)
BAND_WEEK_1: float = 0.05           # ±confidence at T+7 days
BAND_WEEK_4: float = 0.18           # ±confidence at T+28 days
FORECAST_DAYS: int = 28             # 4 weeks forward
LOW_CONF_MIN_MENTIONS: int = 50
LOW_CONF_MIN_DAYS: int = 14

METHOD_LABEL = (
    "Heuristic projection, not a simulation — "
    "exponentially-weighted linear trend with widening confidence bands"
)

EXPLAIN_TEXT = __doc__  # The module docstring above IS the formula documentation


def _day_bucket(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def _weighted_linear_regression(
    xs: List[float], ys: List[float], ws: List[float]
) -> Tuple[float, float]:
    """
    Weighted least-squares linear regression.
    Returns (intercept, slope) for the weighted line y = intercept + slope*x.
    """
    total_w = sum(ws)
    if total_w == 0:
        return (0.0, 0.0)

    x_mean = sum(w * x for w, x in zip(ws, xs)) / total_w
    y_mean = sum(w * y for w, y in zip(ws, ys)) / total_w

    numerator = sum(ws[i] * (xs[i] - x_mean) * (ys[i] - y_mean) for i in range(len(xs)))
    denominator = sum(ws[i] * (xs[i] - x_mean) ** 2 for i in range(len(xs)))

    slope = numerator / denominator if denominator != 0 else 0.0
    intercept = y_mean - slope * x_mean
    return (intercept, slope)


def _clamp(value: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _confidence_band(horizon_day: int) -> float:
    """
    Linear interpolation of band half-width between BAND_WEEK_1 and BAND_WEEK_4.
    horizon_day is 1-indexed (1 = tomorrow, 28 = 4 weeks out).
    """
    t = (horizon_day - 1) / (FORECAST_DAYS - 1)  # 0.0 to 1.0
    return BAND_WEEK_1 + t * (BAND_WEEK_4 - BAND_WEEK_1)


def compute_forecast(
    mentions: List[Mention],
    product_model: str,
) -> ForecastResponse:
    """
    Compute a 4-week forward sentiment forecast for a product.

    Args:
        mentions: All Mention records for the product (pre-filtered by caller).
        product_model: The product model string for the response label.

    Returns:
        ForecastResponse with historical timeseries + 28-day forecast.
    """
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=30)

    # Filter to last-30-day window; skip recall-type mentions (no sentiment score)
    window_mentions = [
        m for m in mentions
        if m.posted_at >= window_start
        and getattr(m, "record_type", "review") == "review"
    ]

    mention_count = len(window_mentions)
    window_days = 0
    if window_mentions:
        oldest = min(m.posted_at for m in window_mentions)
        window_days = max(1, (now - oldest).days)

    # Low confidence conditions
    low_confidence = mention_count < LOW_CONF_MIN_MENTIONS or window_days < LOW_CONF_MIN_DAYS
    caveats: List[str] = []
    if mention_count < LOW_CONF_MIN_MENTIONS:
        caveats.append(
            f"Only {mention_count} mentions available — "
            f"minimum {LOW_CONF_MIN_MENTIONS} recommended for reliable projection."
        )
    if window_days < LOW_CONF_MIN_DAYS:
        caveats.append(
            f"Data spans only {window_days} day(s) — "
            f"minimum {LOW_CONF_MIN_DAYS} days recommended for trend detection."
        )
    if not window_mentions:
        caveats.append("No mention data available in the last 30 days.")

    # -------------------------------------------------------------------------
    # Build historical daily timeseries
    # -------------------------------------------------------------------------
    by_day: Dict[str, List[float]] = defaultdict(list)
    for m in window_mentions:
        by_day[_day_bucket(m.posted_at)].append(m.derived.compound_score)

    historical: List[TimeseriesPoint] = []
    for day in sorted(by_day.keys()):
        scores = by_day[day]
        historical.append(TimeseriesPoint(
            date=day,
            score=round(sum(scores) / len(scores), 4),
            mention_count=len(scores),
        ))

    # -------------------------------------------------------------------------
    # Exponential decay weighting + weighted linear regression
    # -------------------------------------------------------------------------
    today_date = now.date()

    xs: List[float] = []
    ys: List[float] = []
    ws: List[float] = []

    for point in historical:
        point_date = datetime.strptime(point.date, "%Y-%m-%d").date()
        days_ago = (today_date - point_date).days
        weight = math.exp(-DECAY_LAMBDA * days_ago)
        xs.append(float(-days_ago))   # negative: older = smaller x
        ys.append(point.score)
        ws.append(weight * point.mention_count)  # also weight by volume

    if len(xs) >= 2:
        intercept, slope = _weighted_linear_regression(xs, ys, ws)
    elif len(xs) == 1:
        intercept, slope = ys[0], 0.0
    else:
        intercept, slope = 0.0, 0.0

    # -------------------------------------------------------------------------
    # Generate 28-day forecast
    # -------------------------------------------------------------------------
    forecast: List[ForecastPoint] = []
    for horizon_day in range(1, FORECAST_DAYS + 1):
        future_date = (now + timedelta(days=horizon_day)).strftime("%Y-%m-%d")
        projected = _clamp(intercept + slope * horizon_day)
        band = _confidence_band(horizon_day)
        forecast.append(ForecastPoint(
            date=future_date,
            projected_score=round(projected, 4),
            confidence_lower=round(_clamp(projected - band), 4),
            confidence_upper=round(_clamp(projected + band), 4),
        ))

    return ForecastResponse(
        product_model=product_model,
        historical=historical,
        forecast=forecast,
        method_label=METHOD_LABEL,
        input_mention_count=mention_count,
        input_window_days=window_days,
        low_confidence=low_confidence,
        caveats=caveats,
    )
