# Round 3 Charter — SharkNinja Consumer Sentiment Dashboard

**Author:** business-leader-v2
**Date:** 2026-04-11
**Status:** Charter (binding spec for v3 engineer spawn)
**Round 2 floor:** PASS — see `contracts/review-round-1.md` + `contracts/review-round-2.md`. Do not regress those findings.
**Reference material (read, do not duplicate):** `contracts/research/references_and_skills.md` (MiroFish/Aaru/skills), `contracts/research/agentforce_sharkninja_story.md` + 4 sibling files (positioning/narrative).

---

## 0. Round Budget Context (3-round ceiling)

Per team-lead addendum 2026-04-11: Vincent has authorized a **3-round maximum iteration budget** while away. Round 3 + Round 4 + Round 5 is the hard ceiling. Team-lead auto-triggers the next round when the current one completes. Vincent returns for acceptance at the end.

**This charter's R3/R4/R5 philosophy:**

- **Round 3 — Stabilize & Enable.** Fix the concrete bugs Vincent flagged (filter propagation, responsive layout), establish aesthetic direction via `frontend-design`, enrich data so subsequent rounds have a realistic sandbox, write the real-API integration proposal. Keep feature additions MINIMAL and surgical (novelty detection + cross-platform severity — both are 3-line backend changes that directly unblock personas). **Round 3 is NOT where Trend Forecast or What-If Simulator land.** Cramming them here risks half-baked execution on the features that most need narrative quality.
- **Round 4 — Feature Depth.** Execute real-API integration per the Round 3 proposal. Ship full-scope MiroFish Trend Forecast panel with confidence bands. Ship Aaru-style What-If Simulator v1 (prompt-chain heuristic). This is the round where prediction/implication features actually arrive.
- **Round 5 — Polish & Acceptance.** README polish pass (Agentforce survivorship framing, Foodi counterfactual, Crossan-Matos vocabulary from `contracts/research/*.md`). Final accessibility pass. Final responsive QA. Residual cleanup from R3/R4. Exportable digest if time permits. This is the "Vincent-ready" round.

**Consequence for this Round 3 charter:** the queue in §6 is intentionally LIGHTER than my first-pass draft. Features I initially labeled "IN Round 3 (minimal v1)" have been reassessed against the guaranteed R4 window and moved where they actually belong. Trend Forecast in particular moved from R3-P1 to R4. This is not retreat — it is scope discipline. A half-rendered forecast panel with heuristic projections delivered in 1 hour under R3 time pressure would damage the pitch more than a clean full-scope forecast in R4.

**Failure mode to avoid:** treating R3 as the last chance. It is not. R4 exists. R5 exists. Resist the urge to cram.

---

## 1. Self-Audit: Does Round 2 PASS Actually Serve the Business Use Case?

Honest answer: **partially.** Round 2 delivered a clean descriptive dashboard. Four of the five personas need at least one feature that is not yet present, and one persona (Darius) has a core-workflow gap that invalidates his "success" criterion from requirements.md §1.

### Persona × current-build matrix

| Persona | What Round 2 gives them | What they need but DO NOT get | Severity | Target round |
|---|---|---|---|---|
| **P1 Maya Chen** — kill the 500-row Google Sheet | Overview + Product Analysis aspect table + drill-through to quoted evidence. **This is actually close to sufficient** for her monthly readout. | Weekly exportable digest (PDF/CSV) she can forward to GMs. Currently she would have to screenshot. | Annoying | **R4/R5** (export) |
| **P2 Darius Okafor** — "tell me a week before Twitter does" | Alerts page with severity sort. But severity is volume × magnitude × recency of **known** aspects — so it only fires on aspects already popular enough to be in the lexicon. | **Early-warning on NOVEL aspects** (the "mopping pad streaks" signal before "mopping pad" is a first-class aspect). **Predictive sentiment trajectory** per SKU so he can see the curve. Plus **filter propagation bug** currently blocks him from scoping to his SKUs. | **BLOCKING** | **R3** (filter bug + novelty detection) + **R4** (Trend Forecast) |
| **P3 Priya Ramanathan** — "4 hours instead of 4 days" | Topic Explorer comparative share-of-aspect view + competitive data model. The NLP correctly attributes comparative claims. | **Deck-ready export** (copy-to-clipboard of chart + quotes + CSV) so her workflow doesn't end at the dashboard; it starts there. | Annoying | **R4/R5** (export) |
| **P4 Terri Williams** — "page me before ticket volume spikes" | Alerts list + acknowledge flow. **But: severity formula is reactive.** It fires when a cluster is already large. Her explicit success criterion is "a week before ticket volume spikes" — that requires **forward-projection**, not current-volume alerting. | **Predictive severity**: forward-looking score integrating sentiment-trajectory forecast. Also **cross-platform confirmation** (Reddit-spike + Amazon-spike = high confidence; single-platform = probably viral). | **BLOCKING** | **R3** (cross-platform confirmation) + **R4** (Trend Forecast integration into severity) |
| **P5 Jordan Liu** — "which aspect drives Reddit vs Amazon conversation" | PlatformComparisonPage heatmap + top-topics-per-platform. **This is close to sufficient** for his actual workflow. | Ideally: **platform-specific tone profiles** (Reddit = technical/sarcastic, Amazon = aspirational) surfaced explicitly rather than inferred from the grid. | Cosmetic | **R5** (if time permits) |

