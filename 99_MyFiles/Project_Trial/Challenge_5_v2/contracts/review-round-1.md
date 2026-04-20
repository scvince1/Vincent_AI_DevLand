# Review Round 1 — SharkNinja Consumer Sentiment Dashboard

**Reviewer:** business-leader-v2
**Date:** 2026-04-11
**Scope:** Task #5 (backend-engineer-v2) + Task #6 (frontend-engineer-v2) deliverables vs `contracts/requirements.md` REQ-IDs and `CLAUDE.md` constraints.
**Methodology:** Self-reports were NOT trusted. Every claim in this report is backed by an on-disk Read, a Grep hit, or a live command run in this review session.

---

## Overall verdict: PARTIAL (very close to PASS)

**Backend: PASS across the board.** NLP edge-case suite is 34/34 real passes with zero mocks; additive robustness suite is 10 passed + 6 explicitly-documented xfails as round 2 refinement markers; scraper ABC + Depends wiring is clean; schemas.py is the single source of truth with `response_model=` on every endpoint; api-contract.yaml has exactly 14 paths matching self-report; refinement A (R4 contrastive-conjunction exclusion) and refinement B (ABSA copular dep-walk) are both present and verified.

**Frontend: PASS on structure, PARTIAL on fixture hygiene.** `npx vite build` succeeds (615 modules, 707 kB bundle, 196 ms). All 5 pages have correct business-question subtitles and wire `useDrilldownStore`. PlatformHeatmap is a real CSS Grid of divs consuming the correct `PlatformComparisonResponse` shape. FilterUrlSync uses `useSearchParams`. Named type aliases are exposed via a new `src/types/index.ts` barrel file (a cleaner choice than my previous suggestion of appending to the auto-generated `api.ts`). But two issues remain:

1. **`src/fixtures/mentions.ts` contains stubbed, type-invalid aspect literals** (e.g. `{ name: '', polarity: '', score: , confidence: 0.9, snippet: '' }` — empty strings and missing `score` value). This yields 10 `tsc -p tsconfig.app.json --noEmit` errors (`Property 'confidence' is missing`; the underlying issue is actually a half-finished fixture migration). `vite build` tolerates this because esbuild is permissive, but the fixture is broken data if `USE_FIXTURES=true` is used at runtime.
2. **`npm run type-check` still runs the solution-style root tsconfig and misleadingly exits 0 despite those 10 errors**. The tsbuildinfo cache masks them. The previous-round action item to point the script at `tsconfig.app.json` directly was not landed. This is why both engineers believe type-check is clean; it is not.

Neither issue blocks the demo when the real backend is running on `:8000` (the CSV adapter emits proper AspectSentiment objects and the broken fixture is dead code in that mode). But both should be fixed in round 2 because a judge inspecting the repo will find them, and the build report should be honest.

**Verdict: PARTIAL.** Round 2 fix scope for frontend-engineer-v2 is **2 files**: (1) fill in `src/fixtures/mentions.ts` aspect literals with real values (or delete the stub entries), and (2) edit `package.json` so `"type-check"` runs `tsc -p tsconfig.app.json --noEmit`. No backend fixes required.

---

## 1. REQ-ID Traceability Matrix

Legend: **PASS** = fully satisfied; **PARTIAL** = intent satisfied but with a residual issue; **MISS** = not done. Evidence column points to the exact file/command that was checked in this review.

