---
name: complex-system
description: "[SLASH-ONLY. DO NOT AUTO-INVOKE.] Methodology scaffold for building a non-trivial system end-to-end. Runs Step 0 GitHub repo bootstrap, Step 1 self-research, Step 2 AI-deep research via parallel subagents, Step 3 live interviews (optional), Step 4 Socratic review in main session, Step 5 data constraint scoping (gate for Step 6), Step 6 simplified design spec, Step 7 parallel frontend + backend build with two-pass ticket decomposition. Emits self-contained ticket markdowns that become GitHub issues via a Python pipeline, then executed by Emdash workers in git worktrees. Runs ONLY when Vincent types the literal slash command /complex-system. Do NOT match on keywords like 'complex system', 'build a system', 'design doc', 'architecture', 'ticket', 'frontend', 'backend'. These are far too generic and produced false positives that required the earlier spec-to-dev-tickets skill to be disabled."
---

# Complex System

> **SLASH-ONLY.** Do not auto-invoke. Runs only when Vincent explicitly types `/complex-system`.
> All artifacts produced by this skill are in **English**, regardless of conversation language.

## Purpose

Process scaffold for building a non-trivial system end-to-end. Skill owns Step 0 through Step 6 plus ticket generation in Step 7. Step 7 execution is delegated to Emdash, which spawns `claude` CLI workers in git worktrees. Keeps the architect session in MeowOS light while workers do isolated code work.

## First action on invocation

Ask Vincent:

1. Project name (used for the GitHub build repo name and local workspace dir)
2. Workspace root path (where to clone the build repo locally; default: current working directory)
3. Current phase (fresh start, or resuming from Step N)

Then proceed to Step 0 if fresh, or the indicated step if resuming. If resuming, Vincent pastes in the previous phase's `_resume_prompts/phase-<N-1>-to-<N>.md` content.

## Workflow

| Step | Name | Where | Template / Prompt | Output |
|---|---|---|---|---|
| 0 | GitHub Repo Bootstrap | main session | `templates/CLAUDE.md.template`, `templates/gitignore.template` | Private repo + skeleton + lightweight CLAUDE.md |
| 1 | Self-Research | main session | `templates/01_research-brief.md` | Self-Research section |
| 2 | AI-Deep Research | parallel sonnet subagents | `templates/01_research-brief.md` | AI-Deep section |
| 3 | Live Interviews (optional) | main session | `templates/01_research-brief.md` | Interviews section + 5-bullet audience summary |
| 4 | **Review / Socratic (must be main session, interactive)** | main session | `templates/02_review-notes.md`, `prompts/socratic-review.md` | Review notes |
| 5 | Data Constraint Scoping (**gates Step 6**) | main session | `templates/03_data-constraints.md` | Design Constraint Summary |
| 6 | Simplified Design Spec (no length limit) | main session | `templates/04_design-spec.md` | Short design doc |
| 7 | Parallel FE + BE Build (ticket emission only) | two-pass subagents | `prompts/ticket-executor.md`, `templates/09_ticket.md` | `04_tickets/*.md` files |

## Step 7 sub-steps (parallel lanes, FE half a beat ahead of BE)

**7.F Frontend** (template `05_frontend-spec.md`, plan `07_ui-version-plan.md`):

| # | Output |
|---|---|
| F1 | Components / pages / nav inventory + mock data contract |
| F2 | UI V0 wireframe + first HTML preview (mock data driven) |
| F3 | V0.x iteration → V1 lock (features frozen) |
| F4 | V1.x polish → V2 pre-launch |

**7.B Backend** (template `06_backend-spec.md`, plan `08_backend-version-plan.md`):

| # | Output |
|---|---|
| B1 | Data model + method shape (aligned with FE mock contract) |
| B2 | Synthetic dataset V0 (approximately resembles real data) |
| B3 | V0.x method increments → V1 real-data integration |
| B4 | V1.x perf / batching → V2 production hardening |

## Step 7 two-pass decomposition

When Vincent reaches Step 7, skill runs:

1. **Pass 1** (single agent): read `04_design-spec.md` + `03_data-constraints.md`, emit epic-DAG JSON listing 5 to 10 epics with `epic_id`, title, dependency edges, estimated ticket count, spec sections referenced.
2. **Pass 2** (N agents in parallel, one per epic): each subagent expands its epic into concrete tickets, writing to a pre-allocated `ticket_id_start / ticket_id_end` range to avoid ID collisions. Emits `04_tickets/<ticket_id>.md` files.

