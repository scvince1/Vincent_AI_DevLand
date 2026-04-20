# Context Compression Patterns — for multi-agent team use

_Research date: 2026-04-11_

---

## Problem statement

In Challenge_5_v2, two v2 engineer teammates entered a "degraded state" after sustained heavy work: their context windows had filled to ~80%+ capacity through the cumulative weight of spawn prompt + file edits + test run output + iterative research cycles. The observable symptom was that protocol-level messages (e.g., `shutdown_request`) still received responses — proving the model was alive — but prose generation failed entirely. This is consistent with leaving insufficient token budget for output generation: the model can process a short structured trigger but cannot allocate headroom for a multi-sentence natural language reply. The root cause is not a crash or tool failure; it is a context exhaustion failure mode that must be proactively managed by each agent rather than reactively diagnosed by the orchestrator.

---

## Published techniques

### LangGraph checkpointing

LangGraph provides a built-in persistence layer via "checkpointers" (InMemorySaver, SqliteSaver, Redis backends). Every time graph state changes, the checkpointer saves a full snapshot. For context management the key patterns are:

- **Message trimming**: `trim_messages()` utility removes older messages before each LLM call, keeping token count under a hard ceiling.
- **Summary nodes**: A dedicated graph node is inserted that calls the LLM to condense long message history into a running summary, then replaces the raw history with the summary + a fixed recent tail.
- **Thread scoping**: Each conversation thread has its own checkpoint namespace; long-term cross-session memory is stored in a separate namespace, so per-session context never accumulates unbounded.

**Pattern without LangGraph**: Maintain a `conversation_summary` variable in your state. At a token threshold, call the LLM with prompt "Summarize the above interaction into ≤500 tokens, preserving decisions, file paths, and open tasks." Replace accumulated history with summary + last N turns.

---

### CrewAI memory tiers

CrewAI implements a four-tier memory architecture that separates context pressure from task memory:

| Tier | Backend | Scope |
|---|---|---|
| Short-Term Memory (STM) | ChromaDB + RAG | Current session working memory |
| Long-Term Memory (LTM) | SQLite3 | Cross-session task results and insights |
| Entity Memory | RAG | Named entities (people, places, concepts) |
| Contextual Memory | Composite (STM + LTM + external) | Injected per-task via RAG retrieval |

The critical implication for context management: agents do NOT need to hold all prior work in-context. Before each task, contextual memory **injects** only the relevant retrieved fragments. After each task, a background process **extracts and externalizes** discrete facts. The live context at any moment is a small window of recent turns plus retrieved snippets — not the full history.

**Pattern without CrewAI**: After every major work block, prompt the agent: "Extract 5-10 discrete facts from the last N messages and write them to `state_facts.md`. Then we will discard those messages." This simulates LTM externalization.

---

### AutoGen memory_config

AutoGen (Microsoft, now merged into Microsoft Agent Framework) handles long context via:

- **CompressibleGroupManager**: A production component that delegates compaction decisions to a background manager, triggering when conversation length exceeds a threshold. The manager calls a summarizer LLM on older turns and injects the summary in place.
- **Active Compression / Focus Agent** (research paper, 2026): The agent introspects its own trajectory, summarizes it into a high-level "learning," then physically **deletes** the raw log entries from its context. This shifts the paradigm from passive retention to active compression.
- **Context Pruning, Injection, Prioritization**: Fine-grained controls to remove low-relevance turns, dynamically add relevant external data, and rank important facts for preservation.

**Key insight**: AutoGen's architecture explicitly treats context management as a first-class agent capability, not an external infrastructure concern.

---

### Anthropic-specific guidance

**Claude Code `/compact` command**: Claude Code provides a `/compact` slash command that triggers immediate summarization of conversation history, collapsing older turns into a compact summary while preserving the recent tail. As of Claude Code 2.0, the command executes immediately and the resulting summary is loaded into a fresh context budget. A complementary `/clear` command resets context entirely.

**Agent SDK automatic compaction**: The Claude Agent Python SDK includes a `compaction_control` parameter. When token usage per turn exceeds a configurable threshold, the SDK injects a summary prompt as a user turn, the model generates a `<summary>...</summary>` block, and the SDK replaces accumulated history with that block. This allows tasks to continue beyond the 200k token context limit without human intervention.

**Subagent isolation pattern**: Claude Code's recommended architecture is to delegate verbose work to subagents, each running in their own context window. Only a structured summary (not raw output) is returned to the orchestrator. This prevents orchestrator context bloat from subagent verbosity.

**Recommended working rhythm**: Anthropic documentation and practitioners both converge on 30-60 minute focused blocks. Each block ends with a written handoff document; the next session loads only the handoff, starting with a clean context.

**Token budget thresholds observed in the wild**:
- Claude Code internal compaction fires at approximately 92% fill (contextWindow minus 16,384 reserve tokens)
- Gemini CLI defaults to 50% threshold
- General practitioner guidance: treat 70-75% as the "amber" threshold for proactive action

---

### Academic / other

**ACON (Optimizing Context Compression for Long-Horizon LLM Agents, arXiv 2510.00615)**: Frames compression as an optimization problem. Uses paired trajectory analysis — cases where full context succeeded but compressed context failed — to identify what information compression lost, then refines the compression prompt to preserve that class in future runs. Achieves 26-54% reduction in peak token usage.

