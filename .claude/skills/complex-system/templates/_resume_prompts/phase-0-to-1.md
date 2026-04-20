# Resume Prompt · Step 0 → Step 1

You are continuing the `/complex-system` workflow in a fresh Claude session.

## What Step 0 did

- Created private GitHub repo: `<PROJECT_NAME>`
- Cloned locally to: `<BUILD_REPO_PATH>`
- Initialized skeleton dirs: `00_research/ 01_design/ 02_frontend/ 03_backend/ 04_tickets/ 05_previews/ _resume_prompts/`
- Wrote `CLAUDE.md` (with `@~/.claude/meowos-core-for-tickets.md` import)
- Wrote `.gitignore` (includes `.claude/`)
- Initial commit pushed to `origin main`

## What Step 1 needs from you (this session)

You are the main session for Step 1 Self-Research. Vincent shares his own rough investigation.

1. Open or create `00_research/01_research-brief.md` (copy from `~/.claude/skills/complex-system/templates/01_research-brief.md` if missing).
2. As Vincent shares findings, help him organize them under the Self-Research section. No AI-generated content here; this section is Vincent's own material.
3. When Vincent signals Step 1 done, emit `_resume_prompts/phase-1-to-2.md` (copy template from skill and fill in the summary blanks) and stop.

## Constraints

- English only.
- Do not start Step 2 in this session (AI-Deep research is a separate session with subagents).
- File I/O via `shell-runner` subagent per MeowOS rule.

## Build repo

`<BUILD_REPO_PATH>`
