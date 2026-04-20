# What-If Simulator Visual Conventions — R4 Prep

**Written:** 2026-04-11  
**Agent:** frontend-engineer-v4  
**Purpose:** Pre-commit design document for the Aaru What-If Simulator panel (R4-P1-2). Written before any component code, per charter §5 protocol. SendMessage team-lead when complete.

---

## 1. Context and Tone

The simulator is fundamentally different from the rest of the dashboard. Every other page displays *observed* data. The simulator generates *hypothetical* reactions — it is a thinking tool, not a measurement tool.

**Design implication:** The simulator panel must visually signal "this is speculative territory" without undermining the usefulness of the output. The pattern here is analogous to forecast_visual_conventions.md's handling of forecast uncertainty: degrade visually (amber, italic, reduced opacity) rather than hide or alarm.

**Placement:** On `ProductAnalysisPage`, below the Trend Forecast panel. Co-location with the product-level forecast is intentional — the simulator is a "what if we made a change" companion to "here is where we're trending." Same product context, different time orientation (retrospective consumer mentions → forward scenario modeling).

---

## 2. Input Form

**Layout:** Full-width text area at the top of the panel card.

- Label: "What if..." in `.section-label` style (11px, uppercase, tracked)
- Textarea: Large, 3 rows minimum, expands with content. Placeholder: "What if Shark launched a $99 budget version targeting renters?"
- Character limit hint below textarea: "Be specific — simulations are grounded in real consumer mentions for the selected product."
- Submit button: `.btn .btn-primary` — label "Simulate reaction"
- Disabled state: button disabled while a simulation is running (`.btn:disabled` opacity 0.4, pointer-events none)

**Form styling:**
- Textarea: `background: var(--bg-surface-raised)`, `border: 1px solid var(--border)`, `border-radius: var(--radius)`, `color: var(--text-primary)`, `font-family: inherit`, `font-size: 13px`, `padding: 10px 12px`, `resize: vertical`
- Focus: `outline: 2px solid var(--accent)` (global :focus-visible rule already handles this)
- No inline `@media` — textarea width is 100% within the card, responsive by default

---

## 3. Loading State

The loading state is the highest-stakes UX moment: the user just submitted a scenario and is waiting. It must communicate that something real is happening.

**Loading copy (not just "Loading..."):**
"Running simulation on {N} real consumer mentions..."

Where N is the `input_mention_count` from the most recent product context. If unknown, use "real consumer mentions" without a number.

**Visual:**
- Skeleton blocks replace the results area (`.skeleton` class, `skeleton-pulse` animation)
- 3 skeleton cards (approximating the 3-5 segment output) at ~80px height each
- Loading copy rendered above skeletons in `.section-label` style with a subtle pulsing text

**Timeout state (30s limit per backend spec):**
- Replace skeletons with a friendly error: "Simulation timed out — the model took too long to respond."
- Retry button: `.btn .btn-ghost` — "Try again"
- This is an error state, not an empty state. Use `.error-state` class styling.

---

## 4. Disclaimer Banner

The `overall_disclaimer` field from the API will always contain:
`"Simulated reaction based on LLM heuristic, not empirical behavior modeling."`

**This text must be displayed verbatim.** Do NOT paraphrase, truncate, or hide it behind a toggle.

**Banner design:**
- Positioned at the TOP of the results area (above segment cards), not at the bottom
- Amber `--color-caution` left border accent (4px solid)
- Italic text, `font-size: 12px`, `color: var(--text-secondary)`
- Background: `rgba(245, 166, 35, 0.06)` — very subtle amber wash
- Padding: `10px 14px`
- Border-radius: `var(--radius-sm)`
- No close/dismiss button — it is always visible when results are shown

```tsx
// Visual reference
<div style={{
  borderLeft: '4px solid var(--color-caution)',
  background: 'rgba(245, 166, 35, 0.06)',
  borderRadius: 'var(--radius-sm)',
  padding: '10px 14px',
  marginBottom: 16,
}}>
  <p style={{ margin: 0, fontSize: 12, fontStyle: 'italic', color: 'var(--text-secondary)' }}>
    {result.overall_disclaimer}
  </p>
</div>
```

---

## 5. Segment Cards

Each `SimulatedSegment` object renders as a card. 3-5 cards per simulation result.

**Card anatomy:**

| Element | Design |
|---|---|
| Segment label | `.section-label` style header at top of card |
| Polarity badge | Pill badge using existing semantic colors |
| Confidence narrative | Body text `font-size: 13px`, `color: var(--text-secondary)` |
| "View quotes" expander | Collapse/expand — shows `key_quotes_used[]` |

**Polarity badge colors (reuse existing tokens):**
- `positive` → `--positive` (#3ecf8e) green
- `negative` → `--negative` (#f05252) red
- `neutral` → `--neutral` (#f0b429) amber
- `mixed` → `--mixed` (#a78bfa) purple

Badge design: pill shape (`border-radius: 999px`), `font-size: 11px`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 0.8px`, `padding: 2px 8px`. Background is `{color}22` (low-opacity fill), text is `{color}` (full).

**"View quotes" expander:**
- Collapsed by default (quotes are secondary evidence, not primary signal)
- Expand button: `.btn .btn-ghost` small — "Show quotes ({N})"
- Collapsed → Expanded reveals a styled blockquote list of `key_quotes_used`
- Each quote: `borderLeft: 3px solid var(--border)`, `paddingLeft: 10px`, italic, 12px, `--text-secondary`
- No animation required — simple conditional render

**Card layout:** `.section-card` class, gap between cards 12px via parent flex column.

---

## 6. Results Layout

```
[Disclaimer banner — amber, italic]
[Segment card 1: Mainstream consumers — POSITIVE]
[Segment card 2: Budget-conscious shoppers — MIXED]
[Segment card 3: Existing Shark owners — NEGATIVE]
...
```

Cards render in the order returned by the API (backend determines segment ordering).

**Model metadata:** Below the segment cards, a subtle footer line:
`Model: {model_used} · {tokens_consumed} tokens` — `font-size: 11px`, `color: var(--text-tertiary)`

---

## 7. Empty and Error States

| State | Treatment |
|---|---|
| No result yet (pre-submit) | Show only the input form; no empty state card |
| Loading | Skeleton + loading copy (see §3) |
| Timeout / API error | `.error-state` class, friendly message, retry button |
| Zero segments returned | Empty state: "No segments returned — try a more specific scenario." |

---

## 8. Motion

Per v3 design protocol constraints (no animation on chart elements):
- No animation on segment cards themselves
- Loading skeleton uses existing `skeleton-pulse` animation only
- Expand/collapse of quotes section: instant (no CSS transition needed for an expander list)

---

## 9. Responsive

All layout uses existing CSS classes from `theme.css`:
- Simulator panel is full-width (no grid needed — single column)
- Textarea is `width: 100%` within `.section-card`
- Segment cards stack vertically — already natural flex column at all widths
- No new `@media` queries needed

---

## 10. New CSS Tokens Required

None. All required tokens already exist or were added in R4-P0-1:
- `--color-caution: #F5A623` (added for forecast low-confidence badge)
- Polarity colors: `--positive`, `--negative`, `--neutral`, `--mixed` (existing)
- `--bg-surface-raised` for textarea background (existing)

No new variables to propose to team-lead.

---

*Word count: ~870.*
