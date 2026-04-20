# MiroFish MVP Analysis — for Trend Forecast panel implementation

*Research date: 2026-04-11 | Sources: GitHub 666ghj/MiroFish, nikmcfly/MiroFish-Offline, amadad/mirofish, OASIS arxiv 2411.11581, multiple blog/explainer articles*

---

## MiroFish pipeline overview

MiroFish runs a **five-stage swarm intelligence pipeline**:

1. **Graph Building** — Source documents (news articles, reports, any text) are processed by GraphRAG. Entities (people, orgs, events, concepts) and their relationships are extracted via LLM to build a knowledge graph. Stored as `graph.json` + `graph_summary.json`.

2. **Agent Generation (Environment Setup)** — The knowledge graph seeds hundreds-to-thousands of agent personas. Each agent gets: unique personality profile, opinion bias, reaction speed, influence level, initial stance, and social relationships to other agents. This is the "digital twin population" step.

3. **Simulation** — Agents interact autonomously on dual simulated social platforms (Twitter-like + Reddit-like) powered by OASIS (CAMEL-AI). OASIS supports 23 social action types (post, reply, follow, share, etc.), dynamic memory via Zep Cloud, and tracks sentiment evolution + influence propagation in real time. Produces `timeline.json`, `top_agents.json`, `actions.jsonl`.

4. **Report Generation** — A ReportAgent analyzes post-simulation data, conducts agent interviews, queries the knowledge graph, and produces structured outputs: `verdict.json` (machine-readable confidence scores + signals), `summary.json`, `report.md`, and SVG visuals (swarm overview, cluster map, timeline, platform split).

5. **Deep Interaction** — Users can query individual agents, interrogate the ReportAgent, and inject new variables mid-run to test counterfactuals. Not part of the core prediction output.

**Full output directory structure per run:**
```
uploads/runs/<run_id>/
├── manifest.json
├── input/           # requirement.txt, source_files/, ontology.json, simulation_config.json
├── graph/           # graph.json, graph_summary.json
├── simulation/      # timeline.json, top_agents.json, actions.jsonl, config.json
├── report/          # verdict.json, summary.json, report.md
└── visuals/         # SVG charts
```

**Technology stack:** Python 3.11-3.12 backend, Vue.js frontend, OpenAI-compatible LLM APIs (recommends Alibaba Qwen-plus), Zep Cloud for agent memory, Docker optional. The offline fork (nikmcfly) replaces Zep with Neo4j and cloud LLMs with Ollama.

---

## Essential stages for forward-projected sentiment

For a **"Trend Forecast" panel showing projected sentiment over time**, only three stages matter:

| Stage | Needed? | Reason |
|---|---|---|
| Graph Building (full GraphRAG) | **Partially** | We need entity/topic extraction, NOT the full graph construction. spaCy NER + simple co-occurrence is sufficient. |
| Agent Generation | **No** | Full persona simulation is overkill for a sentiment curve. We need statistical population modeling, not individual agents. |
| Simulation (OASIS) | **No** | The LLM-driven agent interaction loop is the "heavy" part. Replace with time-series extrapolation on real mention data. |
| Report Generation (ReportAgent) | **Partially** | We need the output schema (verdict + sentiment timeline), not the LLM synthesis layer. |
| Deep Interaction | **No** | Interactive querying is a UI feature, not a forecast output. |

**Essential reduced pipeline for our purposes:**

```
Real mentions input
    → Sentiment scoring (VADER per mention)
    → Aspect extraction (spaCy NER + noun chunks)
    → Temporal aggregation (pandas resample)
    → Trend detection (Prophet or statsmodels)
    → Alert scoring (threshold + slope rules)
    → Forecast output (next 7/14/30 days)
```

This is MiroFish's insight — simulate how opinion evolves — but implemented with statistical extrapolation on real data instead of LLM agent loops.

---

## Lightweight library replacements

