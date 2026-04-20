# Multi-Round Autonomous Iteration Patterns
*Research compiled: 2026-04-11 | Scope: R3→R4→R5 playbook grounding*

---

## Question 1 — Round-Boundary Task Shape

### Core Problem
When a multi-agent team completes one round and automatically iterates into the next, scope creep, redundant work, and unbounded expansion are the primary failure modes.

### Published Patterns

**Charter Freeze at Round Entry**
The most reliable scope control pattern treats each round boundary as a "context gate." The scope for round N is *locked at spawn time*. No worker in round N can add new scope items that weren't in the round's task manifest. Any discovered work goes into a *deferred queue* for the next round, not the current one. (Source: ASDLC Ralph Loop, Google ADK LoopAgent)

**Task Ledger Pattern (HZL)**
A durable external task ledger survives context compaction, session restarts, and model switches. Each item has: `task_id`, `status` (pending / in_progress / completed / blocked / deferred), `owner`, `dependencies`, `round_added`, `round_completed`. The lead agent reads the ledger at round boundary to determine what the *next* round scope should be. This prevents re-doing completed items and surfaces blocked items for human escalation. Workers get a *frozen slice* of the ledger — they cannot add to it mid-round.

**Scope Baseline Document**
Project management literature calls this "scope baseline locking." Applied to agents: at round-start, the orchestrator writes a scope manifest (frozen). Workers receive only their slice. Any worker that proposes scope expansion is required to route it to a "deferred" list rather than executing it. The orchestrator merges deferred items during round-close.

