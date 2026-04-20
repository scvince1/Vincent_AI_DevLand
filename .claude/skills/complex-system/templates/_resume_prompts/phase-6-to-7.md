# Resume Prompt · Step 6 → Step 7

You are continuing the `/complex-system` workflow in a fresh Claude session.

## What Step 6 did

`01_design/04_design-spec.md` locked. Vincent signed off.

## What Step 7 needs from you

Two-pass ticket decomposition, then handoff to Emdash.

### Pass 1 (single agent in this session)

1. Read `04_design-spec.md` + `03_data-constraints.md`.
2. Emit epic DAG as JSON to `04_tickets/_epics.json` per `~/.claude/skills/complex-system/prompts/ticket-executor.md` schema (5 to 10 epics, each with `epic_id`, title, summary, `depends_on_epics`, `estimated_ticket_count`, `spec_sections`).
3. Show the DAG to Vincent. Let him adjust.

### Pass 2 (N subagents in parallel)

1. Dispatch one sonnet subagent per epic (`Agent` tool, `subagent_type=general-purpose`, `model=sonnet`).
2. Each subagent expands its epic to concrete tickets in its pre-allocated ID range; writes ticket files to `04_tickets/<ticket_id>.md` per `templates/09_ticket.md` format.
3. Subagents also initialize V0 stubs of `05_frontend-spec_v0.md` and `06_backend-spec_v0.md` as they surface FE/BE needs.

### After Pass 2

1. Show Vincent the ticket list.
2. Let him edit ticket files directly if needed.
3. Tell Vincent to run: `python ~/.claude/skills/complex-system/pipeline/push_tickets.py <BUILD_REPO_PATH>` when ready to push to GitHub.
4. Skill ends. Emdash takes over execution.

## Constraints

- Do not push to GitHub in this session (Vincent triggers the pipeline manually).
- Do not spawn Emdash tasks in this session (Vincent does that in Emdash UI).
- Tickets must have complete `## Agent Prompt` sections (self-contained, no "as we discussed" references).
- English only.

## Build repo

`<BUILD_REPO_PATH>`
