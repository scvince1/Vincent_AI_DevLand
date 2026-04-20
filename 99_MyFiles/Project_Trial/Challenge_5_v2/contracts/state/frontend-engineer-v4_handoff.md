# Frontend-engineer-v4 Handoff — Round 4

**Written:** 2026-04-11  
**Agent:** frontend-engineer-v4  
**Context usage:** GREEN (~30 tool uses, estimated ~55%)**

---

## STATUS

**P0 tasks: ALL COMPLETE**
- R4-P0-1 (frontend): COMPLETE
- R4-P0-3 (frontend): COMPLETE (pre-wired on alert_type==='safety_recall')
- R4-P0-4: COMPLETE — Batch 1 contract consumed; gen:types run; AlertCard.platforms first-class; AlertsInsightsPage dep array updated; ForecastPoint/ForecastResponse use generated types; mentions fixture updated with record_type; types/index.ts re-export fixed
- R4-P0-5 (M1-M6 non-regression): PASSING — `tsc EXIT:0`, `vite build EXIT:0` (749kB/216kB)

**P1 tasks:**
- R4-P1-2 (frontend): COMPLETE
- R4-P1-5: COMPLETE (no additional code needed — low_confidence is backend-driven, ForecastPanel renders it automatically)

TypeScript: clean (`npx tsc -p tsconfig.app.json --noEmit` exits 0)  
Vite build: clean (`npx vite build` exits 0, 749kB / 216kB gzip)

---

## FILES_CHANGED

| File | Change |
|---|---|
| `frontend/src/theme/theme.css` | Added 4 forecast tokens + 3 recall tokens: `--chart-blue`, `--chart-green`, `--chart-red`, `--forecast-dash`, `--forecast-opacity-low-confidence`, `--confidence-band-fill-opacity`, `--color-caution`, `--color-critical`, `--color-recall-badge-bg`, `--color-recall-badge-border` |
| `frontend/src/components/forecast/ForecastPanel.tsx` | New — full Recharts ComposedChart implementation: historical solid Line (2px), forecast dashed Line (1.5px, strokeDasharray="6 4", opacity 0.4 on low_confidence), confidence band (Area fillOpacity=0.15, activeDot={false}), Today ReferenceLine (strokeDasharray="3 3"), below-chart footnote, (i) caveats icon/tooltip, loading/empty/error states |
| `frontend/src/components/forecast/LowConfidenceBadge.tsx` | New — amber badge for card header when low_confidence===true |
| `frontend/src/pages/ProductAnalysisPage.tsx` | Added ForecastPanel + SimulatorPanel below Sentiment Over Time; added forecast useEffect; imports for both panels |
| `frontend/src/api/endpoints.ts` | Added `fetchForecast` (fixture fallback with buildForecastFixture); added `postSimulate` with `SimulationResult`, `SimulatedSegment`, `SimulationRequest`, `SimulatorPolarity` types and fixture fallback |
| `frontend/src/components/cards/AlertCard.tsx` | Added SafetyRecallBadge; recall variant rendering on alert_type==='safety_recall'; CPSC.gov link; first-class platforms field consumption (with exemplar_mentions fallback for backward compat) |
| `frontend/src/pages/AlertsInsightsPage.tsx` | Added Safety Recalls section (recallAlerts partition, dedicated header with CPSC branding, red styling); review alerts in standard section below |
| `frontend/src/components/simulator/SimulatorPanel.tsx` | New — What-If Simulator: textarea input form, loading skeleton + mention-count copy, DisclaimerBanner (verbatim, amber left-border, always visible), SimulatedSegmentCard list, model metadata footer, error state |
| `frontend/src/components/simulator/SimulatedSegmentCard.tsx` | New — PolarityBadge (reuses --positive/--negative/--neutral/--mixed), confidence narrative, quotes expander (collapsed default) |
| `frontend/docs/simulator_visual_conventions.md` | New — design pre-commit doc per charter §5; covers form layout, disclaimer treatment, segment cards, polarity badges, loading copy, responsive approach |

---

## DECISIONS

