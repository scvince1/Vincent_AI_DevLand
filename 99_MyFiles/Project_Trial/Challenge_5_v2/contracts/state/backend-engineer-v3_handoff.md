# Backend-engineer-v3 Handoff — Round 3 Complete

**Agent:** backend-engineer-v3
**Date:** 2026-04-11
**Status:** ROUND 3 COMPLETE — all P0 and P1 backend tasks finished + research window (UCSD, TikTok, alt-sources) in progress

---

## STATUS

All assigned Round 3 backend tasks completed. Tests: 44 passed, 6 xfailed (expected), 0 failures. Contract regenerated. Frontend-v3 notified and confirmed both contract changes consumed. Research queue (UCSD ingest, TikTok feasibility, alt consumer signals) executed during idle window.

---

## FILES_CHANGED

| File | Change |
|---|---|
| `contracts/real_api_integration_proposal.md` | NEW — R3-P0-4: full API integration proposal for Round 4 |
| `backend/scripts/generate_fixtures.py` | NEW — R3-P1-1: fixture generator script |
| `backend/data/reviews_shark.csv` | REPLACED — 171 rows (was 25), preserves all 16 edge-case texts verbatim |
| `backend/data/reviews_ninja.csv` | REPLACED — 64 rows (was 25) |
| `backend/data/reviews_competitors.csv` | REPLACED — 65 rows (was 25) |
| `backend/models/schemas.py` | MODIFIED — R3-P1-2: added `is_novel: bool` to `TopicCluster` |
| `backend/app/aggregations.py` | MODIFIED — R3-P1-2 + R3-P1-3: novelty detection in `compute_topics`, cross-platform + novelty multipliers in `compute_alerts` |
| `contracts/api-contract.yaml` | REGENERATED — reflects `TopicCluster.is_novel` field |
| `contracts/research/orchestrator/ucsd_amazon_ingest_plan.md` | NEW — R3 research window: UCSD Amazon '23 ingest plan |
| `contracts/research/orchestrator/tiktok_scraping_feasibility.md` | NEW — R3 research window: TikTok signal vectors |
| `contracts/research/orchestrator/alt_consumer_signal_sources.md` | NEW — R3 research window: alt data sources brainstorm |

---

## DECISIONS (with WHY per item)

### Fixture generator (R3-P1-1)
- 300 rows total: 171 Shark, 64 Ninja, 65 Competitors
- 13 distinct SKUs: PowerDetect UV Reveal, PowerDetect, Shark Matrix, Shark IQ, Shark Navigator, Ninja Foodi DualZone, Ninja Creami, Ninja Espresso Bar, Ninja Coffee Bar, Dyson V15, iRobot Roomba j7+, Roborock S8, KitchenAid Pro
- All 5 platforms populated; PowerDetect UV Reveal has 6 aspects with 10+ mentions each
- 5 novelty-seed rows: "charging dock LED flickering" on PowerDetect UV Reveal, first_seen_at 5-14 days ago
- **WHY 300 rows exactly:** minimum to satisfy exit criteria without bloating CSVAdapter startup — it runs NLP pipeline on every row at init, so more rows = slower dev loop. Exactly at the floor.
- **WHY novelty seed on PowerDetect UV Reveal:** most rows of any SKU → most realistic cluster density. A novelty cluster on a sparse SKU would be trivially easy to trigger and less useful as a demo test case.

### Novelty detection (R3-P1-2)
- `is_novel` threshold: momentum > 0.3 AND mention_count < 25 AND first_seen_at within last 14 days
- `compute_alerts` re-derives novelty from raw mention list (not from TopicCluster results)
- **WHY momentum threshold 0.3 (float, not integer):** momentum is stored as `float(this_week - last_week)`. A new cluster with 1 mention this week, 0 last week = momentum 1.0, clearly above 0.3. Filters zero-activity aspects while catching any genuinely new cluster.
- **WHY re-derive novelty in `compute_alerts` rather than consuming TopicCluster output:** `compute_alerts` and `compute_topics` are independent functions called from different routers. Coupling them would complicate unit testing and router architecture. Re-derivation is slightly redundant but keeps both functions independently testable.

### Cross-platform severity (R3-P1-3)
- Formula: `severity = base * (1 + 0.5 * (platform_count - 1)) * novelty_multiplier`
- Both multipliers in single `compute_alerts` rewrite
- **WHY combined in one rewrite:** charter §3.2 and §3.3 both touch `compute_alerts`. Two separate edits would risk logic conflicts. Single rewrite is cleaner and the combined formula remains readable.
- **WHY 0.5 step:** direct charter spec — not a design choice by this agent.

