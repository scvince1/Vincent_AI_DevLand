# Ticket Executor · Step 7 Meta-Prompt

Two-pass ticket decomposition. Pass 1 is single-agent for DAG consistency. Pass 2 parallelizes ticket expansion with pre-allocated ID ranges.

---

## Pass 1 · Epic Decomposition (single agent)

### Input
- `01_design/04_design-spec.md`
- `01_design/03_data-constraints.md`

### Output
- `04_tickets/_epics.json`

### Schema

```json
{
  "project": "<PROJECT_NAME>",
  "generated_at": "YYYY-MM-DDThh:mm:ssZ",
  "epics": [
    {
      "epic_id": "EPIC-01",
      "title": "Short imperative title",
      "summary": "One paragraph describing the epic's scope.",
      "phase": "frontend | backend | research | data | design",
      "estimated_ticket_count": 5,
      "depends_on_epics": ["EPIC-00"],
      "spec_sections": ["core flows > Flow 1", "data constraints > In scope > row 3"]
    }
  ]
}
```

### Rules

- Emit 5 to 10 epics. Fewer if the spec is small; more only if genuinely needed.
- Prefer **vertical slices** (one epic = one user flow end-to-end, spanning FE + BE) over horizontal slices when possible.
- `depends_on_epics` must be acyclic. Leaf epics (no deps) should be pushable first.
- Each `spec_sections` entry is a path reference into the design spec for downstream subagent context.
- Do not invent scope not in the spec.
- Output must be valid JSON matching the schema. No markdown fences inside the file.

---

## Pass 2 · Ticket Expansion (N agents in parallel, one per epic)

Each subagent receives one epic's row from `_epics.json` plus this prompt.

### Subagent Input Template (filled per dispatch)

```
You are subagent for {epic_id}: "{title}".

Design spec: <path>
Data constraints: <path>
Your epic slice: <the epic's row from _epics.json>

Your ticket ID range: {ticket_id_start} to {ticket_id_end} inclusive.
Your ticket IDs must follow the format {PHASE}-{VERSION}-{seq}, e.g., FE-V1-003.
Do not emit ticket IDs outside this range.

Write each ticket to 04_tickets/<ticket_id>.md using the template at
~/.claude/skills/complex-system/templates/09_ticket.md.

Return JSON summary: { "epic_id": "...", "tickets_created": ["FE-V1-003", ...], "failures": [] }.
```

### Rules

- Each subagent owns a non-overlapping ID range. Coordinator assigns ranges before dispatch.
- Ticket granularity: roughly half a day to one day of worker execution.
- Every ticket must include a complete `## Agent Prompt` section per `templates/09_ticket.md`. The prompt must be self-contained (no "as we discussed" references).
- `depends_on` in ticket frontmatter: cross-ticket deps (not cross-epic). Reference specific ticket IDs.
- `spec_refs`: relative paths to design spec + relevant frontend/backend spec.
- `issue_number`: always `null` at emission time (pipeline fills in later).
- `appended_prompt`: usually `null`. Set to a file path only if the ticket needs extra context beyond the issue body (rare, maybe 1 in 10).

### Coordinator responsibilities after all subagents return

- Validate: no duplicate ticket IDs, no unresolved `depends_on`, all `spec_refs` exist.
- If any subagent failed, retry or surface the failure to Vincent.
- Write `04_tickets/_index.md` summarizing the ticket list (ticket_id, title, phase, version, depends_on).

---

## What NOT to do

- Do not push tickets to GitHub in this session. That is the pipeline's job (`pipeline/push_tickets.py`), triggered manually by Vincent.
- Do not spawn Emdash tasks in this session. Vincent does that in Emdash UI after the pipeline runs.
- Do not invoke other skills.
- Do not modify the design spec or data constraints during this step.