**Scope Items to Freeze Explicitly:**
- File manifest (which files are in-scope)
- Acceptance criteria (what constitutes done)
- Agent roles (no role creep into other agents' slices)
- Token budget per agent per round

**Preventing Re-Doing Work**
- Every completed task must produce a `completed_artifact` field pointing to evidence (file hash, test run ID, diff checksum)
- At round-start, the task ledger is diff'd against artifacts on disk — if artifact exists and matches, task is skipped
- Workers get an explicit "already done" list at spawn time

**Informing Round N+1 from Round N Findings**
The round-close step produces a `round_summary.md` with: completed items, deferred items, blocking discoveries, and recommended adjustments to round N+1 scope. The orchestrator reads this before spawning round N+1 workers. This is the *only* channel through which findings propagate forward — workers do not directly modify the next round's charter.

---

## Question 2 — Charter Revision Protocols

### The Race Condition Problem
Charter was revised during worker spawn. Workers were already executing against the old spec. This is a known distributed systems problem analogous to a database schema change during active transactions.

### Published Patterns

**LangGraph interrupt() + State Checkpoint Pattern**
LangGraph supports mid-execution state revision via `interrupt()`. When a spec change is detected, the orchestrator can:
1. Call `interrupt()` on running nodes — this pauses execution, persists current graph state to checkpoint
2. Edit the state checkpoint directly (the checkpointed TypedDict)
3. Resume from checkpoint with `graph.invoke(Command(resume=new_spec_data), thread_id)`

Workers that already completed are not affected. Workers mid-execution are paused, receive the updated state on resume. This is the cleanest published pattern for "spec changed mid-execution" in agentic systems.

**Temporal Saga / Compensation Pattern**
Temporal treats spec changes as compensating actions on a workflow. If a step has already succeeded under old spec and is now invalidated, a *compensating activity* is registered that undoes or adjusts that work. Pattern:
1. Record compensating action when each step begins (not when it ends)
2. If spec changes, execute compensations in reverse order for steps that are now invalid
3. Then re-execute with new spec
Limitation: compensation must be designed upfront. Cannot be bolted on post-hoc.

**Out-of-Band Amendment (what you did in R3 — validated but improvable)**
Sending amendment messages to spawned workers is a valid fallback when interrupt() isn't available. The improvement is to make amendments *structured*, not prose. A structured amendment message should contain:
- `amendment_id` — unique
- `supersedes_section` — exact section of charter being replaced
- `new_text` — replacement
- `workers_affected` — list of agent IDs
- `already_completed_tasks_affected` — list of task IDs that need re-evaluation

This structure lets workers apply the amendment deterministically rather than interpreting free-form corrections.

**CrewAI Replay Pattern**
CrewAI's `crewai replay -t <task_id>` allows re-running from a specific task checkpoint. If a spec revision invalidates tasks T3-T7 but T1-T2 are clean, replay from T3 with the updated spec. This is the closest CrewAI equivalent to LangGraph's interrupt/resume.

**Race Condition Prevention (proactive)**
The canonical prevention is a *spawn gate*: workers are only spawned after charter is marked `FROZEN` in a shared manifest file. The orchestrator writes `charter_status: FROZEN` before issuing any spawn calls. Any charter revision must first de-freeze the charter (setting `charter_status: DRAFT`), which blocks any pending spawns until re-frozen. This eliminates the race condition at the source.

---

## Question 3 — Successor Agent Handoff Schemas

### Published Fields (Composite from Multiple Sources)

The AMBER/RED protocol fields (STATUS / FILES_CHANGED / DECISIONS / BLOCKED / NEXT_STEPS) are a *minimum viable* schema. Published patterns suggest these additional fields:

**Claude Code Agent Teams / Session Handoff (from `.claude/handoff.md` convention):**
```
STATUS: AMBER|RED|GREEN
ACCOMPLISHED: [list of completed items with artifact references]
FILES_CHANGED: [file, what changed, why]
DECISIONS: [decision, rationale, alternatives considered]
BLOCKED: [what is blocked, why, what is needed to unblock]
NEXT_STEPS: [prioritized list]
TRIED_AND_ABANDONED: [approach, why it failed, why not to retry]
OPEN_QUESTIONS: [unresolved items that need human or next-agent judgment]
GOTCHAS: [edge cases, traps, non-obvious constraints discovered]
```
This is close to the documented Claude Code session handoff spec: "what was accomplished, what was tried and explicitly abandoned and why, what's still in progress, recommended next steps, any gotchas."

**The Missing Fields (beyond AMBER/RED):**

| Field | Purpose | Source Pattern |
|---|---|---|
| `WHY` (per-decision) | Causal traceability — not just what was decided but why | Agent trace design, XTrace pattern |
| `TRIED_AND_REJECTED` | Prevent successor re-exploring known dead ends | Claude Code handoff spec (called "tried and abandoned"), agentic coding loop specs |
| `ARTIFACT_HASHES` | Proof that completed items actually exist on disk | Diff-based completion verification, CI/CD patterns |
| `ASSUMPTION_LOG` | Assumptions made that successor should be aware of | LangGraph state annotation pattern |
| `SCOPE_CHANGES_DEFERRED` | Items discovered but explicitly out of scope for this round | Task ledger / HZL pattern |
| `CONFIDENCE_LEVEL` | Agent's self-assessed certainty (LOW/MED/HIGH) per completed item | Multi-agent eval frameworks |

**Why `TRIED_AND_REJECTED` is the highest-value missing field:**
The most common cause of redundant work in multi-round iteration is the successor agent re-exploring approaches the predecessor already proved wrong. No published framework defaults to capturing this — it must be explicitly required in the handoff schema. Without it, each round has positive probability of re-attempting the same failed fix, burning tokens and rounds.

**LangGraph Reducer Approach (programmatic)**
LangGraph's TypedDict state supports annotated reducer functions. A `failed_approaches` field with a list-append reducer accumulates across the entire session graph: every agent appends its failures, and successors receive the full failure history via state injection. This is the most elegant programmatic approach for teams using LangGraph.

---

## Question 4 — Autonomous PASS/FAIL Detection

### Published Quantitative Signals

**Tier 1: Binary / Machine-Verifiable Signals (highest confidence)**
- **Test suite exit code**: `exit 0` = tests pass = PASS signal. Most reliable single signal.
- **Test count delta**: If round started with N failing tests and ends with M, `M < N` = PARTIAL PASS, `M = 0` = PASS, `M >= N` = FAIL.
- **Build exit code**: Compiler/linter non-zero = blocking FAIL regardless of other signals.
- **Diff size vs budget**: If round produced zero diff = FAIL (no work done). If diff exceeds pre-set budget (e.g., 300 lines) = suspicious, flag for review.
- **Artifact existence check**: Does the output file / function / endpoint actually exist on disk? Hash verification.

**Tier 2: Heuristic Signals (medium confidence)**
- **Iteration velocity**: Rapid improvement in tests 3-10 iterations, marginal after 10 — use this to set per-task iteration ceilings (not per-round)
- **Output similarity across iterations**: >90% string similarity across 3 consecutive agent outputs = stuck state = PARTIAL/FAIL escalation trigger
- **Token expenditure vs progress ratio**: If token spend in last N attempts produced no test improvement, declare diminishing returns
- **Diff size stability**: If diffs shrink each attempt toward zero without green tests, agent is oscillating — escalate

**Tier 3: Structural Signals (lower confidence, use as tie-breakers)**
- All acceptance criteria items have a corresponding artifact reference → lean PASS
- Blocked items still blocked at round end → PARTIAL
- `TRIED_AND_REJECTED` list grew significantly → agent struggled, flag for scrutiny

**Recommended Autonomous Decision Rule (composite)**
```
if (build_exit_code != 0):           → FAIL (hard)
elif (test_exit_code == 0 and all_acceptance_criteria_met):  → PASS
elif (test_count_delta > 0 and no_stuck_signals):            → PARTIAL PASS (continue)
elif (stuck_signal OR no_diff OR iteration_ceiling_hit):     → FAIL (escalate)
else:                                                        → PARTIAL (one more round)
```

**Anthropic's Eval Framework Guidance**
Anthropic engineering guidance on agent evals recommends: "completion promises" — agents output an explicit string like `ALL_TESTS_PASSING` only when criteria are met; the orchestrator pattern-matches this rather than doing fuzzy interpretation. This removes ambiguity from PASS detection.

---

## Question 5 — Loop Termination Heuristics

### When to Stop Pushing a Task Within a Round

**The Ralph Loop Principle**
Ralph Loop is the most published named pattern for this. Core insight: "Define the finish line through machine-verifiable tests, then let the agent iterate toward that finish line." The finish line is not self-reported — it is externally verified. The loop terminates when external verification passes, *or* when a ceiling is hit.

**Published Termination Signals:**

1. **Hard ceiling** — Vincent's R3/R4/R5 ceiling is the right meta-level control. Within a round, each task should have `MAX_ATTEMPTS = 3`. After 3 attempts with no progress, the task is marked `BLOCKED` and escalated, not retried.

2. **No-progress detector** — If the last N iterations produced the same test delta (or zero delta), declare no-progress. Published threshold: 3 consecutive zero-delta iterations = stuck. The Ralph Loop implementation blocks agent exit and re-injects the prompt, but if still no progress after 3 re-injections → abandon and escalate.

3. **Stochastic Convergence Spiral escape** — If reward/error signals are oscillating without converging (the "spiral" pattern), the escape is: inject perturbation (try a different approach), or escalate to human review. Do not keep retrying the same approach.

4. **Partial fix anti-pattern** — The specific pattern to detect: agent applies fix, tests improve partially, agent re-applies a variant of the same fix, tests stay the same or regress. Detection: compare the diff of attempt N+1 to attempt N — if >70% overlap, the agent is in a partial-fix loop. Countermeasure: require agent to attempt a *structurally different* approach (documented by requiring `new_approach_rationale` field in its attempt log).

5. **Fallback path trap** — Agents equipped with fallback behaviors (retry on error) sometimes re-trigger the same error in a loop. Fix: distinguish stop errors (auth failure, validation failure, policy block = non-retriable) from transient errors (network timeout = retriable). Non-retriable errors must terminate the loop immediately.

6. **Financial/token governor** — Hard spend ceiling per round. When ceiling is hit, force round close regardless of task completion state. Unfinished tasks → BLOCKED in handoff.

**The Escape Hierarchy (ranked by preference):**
```
1. Task completes (PASS) → normal exit
2. Ceiling hit (MAX_ATTEMPTS) → mark BLOCKED, move on
3. No-progress detected → mark BLOCKED, move on  
4. Stuck-loop detected (>90% output similarity) → escalate to orchestrator
5. Budget exhausted → force round close, full BLOCKED list in handoff
```

Do NOT allow a 6th category: "agent decides it is done via self-assessment." Self-assessment without external verification is the root cause of the "agent claims done, isn't" failure mode. External verification is mandatory for PASS.

---

## Synthesis — Immediately Applicable Changes to R4/R5 Approach

### 1. Add `TRIED_AND_REJECTED` to Every Handoff File (Highest Priority)
The current AMBER/RED schema is missing the single most valuable field. Before spawning R4, add this field to the handoff template. Each agent must document failed approaches before closing. This prevents R4 workers from repeating R3's dead ends. Implementation: add to handoff template, make it a required field (non-empty required for PASS judgment on agent close).

### 2. Implement Charter Freeze Gate Before Spawning
Adopt the `charter_status: FROZEN` flag. Write it to the charter file only after all revisions are complete, before issuing any spawn calls. If a revision arrives after FROZEN, route it through a structured amendment object (not free-form prose). This eliminates the R3 race condition for all future rounds.

### 3. Use Binary Exit-Code + Test-Delta as Primary PASS/FAIL Signal
Replace subjective completion judgment with: build exit code + test delta. If `test_delta > 0 AND no stuck signal` = PARTIAL (continue). If `build clean AND test_exit_code == 0` = PASS. Require agents to output a completion promise token (`ACCEPTANCE_CRITERIA_MET`) only when all acceptance criteria have an artifact reference. Orchestrator pattern-matches this token, not prose.

### 4. Add Per-Task `MAX_ATTEMPTS = 3` Ceiling with Mandatory BLOCKED Escalation
Current setup uses round-level ceilings but not per-task ceilings. Add explicit attempt counter per task. After 3 attempts with zero test delta, automatically mark task BLOCKED (not failed, not retrying). BLOCKED items surface in round handoff for human review. This prevents any single task from consuming the whole round budget.

### 5. Add `SCOPE_CHANGES_DEFERRED` Field to Round-Close Handoff
Any scope discovered during the round that is outside the current round's manifest goes into this field — not executed, not ignored. At round-start, the orchestrator reads this field from the previous round's handoff and decides whether to absorb items into the new scope. This makes scope evolution explicit and auditable rather than implicit drift.

---

*Sources consulted: LangGraph interrupt/checkpoint docs, CrewAI memory and replay docs, Temporal Saga pattern, Ralph Loop / ASDLC patterns, GitHub Blog multi-agent engineering guide, Claude Code agent teams documentation, HZL task ledger pattern, Stochastic Convergence Spiral framework, XTrace agent handoff patterns, autonomous agent eval frameworks (Anthropic, Braintrust), agent loop termination production patterns.*
