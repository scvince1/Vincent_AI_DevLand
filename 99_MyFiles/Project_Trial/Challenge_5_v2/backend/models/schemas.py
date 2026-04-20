"""
Canonical API shapes. This file is the single source of truth.
All routers use response_model=... referencing these classes.
contracts/api-contract.yaml is generated from this file via scripts/export_openapi.py.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SourcePlatform(str, Enum):
    reddit = "reddit"
    amazon = "amazon"
    youtube = "youtube"
    trustpilot = "trustpilot"
    twitter = "twitter"
    other = "other"


class Brand(str, Enum):
    shark = "shark"
    ninja = "ninja"
    dyson = "dyson"
    irobot = "irobot"
    roborock = "roborock"
    kitchenaid = "kitchenaid"
    breville = "breville"
    cuisinart = "cuisinart"
    keurig = "keurig"
    delonghi = "delonghi"
    other = "other"


class Category(str, Enum):
    robot_vacuum = "robot_vacuum"
    cordless_stick = "cordless_stick"
    upright = "upright"
    air_fryer = "air_fryer"
    pressure_cooker = "pressure_cooker"
    blender = "blender"
    ice_cream_maker = "ice_cream_maker"
    coffee = "coffee"
    air_purifier = "air_purifier"
    hair_tool = "hair_tool"
    other = "other"


class SentimentLabel(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"
    mixed = "mixed"


class Polarity(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"
    mixed = "mixed"


# ---------------------------------------------------------------------------
# Core sentiment objects
# ---------------------------------------------------------------------------

class AspectSentiment(BaseModel):
    name: str = Field(..., description="Canonical aspect name, e.g. 'suction', 'battery', 'brushroll'")
    polarity: Polarity
    score: float = Field(..., ge=-1.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    snippet: str = Field(..., description="Text fragment that triggered this aspect extraction")


class ComparativePair(BaseModel):
    brand: Brand
    aspect: str = Field(..., description="Canonical aspect name")
    polarity: Polarity
    score: float = Field(..., ge=-1.0, le=1.0)


class DerivedSentiment(BaseModel):
    overall_sentiment: SentimentLabel
    compound_score: float = Field(..., ge=-1.0, le=1.0, description="Single scalar for charting")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Pipeline confidence in this result")
    sarcasm_flag: bool = Field(..., description="True if sarcasm heuristics fired")
    aspects: List[AspectSentiment] = Field(default_factory=list)
    comparative_pairs: Optional[List[ComparativePair]] = Field(
        default=None, description="Only populated when a comparative claim is detected"
    )


# ---------------------------------------------------------------------------
# Core mention / review object
# ---------------------------------------------------------------------------

class Mention(BaseModel):
    mention_id: str = Field(..., description="Stable UUID identifier")
    source_platform: SourcePlatform
    source_url: Optional[str] = Field(default=None, description="URL to original mention; null for closed sources")
    author_handle: Optional[str] = Field(default=None, description="Anonymized/hashed author handle")
    posted_at: datetime = Field(..., description="When the mention was published (UTC)")
    ingested_at: datetime = Field(..., description="When our pipeline processed it (UTC)")
    brand: Brand
    category: Category
    product_model: Optional[str] = Field(default=None, description="Specific SKU name if available")
    text: str = Field(..., description="Raw mention text, pre-NLP")
    rating: Optional[float] = Field(default=None, description="Source-provided star rating if available")
    language: str = Field(default="en", description="ISO-639-1 language code")
    derived: DerivedSentiment
    record_type: Literal["review", "recall"] = Field(
        default="review",
        description="'review' for normal mentions; 'recall' for CPSC recall records",
    )


# ---------------------------------------------------------------------------
# Request / filter models
# ---------------------------------------------------------------------------

class MentionFilter(BaseModel):
    platform: Optional[SourcePlatform] = None
    brand: Optional[Brand] = None
    category: Optional[Category] = None
    product_model: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    topic_id: Optional[str] = Field(default=None, description="Filter mentions by topic cluster ID")


# ---------------------------------------------------------------------------
# Response models — Overview (Page 1)
# ---------------------------------------------------------------------------

class OverviewKPIs(BaseModel):
    total_mentions: int
    overall_score: float = Field(..., ge=-1.0, le=1.0)
    wow_delta: float = Field(..., description="Week-over-week score change")
    top_rising_negative: List[str] = Field(..., description="Aspect names with worst score drops")
    top_rising_positive: List[str] = Field(..., description="Aspect names with best score gains")


class TimeseriesPoint(BaseModel):
    date: str = Field(..., description="ISO date YYYY-MM-DD")
    score: float = Field(..., ge=-1.0, le=1.0)
    mention_count: int


class TimeseriesResponse(BaseModel):
    series: List[TimeseriesPoint]
    brand: Optional[Brand] = None
    category: Optional[Category] = None


# ---------------------------------------------------------------------------
# Response models — Mentions list (drill-through, all pages)
# ---------------------------------------------------------------------------

class MentionListResponse(BaseModel):
    total: int
    items: List[Mention]


# ---------------------------------------------------------------------------
# Response models — Product Analysis (Page 2)
# ---------------------------------------------------------------------------

class AspectTrend(BaseModel):
    aspect: str = Field(..., description="Canonical aspect name")
    mention_count: int
    avg_score: float = Field(..., ge=-1.0, le=1.0)
    trend_delta: float = Field(..., description="30-day score change")
    severity: float = Field(..., description="volume x magnitude x recency composite")
    sparkline: List[float] = Field(..., description="Weekly scores, most recent last")


class ProductAspectResponse(BaseModel):
    product_model: str
    brand: Brand
    category: Category
    aspects: List[AspectTrend]
    exemplar_mentions: List[Mention]


class ProductListResponse(BaseModel):
    products: List[str] = Field(..., description="List of unique product_model strings")


# ---------------------------------------------------------------------------
# Response models — Platform Comparison (Page 3)
# ---------------------------------------------------------------------------

class PlatformAspectCell(BaseModel):
    platform: SourcePlatform
    aspect: str
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    mention_count: int


class PlatformComparisonResponse(BaseModel):
    grid: List[PlatformAspectCell]
    top_topics_by_platform: Dict[str, List[str]] = Field(
        ..., description="platform -> top topic labels"
    )


# ---------------------------------------------------------------------------
# Response models — Topic Explorer (Page 4)
# ---------------------------------------------------------------------------

class TopicCluster(BaseModel):
    topic_id: str
    label: str
    mention_count: int
    avg_score: float = Field(..., ge=-1.0, le=1.0)
    momentum: float = Field(..., description="Recent growth rate")
    exemplar_quotes: List[str]
    trend: List[TimeseriesPoint]
    is_novel: bool = Field(
        default=False,
        description="True when momentum > 0.3, mention_count < 25, and first_seen_at within last 14 days",
    )


class TopicExplorerResponse(BaseModel):
    topics: List[TopicCluster]


class ShareOfAspect(BaseModel):
    brand: Brand
    aspect: str
    mention_share: float = Field(..., ge=0.0, le=1.0, description="Fraction of all mentions for this aspect")
    avg_score: float = Field(..., ge=-1.0, le=1.0)


class ComparativeTopicResponse(BaseModel):
    brand_a: Brand
    brand_b: Brand
    share_of_aspect: List[ShareOfAspect]


# ---------------------------------------------------------------------------
# Response models — Alerts & Insights (Page 5)
# ---------------------------------------------------------------------------

class AlertEvent(BaseModel):
    alert_id: str
    product_model: Optional[str] = None
    brand: Brand
    aspect: str
    severity: float = Field(..., description="Composite severity score")
    score_drop: float = Field(..., description="How much the aspect score dropped")
    triggered_at: datetime
    acknowledged: bool = False
    exemplar_mentions: List[Mention] = Field(default_factory=list)
    platforms: List[SourcePlatform] = Field(
        default_factory=list,
        description="Distinct set of source platforms from exemplar_mentions[*].source_platform",
    )


class AlertListResponse(BaseModel):
    total: int
    items: List[AlertEvent]


class AlertAcknowledgeResponse(BaseModel):
    alert_id: str
    acknowledged: bool


# ---------------------------------------------------------------------------
# Response models — Product list with summary (replaces ProductListResponse)
# ---------------------------------------------------------------------------

class ProductSummary(BaseModel):
    brand: Brand
    category: Category
    product_model: str
    overall_score: float = Field(..., ge=-1.0, le=1.0)
    mention_count: int


# ---------------------------------------------------------------------------
# Response models — Share of Voice (Page 1 / Overview)
# ---------------------------------------------------------------------------

class BrandShare(BaseModel):
    brand: Brand
    mention_count: int
    share: float = Field(..., ge=0.0, le=1.0, description="Fraction of total mentions")


class ShareOfVoiceResponse(BaseModel):
    total_mentions: int
    brands: List[BrandShare]


# ---------------------------------------------------------------------------
# Response models — MiroFish Trend Forecast (R4-P0-1)
# ---------------------------------------------------------------------------

class ForecastPoint(BaseModel):
    date: str = Field(..., description="ISO date YYYY-MM-DD")
    projected_score: float = Field(..., ge=-1.0, le=1.0)
    confidence_lower: float = Field(..., ge=-1.0, le=1.0)
    confidence_upper: float = Field(..., ge=-1.0, le=1.0)


class ForecastResponse(BaseModel):
    product_model: str
    historical: List[TimeseriesPoint]
    forecast: List[ForecastPoint]
    method_label: str = Field(
        ...,
        description="Human-readable label for the forecasting method used",
    )
    input_mention_count: int
    input_window_days: int
    low_confidence: bool = Field(
        ...,
        description="True when mention_count < 50 OR window_days < 14",
    )
    caveats: List[str] = Field(
        default_factory=list,
        description="Reasons for low confidence or forecast limitations",
    )


# ---------------------------------------------------------------------------
# Request/Response models — Aaru What-If Simulator (R4-P1-2)
# ---------------------------------------------------------------------------

class SimulationRequest(BaseModel):
    scenario: str = Field(
        ...,
        description="Natural language scenario, e.g. 'What if Shark launched a $99 budget version?'",
    )
    product_model: Optional[str] = Field(
        default=None,
        description="Product context anchor — filters grounding mentions to this SKU if provided",
    )
    filter_context: Optional[MentionFilter] = Field(
        default=None,
        description="Current dashboard filter state for grounding mention selection",
    )


class SimulatedSegment(BaseModel):
    segment_label: str = Field(
        ...,
        description="Consumer segment label, e.g. 'Price-sensitive first-time buyers'",
    )
    predicted_reaction: Literal["positive", "negative", "mixed", "neutral"]
    confidence_narrative: str = Field(
        ...,
        description="Plain English 2-3 sentence explanation of why this segment reacts this way",
    )
    key_quotes_used: List[str] = Field(
        default_factory=list,
        description="Actual review text snippets from grounding mentions that informed this segment",
    )


_SIMULATOR_DISCLAIMER = (
    "Simulated reaction based on LLM heuristic, not empirical behavior modeling."
)


class SimulationResult(BaseModel):
    scenario: str = Field(..., description="Echo of the input scenario")
    product_model: Optional[str] = None
    segments: List[SimulatedSegment] = Field(
        ...,
        description="3-5 consumer segments with predicted reactions",
    )
    overall_disclaimer: str = Field(
        default=_SIMULATOR_DISCLAIMER,
        description=(
            "Anti-theater honesty label. "
            "MUST contain: 'Simulated reaction based on LLM heuristic, "
            "not empirical behavior modeling.'"
        ),
    )
    model_used: str = Field(..., description="LLM model ID used for this simulation")
    tokens_consumed: int = Field(..., description="Total tokens used (prompt + completion)")