Prompts for both passes are in `prompts/ticket-executor.md`. Pass 2 is the primary parallelization path; do not attempt to parallelize Pass 1.

## Ticket pipeline (push to GitHub)

After Step 7, skill tells Vincent to run:

```
python ~/.claude/skills/complex-system/pipeline/push_tickets.py <build-repo-path>
```

The pipeline is DAG-aware, idempotent (writes `issue_number` back into each ticket frontmatter), and manual-only (no auto-push on ticket emission). See `pipeline/README.md`.

## Naming convention (cross-system traceability)

`ticket_id` format: `<PHASE>-<VERSION>-<ID>`. Example: `FE-V1-003`, `BE-V0-001`, `RES-V0-A`.

The same `ticket_id` appears in:

| Location | Format | Example |
|---|---|---|
| ticket.md filename | `<ticket_id>.md` | `04_tickets/FE-V1-003.md` |
| GitHub issue title | `[<ticket_id>] <Title>` | `[FE-V1-003] Add navbar` |
| Emdash Task name (user types) | `<ticket_id> <Title>` | `FE-V1-003 Add navbar` |
| Git branch (Emdash auto-generates) | `emdash/<slug>-<rand>` | `emdash/fe-v1-003-add-navbar-a3f` |
| Commit message | `<ticket_id>: <summary>` | `FE-V1-003: add nav component` |
| PR title | `<ticket_id> <title>` | `FE-V1-003 Add navbar` |

**Critical**: at Emdash `+ New Task`, type `<ticket_id> <Title>` into the "Task name" field. Do not leave it blank (Emdash auto-generates a random name and breaks traceability).

## Phase handoff

At the end of each phase, skill emits `<build-repo>/_resume_prompts/phase-<N>-to-<N+1>.md` summarizing: what was decided, what the next phase should read, open questions. Vincent opens a fresh Claude session and pastes it in to continue.

Templates are in `templates/_resume_prompts/`.

## Emdash configuration (one-time per machine, covered in Step 0)

| Setting | Value | Where in Emdash |
|---|---|---|
| Integrations > GitHub | Connected (OAuth: emdash + Emdash Server) | Settings > Integrations > GitHub |
| Repository > Auto-push to origin | **ON** | Settings > Repository |
| Repository > Auto-close linked issues on PR creation | **ON** | Settings > Repository |
| Agents > Claude Code > CLI Command | `claude.cmd` on Windows, `claude` on Mac | Settings > Agents > Claude Code |
| Agents > Claude Code > Initial Prompt Flag | Inject `prompts/worker-initial-prompt.md` content | same |

## Execution rules (for Claude while driving this skill)

- Never skip Step 5. It gates Step 6.
- Never move forward until the current phase's template is filled in and Vincent confirms.
- All artifacts are **English only**.
- File I/O goes through the `shell-runner` subagent (MeowOS rule).
- On ambiguity about scope or phase, ask Vincent. Do not guess.
- Never auto-invoke other skills (superpowers, feature-dev, brainstorming, etc.).
- If Step 7 parallelization fails on Windows (PowerShell subagent dispatch quirks), fall back to sequential Pass 2 and warn Vincent.

## Cross-platform notes (Windows + Mac)

- Skill uses `~` expansion for all paths. Never hard-code drive letters or absolute paths.
- Build repo context import: `@~/.claude/meowos-core-for-tickets.md` (works on both OSes).
- Pipeline uses Python (no shell-specific quoting).
- Emdash CLI Command differs by OS (see config table above).
- Step 0 install guidance splits by platform: `.msi` installer for Windows `gh`, `brew install gh` for Mac.

## Exit

Skill session ends when Vincent says "stop," "done," or moves to a different topic. Do not auto-chain phases. Each phase transition is explicitly confirmed by Vincent.

## Out of scope

- Does not execute FE / BE code (that is Emdash worker territory).
- Does not merge PRs automatically (Vincent reviews and merges manually).
- Does not auto-spawn Emdash tasks in bulk (manual clicks per ticket until batch tool exists).
- Does not touch MeowOS knowledge base.

## References

- Templates (methodology artifacts): `templates/01_research-brief.md` through `templates/10_html-preview-shell.html`
- Build repo scaffolding: `templates/CLAUDE.md.template`, `templates/gitignore.template`
- Phase handoff: `templates/_resume_prompts/phase-<N>-to-<N+1>.md`
- Worker prompts: `prompts/ticket-executor.md`, `prompts/socratic-review.md`, `prompts/worker-initial-prompt.md`
- Pipeline: `pipeline/push_tickets.py`, `pipeline/README.md`
