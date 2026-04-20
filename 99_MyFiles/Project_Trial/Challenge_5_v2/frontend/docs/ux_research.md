# UX Research — SharkNinja Consumer Sentiment Dashboard

**Purpose:** INFORMATIONAL ONLY. This document was compiled during a code-freeze research window (post-round-1, pre-round-2 verdict). It feeds post-round-2 polish and potential round 3+ UX refinements. No code changes were made as part of this research pass. All implementation ideas below are labeled as recommendations for future rounds, not the current build.

**Stack context:** React + TypeScript + Vite + Recharts + Zustand + CSS variables dark theme. `bg-base: #0d0f14`, `text-primary: #e8ecf4`, `accent: #4f8ef7`, `positive: #3ecf8e`, `neutral: #f0b429`, `negative: #f05252`.

---

## Topic 1 — Incumbent Competitive Dashboard UX Tour

### Observation
Cataloging how Brandwatch, Sprout Social, Meltwater, and Talkwalker visually present sentiment data establishes a shared vocabulary for any future design polish. Understanding the visual conventions judges have already internalized from these tools is prerequisite to differentiating from them or referencing them.

### Existing Approaches

**Brandwatch Consumer Research:** Sentiment displayed as a three-band breakdown widget (Positive / Neutral / Negative) with counts and percentages. Time-series sentiment layered as stacked area. Content feed below charts lets users click through to individual post cards (Card view or List view) — the drill path goes: sentiment widget → filtered content feed → individual post. Platform (channel) breakdown exists as a separate component. Topic clouds are a common widget type (our product deliberately avoids these per REQ-016). G2 gallery and `brandwatch.com/products/consumer-research/features/` carry the most accessible screenshots.

**Sprout Social Listening:** Sentiment presented as a gauge/donut for overall score plus a time-series line underneath, in their Listening add-on. Platform breakdown is surface-level (by network icon). Drill path: spike alert → filtered message stream in Smart Inbox. AI spike alerts fire on sudden volume changes and link directly to the message list. The "Sentiment for Messages" feature lets you triage individual messages by sentiment label — closest competitor pattern to our EvidenceDrilldown.

**Meltwater:** Configurable widget dashboards; sentiment displayed as bar chart of emotions (love, fear, hatred as discrete bars), not just positive/neutral/negative. Word-cloud variant by sentiment polarity (breaking them out by positive vs. negative keywords rather than showing one unified cloud). Geographic heatmaps for mention density. No prominent one-click drill to individual mentions in the public documentation.

**Talkwalker:** Core metrics broken out as KPI cards: Mentions, Sentiment score, Hashtags, Engagement. Sentiment is a top-line score displayed prominently alongside volume. Platform breakdown is a separate chart. Drill path not prominently documented in public materials.

### Relevant to Our Stack
The clearest industry convention is: **top-line sentiment score as a prominent number with trend delta → time-series line → per-aspect or per-platform breakdown → individual mention list**. Our OverviewPage and EvidenceDrilldown already follow this exact path. The one gap is that Sprout-style spike alerting visually links the alert card directly to the relevant message stream — our AlertsInsightsPage has `onViewEvidence` but the connection is less visually prominent than Sprout's inline call-to-action.

Preferred technique: keep current flow, but consider making the "View mentions" CTA in AlertCard more visually prominent (color-accent the button, show exemplar quote text inline on the card as a preview before opening the drilldown).

### Implementation Sketch (future round recommendation)
```tsx
// AlertCard: inline preview quote before opening drilldown
{alert.exemplar_mentions?.[0] && (
  <blockquote style={{ borderLeft: '3px solid var(--negative)', padding: '4px 8px', fontSize: 12 }}>
    "{alert.exemplar_mentions[0].text.slice(0, 120)}..."
  </blockquote>
)}
<button onClick={onViewEvidence} style={{ background: 'var(--accent)', ... }}>
  View {exemplarCount} mentions →
</button>
```