| REQ-ID | Pri | Description | Satisfied by (verified) | Status |
|---|---|---|---|---|
| REQ-001 | P0 | NLP edge-case suite, real pipeline, no mocks, failing-before/passing-after | `backend/tests/test_nlp_edge_cases.py` — live run `pytest test_nlp_edge_cases.py -v` = **34 passed, 0 xfailed, 0.92s**. Grep for `mock\|Mock\|patch\|MagicMock` in `backend/tests/` returns only the docstring phrase "Zero mocks" in both test files. Structure: `test_*_vader_fails` + `test_*_enhanced_passes` parametrized pairs per category. | **PASS** |
| REQ-002 | P0 | Enhanced NLP: sarcasm, comparative, ABSA, domain ≥40 terms | `backend/app/nlp/pipeline.py` is a real 9-step pipeline. `sarcasm.py` has 4 R-rules including R4 contrastive exclusion (lines 87-95: `_R4_EXCLUSION_CONJUNCTIONS = {"but", "however", "unlike", "finally", "compared to"}`). `absa.py` has `_COPULAR_VERBS` set (line 320) + `nsubj`/`acomp`/`attr`/`xcomp` dep-walk (lines 340-373). `domain_lexicon.py::DOMAIN_TERMS` counts ~75 surface forms / ~50 canonical aspects across vacuum/kitchen/coffee/air/hair/general — floor is 40. | **PASS** |
| REQ-003 | P0 | BaseScraper ABC + CSVAdapter + Depends; routers never import CSVAdapter by name | `scrapers/base.py` = real `ABC` + two `@abstractmethod` methods. `scrapers/__init__.py::get_scraper()` singleton factory where `from backend.app.scrapers.csv_adapter import CSVAdapter` appears ONLY inside the `if adapter == "csv":` conditional. **Grep for `CSVAdapter` across `backend/app/routers/` returns zero matches.** Grep for `Depends(get_scraper)` returns 13 hits in all 6 router files (alerts, mentions, overview, platforms, products, topics). | **PASS** |
| REQ-004 | P0 | `schemas.py` single source of truth, `api-contract.yaml` exported from schemas.py, frontend reads YAML | `backend/models/schemas.py` declares 22 Pydantic models. Live YAML enumeration via `python -c "yaml.safe_load(...)"` returns **14 paths** including `/api/platforms/comparison`, `/api/topics/comparative`, `/api/alerts/{alert_id}/acknowledge`, `/health`, etc. `scripts/export_openapi.py` exists as the generator. `frontend/src/types/api.ts` is openapi-typescript-generated output (header: "This file was auto-generated by openapi-typescript"). All 13 router endpoints use `response_model=<PydanticClass>`. | **PASS** |
| REQ-005 | P0 | 5 dashboard pages, each answering a named business question | All 5 page files exist. Business-question subtitles verified by Grep against `frontend/src/pages/` — each page has the literal subtitle from requirements.md §6 (see §5.4 below). | **PASS** |
| REQ-006 | P0 | Every UI number traceable to source mentions, one click | `components/shared/EvidenceDrilldown.tsx` exists and imports `Mention` from the barrel. `store/drilldownStore.ts` exists. **All 5 page files grep-hit `openDrilldown`** (AlertsInsights, TopicExplorer, PlatformComparison, ProductAnalysis, Overview). `PlatformHeatmap.tsx` exposes an `onCellClick` prop for drill from the heatmap. | **PASS** |
| REQ-010 | P1 | Product filter hierarchy brand → category → model | `store/filterStore.ts` carries `brands: Brand[]`, `categories: Category[]`, `productModel?: string`. `components/filters/FilterBar.tsx` imports those types from the barrel. `FilterUrlSync.tsx` serializes all three into URL params. | **PASS** |
| REQ-011 | P1 | Time range selector (7/30/90/custom) drives every chart | `filterStore.ts::dateRange: '7d' \| '30d' \| '90d' \| 'custom'` with `dateRangeToFromTo` helper that computes `dateFrom`/`dateTo` ISO dates from the range. Passed to every `fetch*` call via the store. | **PASS** |
| REQ-012 | P1 | Per-aspect sentiment breakdown, not just overall | `schemas.AspectTrend` with `aspect/mention_count/avg_score/trend_delta/severity/sparkline`. `routers/products.py::get_product_aspects` returns `ProductAspectResponse`. `pages/ProductAnalysisPage.tsx` consumes it. | **PASS** |
| REQ-013 | P1 | Platform breakdown Reddit/Amazon/YouTube/Trustpilot/Twitter | `schemas.SourcePlatform` enum has all 5 platforms + `other`. CSV fixtures in `backend/data/` have a `source_platform` column. `PlatformComparisonResponse.grid: PlatformAspectCell[]` is consumed by the rewritten `PlatformHeatmap.tsx` as real CSS Grid with `display: 'grid'` + `gridTemplateColumns` (lines 49 & 63). | **PASS** |
| REQ-014 | P1 | Competitive view Shark vs Dyson etc. | `schemas.ComparativeTopicResponse` with `brand_a`, `brand_b`, `share_of_aspect`. `routers/topics.py::get_comparative_topics` endpoint exists. `endpoints.ts::fetchTopicComparative(brand_a, brand_b)` function wired. `TopicExplorerPage.tsx` imports `ComparativeTopicResponse` and `ShareOfAspect` from the barrel. | **PASS** |
| REQ-015 | P1 | Alerts with severity (volume × magnitude × recency) + exemplar links | `schemas.AlertEvent.severity: float` + `exemplar_mentions: List[Mention]`. `backend/app/aggregations.py::compute_alerts` exists. `routers/alerts.py` exposes list + `/acknowledge` PATCH. `AlertsInsightsPage.tsx` imports `AlertEvent` from the barrel and wires acknowledge + drill. | **PASS** |
| REQ-016 | P1 | Topic Explorer via aspect clustering, not word clouds | `schemas.TopicCluster.momentum`. `routers/topics.py::get_topics` endpoint. **No word cloud component anywhere in the codebase** — grep for `wordcloud\|WordCloud\|word-cloud` returned zero matches in `frontend/src/`. | **PASS** |
| REQ-020 | P2 | CSV/PNG export | Not observed in this review. | MISS (nice-to-have) |
| REQ-021 | P2 | Confidence score displayed alongside each score | `schemas.AspectSentiment.confidence` + `DerivedSentiment.confidence` exposed and populated by pipeline. No frontend surface observed displaying it. | PARTIAL (backend-present, no frontend surface) |
| REQ-022 | P2 | Language detection flag | `schemas.Mention.language: str = "en"`. No non-English handling logic observed. | PARTIAL (flag present, no routing) |
| REQ-023 | P2 | Dark mode | `theme/index.ts` uses CSS custom properties (`var(--bg-surface)`, `var(--text-primary)`) which are dark-mode-ready, but no explicit toggle observed. | PARTIAL |