**Verdict on the REQs themselves:** REQ-015 ("Alerts page shows rising negative aspects with severity") is **under-specified**. It tolerates a purely reactive alert system that fires on already-popular complaints, which breaks Darius's and Terri's core workflows. Proposed requirement amendment (for team-lead decision, not executed in this round): REQ-015 should call out **novelty** (new-cluster detection) and **cross-platform confirmation** as severity components, not just volume × magnitude × recency. Similarly, REQ-016 Topic Explorer ("emerging themes") is permissive enough that a fully-populated existing-aspect clustering passes the letter but misses the spirit — emerging implies **new**, not **recently-trending**.

**Strategic thesis check:** the positioning work in `contracts/research/foodi_op300_failure_chain.md` argues that the Foodi counterfactual only holds if we have novelty + cross-platform detection. Round 2 does not yet have either. **The pitch and the product are currently misaligned.** Round 3 closes that gap or we lose the Foodi story.

---

## 2. Vincent's Direct Feedback Items → Decisions

Source: team-lead's Round 3 GO message summarizing Vincent's hands-on review.

| # | Item | Owner | Priority | Acceptance criterion |
|---|---|---|---|---|
| V1 | Filter-bar propagation bug — only Overview Sentiment Over Time chart re-fetches on filter change; all other widgets mounted-once-ignore-change. Team-lead confirmed via curl that `/api/overview/kpis` returns correct per-filter results, so this is a frontend `useEffect` dependency bug, not backend. | **frontend-v3** | **P0** | Every widget on every page re-fetches when any filter (brand/category/platform/dateRange/productModel) changes. Validated by: (a) clicking a filter and watching a network-tab re-fetch of ALL widget endpoints on that page, not just one; (b) no widget shows stale data after filter change. |
| V2 | Responsive layout broken on window resize. | **frontend-v3** | **P0** | Dashboard is usable at ≥360px (mobile), ≥768px (tablet), ≥1280px (desktop) viewport widths. Media queries / flex-wrap / CSS Grid auto-fit where needed. Test: resize Chrome window from 1920 down to 360 — nothing breaks, nothing horizontally overflows except tables (which can scroll). |
| V3 | Data sparsity — 75 CSV rows too thin for Product Analysis. | **backend-v3** | **P1** | See §4 below for strategy decision. Minimum: 300+ rows across ≥12 SKUs spanning ≥3 brands and ≥4 platforms, with aspect distribution that actually fills the aspect table realistically (no 1-row aspects). |
| V4 | Feature depth — wants PREDICTION and IMPLICATION, not just "what is". Pointed at MiroFish + Aaru. | **backend-v3 + frontend-v3** | **P1** (minimum viable scope, see §3) | At least ONE predictive feature (Trend Forecast) reaches the dashboard with honest labeling and visible confidence bands. "What-if" simulation is DEFERRED to Round 4 unless time permits — see §3. |
| V5 | Frontend maturity — reads as "college hobby project". | **frontend-v3** | **P0** | Passes the 6-criterion maturity rubric in §5. Uses `frontend-design` skill BEFORE touching component code. |
| V6 | (cross-cutting, implied by V4) REQ-015 and REQ-016 are under-specified; novelty and cross-platform confirmation are missing. | **business-leader** (charter notes) + **backend-v3** (implementation) | **P1** | Treat novelty/cross-platform as scope additions in §3, not requirement amendments. Team-lead decides whether to amend requirements.md in a later round. |

---

## 3. Prediction & Implication Features — Scope Decisions

