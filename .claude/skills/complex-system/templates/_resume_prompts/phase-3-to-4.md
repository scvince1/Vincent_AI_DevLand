# Resume Prompt · Step 3 → Step 4

You are continuing the `/complex-system` workflow in a fresh Claude session.

## What Step 3 did

`00_research/01_research-brief.md` is locked. Audience Understanding Summary (5 bullets) confirmed by Vincent. Interview section either filled (3 to 5 interviews) or marked skipped.

## What Step 4 needs from you

Step 4 is **Review / Socratic**. It **must run in the main session, interactively with Vincent**. Do not delegate to a subagent.

1. Load the Socratic engine: read `~/.claude/skills/complex-system/prompts/socratic-review.md` and follow its discipline.
2. Anchor on the 5-bullet summary. Ask Vincent if he wants to pull in external KB (`--kb-path`) for the session.
3. Run a deep Socratic conversation (3 to 5 lineages, Q → A → reframe). Write transcript to `01_design/02_review-notes.md`.
4. Vincent writes "What I now understand (5 bullets)" at the end.
5. When locked, emit `_resume_prompts/phase-4-to-5.md` and stop.

## Constraints

- Engine rigor matches `socratic-learning` skill (deep probing, assumption challenge).
- KB citation optional (default: project's `00_research/`). External KB only if Vincent passes `--kb-path`.
- Do not auto-answer for Vincent.
- English only.

## Build repo

`<BUILD_REPO_PATH>`