**Scoring summary (against the 5 judge-facing axes in requirements.md §5):**
- NLP Quality (40%): **PASS** — suite green, pipeline real, refinements present, no mocks.
- Architecture Cleanliness (20%): **PASS** — ABC clean, schemas.py canonical, YAML export clean.
- Dashboard Utility (20%): **PASS** with 2 fixture hygiene nits (§5.1).
- Evidence & Traceability (10%): **PASS** — drilldown wired on all 5 pages.
- Competitive Story (10%): **PASS at current README state** — strategic polish reserved for a post-round-2 README round (§9).

---

## 2. NLP Edge-Case Verification (REQ-001 + REQ-002 deep dive)

### 2.1 Live pytest output

```
$ python -m pytest backend/tests/test_nlp_edge_cases.py -v
backend/tests/test_nlp_edge_cases.py::test_copular_construction_absa PASSED [100%]
... (tail)
======================= 34 passed, 4 warnings in 0.92s ========================
```

- **34 tests, 0 xfailed, 0 skipped.** The 4 warnings are unrelated `vaderSentiment.py::codecs.open()` deprecation warnings from the VADER library — not our code.
- Structure: 16 verbatim edge cases × 2 test functions each = 32 parametrized tests, plus 2 refinement tests = 34.
  - **S1–S4** sarcasm: `test_sarcasm_vader_fails` (asserts VADER has no `sarcasm_flag` output, and for S1/S2/S3 also asserts VADER label ≠ negative as the incidental label failure) + `test_sarcasm_enhanced_passes` (asserts enhanced pipeline returns `overall_sentiment == 'negative'` AND `sarcasm_flag is True`)
  - **C1–C4** comparative: `test_comparative_vader_fails` (asserts VADER has no `comparative_pairs` output — structural gap assertion) + `test_comparative_enhanced_passes` (asserts the right brand→aspect→polarity pairs are emitted)
  - **A1–A4** ABSA: `test_absa_vader_fails` + `test_absa_enhanced_passes` (asserts `len(result.aspects) >= 2` and specific aspect-name/polarity matches)
  - **D1–D4** domain: `test_domain_vader_fails` + `test_domain_enhanced_passes` (asserts domain terms survive into `result.aspects` and score correctly)
  - **SN1** refinement A (sarcasm R4 contrastive exclusion): `test_sarcasm_negative_cases` parametrized with "Finally a vacuum that doesn't die or jam like my old Dyson — the suction is great and the brushroll doesn't tangle" — asserts `sarcasm_flag is False` and `overall_sentiment != 'negative'`
  - **Refinement B** (ABSA copular dep-walk): `test_copular_construction_absa` with "The portafilter is solid and the bean hopper is generous." — tests that both aspects (portafilter, bean_hopper) are extracted with `positive` or `mixed` polarity. Critically, **`solid` and `generous` are NOT in `STRONG_POSITIVES`/`STRONG_NEGATIVES` lexicons** (I checked — `absa.py` lines 27-47 is the full `STRONG_POSITIVES` dict, `solid` and `generous` are absent). This test therefore passes ONLY because the copular dep-walk path in `_refine_with_spacy` is providing the positive signal via spaCy's `acomp`/`attr`/`xcomp` children of the copular head. Real refinement, verifiable.

**No suspicious tests detected.** No `pytest.mark.skip`, no `pytest.mark.skipif`, no bare `pytest.xfail()` calls in `test_nlp_edge_cases.py`. Every test runs against `pipeline.analyze(text)`, which is the real layered pipeline (VADER → sarcasm → comparative → ABSA → compound recomputation → label derivation).

### 2.2 Robustness suite (additive, not gating)

`backend/tests/test_nlp_robustness.py`: **10 passed + 6 xfailed** (live `pytest test_nlp_robustness.py -v` output).

This is a **new additive file** whose docstring reads: *"additive coverage beyond the 16 gating edge cases. Some are expected to pass today; others are marked xfail to document known refinement opportunities for round 2."*

The 6 xfails are **documentation-as-tests**, each with an explicit `reason=` string:
1. `test_mixed_contrastive_dustbin_negative` — contrastive "but" clause resolution for the negative-side aspect
2. `test_three_brand_comparative_four_pairs` — three-brand comparative chains currently emit only 2 brands
3. `test_roomba_brand_alias_comparative` — `Roomba` → `irobot` alias plumbed in the lexicon but not all the way through comparative-pair emission
4. `test_multi_aspect_correct_polarities` — `buggy`, `drains too fast` not in `STRONG_NEGATIVES` lexicon
5. `test_sarcasm_brilliant_cue` — `Brilliant` as mid-sentence sarcastic opener needs new R rule
6. `test_rhetorical_question_negative` — rhetorical question polarity detection

