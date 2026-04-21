# Routing Rules v1.3 — MacBook (Slim)
_Updated: 2026-04-21_
_Derived from the MeowOS Routing v1.3 on the primary PC; slimmed to only the targets that exist on this machine. Add rows as new agents are built locally._

## Intent Classification

| Trigger / Intent | Route Target |
|---|---|
| `system diagnostic` / `system enhancement` | → system-diagnostics |
| `read ...` / `think about ...` / `log this concept` / `organize XX` / `this idea` / `file it` / `knowledge` / `archive knowledge` | → knowledge-agent |
| `remember this` / `obs:` | → main session handles directly (append to `83_Observations/habits.md`) |
| Ambiguous intent | → Ask Vincent to confirm; do not guess. |

## Main-session auto-dispatch (silent, no explicit trigger)

The following agents are auto-invoked by the main session when the relevant context is detected. Vincent does not usually trigger them explicitly.

| Agent | Auto-trigger context |
|---|---|
| knowledge-agent | Ingesting external knowledge, reading/writing person profiles, cross-category queries across `80_Knowledge/` |

## Cross-agent orchestration rules

- When an agent emits a `cross_agent_required` flag, the main session dispatches to the listed `target` agents **sequentially** (vertical orchestration).
- Agents **must not** call other agents horizontally. This prevents nested-call runaway and keeps behavior debuggable.
- The main session synthesizes outputs from multiple agents before presenting to Vincent.

## Conflict rules
- Multiple intent signals in one message → pick the primary intent, handle it, and tell Vincent the order.

## File-operation principle

All read/write operations are delegated to the `shell-runner` subagent. The main session does not call Read / Edit / Grep / Glob directly for verbose work.

**Exceptions (direct tools are fine):**
1. Vincent explicitly asks for direct file operations.
2. The session is dedicated to coding / development / using the `complex-system` skill.
