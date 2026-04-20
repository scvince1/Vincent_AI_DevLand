# frontend-design Skill — operational reference for team-lead

> Researched: 2026-04-11  
> Source: locally installed SKILL.md at `C:/Users/scvin/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`, GitHub repo `anthropics/claude-code`, and web sources.  
> Plugin status: `frontend-design@claude-plugins-official` — user scope, enabled.

---

## Invocation

**Auto-invocation (primary path):** The skill's YAML frontmatter description is `"Use this skill when the user asks to build web components, pages, or applications."` Claude Code's harness auto-loads it when that condition matches. No explicit `Skill()` call required in most sessions.

**Explicit invocation (guaranteed path for subagents/teammates):**

```
Skill("frontend-design")
```

No positional args are defined. The skill accepts no structured input object — the user's (or agent's) natural-language task description IS the input. There is no `args` field in the SKILL.md frontmatter beyond `name` and `description`.

**Slash command equivalent (terminal/REPL):**
```
/frontend-design Create a [description of what to build]
```

**For a spawned teammate:** Because auto-invocation depends on the harness reading the task description, the safest pattern in a spawn prompt is to instruct `frontend-engineer-v3` to call `Skill("frontend-design")` explicitly at the start of any UI/component generation task, before writing a single line of code.

---

## Workflow enforced

The skill enforces a **design-first, then code** sequence. It does NOT ask interactive questions or generate a separate design brief document — all design thinking happens inline as reasoning before code output.

**Step-by-step procedural flow (per SKILL.md):**

1. **Read the task context.** Understand the component/page/application being built: purpose, audience, technical constraints.
2. **Commit to a BOLD aesthetic direction** across four axes before touching code:
   - *Purpose* — what problem the UI solves and who uses it
   - *Tone* — choose one extreme (brutally minimal / maximalist chaos / retro-futuristic / organic-natural / luxury-refined / playful-toy-like / editorial-magazine / brutalist-raw / art deco-geometric / soft-pastel / industrial-utilitarian, etc.)
   - *Constraints* — framework, performance, accessibility requirements
   - *Differentiation* — one memorable, unforgettable design decision
3. **Match implementation complexity to the chosen aesthetic** (maximalist vision = elaborate animations and effects; minimalist vision = precision spacing and typography restraint).
4. **Generate production code** (HTML/CSS/JS, React, Vue) that is functional, visually striking, cohesive, and meticulous in every detail.

The skill does NOT generate a separate mood board, color palette file, or design token document as an artifact. Design direction is expressed as reasoning prose followed by the code itself.

---

## Outputs produced

- **Chat prose:** The aesthetic direction commitment (tone, differentiation) stated before the code block. This is reasoning, not a file.
- **Code block(s):** Working production code — React/JSX, CSS with CSS custom properties, or full HTML/CSS/JS as appropriate. The skill writes to the component files directly when operating in an agent context with file-write capability.
- **No separate design artifact files** are produced by the skill itself (no `design-tokens.json`, no `palette.md`, no mood board). All aesthetic decisions are embedded in the generated code via CSS variables.

---

## CSS framework compatibility

**Native approach: CSS custom properties (variables).** The SKILL.md explicitly instructs: *"Use CSS variables for consistency"* under Color & Theme. This is the skill's first-class mechanism — not Tailwind, not styled-components.

**Compatibility verdict for our stack (`theme/theme.css` with CSS variables): FULLY COMPATIBLE.**

- The skill will naturally write `--color-*`, `--font-*`, `--spacing-*` style properties.
- It does NOT assume Tailwind utility classes or impose a CSS-in-JS system.
- When instructed to respect an existing `theme.css`, it will reference those variables rather than invent new ones — as long as the spawn prompt explicitly points to the file.

**Tailwind note:** The skill is framework-agnostic. If the project uses Tailwind, state that in the task. If the project uses CSS vars, state that. The skill adapts to the stated constraint axis.

---

## Fresh vs existing project behavior

**The skill has no explicit "existing project mode."** Its SKILL.md contains no branching logic for fresh vs. existing codebases. All instructions are oriented toward *generating* new components.

**Practical implications for a project with 5 pages and 20+ components:**

- The skill will NOT automatically audit existing files before generating.
- If invoked naively, it may produce a new design direction that diverges from established conventions in the codebase.
- It will NOT attempt a wholesale rewrite unless the task description asks for one.
- **Risk:** Without explicit constraints in the prompt, the skill may introduce new fonts, new color schemes, or new CSS variables that conflict with `theme.css`.

**Mitigation (critical for spawn prompt):** The spawn prompt for `frontend-engineer-v3` must explicitly pass:
1. The existing CSS variable namespace from `theme/theme.css`
2. The established component conventions
3. An instruction like: *"Do not introduce new CSS variables not already in theme.css. Extend, do not replace."*

---

## Recommended sequence for frontend-engineer-v3

1. **Invoke the skill explicitly** at task start: `Skill("frontend-design")` — do not rely on auto-trigger in a teammate context.
2. **Read `theme/theme.css` first** and pass its variable list as a constraint in the design thinking phase under "Constraints." State: "Existing CSS variable system in use — extend only, do not replace."
3. **Commit to an aesthetic direction** that is consistent with the existing project's established tone (read 1-2 existing pages first to infer the current design language). State the tone and differentiation choice as a reasoning block before any code.
4. **Generate or modify components** using the committed aesthetic direction, referencing only existing CSS variables except where explicitly approved to add new ones.
5. **Apply motion selectively** — the skill pushes for CSS animations and scroll-triggers; for a data dashboard with Recharts, constrain motion to page-load stagger and hover states only, not chart animations (which Recharts controls).
6. **Verify visual coherence** against existing pages before committing — do a diff of any new CSS variables introduced and flag them back to the orchestrator for approval.
7. **Commit** only after coherence check passes; include the aesthetic direction statement in the commit message or PR description for team visibility.

---

## Unknowns / risks

| Item | Status | Impact |
|---|---|---|
| Whether `Skill("frontend-design")` with no args auto-passes the current task context, or requires the task description as an arg | Unverified from SKILL.md alone — SKILL.md has no `args` schema, but harness behavior is undocumented | Medium: spawn prompt should include task in the natural-language instruction, not as a Skill arg |
| Whether the skill reads existing files autonomously before designing | Not stated in SKILL.md; presumed NO | High: must explicitly pass existing theme context in spawn prompt |
| Motion library ("Motion for React") availability in the project | Not verified | Low: skill falls back to CSS-only if Motion is absent |
| Recharts aesthetic integration | Skill is unaware of Recharts; chart theming is separate | Medium: engineer must apply color variables to Recharts `<CartesianGrid>` and axis props manually |
| Whether skill behaves differently inside a Claude Code team (teammate) context vs. solo session | Not documented | Medium: explicit `Skill("frontend-design")` call is safer than relying on auto-trigger |
| No interactive design brief / Q&A phase | Confirmed absence | Low risk if spawn prompt pre-answers the four design axes (Purpose, Tone, Constraints, Differentiation) |