Time budget assumption: **1–2 hours of engineer work per major feature** per team-lead. R3 + R4 + R5 is the ceiling. Features below are labeled with their target round.

### 3.1 MiroFish-style Trend Forecast — **DEFER to Round 4 (full scope)**

**Original plan (superseded):** I initially slotted this as R3-minimal-v1. The 3-round ceiling addendum from team-lead means R4 is guaranteed, so the honest call is to ship this at full scope in R4 instead of half-baked in R3.

**Round 4 scope spec (for the charter team-lead will issue at R4 kickoff):**
Backend adds `GET /api/products/{model}/forecast` returning a 4-week forward-projected sentiment trajectory with confidence bands. Implementation is a **GraphRAG-lite heuristic** (not full OASIS/agent-based simulation): read the product's recent mentions, build a simple aspect-mention graph, apply a decay-weighted linear projection with widening confidence bands (narrower on aspects with high mention_count, wider on sparse aspects). Frontend adds a "Trend Forecast" panel to Product Analysis that renders the projection as a dashed-line continuation of the existing sentiment line chart, with a shaded confidence band and an explicit "Projected — based on recent trajectory and review velocity" subtitle. **Label it honestly as a heuristic projection, not a simulation.** No OASIS runtime, no Zep memory, no LLM call in the forecast path (pure Python math), no multi-scenario branching.

**Why DEFER from R3 to R4:** the forecast endpoint + frontend panel + confidence bands + contract change is ~2h backend + ~1.5h frontend = ~3.5h total. That is >1/3 of the R3 budget and it is the feature most likely to ship half-baked under time pressure. R4 is guaranteed and has more room. Round 3 gains meaningful breathing room by shedding this.

**Dependency note:** R3's **novelty detection (§3.2)** and **data enrichment (§4)** both feed R4's Trend Forecast. Novelty gives the forecast something interesting to project. Enriched data gives it enough signal density to produce non-noisy projections. So R3 is setting up R4's foundation here — the feature isn't abandoned, it's scheduled.

### 3.2 Novelty Detection — **IN Round 3 (MINIMAL V1)**

**Scope spec for engineers:**
Add an `is_novel: bool` field to `schemas.TopicCluster` and populate it in `aggregations.compute_topics` via the rule: `momentum > threshold AND mention_count < small_cluster_floor AND first_seen_at within last 14 days`. Thresholds are tunable constants; v1 ballpark: `momentum > 0.3`, `mention_count < 25`, `first_seen_at` computed as min(posted_at) of the cluster. Frontend Topic Explorer shows a "NEW" badge on novel clusters and an optional filter "Show emerging only" that filters to `is_novel=true`. **Alerts page also reads `is_novel`**: novel clusters get a severity multiplier of 2× so they surface above known-aspect volume spikes. This is the Darius + Terri early-warning fix.

**Why IN at minimal scope:** this is a 1-field data model change + a 3-line aggregation computation + a frontend badge. Small implementation, high leverage — it closes the biggest persona gap (P2 Darius and P4 Terri both require this), directly enables the Foodi counterfactual claim, AND prepares the data the R4 Trend Forecast needs.

**Contract impact:** `schemas.TopicCluster` change → regenerate `api-contract.yaml` → regenerate `frontend/src/types/api.ts` via `gen:types`. Standard cross-cutting change. Backend-v3 owns the regen + notifies frontend-v3 via SendMessage per CLAUDE.md §4.

### 3.3 Cross-Platform Confirmation in Severity — **IN Round 3 (MINIMAL V1)**

**Scope spec for engineers:**
Update `aggregations.compute_alerts::severity` formula to multiply by `(1 + 0.5 × (platform_count − 1))` where `platform_count` is the number of distinct `source_platform` values among mentions contributing to the alert's aspect. Single-platform alerts keep current severity; 2-platform gets 1.5×; 3-platform gets 2×. Frontend Alerts page shows a small "Reddit + Amazon + Trustpilot" platform-list chip on each alert so users can see the confirmation at a glance.

**Why IN at minimal scope:** zero new endpoints, one formula line, one frontend chip. Critical for Priya and Terri workflows and central to the "we do what Brandwatch cannot" pitch. ~20 minutes of implementation.

### 3.4 Aaru-style What-If Simulator — **DEFER to Round 4**

**Rationale for DEFER:** the v1 implementation ("prompt-chain heuristic that reads as executive-grade") requires LLM calls on every user interaction. That is a new dependency (OpenAI/Anthropic SDK, API key management, latency budget, error handling) that is not currently in the backend. Out of budget for R3. In R4, this lands alongside the Trend Forecast and shares the cost of adding an LLM dependency to the backend.

