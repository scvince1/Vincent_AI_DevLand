**STATUS: FROZEN**

# Round 4 Charter — SharkNinja Consumer Sentiment Dashboard

**Author:** business-leader-v2
**Date:** 2026-04-11
**Status:** FROZEN per team-lead R4 spawn protocol. No revisions without explicit team-lead coordination (SendMessage first → pause → edit).
**Round context:** R4 is "feature depth" per `round_3_charter.md §0` and §3.6 allocation table. R5 remains the hard ceiling and is reserved for README polish + final accessibility + residual cleanup.
**Round 3 floor:** PASS — see `contracts/review-round-3.md`. Filter-propagation bug fixed, responsive breakpoints landed, novelty detection + cross-platform severity live, real-API proposal honest on all internet-verified claims, 300 data rows, 44/6 pytest green, `tsc -p tsconfig.app.json` clean, `vite build` 615 modules. **Do not regress any of this.**

**Reference material (binding, read once, do not duplicate):**
- `contracts/round_3_charter.md` — R3/R4/R5 allocation table (§3.6) and REQ amendment proposals (§8)
- `contracts/review-round-3.md` — R3 audit findings and my own minor-observation notes carried forward
- `contracts/real_api_integration_proposal.md` — R3-P0-4 proposal, internet-verified for accuracy in R3 audit
- `contracts/research/orchestrator/ucsd_amazon_ingest_plan.md` — backend-v3 UCSD implementation plan, YELLOW LIGHT licensing conclusion (§6)
- `contracts/research/orchestrator/alt_consumer_signal_sources.md` — CPSC Recalls API GREEN LIGHT (Tier 1), Reddit niche subs, StackExchange, others
- `contracts/research/orchestrator/tiktok_scraping_feasibility.md` — TikTok is SUPPLEMENTAL at best, Research API is academic-only
- `contracts/research/r4_prep_forecast_demo_framing.md` — R5-facing forecast demo rubric (my earlier research)
- `frontend/docs/forecast_visual_conventions.md` — frontend-v3's Recharts-specific implementation table for the forecast panel
- `contracts/research/r4_prep_foodi_precedent.md` — 45% precedent + Samsung Note 7 timeline (feeds R5, not R4)
- `contracts/research/r4_prep_absa_benchmarks.md` — rule-based ABSA defensive talking points (feeds R5)
- `contracts/research/r4_prep_alt_signal_case_studies.md` — lead-time case studies (feeds R5)

---

## 0. Round 4 philosophy

**R4 is feature depth, not feature cram.** The 3-round ceiling means R5 exists. If a feature can land at 80% quality in R4 and reach 95% in R5 polish, that is **better** than landing it at 60% quality in R4 under time pressure. Apply the same scope discipline my R3 charter draft 2 applied when moving Trend Forecast from R3 to R4 (charter §3.1).

**What R4 must absolutely ship:**
1. Trend Forecast — full scope, visual conventions per `frontend/docs/forecast_visual_conventions.md`, honest heuristic labeling
2. Real-API integration EXECUTION — Reddit PRAW + HN Algolia as GREEN-LIGHT primary, UCSD Appliances as optional tier-2 add
3. CPSC Recalls API integration as a new data source — discovered in backend-v3 research, GREEN-LIGHT government data, directly serves Terri Williams persona
4. AlertEvent.platforms top-level field — R3 audit §6 identified this as the unify-semantics debt from Round 3

**What R4 should ship if time allows:**
5. Aaru-style What-If Simulator v1 — LLM prompt-chain, explicit "simulated not measured" labeling
6. Novelty + forecast integration — forecast trajectory visibility on novel clusters even with thin data
7. Charter-prescribed contract protocol (§8)

**What R4 must NOT ship:**
- README polish — that is R5 business-leader work
- Accessibility deep-pass beyond what already landed in R3 — that is R5 scope
- Dark mode — R5 optional
- Export to PDF/CSV — R5
- Pixel-perfect Figma polish — never in this project's scope

---

## 1. Vincent's Round-3 Feedback Residuals + R4 Additions

Items that rolled forward from R3 or emerged during R3 audit.

