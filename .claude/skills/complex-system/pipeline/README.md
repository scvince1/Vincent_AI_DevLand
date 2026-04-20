# Pipeline · ticket.md to GitHub issue

`push_tickets.py` is the manual-trigger pipeline that converts local `04_tickets/*.md` files into GitHub issues.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status` shows green).
- Build repo has a GitHub remote origin.
- Ticket files follow the `templates/09_ticket.md` format (YAML frontmatter with `ticket_id`, `title`, `phase`, `version`, `depends_on`, `issue_number: null` initially).

## Usage

Dry run (print what would happen, no `gh` calls):

```
python ~/.claude/skills/complex-system/pipeline/push_tickets.py /path/to/build-repo --dry-run
```

Live push:

```
python ~/.claude/skills/complex-system/pipeline/push_tickets.py /path/to/build-repo
```

## What it does

1. Reads every `*.md` under `<build-repo>/04_tickets/` (skips files starting with `_`).
2. Parses YAML frontmatter on each.
3. Topologically sorts by `depends_on` (blockers first).
4. For each ticket without an `issue_number`:
   - Calls `gh issue create` with title, body, and `phase:*` / `version:*` labels.
   - If `depends_on` contains already-pushed ticket IDs, appends a `**Blocked by**: #X, #Y` footer so the worker sees it.
   - Writes the returned issue number back into the ticket's frontmatter.
5. On any failure, aborts. Already-written `issue_number` values stay, so re-running picks up where it left off.

## Idempotency

- Tickets with `issue_number` already set are skipped.
- Safe to re-run after a failure.
- Safe to add new tickets later and re-run; only new ones get pushed.

## Manual trigger (by design)

Skill never calls this automatically. Vincent runs it when he is ready to move tickets from local markdowns to the GitHub issue tracker.

## Labels

- `phase:frontend` / `phase:backend` / `phase:research` / etc.
- `version:v0.1` / `version:v1.0` / etc.

GitHub auto-creates missing labels on first use.

## DAG handling

Dependencies are expressed two ways:

1. **In frontmatter** (`depends_on: [FE-V1-001]`): used by this script to sort push order.
2. **In issue body** (auto-appended `**Blocked by**: #N` footer): read by Emdash workers at execution time.

Emdash itself does not enforce DAG; the worker resolves it via `git branch -a` + `git merge`. See `prompts/worker-initial-prompt.md`.

## Failure modes

- `gh auth status` not green → authenticate first.
- Circular dependency in `depends_on` → script errors out with the cycle.
- Ticket file missing frontmatter → script errors out with the filename.
- `gh issue create` returns non-zero → script aborts; partial progress preserved via idempotency.

## Not covered by this pipeline

- Does not create Emdash Tasks. That is manual in Emdash UI (or future batch tool `Dnew1`).
- Does not merge PRs. Vincent reviews and merges in GitHub or Emdash.
- Does not close issues. GitHub auto-closes on PR merge via `Closes #N` footer from worker PRs.