**Round 4 scope (preview, not binding on this charter):** Backend adds `POST /api/simulate` that accepts a natural-language scenario ("what if we launched a mini version at $199 targeting first-apartment renters") plus filter context, chains LLM calls against Crossan-Matos-audience-framed prompts (see `contracts/research/crossan_matos_public_positioning.md` for vocabulary), and returns a structured `SimulationResult` with predicted segment reactions. Frontend surfaces this as a "What-If" panel on Product Analysis or as a new dedicated page. Labeling honesty rule: the response MUST be marked "Simulated reaction based on LLM heuristic, not empirical behavior modeling."

### 3.5 Exportable Digest (Maya + Priya) — **DEFER to Round 4 or Round 5**

**Rationale:** P1 (Maya) and P3 (Priya) both want a shareable export. A PDF lib (e.g., `react-pdf`, `pdfmake`) or a clipboard-image implementation (`html-to-image`) is non-trivial but not impossibly so. Better fit for R5 polish round after the feature depth of R4 is in place — no point exporting a dashboard that is about to gain predictive features. Preliminary target: **R5**, CSV-only as a first cut (simpler than PDF), upgrade to PDF if time allows.

### 3.6 R3/R4/R5 feature allocation summary (for team-lead round-queue planning)

| Feature | Round | Label | Owner |
|---|---|---|---|
| Filter binding fix (Vincent V1) | **R3** | P0 | frontend-v3 |
| Responsive layout (Vincent V2) | **R3** | P0 | frontend-v3 |
| `frontend-design` skill invocation + design tokens | **R3** | P0 | frontend-v3 |
| Real-API integration proposal document | **R3** | P0 | backend-v3 |
| Frontend maturity rubric M1–M6 | **R3** | P0 | frontend-v3 |
| Data enrichment generator (§4) | **R3** | P1 | backend-v3 |
| Novelty detection (§3.2) | **R3** | P1 | backend-v3 + frontend-v3 |
| Cross-platform severity (§3.3) | **R3** | P1 | backend-v3 + frontend-v3 |
| **MiroFish Trend Forecast (§3.1)** | **R4** | P0 of R4 | backend-v4 + frontend-v4 |
| **Aaru What-If Simulator (§3.4)** | **R4** | P1 of R4 | backend-v4 + frontend-v4 |
| **Real-API integration execution** (per R3 proposal) | **R4** | P0 of R4 | backend-v4 |
| **README polish pass** (post-charter business-leader work) | **R5** | P0 of R5 | business-leader |
| **Exportable digest CSV → PDF** (§3.5) | **R5** | P1 of R5 | frontend-v5 |
| Accessibility final pass | **R5** | P1 of R5 | frontend-v5 |
| Responsive deep QA | **R5** | P1 of R5 | frontend-v5 |
| R3/R4 residual cleanup | **R5** | P2 of R5 | whoever owns the residual |
| Dark mode (REQ-023 P2) | **R5 optional** | P2 of R5 | frontend-v5 if time permits |
| Platform-specific tone profiles (P5 Jordan) | **R5 optional** | P2 of R5 | frontend-v5 if time permits |

This table is **not** the Round 3 work queue — that is §6. This table is the R3+R4+R5 forward plan so team-lead can queue rounds without re-asking me.

---

## 4. Data Enrichment Strategy for Round 3

**Decision: hybrid — generate expanded CSV fixtures in Round 3, defer real-API integration to Round 4.**

**Rationale:** Vincent's feedback V3 is that Product Analysis feels sparse with 75 rows. A real-API integration (Reddit/Amazon/Trustpilot scrapers) is (a) legally encumbered per `contracts/research/foodi_op300_failure_chain.md` and the JailBreak study doc's §III (Amazon ToS, Reddit API repricing, GummySearch cautionary tale), (b) high implementation cost, (c) NOT in Vincent's round-3 critical path. Meanwhile, expanding CSVs to 300+ rows is a ~30-minute generator-script task that immediately fixes the sparse-feel complaint.