| # | Item | Owner | Priority | Acceptance |
|---|---|---|---|---|
| V3-R | AlertsInsightsPage filter scope: currently accepts brand+category+dateRange. Needs `platforms` filter parameter to unify filter semantics across all 5 pages. | backend-v4 + frontend-v4 | **P1** | `AlertEvent` schema gains `platforms: List[SourcePlatform]` field computed from `exemplar_mentions[*].source_platform` distinct set. `fetchAlerts` accepts `platforms` query param. `AlertsInsightsPage` dep array includes `platforms`. |
| V4 | Prediction feature depth — MiroFish Trend Forecast (full scope, not minimal-v1) | backend-v4 + frontend-v4 | **P0** | See §3.1 |
| V4-b | Implication feature — Aaru-style What-If Simulator | backend-v4 + frontend-v4 | **P1** | See §3.2 |
| V5-continue | Frontend maturity rubric M1-M6 continuing polish | frontend-v4 | **P1** | No regression from R3 rubric pass. Typography scale unified. Any new forecast/simulator components inherit tokens, not raw values. |
| Chunk size | R3 vite build warns >500 kB chunk (716 kB JS). | frontend-v4 | **P2** | If time permits, code-split the Recharts bundle. Non-blocking. R5 fallback. |

---

## 2. P0 / P1 / P2 Feature Queue for Round 4

### P0 — blocking for Round 4 sign-off

| ID | Feature | Owner | Acceptance |
|---|---|---|---|
| R4-P0-1 | **MiroFish Trend Forecast — full scope** (backend endpoint + frontend panel + visual conventions) | backend-v4 + frontend-v4 | See §3.1 — full acceptance criteria. Exit: `GET /api/products/{model}/forecast` returns `ForecastResponse`; Product Analysis page renders forecast panel per `frontend/docs/forecast_visual_conventions.md` §6 table; all 5 visual primitives landed; honest "Heuristic projection, not a simulation" footnote present. |
| R4-P0-2 | **Real-API integration execution — Reddit PRAW + HN Algolia** (GREEN-LIGHT primary combo) | backend-v4 | `RedditScraper(BaseScraper)` and `HackerNewsScraper(BaseScraper)` exist and register via `get_scraper()` factory under `SCRAPER_ADAPTER` env values `reddit` and `hn`. Routers unchanged (BaseScraper ABC compliance). Live queries return real Reddit posts and HN comments for at least 3 SharkNinja SKUs, field-mapped to `Mention` schema. OAuth credentials documented in `.env.example`, NOT committed. Rate limit handling: 100 QPM for Reddit, best-effort for HN Algolia. |
| R4-P0-3 | **CPSC Recalls API integration** (discovered in `alt_consumer_signal_sources.md` Tier 1 — GREEN-LIGHT government data) | backend-v4 + frontend-v4 | New scraper `CPSCScraper(BaseScraper)` fetches recall records via https://www.cpsc.gov recalls API, filters by `firm_name` containing "Shark" / "Ninja" / "SharkNinja" / "Dyson" / "iRobot" / "Roborock" / "KitchenAid", maps to `Mention` schema with `source_platform = other` and a new optional `record_type: 'review' \| 'recall'` field. Alerts page shows a dedicated "Safety Recalls" alert row with max severity when firm-matched recalls exist. Frontend: recall alerts show a red badge and link to the official CPSC URL. |
| R4-P0-4 | **AlertEvent.platforms field** (debt from R3 audit) | backend-v4 + frontend-v4 | `schemas.AlertEvent.platforms: List[SourcePlatform]` added, populated in `compute_alerts` as the distinct-set of `exemplar_mentions[*].source_platform`. `fetchAlerts(...)` gains `platforms` query param. `AlertsInsightsPage` useEffect dep array gains `platforms`. api-contract.yaml regenerated. frontend types regenerated via `gen:types`. |
| R4-P0-5 | **Frontend maturity rubric M1-M6 non-regression** | frontend-v4 | All new components (forecast panel, recall alerts, simulator panel if R4-P1-2 lands) inherit design tokens from `theme/index.ts`. No hardcoded colors. No inline font-sizes. No fetch effects without loading/empty/error states. Focus-visible styles on all new interactive elements. `tsc -p tsconfig.app.json --noEmit` EXIT:0. `npm run type-check` EXIT:0. `npx vite build` EXIT:0. |

### P1 — strongly expected, ship if time allows

