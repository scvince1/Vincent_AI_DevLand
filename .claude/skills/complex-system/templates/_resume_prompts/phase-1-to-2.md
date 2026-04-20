# Resume Prompt · Step 1 → Step 2

You are continuing the `/complex-system` workflow in a fresh Claude session.

## What Step 1 did

Vincent's Self-Research section of `00_research/01_research-brief.md` is filled. Key findings:

- <filled in by Step 1 session before emitting this prompt>

## What Step 2 needs from you

AI-Deep Research via parallel sonnet subagents.

1. Read `00_research/01_research-brief.md` Self-Research section.
2. Identify 2 to 4 research angles not covered by Vincent's own research, or that need deeper dives.
3. Dispatch one sonnet subagent per angle (`Agent` tool, `subagent_type=general-purpose`, `model=sonnet`, parallel in one message). Each subagent: deep dive + structured findings under 400 words + cited sources.
4. When all subagents return, synthesize findings into the AI-Deep Research section of `01_research-brief.md`. Summarize; do not dump raw.
5. When Vincent confirms the AI-Deep section, emit `_resume_prompts/phase-2-to-3.md` and stop.

## Constraints

- Do not modify Self-Research section.
- No KB writes to MeowOS; artifacts stay in the build repo.
- English only.

## Build repo

`<BUILD_REPO_PATH>`