**Concrete spec for backend-v3:**
Write `backend/scripts/generate_fixtures.py` that emits expanded CSVs meeting these targets:
- **≥300 total rows** across `reviews_shark.csv`, `reviews_ninja.csv`, `reviews_competitors.csv`
- **≥12 distinct SKUs**: expand current 4-5 to include Shark Matrix, Shark IQ, PowerDetect UV Reveal, Shark Navigator (4 vacuum SKUs); Ninja Foodi DualZone, Ninja Creami, Ninja Espresso Bar, Ninja Coffee Bar (4 kitchen SKUs); Dyson V15, iRobot Roomba j7+, Roborock S8, KitchenAid Pro (4 competitor SKUs)
- **All 5 platforms populated**: reddit, amazon, youtube, trustpilot, twitter (current fixtures may be missing youtube/twitter rows)
- **Aspect realism**: each SKU has ≥5 aspect mentions distributed across suction/battery/navigation/app/noise/durability — no 1-row aspects that would leave the Product Analysis aspect table looking sparse
- **Preserve the 16 edge-case texts** from `requirements.md §3` verbatim — do NOT delete them, they are the demo content that ties drill-through to the pytest suite
- **Timestamp spread**: rows span 60 days so the 30-day and 7-day filter windows both return meaningful content
- **Novelty seed**: include ~5 rows of a deliberately NEW aspect cluster (e.g., "charging dock LED flickering" on a specific SKU) with first_seen_at in the last 14 days — this is the test case for the novelty detection in §3.3

**Exit criterion:** `pytest backend/tests/` still 34/34 green on edge-case suite (fixtures are additive, not replacing). `GET /api/mentions?limit=1000` returns ≥300 rows. Product Analysis aspect table for PowerDetect UV Reveal shows ≥6 aspect rows with double-digit mention counts.

**Backend-v3 also writes `contracts/real_api_integration_proposal.md`** (proposal document only, NOT code). This is V1 from Vincent's implied ask — a written plan for how a future round would integrate real Reddit + Amazon + Trustpilot data via legal-safe paths (UCSD Amazon dataset, Arctic Shift Reddit, Trustpilot API). Per-source: access method, legal posture, cost, required schema additions, estimated round-4 scope. No implementation.

---

## 5. Frontend Maturity Acceptance Rubric

This is the rubric I will audit against when frontend-v3 reports complete. 6 named criteria. Frontend-v3 MUST invoke the `frontend-design` skill BEFORE touching component code — the skill is listed in §6 as a P0 deliverable. The criteria below are what "maturity" means in this review's vocabulary; the skill choices to satisfy them are frontend-v3's call.

| # | Criterion | What "pass" looks like |
|---|---|---|
| M1 | **Aesthetic direction is deliberate, not default.** | There is a documented design decision (color palette, typography scale, spacing scale) that is consistent across all 5 pages. No bare `<button>` elements with browser defaults. No `color: blue` strings. Design tokens live in a single source (`theme/index.ts` or equivalent) and are referenced everywhere. |
| M2 | **Typography is intentional.** | Headings, body, labels, and numeric display all use deliberate font-size/weight/line-height pairs. No `<h1 style="fontSize: 22">` random inline sizes. Numeric values in KPI cards use a tabular-figures font feature so they don't jitter when updating. |
| M3 | **Empty states, loading states, error states exist on every page.** | Every `fetch*` call has three rendered states: (1) skeleton/spinner while loading, (2) empty-state illustration or text when no data, (3) error fallback with actionable retry. Vincent's resize-breakage complaint was partly about states not handling re-render properly. |
| M4 | **Interactive elements have hover, focus, active, and disabled states.** | Buttons, chips, links, filters all have visible hover + focus-visible + active + disabled styling. Focus ring is keyboard-navigable. This is table-stakes for "mature product" feel. |
| M5 | **Responsive layout tested at 3 breakpoints.** | Dashboard adapts at ≥360px, ≥768px, ≥1280px. Cards reflow. The PlatformHeatmap scrolls horizontally on mobile rather than overflowing. Filter bar collapses or scrolls. |
| M6 | **Accessibility floor.** | Every interactive element is keyboard-reachable. Every image or chart has an `aria-label` or a text equivalent. Color contrast meets WCAG AA for primary text (4.5:1) and UI chrome (3:1). Frontend-v3 may use `Accessibility Agents` from the skill research file as a review pass, or may do manual checks — either is acceptable. |

**What I will NOT require** (protecting time budget): pixel-perfect Figma compliance, animation polish, dark mode, mobile-native UX, icon consistency across pages. These are nice-to-have but out of scope for Round 3.

---

## 6. P0 / P1 / P2 Feature Queue for Round 3

Numbered, owner-tagged, with acceptance criteria.

### P0 — blocking for Round 3 sign-off