| MiroFish Component | Heavy Implementation | Our Lightweight Replacement |
|---|---|---|
| GraphRAG entity extraction | LLM-based entity + relationship extraction, graph DB | **spaCy en_core_web_sm** — NER for product/brand/feature entities; noun chunk extraction for aspect terms. No graph DB needed. |
| Agent persona generation | LLM generates hundreds of distinct personality profiles | **SKIP** — replaced by statistical segment modeling (high/mid/low sentiment cohorts from real data distribution) |
| Zep Cloud / Neo4j memory | Cloud-based episodic memory for agent state | **pandas DataFrame** — simple time-indexed mention store, no persistent agent memory needed |
| OASIS simulation engine | CAMEL-AI multi-agent social interaction framework, 23 action types | **Prophet (Facebook)** for trend + seasonality decomposition, or **statsmodels ARIMA/ETS** for time-series forecasting |
| Embedding / semantic search | nomic-embed-text 768-dim vectors, hybrid BM25+vector search | **TF-IDF via scikit-learn** for aspect clustering, or optionally **sentence-transformers MiniLM-L6** if semantic grouping is needed |
| Opinion dynamics / polarization modeling | OASIS group polarization via LLM agent disagreement | **Slope-of-sentiment rule**: compute 7-day rolling sentiment mean + detect inflection points via second derivative sign change |
| ReportAgent (LLM synthesis) | GPT/Qwen LLM generates narrative verdict | **Template-based verdict** with threshold logic: if forecast slope > X and volume > Y → "Rising concern alert" |
| SVG visualization | React/Vue charting components | **Out of scope** for backend data contract; frontend handles rendering |

---

## Citable algorithm (if any)

**Opinion Dynamics via Bounded Confidence (Deffuant-Weisbuch model), as implemented in OASIS**

The OASIS paper (arxiv 2411.11581, CAMEL-AI, 2024) demonstrates that in multi-agent social simulations, opinions evolve through selective interaction: agents update their stance only when they encounter other agents whose opinions are within a "confidence threshold" of their own. This produces the empirically observed pattern of **group polarization** — the simulated population bifurcates into opinion clusters over time, with moderate positions eroding and extreme positions amplifying.

For our lightweight implementation, we cite this as the theoretical basis but implement it statistically: we track the **distribution of sentiment scores over time** (mean, variance, skewness) rather than simulating individual agent interactions. A widening variance + bimodal distribution in recent mentions signals the onset of polarization, which our forecast model treats as an "escalation risk" flag. This is the MiroFish insight operationalized without the LLM overhead.

---

## Input requirements

MiroFish does not publish explicit minimum mention counts in its documentation. Based on:
- OASIS group polarization experiments using 196 agents as a reference cohort
- Time-series forecasting best practices (Prophet requires ~2 seasonal cycles minimum)
- Practical sentiment dashboard standards in consumer analytics

**Recommended minimums for a defensible forecast (not a toy):**

| Parameter | Minimum | Recommended |
|---|---|---|
| Total mentions in corpus | 50 | 200+ |
| Temporal span | 14 days | 30 days |
| Mentions per day (average) | 3-5 | 10+ |
| Distinct aspects/entities tracked | 2 | 5+ |
| Category coverage | 1 product/topic | 3+ for comparison |

**Below 50 mentions / 14 days:** output should be flagged as "insufficient data — indicative only."

**Input data shape expected:**
```python
# Each mention record
{
    "mention_id": str,
    "text": str,
    "timestamp": datetime,        # UTC
    "source": str,                # "reddit" | "twitter" | "review" | "news"
    "product_id": str,
    "aspects": List[str],         # spaCy-extracted, can be empty pre-processing
    "sentiment_score": float,     # VADER compound, -1.0 to +1.0
    "sentiment_label": str        # "positive" | "neutral" | "negative"
}
```

---

## Output data contract for Trend Forecast panel

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class SentimentDataPoint(BaseModel):
    date: date
    sentiment_mean: float           # -1.0 to +1.0
    sentiment_lower: float          # 80% confidence interval lower bound
    sentiment_upper: float          # 80% confidence interval upper bound
    mention_volume: int             # actual or forecasted mention count
    is_forecast: bool               # False = historical, True = projected

class RisingAspect(BaseModel):
    aspect: str                     # e.g. "battery life", "delivery speed"
    current_sentiment: float
    trend_slope: float              # change per day, last 7 days
    mention_share: float            # fraction of total mentions containing this aspect
    trend_direction: str            # "rising_positive" | "rising_negative" | "stable" | "declining"