| ID | Feature | Owner | Acceptance |
|---|---|---|---|
| R4-P1-1 | **UCSD Appliances offline corpus adapter** (per `orchestrator/ucsd_amazon_ingest_plan.md` — YELLOW LIGHT on license, see §4 legal posture below) | backend-v4 | `UCSDAdapter(BaseScraper)` downloads `Appliances.jsonl.gz` + `meta_Appliances.jsonl.gz` from the UCSD datarepo, filters by brand whitelist, field-maps per ingest plan §3. Registered in `get_scraper()` factory under `SCRAPER_ADAPTER=ucsd`. Pipeline runs on ingested text, stores `Mention` records. UI label: "Historical Amazon (pre-Oct 2023)" on any UCSD-sourced data. |
| R4-P1-2 | **Aaru-style What-If Simulator v1** (LLM prompt-chain) | backend-v4 + frontend-v4 | See §3.2 — full acceptance criteria. Exit: `POST /api/simulate` accepts natural-language scenario, returns `SimulationResult`. Frontend "What-If" panel on Product Analysis page. Explicit "Simulated reaction, not empirical behavior modeling" disclaimer. LLM dependency documented in `.env.example`. |
| R4-P1-3 | **AlertEvent.platforms filter propagation fix** (if not absorbed into R4-P0-4) | frontend-v4 | Covered by R4-P0-4 acceptance — listed separately for visibility. |
| R4-P1-4 | **Reddit niche subreddit expansion** (per `alt_consumer_signal_sources.md`) | backend-v4 | `RedditScraper` default subreddit list expands beyond r/sharkninja to: r/BuyItForLife, r/Appliances, r/Coffee, r/airfryer, r/VacuumCleaners, r/homeautomation. Zero additional infra — extends R4-P0-2. |
| R4-P1-5 | **Forecast-novelty integration** (novelty clusters with thin data still get a "Low confidence — projection shown anyway" forecast card per forecast_visual_conventions.md §4) | backend-v4 + frontend-v4 | Novelty clusters (`is_novel=true`) with `mention_count < 50` get a forecast with `low_confidence=true` flag. Frontend shows amber "Low confidence" chip and reduced-opacity dashed line per the visual conventions table. |

### P2 — deferred with explicit target round

| ID | Feature | Status | Target round | Rationale |
|---|---|---|---|---|
| R4-P2-1 | README polish pass (Agentforce survivorship framing, Foodi counterfactual, Crossan-Matos vocabulary) | **DEFERRED** | **R5** | Per round_3_charter.md §3.6 allocation table, this is R5 business-leader work. R4 engineers MUST NOT touch README.md. |
| R4-P2-2 | Exportable digest (CSV-first, PDF if time) | **DEFERRED** | **R5** | Wait until forecast + simulator are in place before exporting. |
| R4-P2-3 | Dark mode (REQ-023 P2) | **DEFERRED** | **R5 optional** | Tokens from R3 make it cheap. Not urgent. |
| R4-P2-4 | Chunk-size code splitting (vite 716 kB warning) | **DEFERRED** | **R5** | Warning only, not error. R5 polish. |
| R4-P2-5 | Google Trends pytrends integration | **DEFERRED** | **R5 optional or later** | YELLOW LIGHT ToS. Interesting as a demo flourish but not R4 critical. |
| R4-P2-6 | StackExchange home-improvement tag ingest | **DEFERRED** | **R5 optional** | GREEN legal but adds complexity; R4 has 5 P0 items already. |
| R4-P2-7 | TikTok any-vector | **DEFERRED** | **R5 with budget decision** | Research API is academic-only; yt-dlp is RED ToS; third-party scrapers are $50-500/mo in a YELLOW-RED gray zone. Not viable for R4, but TikTok Shop velocity signal is the interesting differentiator — R5 reopens if budget justifies paid third-party tools. |
| R4-P2-8 | eBay resale price signal | **REJECTED** | — | Requires new data model (prices, not sentiment text). Out of scope for an NLP-focused dashboard. |
| R4-P2-9 | Discord public-server sentiment | **REJECTED** | — | Low SharkNinja-specific volume, requires server discovery, low ROI. |

---

## 3. Prediction and Implication Feature Specs

### 3.1 MiroFish Trend Forecast — full scope (R4-P0-1)

**Backend scope:**

New endpoint `GET /api/products/{model}/forecast` returning:
```python
class ForecastPoint(BaseModel):
    date: str  # ISO YYYY-MM-DD
    projected_score: float  # [-1.0, 1.0]
    confidence_lower: float  # [-1.0, 1.0]
    confidence_upper: float  # [-1.0, 1.0]

class ForecastResponse(BaseModel):
    product_model: str
    historical: List[TimeseriesPoint]  # the observed series, unchanged
    forecast: List[ForecastPoint]  # 4 weeks forward, one point per week
    method_label: str  # e.g. "Linear decay-weighted projection on 30-day velocity"
    input_mention_count: int  # how many mentions fed the projection
    input_window_days: int  # the lookback window used
    low_confidence: bool  # computed: mention_count < 50 OR window_days < 14
    caveats: List[str]  # explicit limitations, e.g. "Not modeled for supply-chain events"
```