| ID | Feature | Owner | Acceptance |
|---|---|---|---|
| R3-P0-1 | **Filter binding fix** — all widgets on all 5 pages re-fetch when any filter changes | frontend-v3 | Network tab shows full re-fetch cascade on any filter change. Every widget updates or shows loading-state. Regression test: click Dyson brand filter on Overview and confirm KPIs, share-of-voice, and timeseries all update. |
| R3-P0-2 | **Responsive layout** — media queries + breakpoints at 360/768/1280px | frontend-v3 | Chrome DevTools responsive mode shows clean layout at all 3 breakpoints. No horizontal scroll (except table regions). No overlap. |
| R3-P0-3 | **Invoke `frontend-design` skill BEFORE component edits** — establish aesthetic direction document, commit design tokens file | frontend-v3 | A design decision document exists at `frontend/docs/design_direction.md` (or equivalent). Tokens defined at `frontend/src/theme/tokens.ts`. All components reference tokens, not raw values. |
| R3-P0-4 | **Backend real-API integration proposal** — written proposal only, no code | backend-v3 | `contracts/real_api_integration_proposal.md` exists; covers Amazon (UCSD dataset), Reddit (Arctic Shift), Trustpilot, YouTube, Twitter; per source: access method / legal posture / cost / schema impact / round-4 scope estimate. |
| R3-P0-5 | **Frontend maturity rubric compliance** (M1–M6 in §5) | frontend-v3 | All 6 criteria pass when I audit. See §7 for audit commands. |

### P1 — strongly expected, ship if time allows

| ID | Feature | Owner | Acceptance |
|---|---|---|---|
| R3-P1-1 | **Data enrichment generator** — per §4 | backend-v3 | `backend/scripts/generate_fixtures.py` exists; running it produces ≥300 rows, ≥12 SKUs, 5 platforms, 60-day spread. All 16 edge-case texts preserved. 34/34 pytest still green. |
| R3-P1-2 | **Novelty detection** — `is_novel` on TopicCluster + Alerts severity × 2 when novel — per §3.2 | backend-v3 + frontend-v3 | `schemas.TopicCluster.is_novel` exists; api-contract.yaml regenerated; aggregations.compute_topics populates it; Alerts page shows NEW badge + 2× severity multiplier applied. |
| R3-P1-3 | **Cross-platform confirmation in severity** — per §3.3 | backend-v3 + frontend-v3 | `compute_alerts::severity` formula updated; Alerts page UI shows platform-list chip. |
| R3-P1-4 | **Aesthetic criteria M1–M4** from §5 (non-responsive, non-a11y criteria) | frontend-v3 | Reviewed as part of R3-P0-5. |

**Note on R3 P1 scope:** Trend Forecast was originally drafted here as R3-P1-4 but moved to Round 4 per §3.1 rationale. The 3-round ceiling means R4 is guaranteed, so shipping the forecast at full scope then beats shipping it half-baked now. R3's P1 queue is intentionally 4 items instead of 5 — that breathing room lets engineers actually deliver the rubric quality M1–M6 demands without skimping.

### P2 — explicit out-of-scope fences for Round 3, with target round

| ID | Feature | Status | Round | Rationale |
|---|---|---|---|---|
| R3-P2-1 | MiroFish Trend Forecast (full scope) | DEFERRED | **R4** | ~3.5h total, doesn't fit R3 without cramming; better at full scope in R4 alongside real data |
| R3-P2-2 | Aaru What-If Simulator | DEFERRED | **R4** | Requires LLM dependency; shares infra cost with Trend Forecast in R4 |
| R3-P2-3 | Real-API integration execution | DEFERRED | **R4** | R3 only writes the proposal (R3-P0-4); R4 executes it |
| R3-P2-4 | Exportable digest (CSV first, PDF if time) | DEFERRED | **R5** | Wait until R4 features are in place before exporting |
| R3-P2-5 | Dark mode (REQ-023 P2) | DEFERRED | **R5 optional** | R3 tokens make it cheap in R5, not urgent |
| R3-P2-6 | Platform-specific tone profiles (P5 Jordan cosmetic gap) | DEFERRED | **R5 optional** | Nice-to-have, not persona-blocking |
| R3-P2-7 | Pixel-perfect Figma polish, animation polish, mobile-native UX | NOT in any round | — | Not required by rubric M1–M6 and out of the Vincent review scope |

---

## 7. Round 3 Audit Plan

When engineers report complete, I will run this checklist. Commands are quoted in full so I can copy-paste.