**ReSum (OpenReview 2025)**: Introduces periodic context summarization that converts growing interaction histories into compact "reasoning states" while maintaining awareness of prior discoveries. Enables indefinite exploration without hard context resets.

**Observation Masking**: Targets only the environment observation (tool output, file content) for compression while preserving the full action and reasoning history. Effective for software engineering agents where observations are large but reasoning chains are compact.

**Anchored Iterative Summarization**: Maintains a persistent "anchor summary" of everything before a sliding window. When new content exits the window, it is merged into the anchor rather than dropped. Prevents catastrophic forgetting while keeping live context small.

**In-Context Distillation (arXiv 2512.02543)**: Retrieves relevant teacher demonstrations at each agent step and provides them as in-context examples to a smaller student model, reducing total token load.

**Chain of Agents (NeurIPS 2024)**: Decomposes long-context tasks across a chain of agents that communicate summaries rather than raw context. Each agent only sees its local slice plus a summary of upstream work.

**Key statistic**: 65% of enterprise AI failures in 2025 were attributed to context drift or memory loss during multi-step reasoning — not raw context exhaustion per se. The distinction matters: context exhaustion is a hard limit, but context drift (important facts falling out of the active window due to dilution) causes failures well before the hard limit.

---

## Self-recognition signals

An agent can detect approaching context exhaustion through the following observable signals, roughly in order of reliability:

1. **Token count introspection**: If the agent has access to its own token usage (via SDK metadata, tool output, or system prompt injection), watch for >70% of context window consumed. At 70% = amber; at 80% = red; at 85%+ = act immediately.

2. **Response latency increase**: Model inference time increases as context grows. Subjectively, if generation feels "sluggish" on what should be a simple request, context pressure may be a contributing factor.

3. **Instruction forgetting**: The agent starts repeating work it has already done, ignoring constraints stated earlier in the session, or asking for information it was already given. This is the clearest behavioral signal of context drift.

4. **Shortened or fragmented outputs**: If responses that previously produced multi-paragraph prose start producing one-liners or truncated outputs, available output budget may be depleted.

5. **Protocol responses succeed but prose fails**: The exact symptom observed in Challenge_5_v2. Short structured outputs still work; free-form generation fails. This indicates the model can match a short pattern but cannot allocate headroom for unstructured generation.

6. **Work scope awareness**: If the agent can track its own work volume (number of files read, number of tool calls made, number of test runs executed), it can reason: "I have done X units of heavy work; my context is likely N% full."

---

## Mitigation actions

Ranked by effectiveness for an in-process teammate that cannot easily call `/compact` on its own behalf:

### Tier 1 — Do immediately (before hitting 80%)

**1. Externalize state to disk (highest value)**
Write a structured state document to disk containing: decisions made, files modified (with patch summaries), current task status, open questions, and explicit next steps. Once written, the agent can treat all prior conversation turns as droppable — the disk file IS the memory. Recommended format: `handoff_state.md` with sections STATUS / FILES_CHANGED / DECISIONS / BLOCKED / NEXT_STEPS.

**2. Selective history pruning**
Identify the largest context consumers (long file reads, verbose tool outputs, repeated error traces) and mentally "drop" them — do not reference or re-read them. Rely on the disk state instead. Do not attempt to re-read large files; reference only the written summary.

**3. Request orchestrator-side compaction**
Signal to the team lead / orchestrator: "Context pressure detected. Requesting /compact or context reset." The orchestrator can trigger `/compact` externally or spawn a successor with a fresh context loaded from the state file.

### Tier 2 — If still operating (amber zone, 70-80%)

**4. Summarize-and-continue (rolling summary)**
Prompt yourself: "Summarize everything before this point in ≤300 tokens: decisions, files touched, current status, open tasks. Treat this summary as the only record of prior work." Then proceed as if the prior context is gone. This is the in-process equivalent of LangGraph's summary node.

**5. Narrow scope aggressively**
Suspend any exploratory or research-mode work. Focus exclusively on completing the single most critical remaining task and writing its output to disk. Defer everything else to successor.

### Tier 3 — When degraded (80%+, prose generation failing)

**6. Stop and write the handoff**
At this point, do not attempt further prose work. Write only a minimal structured handoff (bulleted, not prose) to disk and emit a shutdown signal. The state file is more valuable than continued degraded operation.

**7. Spawn or request a successor**
The team lead spawns a v_next agent with: (a) the original spawn prompt, (b) the state file loaded as initial context, (c) a one-sentence "continue from state file" instruction. Do NOT pass raw conversation history — only the structured state file.

### Anti-patterns to avoid

- Do NOT keep loading more files when context is already high — each file read multiplies the problem
- Do NOT attempt to re-run full research cycles in a degraded state
- Do NOT wait for the orchestrator to notice the problem — signal proactively
- Do NOT try to summarize in prose when generation is failing — use bullet points or structured JSON

---

## Recommended v3 spawn-prompt instructions

The following block is designed to be copy-pasted directly into engineer spawn prompts. Adjust threshold numbers to match observed team behavior.

---

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

_Sources consulted: Anthropic Claude Code docs, LangGraph memory docs, CrewAI memory docs, AutoGen memory docs, arXiv ACON (2510.00615), arXiv In-Context Distillation (2512.02543), ReSum (OpenReview 2025), JetBrains Research efficient context management (2025-12), Zylos Research AI agent context compression (2026-02), Automatic Context Compression in LLM Agents (Medium/The AI Forum 2026-03), ADK context compaction docs._
