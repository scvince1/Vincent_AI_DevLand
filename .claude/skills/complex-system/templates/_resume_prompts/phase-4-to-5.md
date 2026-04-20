# Resume Prompt · Step 4 → Step 5

You are continuing the `/complex-system` workflow in a fresh Claude session.

## What Step 4 did

`01_design/02_review-notes.md` locked. Socratic transcript and Vincent's 5-bullet "What I now understand" committed.

## What Step 5 needs from you

Step 5 is **Data Constraint Scoping** and it **gates Step 6**. No design spec work until this is locked.

1. Open / create `01_design/03_data-constraints.md` (copy from `~/.claude/skills/complex-system/templates/03_data-constraints.md`).
2. With Vincent, enumerate every data source the product might need. One row per source in the inventory table. Populate Obtainable / Cost / Latency / Legal.
3. For every Partial or N, explain briefly in Notes.
4. Co-write Design Constraint Summary (In scope / Out of scope / Deferred).
5. When Vincent locks the Summary, emit `_resume_prompts/phase-5-to-6.md` and stop.

## Critical rule

Step 6 does not start in this session. Even if Vincent is eager. The summary must be committed to the build repo first.

## Build repo

`<BUILD_REPO_PATH>`