**I commend this approach.** It is strictly better than hand-wavy TODO comments: each known limitation is a live test assertion that will automatically start passing when the refinement lands, and the `reason=` string makes the technical debt legible. It also documents a clear round 2 stretch scope. **None of these xfails count against REQ-001** because REQ-001 is scoped to `test_nlp_edge_cases.py`, not the additive robustness file. The 6 xfails are not cheating — they are a pattern I would recommend to any serious test suite.

### 2.3 Pipeline defensibility — refinement A verified

`backend/app/nlp/sarcasm.py` lines 87-95:
```python
# R4: VADER says positive but multiple negative signals present
# Exclusion: if a contrastive conjunction precedes the negative signals, this is likely
# a genuine positive review mentioning past issues (e.g. "finally a vacuum that doesn't die
# like my old Dyson") — do NOT fire R4 in this case.
_R4_EXCLUSION_CONJUNCTIONS = {"but", "however", "unlike", "finally", "compared to"}
_r4_has_exclusion = any(conj in lower for conj in _R4_EXCLUSION_CONJUNCTIONS)
if vader_scores.get("compound", 0) >= 0.2 and neg_signal_count >= 2:
    if cue_positions and not _r4_has_exclusion:
        return True, 0.75
```

Confirmed: the R4 exclusion is in the actual code path, and `test_sarcasm_negative_cases` (SN1) tests this behavior by including "finally" in the positive-review sentence.

### 2.4 Pipeline defensibility — refinement B verified

`backend/app/nlp/absa.py` lines 320-373: `_COPULAR_VERBS = {"be", "seem", "feel", "look", "sound", "remain", "become"}` and the `_refine_with_spacy` function walks `token.dep_ == "nsubj"` + `token.head.lemma_ in _COPULAR_VERBS` + iterates children with `dep_ in ("acomp", "attr", "xcomp")`, collects the subtree, scores via `_score_clause`. The comment on line 341 literally uses "The portafilter is solid" as the example. `test_copular_construction_absa` in the edge-case file passes against this code path, and since "solid"/"generous" are not in the strong-opinion lexicons, the dep-walk is **the only** code path that can provide positive signal for this sentence. Real refinement.

### 2.5 Domain lexicon coverage

`domain_lexicon.py::DOMAIN_TERMS`: ~75 surface forms mapping to ~50 canonical aspects. Categories: vacuums (~19), kitchen/air-fryer (~14), coffee (~18), air care (~5), hair tools (~4), general (~14). The 40-term floor in requirements.md §2 REQ-002 is comfortably exceeded.

---

## 3. Architecture Cleanliness Audit (REQ-003 + REQ-004)

### 3.1 Scraper abstraction (REQ-003)

Verified by file read and grep:

- `backend/app/scrapers/base.py`: real `class BaseScraper(ABC)` from `abc`, with `@abstractmethod` on both `fetch(...)` and `count(...)`.
- `backend/app/scrapers/csv_adapter.py`: `class CSVAdapter(BaseScraper)` implements both methods; loads CSVs at init, runs `pipeline.analyze()` on every row so derived sentiment is real NLP output not prebaked data.
- `backend/app/scrapers/__init__.py::get_scraper()`: singleton factory where `from backend.app.scrapers.csv_adapter import CSVAdapter` is inside the `if adapter == "csv":` branch (module-level import is not possible because the concrete class is NOT imported at the top of `__init__.py`).
- **Router grep: `grep -rn CSVAdapter backend/app/routers/` → zero matches.**
- **Router grep: `grep Depends(get_scraper) backend/app/routers/` → 13 hits** across alerts.py (2), mentions.py (2), overview.py (3), platforms.py (1), products.py (3), topics.py (2). This matches the 13 `@router.(get|patch)` endpoints and the 13 `response_model=` decorators. Full Depends coverage.

When a real Reddit/Trustpilot scraper is added later, it is a new class + a new `elif` branch in `get_scraper()` + an env var flip. Zero router edits.

### 3.2 Pydantic contract (REQ-004)