**Implementation constraints:**
- **NO LLM calls in the forecast path.** Pure Python math. If engineers feel tempted to "just call OpenAI for the projection," that is an automatic R4 scope violation.
- **Method: decay-weighted linear projection.** Read mentions from the last 30 days, compute aspect-level velocity (mentions per week per aspect), apply exponential decay weighting (recent mentions count more), project forward 4 weeks linearly. Widen confidence bands as horizon grows — at T+1 week band is ±0.05, at T+4 weeks band is ±0.18 (rough anchoring, tunable constants).
- **Method transparency:** the `method_label` field must accurately describe the implementation. Backend-v4 includes a comment block in `backend/app/forecast.py` (or equivalent) documenting the formula, and exposes it via a `/api/products/{model}/forecast?explain=true` query parameter that returns method documentation.
- **Honest thresholds:** if `mention_count < 50` or `window_days < 14`, set `low_confidence=true`. The forecast still returns — it degrades visually, it does not hide.

**Frontend scope (per `frontend/docs/forecast_visual_conventions.md` §6 table — this is mandatory, not optional):**

On `ProductAnalysisPage`, below the existing sentiment line chart:
- New card: "Trend Forecast" with subtitle displaying `method_label` and `input_mention_count` ("47 mentions over 30 days")
- Historical line: `<Line strokeWidth={2} stroke={cssVar('--chart-blue')} />`
- Forecast line: `<Line strokeDasharray="6 4" strokeWidth={1.5} stroke={cssVar('--chart-blue')} opacity={lowConfidence ? 0.4 : 1} />`
- Confidence band: `<Area fillOpacity={0.15} fill={cssVar('--chart-blue')} />` (upper + lower)
- Today marker: `<ReferenceLine x={todayIndex} strokeDasharray="3 3" label="Today" />`
- Low-confidence amber badge in card header (not on chart canvas) when `response.low_confidence === true`: amber dot + "Low confidence — {input_mention_count} mentions over {input_window_days} days"
- Below-chart footnote, italic, 12px, `var(--text-tertiary)` color: *"Projections are model-generated estimates based on observed trends. Not a guarantee of future outcomes."*
- `(i)` icon in the card title that reveals `caveats[]` on hover

**Scope fence:** NO scenario comparison (base/optimistic/pessimistic overlay). That is an R5 polish item. R4 ships single-scenario only.

**Theme token additions** (per forecast_visual_conventions.md §7):
Add to `theme.css`:
```css
--forecast-dash: 6 4;
--forecast-opacity-low-confidence: 0.4;
--confidence-band-fill-opacity: 0.15;
--color-caution: #F5A623;  /* amber for low-confidence badge */
```

**Acceptance test:** open Product Analysis for any seeded product with ≥50 mentions. Forecast card renders with dashed line extending 4 weeks beyond the "Today" marker. Confidence band widens visually. Footnote present. Hover on `(i)` icon shows caveats. Open Product Analysis for a product with <50 mentions (e.g. the novelty seed from R3 fixtures). Forecast still renders, with amber low-confidence chip, 0.4 opacity dashed line, and wider band.

### 3.2 Aaru-style What-If Simulator v1 (R4-P1-2)

**Backend scope:**

New endpoint `POST /api/simulate` accepting:
```python
class SimulationRequest(BaseModel):
    scenario: str  # natural language: "What if Shark launched a $99 budget version targeting renters?"
    product_model: Optional[str]  # context anchor
    filter_context: Optional[MentionFilter]  # current dashboard filter state
```

Returning:
```python
class SimulatedSegment(BaseModel):
    segment_label: str  # e.g. "Price-sensitive first-time buyers"
    predicted_reaction: Literal["positive", "negative", "mixed", "neutral"]
    confidence_narrative: str  # plain English, 2-3 sentences
    key_quotes_used: List[str]  # grounding — which real review snippets informed this segment

class SimulationResult(BaseModel):
    scenario: str  # echo
    product_model: Optional[str]
    segments: List[SimulatedSegment]  # 3-5 segments
    overall_disclaimer: str  # MUST contain "Simulated reaction based on LLM heuristic, not empirical behavior modeling"
    model_used: str  # e.g. "claude-sonnet-4-5"
    tokens_consumed: int
```