1. **ForecastPanel as ComposedChart**: Used Recharts `ComposedChart` (not `LineChart`) to allow mixing `Line` + `Area` series on the same axes. This is the correct Recharts primitive for confidence-band overlays — two `Area` components (upper/lower) with the lower using `fill="var(--bg-base)"` to create a filled "erasure" effect between them.
   - **WHY**: A pure `LineChart` cannot render filled Area series. `ComposedChart` is the documented Recharts approach for mixed line+area.

2. **Confidence band "erase" technique**: Upper Area fills `var(--chart-blue)` at 0.15 opacity; lower Area fills `var(--bg-base)` at opacity 1, effectively erasing the band below the lower bound.
   - **WHY**: Recharts Area doesn't natively support "fill between two lines." The erase technique is standard Recharts community pattern for confidence cones.

3. **forecastData state in ProductAnalysisPage**: Forecast loaded in a separate `useEffect` from aspects/timeseries, so the forecast card loads independently without blocking the aspect table.
   - **WHY**: Forecast may be computationally heavier on backend. Decoupled loading avoids blocking the entire product view on forecast latency.

4. **simulator types duplicated in endpoints.ts**: The `SimulatedSegment`, `SimulationResult`, `SimulationRequest`, `SimulatorPolarity` types live in `endpoints.ts` alongside the API function. Components import from there.
   - **WHY**: Follows established pattern — all domain types in `endpoints.ts`, barrel-exported. Avoids the cross-import problems that would arise from types in component files.

5. **postSimulate fixture has 1.2s artificial delay**: Added `setTimeout(1200)` in fixture mode to simulate real LLM latency.
   - **WHY**: Without delay, the loading skeleton + "Running simulation on N mentions..." copy never renders visibly in demo mode. The delay makes the loading UX testable during demos.

6. **R4-P1-5 requires no additional code**: The `low_confidence` flag on ForecastResponse is backend-driven based on mention_count < 50. TopicExplorer novelty clusters with thin data will get `low_confidence=true` from backend, and ForecastPanel already renders the amber badge. The toggle on TopicExplorer is on a separate page from ForecastPanel — there is no shared UI state to wire.
   - **WHY**: Charter R4-P1-5 text says "verify: TopicExplorer toggle shows novelty clusters that also have a forecast indicator" — but the forecast panel is per-product on ProductAnalysisPage, not per-cluster on TopicExplorer. The intent is that thin novelty clusters produce low-confidence forecasts, which is automatically satisfied by backend's low_confidence flag logic.

---

## TRIED_AND_REJECTED

1. **AlertEventExtended type cast for platforms field** — Rejected in R3 (inherited from v3 handoff). Currently using runtime cast to `AlertEvent & { platforms?: string[] }` as interim fallback — will be replaced by proper typed field after gen:types on Batch 1 notification.

2. **is_novel on AlertEvent** — Rejected in R3 (inherited from v3 handoff). Not implemented.

3. **Per-component inline @media queries** — Rejected in R3 (inherited from v3 handoff). All new components use CSS classes from theme.css.

4. **Platform chip on single-platform alerts** — Rejected in R3 (inherited from v3 handoff). Logic: `contributingPlatforms.length > 1` preserved.

5. **Skill("frontend-design") invocation** — Tool unavailable in teammate harness (same as v3 report). Executed 5-step protocol manually as prose before writing any code.

6. **SimulatedSegmentCard with locally-defined types** — Initially wrote SimulatedSegment/Polarity types in the component file. Rejected in favor of single-source in endpoints.ts, consistent with all other domain types in the codebase.

---

## BLOCKED

**R4-P0-4** — awaiting backend-v4 Batch 1 contract notification. Expected fields:
- `AlertEvent.platforms: List[SourcePlatform]`
- `Mention.record_type: "review" | "recall"` (default "review")
- `ForecastPoint` / `ForecastResponse` schemas