- `backend/models/schemas.py`: 22 Pydantic models. Every enum defined once as `str, Enum`. `DerivedSentiment` is the canonical sentiment object per requirements.md §7 (contains `overall_sentiment`, `compound_score`, `confidence`, `sarcasm_flag`, `aspects`, `comparative_pairs`). `Mention` is the canonical row object. Response models are one per page (`OverviewKPIs`, `ProductAspectResponse`, `PlatformComparisonResponse`, `TopicExplorerResponse`, `AlertListResponse`) plus helpers.
- `contracts/api-contract.yaml` — live enumeration via `python -c "import yaml; d=yaml.safe_load(open(...)); print(len(d['paths']))"` → **14 paths**:
  ```
  /api/alerts
  /api/alerts/{alert_id}/acknowledge
  /api/mentions
  /api/mentions/{mention_id}
  /api/overview/kpis
  /api/overview/share_of_voice
  /api/overview/timeseries
  /api/platforms/comparison
  /api/products
  /api/products/{product_model}/aspects
  /api/products/{product_model}/timeseries
  /api/topics
  /api/topics/comparative
  /health
  ```
  Matches backend-engineer-v2's self-report of 14 paths exactly. Matches the 13 `@router.*` decorators + 1 `/health` endpoint in `main.py`.
- `scripts/export_openapi.py`: exists, generates the YAML from `schemas.py`/FastAPI.
- **Every router endpoint uses `response_model=<PydanticClass>`** — 13 matches from grep, no hand-rolled response dicts.
- `frontend/src/types/api.ts`: openapi-typescript-generated. The first line is `/** This file was auto-generated by openapi-typescript. */`. Frontend never reads `schemas.py` directly; contract crosses the wire via YAML and lands as `components["schemas"][...]` types.

### 3.3 Refinement C — pipeline SentimentResult conversion

Verified: `backend/app/nlp/pipeline.py::SentimentResult.to_derived_sentiment()` converts the internal pipeline result into the Pydantic `DerivedSentiment` object used in API responses. This is a clean boundary: the pipeline uses plain Python dicts internally for speed, the converter builds Pydantic objects for the API, and the converter is the only place where the two layers touch. Matches backend-engineer-v2's self-report of "Refinement C applied via SentimentResult.to_derived_sentiment() converter."

### 3.4 aggregations module

`backend/app/aggregations.py`: helper module containing `compute_alerts` and related aggregation functions. Used by the alerts router and (per the imports in other routers) by overview/products for computed KPIs. This keeps aggregation logic out of the routers — routers are thin. Good separation.

---

## 4. Strategic Thesis Check (non-gating, informational)

Reminder of the real strategic thesis pulled from `99_MyFiles/Project_Trial` study doc and WebSearch ground-truth: the real audience for the README is a CGO-level SharkNinja exec whose mandate (April 29 2025) is consumer-first measurement; the Foodi OP300 recall (May 1 2025, 1,846,400 units, 106 burn reports, 26 lawsuits per CPSC) is the emotional anchor; cross-platform confirmation + novelty detection + survivorship-bias framing vs Agentforce are the sharpest angles.

**None of this is a blocker for round 1.** The current backend and dashboard satisfy the formal REQ-IDs. These thesis-level observations are reserved for a post-round-2 README polish round (§9) and are not engineer action items.

---

## 5. Frontend Audit (REQ-005 + REQ-006 + contract consumption)

### 5.1 Build status — the critical verification

```
$ cd frontend && npx vite build
vite v8.0.8 building client environment for production...
transforming...✓ 615 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.45 kB │ gzip:   0.29 kB
dist/assets/index-CpovdpSw.css    1.08 kB │ gzip:   0.56 kB
dist/assets/index-BybFNPib.js   707.66 kB │ gzip: 206.49 kB
✓ built in 196ms
```

**Production build succeeds.** Dashboard is deployable.

Type-check status is nuanced:
- `npm run type-check` (root tsconfig, solution-style) → exits 0 with empty output. **Misleading**; the tsbuildinfo cache masks errors.
- `npx tsc -p tsconfig.app.json --noEmit` → **10 errors, all in `src/fixtures/mentions.ts`**, all identical: `TS2741: Property 'confidence' is missing in type '{ name: string; polarity: "negative"; score: number; snippet: string; }' but required in type '{ name: string; polarity: ...; score: number; confidence: number; snippet: string; }'`.