**Implementation constraints:**
- **LLM dependency:** backend-v4 introduces one LLM client (OpenAI SDK or Anthropic SDK). API key in `.env` as `SIMULATION_LLM_API_KEY`, NOT committed. `.env.example` documents required env vars.
- **Grounding:** every LLM prompt MUST include 5-10 real `Mention` records from the filter context as grounding data. The LLM is reasoning over actual consumer text, not hallucinating from the product name alone. `key_quotes_used` field captures which mentions were sent to the LLM.
- **Prompt structure** (backend-v4 finalizes): system prompt frames the LLM as a consumer insights analyst; user prompt includes the scenario + filter context + 5-10 grounding mentions; response_format requires structured output matching `SimulationResult` schema.
- **Caching:** if the same `(scenario, product_model, filter_context_hash)` tuple has been simulated before, return the cached result. Prevents LLM cost blowup on repeated demo runs.
- **Timeout:** 30 seconds max per simulation. On timeout, return a structured error with a friendly message, NOT a crash.
- **Honesty label:** `overall_disclaimer` MUST contain the literal string "Simulated reaction based on LLM heuristic, not empirical behavior modeling." Hardcoded. This is the Aaru anti-theater protection.

**Frontend scope:**

New panel on ProductAnalysisPage (or new dedicated "What-If" page if the simulator requires more real estate — frontend-v4's call, charter does not mandate):
- Large text input: "What if..." scenario entry, placeholder: "What if Shark launched a $99 budget version targeting renters?"
- Submit button: "Simulate reaction"
- Loading state: skeleton + "Running simulation on {N} real consumer mentions..."
- Results: 3-5 segment cards, each showing segment label, polarity badge, confidence narrative, and "View quotes" expander revealing `key_quotes_used`
- Prominent disclaimer banner at the top of the result: the `overall_disclaimer` field rendered in italic with amber `--color-caution` accent
- Error state: friendly timeout/error message with retry button

**Scope fence:** NO multi-scenario branching (compare scenario A vs B). Single scenario per request. R5 polish item.

---

## 4. Data Integration Strategy for Round 4

### 4.1 Primary combo — Reddit PRAW + HN Algolia (GREEN LIGHT)

Per `real_api_integration_proposal.md` and team-lead's R4 mandate note:

- **Reddit PRAW** implementation: `RedditScraper(BaseScraper)` under `backend/app/scrapers/reddit_adapter.py`. OAuth client_id + client_secret in env. Subreddit list starts with r/sharkninja then expands per R4-P1-4 to 6 additional niche subs. Rate limit: 100 QPM authenticated. Field mapping: `submission.selftext + "\n\n" + top_N_comments` → `Mention.text`. `source_platform = SourcePlatform.reddit`. `posted_at = datetime.fromtimestamp(submission.created_utc, tz=UTC)`. Run text through existing NLP pipeline.
- **HN Algolia** implementation: `HackerNewsScraper(BaseScraper)` under `backend/app/scrapers/hn_adapter.py`. `GET https://hn.algolia.com/api/v1/search?query={brand}` for each brand in the whitelist. Each hit's comments via Firebase API item lookup. Field map as above. `source_platform = SourcePlatform.other` (no HN enum value — acceptable for R4, enum extension is R5 cleanup if judges notice).
- Both adapters register in `backend/app/scrapers/__init__.py::get_scraper()` factory via new env value cases (`reddit`, `hn`). Router code UNCHANGED per REQ-003.
- `.env.example` documents required variables.

**Legal posture:** both GREEN LIGHT for internal/non-public demo. Proposal §commercial-ToS-risk section lines 338-343 applies if the demo ever becomes public — team-lead's call, not charter's.

### 4.2 Optional Tier 2 — UCSD Appliances offline corpus (YELLOW LIGHT)

**Charter decision: INCLUDE as R4-P1-1, with explicit legal posture disclosure.**

Rationale: the YELLOW LIGHT in `orchestrator/ucsd_amazon_ingest_plan.md §6` is specifically about **commercial** use. Round 4 is internal-Vincent-facing demo, not SharkNinja-client-facing production. Backend-v3's own risk assessment rates internal demo as LOW-MEDIUM risk. Including it fills the Amazon-brand data gap the dashboard currently cannot serve (commercial Amazon API is legally unavailable).

**Mandatory charter constraints for R4-P1-1:**
- UI label: any Amazon brand data from UCSD ingest MUST display "Historical Amazon (pre-Oct 2023)" in a metadata tag on mention cards, drill-through panels, and any aggregate view filter that includes UCSD-sourced data.
- Backend emits `Mention.source_url = None` for UCSD rows (dataset has no source URL). This is correct and documented.
- `README.md` is NOT updated in R4 — but the R4 engineers document the UCSD data origin in a new section of `contracts/real_api_integration_proposal.md` as an R4-landed implementation note.
- **Pre-R5 action item for team-lead (not for engineers):** obtain written clarification from McAuley Lab (contact: yphou@ucsd.edu) on whether commercial demo use is permitted, BEFORE any client-facing demo that uses UCSD data.

**Exit criterion:** engineers download the Appliances subset (~1-2 GB), filter by brand whitelist, ingest ≥100 UCSD-sourced mentions covering ≥3 SharkNinja SKUs. Product Analysis for those SKUs shows UCSD mentions intermixed with Reddit/HN mentions. UI label "Historical (pre-Oct 2023)" visible on UCSD-sourced rows.

### 4.3 New data source — CPSC Recalls API (GREEN LIGHT, R4-P0-3)

Not in the R3 proposal. Discovered in `orchestrator/alt_consumer_signal_sources.md` Tier 1. **This is a meaningful R4 addition because it directly supports the Terri Williams (P4) persona with authoritative government-sourced safety signal.**

- Endpoint: CPSC public recalls API (exact URL to be confirmed by backend-v4 via WebSearch during implementation — `https://www.cpsc.gov` API landing page)
- Legal posture: GREEN. US government public data, no ToS, no key, no rate limit published.
- Scraper: `CPSCScraper(BaseScraper)`. Filter by `firm_name` containing brand whitelist. Each recall record maps to a `Mention` with `source_platform = SourcePlatform.other`, `text = recall.title + "\n\n" + recall.description`, `posted_at = recall.announcement_date`.
- Alerts integration: backend-v4 adds a "Safety Recall" flag to alerts whose underlying mentions include a CPSC-sourced record. These alerts get maximum severity (effectively overriding the cross-platform multiplier ceiling) and show a prominent red banner + link to the official CPSC URL.
- Frontend: `AlertCard` gains a "Safety Recall" variant with red badge and "View on CPSC.gov" external link.

**Why this matters for the pitch:** a dashboard that surfaces a real CPSC recall in its alerts layer is instantly credible to a CGO audience. The Foodi counterfactual (research/r4_prep_foodi_precedent.md) explicitly lists CPSC as the authoritative downstream signal; our tool now connects directly to that layer.

### 4.4 Deferred/rejected data sources

- **Google Trends (pytrends):** R5 optional. Captures pre-purchase intent, unique angle, but YELLOW legal posture for commercial use and unofficial wrapper.
- **StackExchange home-improvement tag:** R5 optional. GREEN legal but adds complexity.
- **TikTok (any vector):** REJECTED per `tiktok_scraping_feasibility.md`. Research API is academic-only, yt-dlp is RED ToS, third-party scrapers are expensive + YELLOW.
- **eBay resale prices:** REJECTED. Requires new data model outside the NLP pipeline.
- **Discord public servers:** REJECTED. Low SharkNinja-specific volume.

---

## 5. Frontend-design Skill Protocol for R4 Spawn

**Finding from R3:** the `frontend-design` skill was NOT available in teammate context; frontend-v3 executed the protocol manually and produced `frontend/docs/design_direction.md` (205 lines), `polish_patterns.md`, `ux_research.md`, and `forecast_visual_conventions.md`. That manual execution worked — the R3 rubric passed.

**Protocol for R4 spawn prompts (team-lead bakes this into the frontend-v4 prompt):**
- Frontend-v4 reads `frontend/docs/design_direction.md` ONCE as the established aesthetic direction. Do NOT re-run the skill protocol from scratch.
- Frontend-v4 inherits the existing design tokens in `theme/index.ts` + `theme.css`. New tokens added per §3.1 for forecast-specific values.
- Frontend-v4 reads `frontend/docs/forecast_visual_conventions.md` as the mandatory implementation spec for the forecast panel. The §6 table is a binding checklist.
- Frontend-v4 invokes the `frontend-design` skill manually (same protocol as v3) ONLY IF they are introducing a new visual paradigm not covered by existing docs. Forecast panel is covered; simulator panel is NOT covered — frontend-v4 writes `frontend/docs/simulator_visual_conventions.md` (or similar) before coding the simulator UI.

---

## 6. Round 4 Audit Plan

When engineers report complete, I run this checklist.

### 6.1 Command-level verification (Round 3 floor non-regression)

```bash
cd "D:/Ai_Project/MeowOS/99_MyFiles/Project_Trial/Challenge_5_v2"
python -m pytest backend/tests/ -v 2>&1 | tail -20   # expect 44+ passed, 0 new failures
python -c "import yaml; d=yaml.safe_load(open('contracts/api-contract.yaml')); print(sorted(d['paths'].keys()))"
# expect 2+ new paths: /api/products/{model}/forecast, /api/simulate (if R4-P1-2 ships)
# expect AlertEvent schema to include 'platforms' field
cd frontend
npx tsc -p tsconfig.app.json --noEmit; echo "EXIT:$?"
npm run type-check; echo "EXIT:$?"
npx vite build 2>&1 | tail -15
```

### 6.2 New disk audits

- `grep -rn "LLM\|openai\|anthropic" backend/app/forecast.py backend/app/routers/products.py` — MUST return zero hits. Any LLM call in the forecast path is a scope violation.
- `grep -n "Simulated reaction based on LLM heuristic, not empirical behavior modeling" backend/` — MUST return at least one hit (the hardcoded disclaimer string).
- `grep -n "Historical.*pre.*2023\|pre-Oct 2023" frontend/src/` — MUST return at least one hit (the UCSD label) IF R4-P1-1 ships.
- `grep -n "CPSC\|cpsc" backend/app/scrapers/` — MUST return hits for the `CPSCScraper` implementation.
- `grep -n "platforms" frontend/src/pages/AlertsInsightsPage.tsx` — MUST hit the dep array (R4-P0-4 completion check).
- Read `contracts/api-contract.yaml` head — confirm `ForecastResponse`, `SimulationResult` (if shipped), `AlertEvent.platforms` all present.
- Read `frontend/docs/design_direction.md` line count — must be ≥205 (unchanged or extended from R3).
- Read `frontend/docs/forecast_visual_conventions.md` — must be unchanged from R3 (frontend-v4 does NOT rewrite it).

### 6.3 Internet-aligned verification (enhanced audit role)

Per standing rule, any NEW external claim engineers make must be WebSearched:

- **CPSC Recalls API endpoint and response schema:** WebSearch to confirm backend-v4's implementation matches the actual 2026 API format. This is a new integration — correctness matters.
- **PRAW OAuth flow 2025/2026:** confirm the OAuth credentials pattern backend-v4 uses is current. Reddit changed OAuth requirements in 2025.
- **Any new library backend-v4 introduces** (e.g. `openai`, `anthropic`, `praw`, `pytrends`) — verify license, latest version, maintenance status.
- **UCSD dataset download URL:** confirm the `datarepo.eng.ucsd.edu` URL pattern is still live (not moved to HuggingFace-only) IF R4-P1-1 ships.

I will NOT re-verify claims I already confirmed in R3 audit (PRAW 100 QPM, UCSD license YELLOW LIGHT, HN Algolia free-no-auth). Those are settled.

### 6.4 Exit criteria for Round 4 PASS

**All of the following must be true:**

1. R4-P0-1 through R4-P0-5 all acceptance-criterion green
2. At least 2 of R4-P1-1 through R4-P1-5 green (partial P1 is acceptable)
3. Round 3 floor intact: 44+ passed pytest, 0 tsc errors, vite build success
4. Trend Forecast panel renders visually per `forecast_visual_conventions.md §6 table`. I will NOT re-verify pixel-perfect match; I will verify the structural primitives (dashed line, confidence band, Today marker, footnote, amber low-confidence chip when applicable).
5. No LLM call in the forecast code path (§3.1 hard constraint)
6. What-If Simulator (if shipped) contains the exact disclaimer string
7. AlertEvent.platforms field exists and propagates to the Alerts page filter dep array

**Failure conditions:**
- Forecast implemented via LLM → automatic FAIL + scope violation flag
- Simulator disclaimer string missing → FAIL
- R3 filter-propagation regression on any page → FAIL
- README.md modified in R4 → scope violation FAIL
- Any R3 pytest regression → FAIL

---

## 7. Contract Change Protocol for R4

R4 adds **up to 4 contract changes** to schemas.py (CLAUDE.md §4 protocol fires each time):

1. `ForecastResponse` + `ForecastPoint` (R4-P0-1)
2. `SimulationRequest` + `SimulationResult` + `SimulatedSegment` (R4-P1-2 if shipped)
3. `AlertEvent.platforms` field (R4-P0-4)
4. `Mention.record_type` optional field (R4-P0-3, for CPSC record type distinction — may be deferred if backend-v4 inlines into `source_platform`)

**Sequencing rule for backend-v4:** batch the schema changes into 1-2 commits. Regenerate `api-contract.yaml` ONCE after the batch. Notify frontend-v4 via SendMessage ONCE with the full change list. Four separate contract-regen cycles would be wasteful; two maximum.

**Frontend-v4 obligation:** run `npm run gen:types` against the new YAML, verify `src/types/api.ts` and `src/types/index.ts` barrel still compile, fix any name drift in a single pass.

---

## 8. Proposed Requirement Amendments (informational, not for execution this round)

Rolled forward from `round_3_charter.md §8`, plus new:

1. **REQ-015 amendment** (unchanged from R3 proposal): severity formula includes platform_count factor + novelty 2× multiplier ← partially landed in R3, remains proposed as formal amendment
2. **REQ-016 amendment** (unchanged): emerging themes require NEW-cluster detection, not recently-trending ← landed in R3
3. **NEW REQ-017 proposed:** Trend Forecast panel with honest heuristic labeling and confidence bands ← lands in R4
4. **NEW REQ-018 proposed:** Frontend maturity rubric M1-M6 as gating criterion with `frontend-design` protocol ← landed in R3, continuing in R4
5. **NEW REQ-019 proposed:** CPSC Recalls API as an authoritative Safety Recall data source for the Alerts page ← lands in R4-P0-3
6. **NEW REQ-020 proposed:** AlertEvent.platforms field for filter unification ← lands in R4-P0-4
7. **NEW REQ-021 proposed (R5 target):** README polish with Agentforce survivorship framing, Foodi counterfactual (cite the peer-reviewed 45% figure from r4_prep_foodi_precedent.md), and Crossan-Matos vocabulary

Team-lead decides whether to amend `requirements.md` in R5 or after Vincent returns.

---

## 9. Handoff Notes for v4 Engineers

**Both engineers must read before starting:**
- This charter (especially §0 philosophy and §2 P0/P1 queue)
- `contracts/round_3_charter.md §0` (R3/R4/R5 allocation context)
- `contracts/review-round-3.md` (R3 floor to protect)

**backend-engineer-v4 reads additionally:**
- `contracts/real_api_integration_proposal.md` (the R3 proposal doc — R4 executes against it)
- `contracts/research/orchestrator/ucsd_amazon_ingest_plan.md` (if R4-P1-1 ships)
- `contracts/research/orchestrator/alt_consumer_signal_sources.md` Tier 1 (CPSC section for R4-P0-3)
- `contracts/research/orchestrator/mirofish_mvp.md` (if it exists — for the forecast method)

**frontend-engineer-v4 reads additionally:**
- `frontend/docs/design_direction.md` (established aesthetic — inherit, do not re-derive)
- `frontend/docs/forecast_visual_conventions.md` (the binding §6 implementation table)
- Existing theme token files

**Communication discipline (from the team rules):**
- Refer to teammates by name: `team-lead`, `backend-engineer-v4`, `frontend-engineer-v4`, `business-leader-v2`
- Contract changes batched — see §7
- Plan approval required from team-lead before writing any code (per CLAUDE.md)

**Handoff file requirement (from new standing rule):**
When engineers finish R4, their `contracts/state/{name}_handoff.md` files MUST include:
- `TRIED_AND_REJECTED`: approaches considered and abandoned, one-line reason each
- `WHY` (per decision): causal rationale for each major decision
These fields were added to the handoff template after R3 (team-lead 2026-04-11 addendum).

---

## 10. Charter Meta

**Status: FROZEN** at 2026-04-11. No revisions without explicit team-lead coordination.

**Author's self-assessment on context compression (per standing rule):**
- Did NOT re-read my 4 existing R4 prep research files — they are in session memory from last cycle
- Did NOT re-read the parallel-authored `r4_prep_topic2/3/4` files from the orchestrator — they would duplicate my own research
- Did NOT re-read `round_3_charter.md` or `review-round-3.md` — cited from session memory
- Read 4 NEW reference files ONCE each with targeted limits: `ucsd_amazon_ingest_plan.md` (full), `forecast_visual_conventions.md` (full), `alt_consumer_signal_sources.md` (first 80 lines for Tier 1), `tiktok_scraping_feasibility.md` (first 60 lines for verdict)
- Total context cost for the charter: 4 targeted reads + 1 Glob sanity check + this Write. Well inside the 50% budget.

**Revision log:**
- **Draft 1 (this version, 2026-04-11, FROZEN):** initial R4 charter incorporating team-lead R4 auto-trigger mandate, UCSD YELLOW LIGHT decision (INCLUDE with disclosure), CPSC Recalls API as NEW R4-P0-3 (discovered in backend-v3 research, not in original scope), frontend visual conventions mandatorily cited, forecast scope fence (NO LLM in forecast path), simulator disclaimer string hardcoded, contract change batching rule, handoff template expansion noted.

**What I did NOT do:**
- Did not touch `README.md` (explicit R5 scope)
- Did not touch `requirements.md` (team-lead decides REQ amendments)
- Did not touch any backend or frontend source files
- Did not spawn v4 engineers (team-lead's job)
- Did not modify engineer handoff files
- Did not re-verify R3 audit findings — the review-round-3.md PASS stands

Charter author: business-leader-v2 (draft 1 FROZEN, 2026-04-11)