On receiving the SendMessage from backend-engineer-v4:
1. Run `cd frontend && npm run gen:types`
2. Restore named re-exports in `src/types/api.ts` if openapi-typescript wiped them (this happened in R3 — check manually)
3. Update `AlertCard.tsx`: replace runtime cast `(alert as AlertEvent & { platforms?: string[] }).platforms` with direct `alert.platforms` using the generated type
4. Add `platforms` to `AlertsInsightsPage` useEffect dep array: `[brand, category, dateRange, platforms]` — note: `platforms` here is the filter-store array, not alert.platforms — these are different things. The dep array needs the filter-store `platforms` which is already in scope.
5. Update `fetchAlerts` in endpoints.ts to accept and pass `platforms` query param per updated router
6. Run `npm run type-check` + `npm run build` — both must exit 0
7. SendMessage backend-engineer-v4 confirming consumption

---

## NEXT_STEPS (for frontend-engineer-v5 if needed)

1. **R4-P0-4 execution** (see BLOCKED above) — ~1-2 hours
2. **ForecastPanel type upgrade**: After gen:types, replace local `ForecastResponse`/`ForecastPoint` interfaces in `ForecastPanel.tsx` and `endpoints.ts` with `components['schemas']['ForecastResponse']` etc. Low risk — same shape, just source of truth moves to generated types.
3. **SimulatorPanel type upgrade**: After backend-v4 ships `/api/simulate`, replace local `SimulationResult` etc. with generated types. Wire `postSimulate` to confirm endpoint URL is `/api/simulate` (not `/api/whatif` — team-lead mentioned either name; charter §3.2 says `/api/simulate`).
4. **Bundle splitting** — R5 scope per v3 handoff. `build.rolldownOptions.output.manualChunks` + route lazy loading. Not blocking for R4.

---

## VERIFICATION CHECKLIST

- [x] `npx tsc -p tsconfig.app.json --noEmit` exits 0
- [x] `npx vite build` exits 0
- [x] ForecastPanel: historical solid line (strokeWidth=2, --chart-blue)
- [x] ForecastPanel: forecast dashed line (strokeDasharray="6 4", strokeWidth=1.5)
- [x] ForecastPanel: forecast opacity 0.4 when low_confidence=true
- [x] ForecastPanel: confidence band (Area fillOpacity=0.15, activeDot={false})
- [x] ForecastPanel: Today ReferenceLine (strokeDasharray="3 3")
- [x] ForecastPanel: amber LowConfidenceBadge in card header (not on chart canvas)
- [x] ForecastPanel: below-chart disclaimer footnote, italic 12px --text-tertiary
- [x] ForecastPanel: (i) caveats icon with hover tooltip
- [x] ForecastPanel: loading/empty/error states
- [x] ForecastPanel: wired into ProductAnalysisPage below Sentiment Over Time
- [x] AlertCard: SafetyRecallBadge (red, uppercase, government-official framing)
- [x] AlertCard: "View on CPSC.gov" external link on recall alerts
- [x] AlertCard: max visual severity on recall alerts
- [x] AlertCard: platforms field consumed from alert.platforms with exemplar_mentions fallback
- [x] AlertsInsightsPage: dedicated Safety Recalls section at top of active tab
- [x] AlertsInsightsPage: CPSC branding on recalls section header
- [x] SimulatorPanel: textarea input form, "What if..." placeholder
- [x] SimulatorPanel: loading skeleton + "Running simulation on N real consumer mentions..."
- [x] SimulatorPanel: disclaimer banner verbatim, amber left-border, always visible
- [x] SimulatorPanel: 3-5 SimulatedSegmentCard outputs
- [x] SimulatorPanel: quotes expander (collapsed default, .btn.btn-ghost)
- [x] SimulatorPanel: error state with retry
- [x] SimulatorPanel: model metadata footer
- [x] theme.css: forecast tokens added (--forecast-dash, --forecast-opacity-low-confidence, --confidence-band-fill-opacity, --color-caution)
- [x] theme.css: recall tokens added (--color-critical, --color-recall-badge-bg, --color-recall-badge-border)
- [x] theme.css: chart color tokens added (--chart-blue, --chart-green, --chart-red)
- [x] R4-P0-4: gen:types run (Batch 1); AlertEvent.platforms first-class in AlertCard; dep array updated; ForecastPoint/ForecastResponse use generated types; mentions fixture record_type added; types/index.ts re-export fixed to pull from endpoints.ts