The root cause of the 10 errors is that `src/fixtures/mentions.ts` contains half-migrated aspect literals — specifically, most aspect objects look like `{ name: '', polarity: '', score: , confidence: 0.9, snippet: '' }`. That is:
- Empty-string `name` and `polarity` (not valid `Polarity` enum members)
- **`score: ,`** with literally no value between the colon and comma — syntactically invalid, but tsc parses past it and reports the missing-confidence error (the other errors likely cascade out under esbuild's more permissive parser during `vite build`, which is why the build passes).

Raw `od -c` dump of the fixture confirmed the actual bytes: `s c o r e : ,` with a space and no value. This is not a Read-tool rendering artifact — the file literally contains broken JS.

This is **a half-finished fixture migration that was never completed**. frontend-engineer-v2 ran `gen:types` and updated the contract layer (good), but `src/fixtures/mentions.ts` was left as a stub with placeholder values that were never filled in.

### 5.2 Impact assessment

- **If the demo runs with `USE_FIXTURES=false` and the backend on localhost:8000** (standard demo mode), the fixture is dead code and the broken content has zero runtime impact. Mentions come from the CSVAdapter-driven pipeline and are well-formed.
- **If the demo runs with `USE_FIXTURES=true`** (offline demo mode), the broken fixture will flow into the UI: `aspect.name === ''` everywhere, drill-through panels will display blank aspect names, and any component that calls `aspect.score.toFixed(...)` will throw at runtime.
- **Judge inspection of the repo** will find the broken fixture and the misleading `npm run type-check` script. This is the worst failure mode — a judge who runs `tsc -p tsconfig.app.json --noEmit` themselves will see the 10 errors and mistrust the whole project. The fix is minutes of work but the reputational cost of shipping it is high.

### 5.3 Contract consumption is otherwise clean

The previous round I flagged ~50 type errors across pages and components caused by two layers of import drift (wrong import path for named types, v1 function names, PlatformComparisonResponse shape, AlertEvent field names). **All of those are fixed.** Verification:

- **Named-alias barrel file**: `src/types/index.ts` exists and re-exports 22 named types from `../api/endpoints`, including all the ones pages need: `OverviewKPIs`, `TimeseriesPoint`, `AspectTrend`, `PlatformComparisonResponse`, `PlatformAspectCell`, `AlertEvent`, `TopicCluster`, `ComparativeTopicResponse`, `Mention`, `Brand`, `Category`, `SourcePlatform`, `SentimentLabel`, `Polarity`, and more. **This is a better solution than my previous-round Option A recommendation** (I had suggested appending to `api.ts`; the barrel file is cleaner because `api.ts` is auto-generated and would be overwritten by the next `gen:types` run).

- **All pages and components import from `'../types'` or `'../../types'`** (the barrel), not from `'../types/api'`:
  ```
  OverviewPage.tsx: from '../types'
  ProductAnalysisPage.tsx: from '../types'
  PlatformComparisonPage.tsx: from '../types'
  TopicExplorerPage.tsx: from '../types'
  AlertsInsightsPage.tsx: from '../types'
  FilterBar.tsx, FilterUrlSync.tsx, SentimentBadge.tsx, PlatformHeatmap.tsx,
  SentimentLineChart.tsx, ShareOfVoiceDonut.tsx, EvidenceDrilldown.tsx,
  TopicBarChart.tsx, MentionQuote.tsx, AlertCard.tsx, TopicCard.tsx,
  AspectRadarChart.tsx, filterStore.ts: all from '../types' or '../../types'
  ```
- **Only `endpoints.ts` and `src/fixtures/*.ts` still import from `'../types/api'`** — these are allowed because they consume the raw openapi-generated `components` type. This is correct layering.

- **Endpoint function names are correct**: `fetchPlatformComparison`, `fetchTopicExplorer`, `fetchTopicComparative`, `fetchProductAspects`, etc. Grep for `/api/platforms/comparison` and `/api/topics/comparative` in `endpoints.ts` returns 2 matches (one per URL); grep for `/breakdown` and `/compare` (legacy) returns zero matches in the endpoint file.

- **PlatformComparisonResponse shape consumption is correct**: `PlatformHeatmap.tsx` declares `data: PlatformComparisonResponse` (singular), reads `data.grid` as `PlatformAspectCell[]`, derives platforms via `[...new Set(data.grid.map(c => c.platform))]`, builds the heatmap via `for (const cell of data.grid) { map[cell.platform][cell.aspect] = ... }`. `PlatformComparisonPage.tsx` declares `useState<PlatformComparisonResponse | null>(null)`, derives `platforms` and `topTopics` and `platformMentions` from `data.grid` and `data.top_topics_by_platform`. **Fully correct shape consumption.** This is a complete rewrite from the v1 shape I flagged in the previous round.

- **FilterUrlSync**: `import { useSearchParams } from 'react-router-dom'` at line 2, used at line 14. Bidirectional URL sync via `setSearchParams(params, { replace: true })`. Clean.

- **PlatformHeatmap is CSS Grid of divs, not Recharts**: verified via grep `display:\s*['"]grid['"]` and `gridTemplateColumns` returning lines 49 and 63 of the file. The file does not import from `recharts` — it imports only React and the `COLORS` theme. Confirmed real CSS Grid implementation with RGB interpolation from `#f05252` (negative) through `#f0b429` (neutral) to `#3ecf8e` (positive). Legend gradient. Hover title shows score × 100 + mention count. Click handler wires `onCellClick` callback. This is an honest implementation of REQ-013.

### 5.4 Business-question subtitles (REQ-005 semantic)

Verified directly via Grep on `subtitle`/`PAGE_SUBTITLE` across `frontend/src/pages/`:
- **OverviewPage**: *"What is the state of consumer sentiment across our portfolio right now, and what changed this week?"* ✓
- **ProductAnalysisPage**: *"For a specific SKU, what are people saying about each aspect of the product, and how is each aspect trending?"* ✓
- **PlatformComparisonPage**: *"How does the conversation about this product differ across Reddit vs Amazon vs YouTube vs Trustpilot, and are the aspects the same?"* ✓
- **TopicExplorerPage**: *"What aspects are people talking about that we did not pre-define, and are any of them gaining or losing ground?"* ✓
- **AlertsInsightsPage**: *"What should I be paying attention to right now that I do not already know about?"* ✓

All 5 pages carry the correct business question from requirements.md §6 in their header subtitle.

### 5.5 EvidenceDrilldown / REQ-006 wiring

All 5 pages grep-hit for `openDrilldown` (the drilldown store action), confirming drill-through is wired on every page. `EvidenceDrilldown.tsx` imports `Mention` from the barrel (the previous round's `fetchMentionsByIds` import error is gone). `PlatformHeatmap.tsx::onCellClick` propagates drill events from the heatmap. REQ-006 intent satisfied; runtime fidelity depends on the fixture state being fixed (§5.1) for offline mode, otherwise the real backend drives drill content.

### 5.6 No word clouds

`grep -ri "wordcloud|WordCloud|word-cloud"` across `frontend/src/` returns zero matches. REQ-016's anti-word-cloud clause is satisfied.

---

## 6. Dashboard UX vs Business Questions

Each page would answer its business question once rendered:

- **Overview** — KPI strip (total_mentions, overall_score, wow_delta, top_rising_negative, top_rising_positive) + timeseries + share-of-voice donut. Answers: "state of sentiment + what changed this week." ✓
- **Product Analysis** — brand → category → model selector + aspect table (AspectTrend: mention_count/avg_score/trend_delta/severity/sparkline) + radar chart. Answers: "what people are saying about each aspect of a SKU and how each is trending." ✓
- **Platform Comparison** — CSS Grid heatmap (platform × aspect, color = sentiment, cell label = volume) + top-topics per platform. Answers: "how the conversation differs across Reddit/Amazon/YouTube/Trustpilot." ✓
- **Topic Explorer** — topic list sorted by `momentum` + comparative share-of-aspect bar chart. Answers: "what aspects are people talking about that we didn't pre-define." ✓ (No word cloud — REQ-016 anti-pattern avoided.)
- **Alerts & Insights** — active/history tabs + severity-sorted list + acknowledge + drill to exemplar mentions. Answers: "what should I be paying attention to right now." ✓

No page needs a design redo. The design and the execution are aligned.

---

## 7. Action Items — `backend-engineer-v2`

### Required (round 2 blockers)
**None.** Backend is PASS. Every P0 and P1 backend REQ is satisfied. Edge-case suite is 34/34 real passes. Architecture is clean. You are frozen for round 2.

### Optional (non-blocking, for round 2 polish or beyond)
1. **Convert some xfails to passes** in `test_nlp_robustness.py`. Good candidates:
   - `test_multi_aspect_correct_polarities`: add `"buggy": -0.55` and `"drains": -0.45` (or multi-word `"drains too fast"`) to `absa.STRONG_NEGATIVES`. One-line fix.
   - `test_sarcasm_brilliant_cue`: `"brilliant"` is already in `SARCASM_POSITIVE_CUES` per my read — if it's not catching, the issue is the rule not the cue; audit R3 opener to allow `"Brilliant engineering"` as a pattern.
   - `test_roomba_brand_alias_comparative`: ensure `BRAND_ALIASES["roomba"] = "irobot"` is respected in `comparative.py` brand resolution.
   Each xfail → pass is a line item in the round 2 highlights.
2. **Add a VADER-contrast report generator** at `scripts/nlp_contrast_report.py` that runs all 16 edge cases through both raw VADER and the enhanced pipeline and emits a markdown table with `case_id | text | vader_label | vader_compound | enhanced_label | enhanced_compound | sarcasm_flag | aspect_count | comparative_pair_count`. Output to `contracts/nlp_contrast_report.md`. Makes the "failing-before / passing-after" claim judge-readable in 10 seconds without opening Python.
3. **(Deferred, round 2+)** Cross-platform upweight in `aggregations.compute_alerts::severity`. `severity × (1 + 0.5 × platform_count)` where `platform_count` is the number of distinct `source_platform` values among mentions for this alert's aspect. Zero router impact. Makes the alerts page a visible differentiator vs Brandwatch/Meltwater single-platform severity.
4. **(Deferred, round 2+)** Novelty flag on `TopicCluster`. Add `is_novel: bool` to `schemas.TopicCluster`; compute it in `aggregations.compute_topics` as `momentum > threshold AND mention_count < floor AND first_seen within N days`. This is the literal Foodi early-warning signal in one boolean field.

None of these are required for round 1 sign-off.

---

## 8. Action Items — `frontend-engineer-v2`

### Required (round 2 blockers — only 2 tight fixes)

**Step 1 — Repair `src/fixtures/mentions.ts`.**
The file contains ~20 aspect object literals in this broken shape:
```ts
{ name: '', polarity: '', score: , confidence: 0.9, snippet: '' }
```
Each needs to become either (a) a real aspect with populated fields, e.g. `{ name: 'suction', polarity: 'positive', score: 0.85, confidence: 0.9, snippet: 'Suction is incredible' }`, or (b) deleted outright if the mention was meant to have no aspect breakdown. Similarly, comparative pair literals in the form `{ brand: '', aspect: '', polarity: '', score: 0 }` need the empty strings populated or the pair deleted.

The fastest correct fix: for each mention in the fixture, look at `text` and manually write 1–3 plausible `AspectSentiment` objects that match the text. Example — the mention at line 192 has `text: 'Descaling takes forever and the pod compartment jams.'`; its aspects should be `[{ name: 'descaling', polarity: 'negative', score: -0.6, confidence: 0.88, snippet: 'Descaling takes forever' }, { name: 'pod_compartment', polarity: 'negative', score: -0.5, confidence: 0.85, snippet: 'the pod compartment jams' }]`.

Exit criterion: `npx tsc -p tsconfig.app.json --noEmit` reports **zero errors**.

**Step 2 — Fix `npm run type-check` to fail on errors.**
Edit `frontend/package.json` and change the `"type-check"` script from:
```json
"type-check": "tsc --noEmit"
```
to:
```json
"type-check": "tsc -p tsconfig.app.json --noEmit && tsc -p tsconfig.node.json --noEmit"
```
This makes the script run the app config explicitly, bypassing the solution-style tsbuildinfo cache. Without this, the same class of regression (broken fixtures, drifted imports) will hide again in any future round.

Exit criterion: after Step 1 lands, `npm run type-check` reports zero errors and exits 0. Before Step 1 lands, running the new script should surface the 10 errors from Step 1 — confirming the script is actually checking.

**Verification sequence you must run and report back:**
```
cd frontend
npx tsc -p tsconfig.app.json --noEmit      # → 0 errors, exit 0
npm run type-check                          # → 0 errors, exit 0 (via the new script)
npm run build                               # → success
```

### Non-blocking (round 2 polish, optional)
- `FilterBar.tsx` custom-range date input: when `dateRange === 'custom'`, the user should be able to set `dateFrom`/`dateTo` — currently they're reset to undefined. One `<input type="date">` pair behind a conditional.
- Confidence score surface (REQ-021 P2): show `AspectSentiment.confidence` as a tooltip or faded subscript when rendering aspects in drill-through. Non-blocking; judges who notice opaque scores may appreciate the transparency.

---

## 9. Non-Blocking Strategic Recommendations (post-round-2 README polish)

Reserved for a business-leader-v2 README polish round AFTER round 2 closes. Not scope for round 1 or round 2.

1. **Agentforce survivorship-bias framing** in README §2: "Even SharkNinja's own Agentforce captures only consumers who chose to contact you. The real signal is in the mentions of consumers who didn't. Our dashboard surfaces that second group."
2. **Foodi recall counterfactual** in the demo script close.
3. **Trustpilot 1.7/5 vs "growing one 5-star review at a time"** tension.
4. **Novelty / outlier surfacing** as a round 2+ feature (see §7 item 4).
5. **Cross-platform confirmation** in alert severity formula (see §7 item 3).

---

## 10. Summary

**Verdict: PARTIAL** (very close to PASS).

- **Backend**: PASS. 34/34 edge-case tests, 0 mocks, pipeline is real multi-layer not a VADER wrapper, R4 contrastive exclusion and copular dep-walk both present and verified. Architecture clean: ABC + factory + Depends, schemas.py canonical, 14-path api-contract.yaml. 6 robustness xfails with explicit reason strings are good engineering, not cheating.
- **Frontend**: 13/16 REQs PASS. Build succeeds, all 5 pages render correct business-question subtitles and wire drilldown, PlatformHeatmap is real CSS Grid, FilterUrlSync uses `useSearchParams`, type imports via a new barrel file (`src/types/index.ts`). **Two mechanical nits**: `src/fixtures/mentions.ts` has half-migrated aspect literals (10 tsc errors hidden by tsbuildinfo cache) and the `npm run type-check` script doesn't surface them. Both are round 2 blockers for fixture hygiene and repo-inspection honesty.
- **Contract layer**: PASS. schemas.py → api-contract.yaml → types/api.ts → types/index.ts chain is coherent and enforced.

**Round 2 scope for frontend-engineer-v2: 2 files.** `src/fixtures/mentions.ts` (fill in or delete the stubbed aspect literals) and `package.json` (point `type-check` at `tsconfig.app.json`). Verification: `npx tsc -p tsconfig.app.json --noEmit` clean + `npm run build` succeeds + `npm run type-check` (via the new script) clean.

**Round 2 scope for backend-engineer-v2: zero required work.** Optional polish items in §7 are stretch, not gating.

Reviewer: business-leader-v2