### 7.1 Command-level verification

```bash
# Backend regressions (Round 2 floor — must not break)
cd "D:/Ai_Project/MeowOS/99_MyFiles/Project_Trial/Challenge_5_v2"
python -m pytest backend/tests/ -v 2>&1 | tail -10   # expect 34+ passed, 0 failures

# Novelty / cross-platform / forecast endpoints present
python -c "import yaml; d=yaml.safe_load(open('contracts/api-contract.yaml')); print(sorted(d['paths'].keys()))"
# expect /api/products/{model}/forecast added

# Data enrichment
python scripts/generate_fixtures.py --dry-run    # if engineers expose a dry-run flag
wc -l backend/data/reviews_*.csv                   # expect ≥300 total

# Frontend build floor (Round 2 floor — must not break)
cd frontend
npx tsc -p tsconfig.app.json --noEmit; echo "EXIT:$?"   # expect EXIT:0
npm run type-check; echo "EXIT:$?"                       # expect EXIT:0
npx vite build 2>&1 | tail -10; echo "EXIT:$?"           # expect EXIT:0

# Responsive (manual — Chrome DevTools responsive mode at 360/768/1280)
# Filter propagation (manual — network tab on filter change, watch ALL widget re-fetches)
```

### 7.2 Disk audits (targeted reads, not full-file reads per compression discipline)

- Grep `frontend/src/pages/*.tsx` for `useEffect` and verify each widget's dep array includes the filter state. **This is the V1 bug audit.**
- Grep `frontend/src/` for hard-coded color literals (`#[0-9a-f]{3,6}` or `rgb(` outside the theme file) — any hits suggest M1 violation.
- Read `frontend/docs/design_direction.md` (or equivalent) — confirm it exists, names specific aesthetic choices, is >50 lines.
- Read `backend/app/aggregations.py::compute_alerts` — confirm the `(1 + 0.5 × (platform_count − 1))` multiplier exists.
- Read `backend/models/schemas.py::TopicCluster` — confirm `is_novel: bool` field exists.
- Read `contracts/real_api_integration_proposal.md` — confirm all 5 platforms covered with per-source legal posture.

### 7.3 Internet-aligned verification (enhanced audit role)

Per team-lead's new standing rule, any external claim engineers make must be WebSearched and cited in the round 3 review.

- If frontend-v3 claims `frontend-design` skill is invoked, WebSearch "anthropic frontend-design skill" to confirm the skill exists and matches what the research file describes. I will NOT re-read `references_and_skills.md` to compare — instead I will grep it once with a targeted pattern.
- If backend-v3's `real_api_integration_proposal.md` claims Arctic Shift is a valid Pushshift successor, WebSearch "Arctic Shift Reddit API 2026" to confirm it is still alive and legally usable.
- If backend-v3 cites the UCSD Amazon Reviews 2023 dataset for data enrichment fallback, WebSearch "UCSD Amazon Reviews 2023 dataset license academic" to confirm the usage terms.
- For any LIBRARY or TECHNIQUE engineers introduce (e.g., `react-window` for virtualization, `react-aria` for a11y), WebSearch to confirm it is real, maintained, and license-compatible.

I will NOT WebSearch claims that I have already verified in round 1 or round 2 or in the existing research files — that would duplicate work. The discipline is: verify anything NEW, trust anything already verified.

### 7.4 Exit criteria for Round 3 PASS

**All of the following must be true:**

1. R3-P0-1 through R3-P0-5 all acceptance-criterion green
2. At least 3 of R3-P1-1 through R3-P1-4 green (partial P1 is acceptable — R3 P1 now has 4 items since Trend Forecast moved to R4)
3. Round 2 floor intact: `pytest` still 34/34, `vite build` still succeeds, `tsc -p tsconfig.app.json` still EXIT:0
4. No net regression on any persona × gap-severity row in §1 (i.e., no previously-working thing is now broken)
5. If R3-P1-1 and R3-P1-2 both ship: novelty detection fires on the seeded "new aspect" test row from the enrichment fixture (integration check)
6. Forward compatibility for R4: `schemas.TopicCluster.is_novel` exists (R3 adds it) so R4 Trend Forecast can consume novelty as a feature input without another contract change

