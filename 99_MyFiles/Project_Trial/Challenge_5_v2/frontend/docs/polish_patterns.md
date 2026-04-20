# Frontend Polish Patterns — Round 2 Research
_Date: 2026-04-11 | Topics: micro-interactions, keyboard/focus management, bundle splitting, TypeScript strictness_

---

## Topic 1: Micro-interactions & Animation

**Problem:** Dashboard transitions (panel slide-in, filter changes, chart updates) feel abrupt with no motion feedback.

**State of the art:**
- Keep animations under 300ms; ease-out easing feels snappiest for exit/enter
- Framer Motion provides spring physics (`useSpring`, `AnimatePresence`) with minimal bundle cost (~35 KB gzip)
- For simple cases (EvidenceDrilldown panel slide-in), a CSS transition `transform: translateX(100%) → 0` with `transition: transform 280ms ease-out` is sufficient — no library needed
- Always guard with `@media (prefers-reduced-motion: reduce)` — set `transition-duration: 0.01ms` inside that query

**Constraint-compatible option:** CSS transitions for the panel; Framer Motion only if chart mount animations are needed later.

**Implementation sketch:**
```css
.evidence-panel {
  transform: translateX(100%);
  transition: transform 280ms ease-out;
}
.evidence-panel.open {
  transform: translateX(0);
}
@media (prefers-reduced-motion: reduce) {
  .evidence-panel { transition-duration: 0.01ms; }
}
```

**Implementation recommendation for round 3.**

---

## Topic 2: Keyboard Navigation & Focus Management (EvidenceDrilldown)

**Problem:** EvidenceDrilldown panel opens on click but has no keyboard support — violates WCAG 2.1.2 (no keyboard trap), 2.4.3 (focus order), 2.4.7 (focus visible).

**State of the art:**
- Panel must have `role="dialog"` and `aria-modal="true"`
- On open: move focus to first focusable element inside panel (close button or heading)
- Focus trap: Tab/Shift+Tab cycle within panel only while open; Escape closes and returns focus to trigger element
- Options: `focus-trap-react` (4 KB gzip, zero deps), native `<dialog>` element (browser-native focus trap, but styling is more constrained), or hand-roll with `querySelectorAll(focusableSelectors)` + keydown handler

**Constraint-compatible option:** `focus-trap-react` — drop-in wrapping `<FocusTrap active={isOpen}>` around panel contents. Escape handling is built-in.

**Implementation sketch:**
```tsx
import FocusTrap from 'focus-trap-react';

<FocusTrap active={isOpen} focusTrapOptions={{ onDeactivate: onClose }}>
  <aside role="dialog" aria-modal="true" aria-label="Evidence Drilldown">
    <button onClick={onClose}>Close</button>
    {/* panel content */}
  </aside>
</FocusTrap>
```

**Priority: HIGH** — this is a WCAG blocker. Recommend for round 3.

---

## Topic 3: Vite Bundle Splitting

**Problem:** All vendor JS (React, Recharts, Zustand, react-router-dom) ships in one chunk. Initial load is heavier than needed.

**State of the art:**
- Vite `build.rollupOptions.output.manualChunks` groups heavy deps: put `recharts`, `d3-*` into a `chart-vendor` chunk; `react`, `react-dom`, `react-router-dom` into `react-vendor`
- `React.lazy` + `Suspense` for route-level code splitting — each page becomes a separate async chunk, typically cuts initial JS by ~35-40%
- **Note:** Vite v7+ (Rolldown) deprecates `manualChunks` in favor of `build.rollupOptions.output.advancedChunks` — migration path is straightforward but not yet stable

**Implementation sketch (vite.config.ts):**
```ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'react-vendor': ['react', 'react-dom', 'react-router-dom'],
        'chart-vendor': ['recharts'],
        'state-vendor': ['zustand'],
      },
    },
  },
},
```

**Route lazy loading (App.tsx):**
```tsx
const OverviewPage = React.lazy(() => import('./pages/OverviewPage'));
// wrap routes in <Suspense fallback={<LoadingSpinner />}>
```

**Implementation recommendation for round 3.**

---

## Topic 4: TypeScript Strictness Ratcheting

**Problem:** `tsconfig.app.json` has `strict: true` but several additional flags that catch real bugs are not enabled. Adding them all at once would generate too many errors to fix in one pass.

**State of the art:**
- `strict: true` already enables `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`
- High-value additional flags: `noUncheckedIndexedAccess` (array/object index access returns `T | undefined`), `exactOptionalPropertyTypes` (prevents assigning `undefined` to optional props), `verbatimModuleSyntax` (enforces `import type` for type-only imports — avoids runtime import side-effects)
- Ratcheting approach: `@betterer/typescript` snapshots current error count and fails CI if count increases — allows incremental adoption without a big-bang fix

**Constraint-compatible option:** Enable `verbatimModuleSyntax` immediately (zero new errors expected given existing `import type` usage). Add `noUncheckedIndexedAccess` in a separate commit with targeted `// @ts-expect-error` annotations where array access patterns are known-safe.

**Implementation sketch (tsconfig.app.json addition):**
```json
{
  "compilerOptions": {
    "verbatimModuleSyntax": true,
    "noUncheckedIndexedAccess": true
  }
}
```

**Implementation recommendation for round 3** — verify zero new errors before committing.

---

## Priority Ranking

| Priority | Topic | Effort | Impact |
|---|---|---|---|
| 1 | Keyboard/Focus (WCAG blocker) | Low (focus-trap-react drop-in) | High — accessibility requirement |
| 2 | Bundle splitting | Low-Medium | Medium — ~35% initial JS reduction |
| 3 | TypeScript strictness | Low | Medium — prevents future runtime bugs |
| 4 | Micro-interactions | Medium | Low-Medium — polish, not correctness |