### References
- [Brandwatch Consumer Research Features](https://www.brandwatch.com/products/consumer-research/features/)
- [Brandwatch Content Analysis Dashboard Help](https://social-media-management-help.brandwatch.com/hc/en-us/articles/7281821613213-Using-the-Content-Analysis-Dashboard)
- [Sprout Social Sentiment for Messages](https://support.sproutsocial.com/hc/en-us/articles/18192983640589-Sentiment-for-Messages)
- [Meltwater Social Listening Platform](https://www.meltwater.com/en/suite/social-listening-analytics)
- [Talkwalker Social Listening](https://www.talkwalker.com/products/social-listening)

---

## Topic 2 — Evidence Drilldown UI Patterns

### Observation
Our EvidenceDrilldown uses a right-side panel (non-modal overlay) that opens on any sentiment number click across all 5 pages, satisfying REQ-006. The question is whether this pattern is best-in-class for a judge-facing demo where clarity and trustworthiness of the evidence chain matter.

### Existing Approaches

**Grafana Drilldown Apps (2024):** Grafana's Explore suite renamed to "Grafana Drilldown" — queryless, point-and-click from a metric panel to a traces/logs detail view. Pattern: clicking a panel opens a **separate full-screen Explore view** (effectively a page navigation). Works for observability (deep investigation), less suited for quick mention preview.

**Looker / Looker Studio:** Two patterns coexist. "Drill fields" opens an **inline table below the chart** showing row-level data that comprises the clicked metric. "Drill through" navigates to a related dashboard page. The inline table is closest to our use case.

**Tableau "View Underlying Data":** Right-click context menu → modal dialog with a full data table of underlying rows. Modal is dismissible, full-width. No context preview — you see raw columns.

**Hex / Observable:** These notebook tools typically use a cell-output interaction model — clicking a chart element updates a downstream cell that shows filtered rows. Equivalent to our filter store + drilldown panel, but visible inline on the same page.

### Relevant to Our Stack
Our **non-modal right side panel** is the strongest pattern for a dashboard demo context. Nielsen Norman Group research confirms non-modal overlays let users maintain spatial context (they can see the chart they clicked behind the panel), whereas full modals interrupt flow. The NNg finding on modals: appropriate only when the task requires full focus and a response is required to continue. Our drilldown is a passive "show me" action — non-modal is correct.

One enhancement: Grafana's Drilldown apps and Looker's inline tables both **animate the transition** so users perceive continuity (the chart they clicked is still visible). Our slide-in panel already preserves the chart context. Adding `transform: translateX` entry animation (CSS only, no library) would reinforce this.

Preferred technique: keep side panel, add CSS slide-in animation and an optional "expand to full page" icon for deep investigations.

### Implementation Sketch (future round recommendation)
```css
/* Add to EvidenceDrilldown panel — CSS only, no library needed */
.drilldown-panel {
  transform: translateX(100%);
  transition: transform 0.2s ease-out;
}
.drilldown-panel.open {
  transform: translateX(0);
}
```
```tsx
// Optional: "open full view" icon in panel header
<button aria-label="Expand to full view" onClick={navigateToMentionsPage}>
  ⤢
</button>
```

### References
- [Grafana Drilldown Apps](https://grafana.com/blog/grafana-drilldown-apps-the-improved-queryless-experience-formerly-known-as-the-explore-apps/)
- [Looker More Powerful Data Drilling](https://cloud.google.com/looker/docs/best-practices/how-to-use-more-powerful-data-drilling)
- [Tableau View Underlying Data](https://tableau.com/drive/viewing-underlying-data)
- [Nielsen Norman Group: Modes in User Interfaces](https://www.nngroup.com/articles/modes/)
- [Carbon Design System Dialog Pattern](https://carbondesignsystem.com/patterns/dialog-pattern/)

---

## Topic 3 — WCAG AA Audit for Our Dark Theme

### Observation
Our dark palette uses near-black backgrounds and light text. WCAG AA compliance is not currently tracked and a judge demo in a conference room (projected screen, ambient light) can expose low-contrast pairs that look fine on a calibrated monitor.

### WCAG AA Requirements
- **Normal text (< 18pt / < 14pt bold):** minimum contrast ratio **4.5:1**
- **Large text (≥ 18pt or ≥ 14pt bold):** minimum ratio **3:1**
- **UI components and graphical objects:** minimum ratio **3:1** (WCAG 2.1 SC 1.4.11)
- These thresholds apply regardless of light/dark theme — dark mode is not an exemption

### Palette Analysis (computed from relative luminance formula)

| Pair | Use | Approx Ratio | AA Status |
|---|---|---|---|
| `#e8ecf4` on `#0d0f14` | Primary body text on base bg | ~17:1 | **PASS** (AAA) |
| `#e8ecf4` on `#161b24` | Primary text on surface | ~14:1 | **PASS** (AAA) |
| `#8b96ab` on `#0d0f14` | Secondary text on base | ~7:1 | **PASS** (AA) |
| `#8b96ab` on `#161b24` | Secondary text on surface | ~5.8:1 | **PASS** (AA) |
| `#556074` on `#0d0f14` | Tertiary text on base | ~3.4:1 | **FAIL** for normal text; PASS for large text only |
| `#556074` on `#161b24` | Tertiary text on surface | ~2.8:1 | **FAIL** — below 3:1 |
| `#4f8ef7` on `#0d0f14` | Accent on base | ~5.2:1 | **PASS** |
| `#4f8ef7` on `#161b24` | Accent on surface | ~4.3:1 | **MARGINAL** — just under 4.5:1 for normal text |
| `#3ecf8e` on `#0d0f14` | Positive on base | ~8.2:1 | **PASS** |
| `#f0b429` on `#0d0f14` | Neutral/warning on base | ~9.1:1 | **PASS** |
| `#f05252` on `#0d0f14` | Negative on base | ~5.0:1 | **PASS** |
| `#a78bfa` on `#0d0f14` | Mixed/sarcasm on base | ~6.1:1 | **PASS** |

**Critical fails:** `textTertiary (#556074)` on both bg-surface and bg-base fails AA for normal text. This color is used for axis tick labels in Recharts (hardcoded as `COLORS.textTertiary`), table header labels, and filter hint text. All of these are small normal-weight text.

**Marginal:** `accent (#4f8ef7)` on `bg-surface (#161b24)` sits at approximately 4.3:1 — just under the 4.5:1 threshold. Used for link text and active tab indicators.

### Existing Audit Tools
- **WebAIM Contrast Checker** (webaim.org/resources/contrastchecker): free, input hex codes directly
- **Coolors Contrast Checker** (coolors.co/contrast-checker): visual picker, shows pass/fail badges
- **Radix Colors** (radix-ui.com/colors): pre-audited dark-mode palette scales designed to pass WCAG AA at every step
- **Stark** (Figma plugin): batch-audits all text/background pairs in a design file

### Preferred Technique (future round recommendation)
Bump `textTertiary` from `#556074` to approximately `#6b7a94` (estimated ratio ~4.6:1 on bg-surface). This is a one-line change in `src/theme/index.ts` and cascades to all Recharts tick labels. Verify with WebAIM before committing.

### Implementation Sketch
```ts
// src/theme/index.ts — one-line fix (future round)
textTertiary: '#6b7a94',  // was #556074 — bumped for WCAG AA compliance
// Verify: #6b7a94 on #161b24 ≈ 4.6:1 (AA pass for normal text)
```

### References
- [W3C WCAG AA Contrast Minimum](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [BOIA: Dark Mode Doesn't Satisfy WCAG Requirements](https://www.boia.org/blog/offering-a-dark-mode-doesnt-satisfy-wcag-color-contrast-requirements)
- [MDN Color Contrast Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Guides/Understanding_WCAG/Perceivable/Color_contrast)

---

## Topic 4 — Sentiment-Specific Visualization Primitives

### Observation
Beyond our current line/donut/bar/radar set, specialized sentiment primitives exist that can communicate trend and distribution more efficiently for specific audiences. An exec-level CGO demo benefits from primitives that are immediately readable without explanation; analyst-level tools can afford denser encodings.

### Existing Approaches

**Diverging Bar Chart (positive/negative around zero baseline):** Bars extend in opposite directions from a center line, making the balance between positive and negative instantly legible. Heavily used in NPS trend visualization, Likert-scale surveys, and brand sentiment over time. The human eye detects symmetry/imbalance naturally — no legend reading required. Appropriate for exec audiences. Supported natively by Recharts `<BarChart layout="vertical">` with a `ReferenceLine` at x=0.

**Temporal Heatmap (time × aspect):** A grid where rows = aspects, columns = weeks/months, cells = color-encoded sentiment. Allows a CGO to see "what changed and when" across all aspects in a single glance. Our PlatformHeatmap is a spatial variant (platform × aspect); a temporal variant would be an aspect × time grid. Dense but readable for exec audiences when cells are well-colored. Recharts does not have a native heatmap but can approximate with a CSS Grid approach (which we already use for PlatformHeatmap).

**Horizon Chart:** An area chart "folded" into colored bands — negative space folds up, positive space uses deeper colors for higher values. Extremely space-efficient for comparing many time series simultaneously. CDC and Powerviz cite it for showing seasonal patterns and sudden changes. Research from "Sizing the Horizon" (CHI 2009) shows it can match area chart comprehension at 1/4 the vertical space. **Analyst-level** — requires a legend explanation and brief orientation.

**Sentiment Arc / Stream Graph:** Topic flow diagrams where stream width = mention volume, stream color = sentiment polarity. Best for showing how topic mix shifts over weeks. Analyst-level, high explanation overhead. Not recommended for exec demo context.

**Aspect Sunburst:** Hierarchical ring chart — outer ring = aspects, inner ring = sentiment distribution per aspect. Rich but requires interaction (hover/click) to read values. Analyst-level.

### Relevant to Our Stack
**Diverging bar chart** is the single highest-value primitive to add. It directly addresses the "Shark vs Dyson" comparative view in TopicExplorerPage and the aspect breakdown in ProductAnalysisPage — both currently use standard positive-only bars. Recharts supports this with zero new dependencies.

Preferred technique: replace the horizontal bar in the TopicExplorer comparison panel with a diverging bar (zero-baseline, Shark left = positive, Dyson right = negative or vice versa), and add a `ReferenceLine x={0}` to the ProductAnalysis aspect bars to show positive/negative split.

### Implementation Sketch (future round recommendation)
```tsx
// Diverging aspect bar — ProductAnalysisPage (future round)
<BarChart data={aspectData} layout="vertical">
  <ReferenceLine x={0} stroke={COLORS.border} />
  <XAxis type="number" domain={[-1, 1]} />
  <YAxis type="category" dataKey="aspect" />
  <Bar dataKey="avg_score" name="Sentiment">
    {aspectData.map((a, i) => (
      <Cell key={i} fill={a.avg_score >= 0 ? COLORS.positive : COLORS.negative} />
    ))}
  </Bar>
</BarChart>
```

### References
- [Tableau: How to Visualize Sentiment and Inclination](https://www.tableau.com/blog/how-visualize-sentiment-and-inclination-48534)
- [Domo: Divergent Bar Charts](https://www.domo.com/learn/charts/divergent-bar-charts)
- [CDC: Horizon Charts](https://www.cdc.gov/cove/data-visualization-types/horizon-charts.html)
- [Wiley: State of the Art in Sentiment Visualization (2018)](https://onlinelibrary.wiley.com/doi/full/10.1111/cgf.13217)

---

## Topic 5 — React Dashboard Performance Patterns

### Observation
Our bundle is 708 kB / 206 kB gzipped across 615 modules (mostly Recharts SVG + React). When the EvidenceDrilldown renders hundreds of mentions or the PlatformHeatmap scales to many aspects, scroll/render performance will degrade without mitigation. This documents what to apply before that happens.

### Existing Approaches

**List Virtualization — TanStack Virtual (recommended):** Framework-agnostic, modern architecture, lower memory footprint than react-window on rapid scrolls. Handles variable item heights natively. `@tanstack/react-virtual` v3 is the current standard. Gotcha: requires knowing or measuring item heights; dynamic heights need a `measureElement` callback. Best fit for our EvidenceDrilldown mention list.

**List Virtualization — react-window:** Lightweight, minimal API, best for fixed-height items. `FixedSizeList` for uniform mention cards is simpler to set up than TanStack Virtual. Less flexible for variable heights. Still maintained but lower momentum than TanStack in 2024-25.

**List Virtualization — react-virtuoso:** Highest-level API — handles dynamic heights, sticky headers, grouping automatically. Simpler integration than TanStack Virtual but larger bundle. Best if our mention list ever gets grouping (by date/platform).

**Recharts Memoization:** Recharts official performance guide recommends wrapping chart components in `React.memo` and stabilizing data/config props with `useMemo`/`useCallback`. Since Recharts renders to SVG, every prop change re-triggers a full SVG redraw. The specific pattern: separate the data transformation (`useMemo`) from the component render, and wrap the `<LineChart>` / `<BarChart>` container in `React.memo`. Estimated 50% reduction in initial load time when combined with lazy loading.

**Chart Lazy Loading:** `React.lazy` + `Suspense` + `react-intersection-observer` — load `<SentimentLineChart>` and `<AspectRadarChart>` only when their container enters the viewport. Defers heavy Recharts SVG work until needed. Especially relevant for ProductAnalysisPage which mounts 3 charts at once.

**Zustand Filter Store Re-renders:** Zustand's selector API prevents components from re-rendering on unrelated store slice changes. Our current pattern `useFilterStore((s) => s.brands)` is correct — only components that subscribe to `brands` re-render when brands changes. The risk is components calling `useFilterStore()` (no selector) which subscribes to the whole store.

### Relevant to Our Stack
Highest-leverage change: **TanStack Virtual for EvidenceDrilldown mention list** (< 50 lines of change, zero architectural disruption, unblocks scaling to thousands of mentions). Second: **`React.memo` on all 5 chart components** in `src/components/charts/` (5 one-line wraps + `useMemo` for the `data` prop in each parent page).

Preferred technique: TanStack Virtual for drilldown list + React.memo on charts. Both are additive changes with no component API changes.

### Implementation Sketch (future round recommendation)
```tsx
// EvidenceDrilldown — virtualized mention list
import { useVirtualizer } from '@tanstack/react-virtual';

const parentRef = useRef<HTMLDivElement>(null);
const rowVirtualizer = useVirtualizer({
  count: mentions.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 120, // approx MentionQuote height in px
});

return (
  <div ref={parentRef} style={{ flex: 1, overflow: 'auto' }}>
    <div style={{ height: rowVirtualizer.getTotalSize(), position: 'relative' }}>
      {rowVirtualizer.getVirtualItems().map((vItem) => (
        <div key={vItem.key} style={{ position: 'absolute', top: vItem.start, width: '100%' }}>
          <MentionQuote mention={mentions[vItem.index]} />
        </div>
      ))}
    </div>
  </div>
);

// Chart memoization — wrap each chart export
export const SentimentLineChart = React.memo(function SentimentLineChart(...) { ... });
```

### References
- [Recharts Performance Guide](https://recharts.github.io/en-US/guide/performance/)
- [TanStack Virtual List Virtualization](https://borstch.com/blog/development/list-virtualization-in-react-with-tanstack-virtual)
- [TanStack vs react-window Comparison](https://mashuktamim.medium.com/react-virtualization-showdown-tanstack-virtualizer-vs-react-window-for-sticky-table-grids-69b738b36a83)
- [Zigpoll: React Dashboard Performance for Large Datasets](https://www.zigpoll.com/content/how-can-i-optimize-the-responsiveness-and-performance-of-my-react-dashboard-when-rendering-large-datasets-with-dynamic-visualizations)

---

## Prioritized Reference Queue

Ranked by estimated relevance to the judge-facing demo scenario (exec-level SharkNinja CGO, live in-person dashboard walkthrough):

1. **Topic 3 — WCAG AA Audit** — Highest immediate risk. `textTertiary` (#556074) fails AA on both bg-surface and bg-base for normal text, and tertiary text is used on every chart axis and table header. A one-token change fixes it. A judge noticing illegible axis labels on a projected screen is an avoidable distraction. Complexity: trivial (1 line in theme/index.ts + verify with WebAIM).

2. **Topic 4 — Diverging Bar Chart** — Second-highest leverage. The Shark vs Dyson comparison in TopicExplorerPage currently uses side-by-side positive-only bars. A diverging bar (positive left, negative right of zero) would make the competitive differentiation story visually immediate for a CGO audience. Recharts supports this natively. Complexity: low (one chart component, no new dependencies).

3. **Topic 1 — Incumbent UX Tour** — Establishes that our Awareness → Insight → Evidence drill path matches or improves on Brandwatch/Sprout conventions. Confirms no glaring vocabulary gaps. No code action required — this is reference material for narrative polish.

4. **Topic 2 — Evidence Drilldown Patterns** — Confirms our non-modal side panel is the correct pattern (NNg-validated for passive "show me" interactions). The slide-in animation recommendation is a 10-line CSS addition that improves perceived polish meaningfully during a live demo. Complexity: trivial.

5. **Topic 5 — Performance Patterns** — Lower priority for the demo build (current fixture data is small). Becomes critical if demo switches to live CSV with thousands of mentions. TanStack Virtual + React.memo are both < 1 hour of implementation each but architectural impact is low-risk. Complexity: low-medium.