**Failure conditions:**
- Filter propagation still broken on any page (V1 must be fixed)
- Responsive broken at any of the 3 breakpoints (V2 must be fixed)
- `frontend-design` skill not invoked / no design direction document (V5 / R3-P0-3 must be real)
- Any backend test regression from Round 2 PASS state
- R3-P0-4 `real_api_integration_proposal.md` missing or fails to cover all 5 platforms with per-source legal posture
- Trend Forecast shipped in R3 at all (scope violation in the other direction — this feature is R4, not R3; R3 engineers should NOT implement it even if they have spare time)
- Aaru What-If shipped in R3 at all (same scope rule)

---

## 8. Proposed Requirement Amendments (informational, not for execution this round)

Listed here so team-lead can decide whether to amend `requirements.md` in a later round. Not in Round 3 scope.

1. **REQ-015 amendment:** "severity (volume × magnitude × recency × platform_count factor), with novelty-flagged clusters receiving 2× severity multiplier"
2. **REQ-016 amendment:** "emerging themes via aspect clustering with explicit NEW-cluster detection (first_seen within 14 days + momentum threshold), not just recently-trending existing clusters"
3. **NEW REQ-017 (P1 proposed):** "Trend Forecast: each SKU MUST have a 4-week forward-projected sentiment trajectory with visible confidence bands, labeled as a heuristic projection not a simulation"
4. **NEW REQ-018 (P0 for any future round that re-touches frontend):** "Frontend maturity rubric (M1-M6 per round 3 charter §5) is a gating criterion for frontend sign-off, with `frontend-design` skill invocation required before component code edits"

---

## 9. Charter Meta

**Revision log:**
- **Draft 1 (initial GO response):** Trend Forecast slotted as R3-P1-4 minimal-v1, 5 P1 items total, Aaru + export rejected/deferred with no explicit target round.
- **Draft 2 (this version, after 3-round-ceiling addendum):** Trend Forecast moved to R4 full-scope per §3.1. Aaru What-If confirmed R4. Exportable digest confirmed R5. Added §0 Round Budget Context at top. Added target-round column to persona audit matrix in §1. Added §3.6 R3/R4/R5 feature allocation summary for team-lead round-queue planning. R3 P1 queue now 4 items not 5. §7 exit criteria updated so "shipping Trend Forecast in R3" is now a scope VIOLATION, not a success. §8 proposed REQ amendments unchanged.

**Author's self-assessment on context compression (per standing rule):** this charter was written using targeted reads only. For draft 1: I re-read `requirements.md §1` (personas, lines 18-77) + `requirements.md §6-8` (page UX + data model + out-of-scope, lines 159-236). `contracts/research/references_and_skills.md` read once. For draft 2 (this revision): I used targeted Grep and Read with `offset`/`limit` to find the exact sections to edit (§3 lines 62-100, §6 lines 156-173, §7 lines 257-273, §9 lines 288-300). I did NOT re-read `review-round-1.md` or `review-round-2.md` at any point. I did NOT re-read my 5 prior `contracts/research/*.md` files. I did NOT re-read `backend/app/aggregations.py` or `backend/models/schemas.py`. Total context cost for draft 2 revision: 4 targeted offset+limit reads + 4 targeted Edits. Still well inside the 50% budget.

**Handoff notes for v3 engineers (to be included in their spawn prompts by team-lead):**
- Both engineers should read this charter (especially §0 for round context, §6 for their specific queue) and the two review files before starting.
- Frontend-v3 reads §2 (V1/V2/V5), §5 (rubric), §6 (P0/P1 queue), §7 (audit plan), and the `frontend-design` skill section of `contracts/research/references_and_skills.md`.
- Backend-v3 reads §2 (V3/V4/V6), §3 (prediction scope — note that §3.1 and §3.4 are R4, not R3), §4 (data enrichment), §6 (P0/P1 queue), §7 (audit plan), and the MiroFish section of `contracts/research/references_and_skills.md`.
- Contract change protocol (CLAUDE.md §4) still applies: any `schemas.py` change → regen `api-contract.yaml` → notify frontend via SendMessage. Round 3 has **exactly 1 contract change** (the novelty field on `TopicCluster`) after the draft 2 revision — Trend Forecast endpoint moved to R4, so R3 does not add it. Protocol fires once, not twice.
- **Explicit R3 scope fence:** do NOT implement the Trend Forecast endpoint `/api/products/{model}/forecast` or any `forecast` code in R3, even opportunistically with spare time. It is scheduled for R4 at full scope. R3 engineers finding free time should instead reinforce maturity rubric M1-M6 compliance or pay down any small residuals from round 2.

Charter author: business-leader-v2 (draft 2, post-3-round-ceiling revision, 2026-04-11)
