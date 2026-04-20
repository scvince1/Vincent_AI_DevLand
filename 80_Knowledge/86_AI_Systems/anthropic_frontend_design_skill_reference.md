---
id: anthropic_frontend_design_skill_reference
title: Anthropic Claude Code frontend-design Skill Reference
tags: [ai-systems, meta, claude-code, frontend, skill-mechanics]
status: confirmed
last_modified: 2026-04-15
summary: Claude Code frontend-design skill 机制参考文档，含 CSS、dashboard、tooling
---
# Anthropic Claude Code — `frontend-design` Skill Reference

**Date captured:** 2026-04-11
**Tags:** claude-code, frontend, UI, skill-mechanics, CSS, dashboard, tooling-reference

---

## Summary

The `frontend-design` skill (part of the official `claude-plugins-official` plugin set for Claude Code) enforces a design-first, single-response workflow for building web components and pages. It commits to an aesthetic direction across four axes before generating any code, does not ask interactive clarifying questions, and produces code with CSS custom properties as the first-class styling mechanism. It has no native "existing project mode" — working within an established codebase requires explicit constraints in the invoking prompt. This document is a practical reference for using the skill in any Claude Code project, solo or team.

---

## Key Takeaways

- **Invocation:** Auto-triggers when task description matches "build web components, pages, or applications." For subagents / spawned teammates, call `Skill("frontend-design")` explicitly at task start — do not rely on auto-trigger in a team context.
  - Slash command equivalent: `/frontend-design Create a [description]`
  - No structured args — the natural-language task description IS the input.
- **Single-response workflow:** The skill does NOT generate a design brief document or ask follow-up questions. All design reasoning happens inline as prose before the code block. One response = aesthetic reasoning + working code.
- **The 4 design axes** (the skill commits to all four before touching code):
  1. *Purpose* — what problem the UI solves and who uses it
  2. *Tone* — commit to one extreme (e.g. "brutally minimal", "luxury-refined", "editorial-magazine", "industrial-utilitarian")
  3. *Constraints* — framework, performance, accessibility
  4. *Differentiation* — one memorable, unforgettable design decision
- **CSS-vars-first:** The skill natively writes `--color-*`, `--font-*`, `--spacing-*` CSS custom properties. Does NOT assume Tailwind or CSS-in-JS. Fully compatible with a pre-existing `theme.css` CSS variable system — as long as the prompt explicitly references it.
- **No "existing project mode":** The skill will NOT audit existing files autonomously before generating. Without explicit constraints, it may introduce CSS variables or design directions that conflict with established codebase conventions.
- **Motion default:** The skill pushes for CSS animations and scroll-triggered effects. For data dashboards, constrain motion to page-load stagger and hover states only — chart libraries (Recharts, Chart.js) control their own animation and must be themed separately via color variable props.

---

## 5-Step Sequence for Using in an Existing Project

1. **Invoke explicitly:** `Skill("frontend-design")` at task start.
2. **Read the existing theme first:** Pass the current CSS variable namespace as a constraint in the "Constraints" design axis. State: "Existing CSS variable system in use — extend only, do not replace."
3. **Infer existing tone:** Read 1-2 existing pages to determine the project's established design language. Include the inferred tone in the "Tone" axis to maintain consistency.
4. **Generate or modify components** using only existing CSS variables. Flag any new variables introduced for explicit approval before committing.
5. **Verify coherence** against existing pages before committing. Include the aesthetic direction statement in the commit message for team visibility.

---

## Known Limitations and Workarounds

| Limitation | Impact | Workaround |
|---|---|---|
| No existing-project audit mode | May diverge from established design system | Explicitly pass `theme.css` variable list + existing conventions in spawn prompt |
| No interactive Q&A phase | Risk of wrong design direction if task is ambiguous | Pre-answer all 4 design axes in the prompt |
| Motion library (Motion for React) assumed available | May generate JS motion code if library is absent | State in "Constraints": "CSS-only motion; no JS animation library available" |
| Chart library theming is separate | Recharts/Chart.js do not inherit CSS vars automatically | Engineer must apply color variables to chart component props manually |
| Skill behavior in teammate vs. solo context not documented | Auto-trigger may not fire in team spawns | Always use explicit `Skill("frontend-design")` call in teammate spawn prompts |

---

## Outputs Produced

- **Prose reasoning block:** Aesthetic direction commitment (tone + differentiation choice) stated before any code. This is reasoning, not a file artifact.
- **Code block(s):** Production-ready React/JSX, CSS with custom properties, or full HTML/CSS/JS. When running with file-write capability, the skill writes directly to component files.
- **No separate design artifacts:** No `design-tokens.json`, no palette file, no mood board. All aesthetic decisions are embedded in the generated code via CSS variables.

---

## Sources

Locally installed SKILL.md at `C:/Users/scvin/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`; GitHub repo `anthropics/claude-code`.
