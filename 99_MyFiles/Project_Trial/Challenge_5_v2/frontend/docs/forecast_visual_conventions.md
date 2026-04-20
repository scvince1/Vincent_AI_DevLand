# Forecast Panel Visual Conventions — R4 Prep

**Written:** 2026-04-11  
**Agent:** frontend-engineer-v3 (idle research window, R3 complete)  
**Budget used:** 3 WebSearches  
**Purpose:** Pre-empt visual design decisions for MiroFish Trend Forecast panel (R4-P0)

---

## 1. Solid/Dashed Line — Known Past vs Forecast Future

**Established convention (Excel, Power BI, Tableau, Bloomberg all agree):**
- Solid line = actuals (data already observed)
- Dashed line = forecast / projection

The visual transition must be **immediately readable without reading labels**. Key implementation rules:

- **Break at the transition point**: the dashed segment starts at the last confirmed data point (not before it). The lines share a connecting dot/circle at the join to signal continuity.
- **Line weight**: actual line slightly heavier (2px) than forecast dashed (1.5px, 6px dash / 4px gap). The weight difference reinforces the certainty gradient.
- **"Today" marker**: vertical dashed line at `t=0` labeled "Today" is standard in finance dashboards. Places the join in spatial context.
- **Avoid mixed styles** (dash-dot, long-short alternating) — they look messy and add no information.

**Recharts implementation note:** Render as two separate `<Line>` series on the same `<LineChart>`: one for `actuals[]`, one for `forecast[]`. The forecast series uses `strokeDasharray="6 4"`. Both series share the final actual data point as their first/last point respectively so the visual join is seamless.

---

## 2. Confidence Cone (Fan Chart)

**Exec-level pattern (Bank of England, FiveThirtyEight, Kalshi):**
- Central line = median forecast (or mean)
- Shaded band = 80% confidence interval (not 95% — 95% looks too wide, alarming to non-statisticians)
- Optional inner band = 50% CI in slightly darker opacity

**Rendering choices that avoid "over-scientific" look:**
- Use opacity `0.15–0.20` for the band fill, same hue as the forecast line. Avoid grey — it reads as "error" rather than "range".
- **Do not label the band with "80% CI"** in an exec context. Label it "Expected range" or leave it unlabeled with a tooltip: "8 out of 10 outcomes expected within shaded area."
- Width of cone expands with horizon — this is correct behavior, not a bug. The visual expansion itself communicates uncertainty growth.

**Recharts implementation:** `<Area>` with `dataKey="upper"` and a second `<Area>` for `lower`, both with `fill` and `fillOpacity`, rendered below the forecast `<Line>`. Use `activeDot={false}` on the Area series to suppress dots on hover.

---

## 3. "Indicative Only" Labels Without Undermining Credibility

**Finance dashboard pattern (Runway, Causal, FP&A tools):**
- Place a small italic footnote **below** the chart, not overlaid on it: *"Projections are model-generated estimates based on observed trends. Not a guarantee of future outcomes."*
- Overlay text on the chart itself should be **avoided** — it clutters the signal area and implies the data is suspect, not just uncertain.
- Alternative: use a subtle `(i)` icon in the chart title that reveals the disclaimer on hover.

**For thin-data degradation** (< 50 mentions / 14-day window):
- Visually degrade the forecast band: reduce line opacity to `0.4`, increase dash gap to `10px`, add a "Low confidence" chip on the chart card header (not over the chart).
- Keep the projection visible — hiding it removes value. Degrading it is the right signal.
- Threshold logic: `mention_count < 50 || data_window_days < 14 → low_confidence = true`.

---

## 4. Data-Quality Flags (Thin Data)

**Pattern from uncertainty visualization research (Claus Wilke, FlowingData):**
- Visual encoding options for low confidence: reduced opacity, increased fuzziness/blur, hatching on the confidence band.
- For an exec dashboard: **opacity reduction is most intuitive**. Blur and hatching require explanation.
- Add a `LowConfidenceBadge` component to the card header: amber dot + "Low confidence — fewer than 50 data points."
- Do NOT use red — red implies error. Amber implies caution.

**Practical implementation:**
```tsx
// Props pattern for the forecast chart card
type ForecastCardProps = {
  data: ForecastSeries;
  lowConfidence?: boolean;  // from: mention_count < 50
  confidenceNote?: string;  // e.g. "Based on 23 mentions over 8 days"
};
```

---

## 5. Scenario Comparison (2-3 Projection Overlays)

**Best-practice pattern (Causal, Runway, FP&A dashboards):**
- Assign each scenario a **fixed semantic color** used consistently across all visuals in the session:
  - Base case: `--chart-blue` (`#4A9EFF`)
  - Optimistic: `--chart-green` (`#56C785`)
  - Pessimistic: `--chart-red` (`#E05656`)
- Render all three as dashed lines (all are projections). Differentiate by color alone — do not vary dash style per scenario (adds noise).
- Include a **scenario legend** inside the chart card (not in the page header) with an on/off toggle per scenario. Default: base case on, others off. User opt-in to comparison view.
- When all three are visible: confidence cones **collapse to lines only** — overlapping cones are unreadable. Show a tooltip note: "Confidence bands hidden in multi-scenario view."

---

## Implementation Recommendations for R4

| Item | Recommendation |
|---|---|
| Historical line | `<Line strokeWidth={2} stroke={cssVar('--chart-blue')} />` |
| Forecast line | `<Line strokeDasharray="6 4" strokeWidth={1.5} stroke={cssVar('--chart-blue')} opacity={lowConfidence ? 0.4 : 1} />` |
| Confidence band | `<Area fillOpacity={0.15} fill={cssVar('--chart-blue')} />` |
| Today marker | `<ReferenceLine x={todayIndex} strokeDasharray="3 3" label="Today" />` |
| Low confidence | Amber badge in card header, not on chart canvas |
| Scenario toggle | Per-scenario checkbox in card header, cones hidden in multi-scenario view |
| Uncertainty label | Below-chart footnote, italic, 12px, `--text-tertiary` color |

---

## Applicable CSS Token Additions (for theme.css in R4)

```css
/* Forecast-specific tokens */
--forecast-dash: 6 4;
--forecast-opacity-normal: 1;
--forecast-opacity-low-confidence: 0.4;
--confidence-band-fill-opacity: 0.15;
--color-caution: #F5A623;       /* amber for low-confidence badge */
--color-scenario-base: var(--chart-blue);
--color-scenario-optimistic: var(--chart-green);
--color-scenario-pessimistic: var(--chart-red);
```

---

*Word count: ~780. Budget: 3 WebSearches used.*