### API integration proposal (R3-P0-4)
- Primary recommendation: Reddit (PRAW) + HN (Algolia); Amazon via UCSD offline corpus
- Twitter/X NOT IN SCOPE without $100/month budget decision
- **WHY HN as co-primary (not secondary):** audit rubric scored HN 23/25 — highest of all sources. Zero cost, zero auth, complementary tech/media audience. Adds multi-source demo story at near-zero implementation cost.
- **WHY UCSD Amazon in separate "offline corpora" section:** team-lead amendment explicitly required this separation. Prevents conflating it with live API sources and double-counting toward the Reddit+HN recommendation.

### Frontend-backend contract (R3-P1-2 coordination)
- `AlertEvent` does NOT have a top-level `platforms` field — frontend-v3 derives from `exemplar_mentions[].source_platform`
- **WHY no `platforms` field added to AlertEvent:** keeping R3 schema changes to exactly ONE (is_novel on TopicCluster) per charter draft 2 constraint. The workaround is functional for R3. R4 should add it properly.

---

## TRIED_AND_REJECTED

| Approach | Reason rejected |
|---|---|
| Adding `platforms: List[str]` to `AlertEvent` in R3 | Charter draft 2 explicitly limits R3 schema changes to ONE (is_novel). Deferred to R4. |
| Implementing Trend Forecast endpoint in R3 | Charter §3.1 and §7 explicitly fence this to R4. Would have been a scope violation. |
| Using TopicCluster.is_novel results to drive `compute_alerts` novelty multiplier | Creates circular dependency between router-level functions; would require restructuring the call graph. Re-derivation from raw mentions is cleaner. |
| Downloading full 571GB UCSD Amazon corpus | Only Appliances (~1-2GB) is needed for SharkNinja coverage. Home_and_Kitchen (15-20GB) is secondary fallback only. |
| Treating UCSD license silence as "commercial use permitted" | Absence of license is legally ambiguous, not permissive. Yellow-light rating issued; legal clarification required before client-deliverable use. |

---

## BLOCKED

None. All R3 tasks completed.

---

## NEXT_STEPS (for backend-engineer-v4 in Round 4)

1. **Real API integration** — Execute `contracts/real_api_integration_proposal.md`. Priority: Reddit PRAW → HN Algolia → UCSD Amazon ingest (see `ucsd_amazon_ingest_plan.md`) → YouTube v3 → GNews. Twitter/X requires team-lead budget decision.

2. **UCSD Amazon ingest** — Read `contracts/research/orchestrator/ucsd_amazon_ingest_plan.md` before starting. Key points: download `Appliances.jsonl.gz` only (~1-2GB), filter by ASIN set from metadata, 3 medium-severity field mapping gaps (product_model resolution, brand normalization, category inference). Write `UCSDAdapter(BaseScraper)` in `backend/app/scrapers/ucsd_adapter.py`.

3. **MiroFish Trend Forecast** (`GET /api/products/{model}/forecast`) — GraphRAG-lite heuristic, 4-week forward projection with confidence bands, NO OASIS/LLM calls. Read `contracts/research/orchestrator/mirofish_mvp.md`.

4. **Aaru What-If Simulator** (`POST /api/simulate`) — LLM dependency, adds OpenAI/Anthropic SDK requirement. Read charter §3.4.

5. **Schema changes for R4 endpoints** — Both Trend Forecast and What-If Simulator need new Pydantic response models. Follow CLAUDE.md §4: update schemas.py → regenerate YAML → notify frontend.

6. **`AlertEvent.platforms: List[str]`** — Add as first-class field for cleaner frontend platform chip. Frontend-v3 current workaround (derive from exemplar_mentions) is fragile if exemplar_mentions is ever truncated.

7. **TikTok and alt-sources** — See `tiktok_scraping_feasibility.md` and `alt_consumer_signal_sources.md` for R4/R5 data source expansion options. TikTok Research API is the only low-legal-risk vector; CPSC SaferProducts.gov and Google Trends are standout alt sources.

---

## FRONTEND_COORDINATION_OUTCOME

Both contract changes confirmed consumed by frontend-engineer-v3. TypeScript type-check exits 0.
- `is_novel`: live on TopicCard ("NEW" badge) and TopicExplorer ("Show emerging only" toggle)
- Platform chip: derived from `exemplar_mentions[].source_platform` at render time; shows on 2+ platform alerts only

**R4 note:** Add `platforms: List[str]` to `AlertEvent` schema for cleaner implementation.

---

## CONTEXT_LEVEL

Approximately 55-65% used after research window. Monitor AMBER threshold if spawned for additional R3 work. Clean spawn recommended for R4.

---

## TEST_RESULTS

```
44 passed, 6 xfailed, 4 warnings in 1.30s
```
- 34 NLP edge-case tests: all PASSED
- 10 NLP robustness tests: all PASSED
- 6 xfailed: expected known edge cases (rhetorical questions) — intentional, not regressions
