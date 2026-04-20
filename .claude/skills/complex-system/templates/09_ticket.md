---
ticket_id: <PHASE>-<VERSION>-<ID>
title: <short imperative title>
phase: frontend | backend | research | review | data | design
version: V1.0
status: draft | ready | in-progress | done
depends_on: []
spec_refs:
  - ../01_design/04_design-spec.md
created: YYYY-MM-DD
issue_number: null
appended_prompt: null
---

# Ticket <ticket_id>: <title>

## Context

What system is this part of? Why does this ticket exist? Include only the context a fresh worker needs; do not duplicate the full design spec.

## Objective

One sentence. What does DONE look like?

## Acceptance Criteria

- [ ] Concrete check 1
- [ ] Concrete check 2

## Inputs (files to read before starting)

- path/to/design-spec.md
- path/to/frontend-spec_vN.md (or backend-spec)
- path/to/mock-data.json (or real data reference)

## Outputs (files to create or modify)

- path/to/new-component.tsx
- path/to/updated-page.html

## Technical Notes

Anything the worker needs: library versions, mock data shape, edge cases, performance constraints.

---

## Agent Prompt

<!-- This section is the worker's behavioral contract. It becomes the body of the GitHub issue the worker reads via `gh issue view`. Keep it self-contained: no "as we discussed" references. -->

You are the worker executing ticket <ticket_id>. Your entire context is this issue body.

Steps (in order):

1. Read every file under `Inputs` above.
2. If `depends_on` lists ticket IDs and the blocker issues are not yet closed, check `git branch -a` for upstream branches (e.g., `emdash/<slug>-<N>`). Run `git fetch origin` if needed, then `git merge` each blocker's branch into your working branch.
3. Plan the minimal change that satisfies every Acceptance Criteria checkbox.
4. Implement. Write only to paths listed under `Outputs`. If you notice unrelated issues, note them in your final report but do not fix them.
5. Verify: for each acceptance criterion, state how you confirmed it.
6. Commit with message `<ticket_id>: <short summary>`.
7. Push the branch.
8. Open a PR against `main` with title `<ticket_id> <short title>` and body including `Closes #<issue_number>` so the issue auto-closes on merge.
9. Report DONE with a diff summary.

Constraints:

- English only (code, comments, commit messages, PR body).
- Do not invoke any skills. Use `gh` and `git` CLI directly.
- Do not expand scope. Ambiguous criteria → ask before acting.
- Do not refactor unrelated code.

Stop conditions:

- All acceptance checkboxes satisfied → report DONE.
- Blocker you cannot resolve → report BLOCKED with the specific question.
