---
id: multi_agent_context_compression_patterns
title: Multi-Agent Context Compression Patterns
tags: [ai-systems, meta, multi-agent, context-management, llm-infra]
status: confirmed
last_modified: 2026-04-15
summary: 多 agent 系统 context 耗尽失效模式及 LangGraph/CrewAI/AutoGen 压缩方案
---
# Multi-Agent Context Compression Patterns

**Date captured:** 2026-04-11
**Tags:** multi-agent, context-management, LLM-infra, orchestration, agent-reliability

---

## Summary

In multi-agent systems, context window exhaustion is a first-class failure mode distinct from a model crash. As agents accumulate file reads, tool outputs, and iterative reasoning, the context window fills until insufficient headroom remains for prose generation. The agent may still respond to short structured triggers (protocol messages, JSON) while failing entirely to produce natural language — a reliable diagnostic signal. This document consolidates published framework techniques (LangGraph, CrewAI, AutoGen, Anthropic) and a production-tested spawn-prompt protocol for managing this in live agent teams.

---

## Key Takeaways

- **Context exhaustion vs. context drift are distinct failure modes.** Exhaustion = hard limit (>95% full). Drift = important facts fall out of active window due to dilution, causing errors well before the hard limit. 65% of enterprise AI failures in 2025 were attributed to context drift, not exhaustion.
- **"Protocol-capable, prose-incapable" is the clearest diagnostic.** If an agent answers short structured messages but cannot produce free-form paragraphs, assume output budget is near zero. This was observed directly in a production multi-agent session: two engineer agents entered this degraded state after sustained heavy work (spawn prompt + file edits + test runs + research cycles filling ~80%+ of context). They answered protocol-level shutdown requests correctly but could not generate prose responses.
- **The 3 highest-value mitigation techniques (ranked):**
  1. **Externalize state to disk** — write a structured handoff file (`STATUS / FILES_CHANGED / DECISIONS / BLOCKED / NEXT_STEPS`). Once written, the disk file IS the memory; prior conversation turns become droppable.
  2. **Rolling summary (summarize-and-continue)** — prompt the agent to condense everything before a threshold point into ≤300-500 tokens, then proceed as if prior context is gone.
  3. **Successor spawn** — orchestrator spawns a fresh agent loaded with only (a) original spawn prompt + (b) the handoff file. Never pass raw conversation history to the successor.
- **Thresholds observed / recommended:** 70% = amber (write state snapshot, stop reading new large files); 80% = red (write handoff, signal orchestrator, bullet-point outputs only); 85%+ = critical (stop prose, spawn successor).
- **Anti-patterns:** Continuing to load more files when context is already high; re-running research cycles in degraded state; waiting for the orchestrator to notice instead of proactively signaling.

---

## Framework Techniques Reference

### LangGraph
- `trim_messages()` utility: removes older messages before each LLM call up to a token ceiling.
- Summary nodes: dedicated graph node calls LLM to condense history, replaces raw history with summary + fixed recent tail.
- Thread scoping: per-session context isolated in its own namespace; long-term memory in a separate namespace.

### CrewAI (4-tier memory)
| Tier | Backend | Scope |
|---|---|---|
| Short-Term Memory | ChromaDB + RAG | Current session |
| Long-Term Memory | SQLite3 | Cross-session task results |
| Entity Memory | RAG | Named entities |
| Contextual Memory | Composite | Per-task RAG injection |

Key implication: agents do NOT hold all prior work in-context. Relevant fragments are injected per-task via RAG retrieval; discrete facts are externalized after each task.

### AutoGen (Microsoft)
- `CompressibleGroupManager`: triggers background summarization when conversation length exceeds a threshold; injects summary in place of older turns.
- Active Compression: agent introspects its own trajectory, summarizes into a "learning," and physically deletes raw log entries from context. Treats compression as a first-class agent capability.

### Anthropic / Claude
- `/compact` command in Claude Code: immediate summarization, collapses older turns, loads result into fresh context budget.
- Agent SDK `compaction_control` parameter: auto-injects a summary prompt at a configurable token threshold; SDK replaces history with the summary block.
- **Subagent isolation pattern:** Delegate verbose work to subagents; only structured summaries return to orchestrator. Prevents orchestrator bloat.
- Recommended working rhythm: 30-60 minute focused blocks, each ending with a written handoff document.

---

## AMBER/RED/SUCCESSOR Protocol (Copy-Paste Block for Spawn Prompts)

```
## Context Management Protocol

You have a 200k token context window. Heavy work (file reads, test runs, research) consumes
context rapidly. Follow this protocol:

AMBER ZONE (est. ~70% full — after heavy file edits + 2+ research cycles):
- Write a state snapshot to disk: decisions, files changed, status, next steps.
- Stop reading new large files. Summarize-and-continue if needed.
- Emit a status message to team lead: "Context at amber threshold."

RED ZONE (est. ~80% full — prose outputs shortening or fragmenting):
- Immediately write a structured handoff to:
  contracts/state/[your_agent_id]_handoff.md
  Sections: STATUS | FILES_CHANGED | DECISIONS | BLOCKED | NEXT_STEPS
- Signal team lead: "Context exhaustion imminent. Handoff written. Ready for successor spawn."
- Do not attempt further prose generation. Bullet-point outputs only.

SUCCESSOR SPAWN:
- Successor loads only: spawn prompt + handoff file. No raw history.
- Successor begins by reading the handoff file and confirming understanding before proceeding.

SELF-DETECTION HEURISTICS (if no token counter available):
- You have read 5+ large files AND run 3+ test/search cycles → assume AMBER
- Responses are shortening without instruction → assume RED
- You can answer protocol messages but not open-ended questions → assume CRITICAL, write handoff immediately
```

---

## Academic References

- **ACON** (arXiv 2510.00615): Paired trajectory analysis to refine compression prompts; achieves 26-54% reduction in peak token usage.
- **ReSum** (OpenReview 2025): Periodic context summarization into compact "reasoning states" for indefinite exploration.
- **Observation Masking**: Compress only tool/file output while preserving full action + reasoning history.
- **Anchored Iterative Summarization**: Persistent "anchor summary" of everything before a sliding window; new content merged into anchor rather than dropped.
- **Chain of Agents** (NeurIPS 2024): Decomposes tasks across a chain of agents that communicate summaries rather than raw context.

---

## Sources

Anthropic Claude Code docs, LangGraph memory docs, CrewAI memory docs, AutoGen memory docs, arXiv ACON (2510.00615), arXiv In-Context Distillation (2512.02543), ReSum (OpenReview 2025), JetBrains Research efficient context management (2025-12), Zylos Research AI agent context compression (2026-02), ADK context compaction docs.