class AlertSignal(BaseModel):
    alert_type: str                 # "negative_surge" | "polarization" | "volume_spike" | "aspect_decline"
    severity: str                   # "low" | "medium" | "high"
    affected_aspect: Optional[str]
    trigger_date: date
    description: str                # human-readable explanation

class TrendForecastResponse(BaseModel):
    product_id: str
    generated_at: str               # ISO8601 datetime
    forecast_horizon_days: int      # 7, 14, or 30
    data_quality: str               # "sufficient" | "indicative_only" | "insufficient"
    mention_count_total: int        # mentions used for this forecast
    temporal_span_days: int         # actual span of historical data

    # Core sentiment timeline (historical + forecast)
    sentiment_timeline: List[SentimentDataPoint]

    # Top rising/declining aspects
    rising_aspects: List[RisingAspect]   # max 5, sorted by |trend_slope|

    # Alert signals
    alerts: List[AlertSignal]            # empty list if none

    # Summary statistics
    current_sentiment_7d: float          # rolling 7-day mean (most recent)
    forecast_sentiment_endpoint: float   # predicted sentiment at horizon end
    forecast_trend: str                  # "improving" | "stable" | "declining" | "volatile"

    # MiroFish-inspired verdict
    confidence_score: float              # 0.0-1.0, based on data volume + span
    verdict_label: str                   # "positive_trajectory" | "neutral" | "concern" | "alert"
    verdict_rationale: str               # 1-2 sentence explanation

    # Model metadata
    model_used: str                      # "prophet" | "arima" | "linear_trend"
    insufficient_data_warning: Optional[str]
```

**Endpoint:** `GET /api/v1/forecast/{product_id}?horizon=7|14|30`

---

## Implementation effort estimate

| Task | Hours |
|---|---|
| Sentiment scoring pipeline (VADER on mentions, per-record) | 0.5h |
| Aspect extraction (spaCy NER + noun chunk grouping) | 1.0h |
| Time-series aggregation (pandas resample, rolling stats) | 0.5h |
| Prophet/statsmodels forecast (fit model, generate CI) | 1.0h |
| Alert logic (slope thresholds, polarization detector) | 0.5h |
| Pydantic response schema + FastAPI endpoint wiring | 0.5h |
| Basic tests + edge case handling (insufficient data) | 0.5h |
| **Total** | **4.5h** |

Achievable in 2-4h if the mentions DataFrame already exists from earlier pipeline stages (i.e., VADER scoring is done upstream). Add 1h if starting from raw text.

---

## What to skip / defer

| Component | Why skip |
|---|---|
| Full GraphRAG graph construction | Requires LLM API calls per document chunk; overkill for aspect extraction. spaCy NER covers 80% of the value. |
| OASIS multi-agent simulation | The core "heavy" component. Requires running 100s-1000s of LLM-agent interaction loops. Latency and cost are prohibitive for a real-time dashboard endpoint. |
| Zep Cloud / Neo4j agent memory | No persistent agents = no memory needed. pandas in-memory DataFrame is sufficient. |
| Agent persona generation | Our forecast is statistical, not simulation-based. Persona diversity is irrelevant. |
| Deep interaction / chat with agents | UI feature; not a data contract concern for the forecast panel. |
| LLM-generated narrative verdict | Template-based rule verdict is sufficient for v1. LLM synthesis deferred to v2 if needed. |
| Dual-platform split (Twitter vs Reddit) | Useful signal, but optional. Implement as a `source` field in input data; aggregate for v1, split for v2. |
| Counterfactual / scenario injection | MiroFish's "God's-eye variable injection" feature. Out of scope for a passive dashboard panel. |

---

*Research sources: GitHub 666ghj/MiroFish (README, backend structure), nikmcfly/MiroFish-Offline (offline fork architecture), amadad/mirofish (output schemas), OASIS paper arxiv 2411.11581, DEV.to/emelia.io/medium.com MiroFish explainers, CAMEL-AI OASIS documentation.*
