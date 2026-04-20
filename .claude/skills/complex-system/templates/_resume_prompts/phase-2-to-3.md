# Resume Prompt · Step 2 → Step 3

You are continuing the `/complex-system` workflow in a fresh Claude session.

## What Step 2 did

AI-Deep Research section of `01_research-brief.md` is filled. Parallel subagents contributed structured findings, synthesized into the document.

## What Step 3 needs from you

Step 3 is **optional but strongly recommended**: 3 to 5 live interviews with people in the target domain.

1. Read Self-Research and AI-Deep Research sections.
2. Ask Vincent: "Did you do any live interviews? If yes, let's capture them. If no, do you want to skip to Step 4?"
3. If YES:
   - Per interview, fill three fields: subject, questions asked, takeaways.
   - After interviews, help Vincent write the 5-bullet Audience Understanding Summary synthesizing Steps 1-3.
4. If SKIP:
   - Help Vincent write the 5-bullet summary from Steps 1-2 only. Flag it as "no interview grounding."
5. When the summary is locked, emit `_resume_prompts/phase-3-to-4.md` and stop.

## Constraints

- Interview content is Vincent's own from his conversations. Do not fabricate.
- Summary is exactly 5 bullets, describes the audience, not the product.
- English only.

## Build repo

`<BUILD_REPO_PATH>`
