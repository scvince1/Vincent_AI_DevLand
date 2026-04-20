---
id: B2_execution_layer
title: "B2 - Execution Layer: Planning, Control Flow, and Tools"
tags: [harness, knowledge, execution-layer, planning, tools]
status: confirmed
last_modified: 2026-04-15
summary: IMPACT 的 P+C+T 三维度深挖：规划、控制流、工具使用
---
# B2 — Execution Layer: Planning, Control Flow, and Tools

**版本：** 2026-04-14
**前置阅读：** `00_master_synthesis.md`（不重复其中已有内容）
**范围：** IMPACT 中的 P（Planning）+ C（Control flow）+ T（Tools）三个维度
**OUT OF SCOPE：** Memory/Context（B1），Evals/Constraints（B3）

---

## Section 1: Conceptual Foundation — Why Orchestration Exists

### The single-call illusion

A bare LLM call is a lookup: prompt in, completion out. It has no memory of prior attempts, no ability to verify its output, and no way to call a function and learn the result before continuing. Almost every interesting task requires more than one inference step. Orchestration is the engineering layer that stitches multiple LLM calls (and tool calls) into a coherent workflow.

The minimal unit is a **loop**:

```
Observe state → Reason → Act → Observe new state → (repeat) → Terminate
```

Simon Willison's canonical definition captures this precisely: "An LLM agent runs tools in a loop to achieve a goal" (2025-09-18). Everything else — graphs, planners, multi-agent architectures — is elaboration of this loop.

### What "control flow" means here

In traditional software, control flow is deterministic: `if`, `while`, `goto`. The machine always takes the same branch given the same input. In agentic systems, control flow has a probabilistic element: the LLM decides which tool to call, whether to loop again, or when to stop. The harness wraps this probabilistic core with deterministic guardrails — maximum iteration counts, required approval steps, error handlers — to make the overall system predictable enough to ship.

**The fundamental tension:**
- **Determinism** (graph/state machine): predictable, auditable, debuggable, brittle when tasks vary
- **Flexibility** (open loop): adapts to novel inputs, harder to reason about, harder to debug, prone to drift

Both approaches co-exist in production. The choice is not philosophical — it is empirical: deterministic workflows for well-specified, repeatable tasks; open-loop agents for open-ended problems where the path can't be pre-specified.

Anthropic states this directly: "Workflows offer predictability and consistency for well-defined tasks, whereas agents are the better option when flexibility and model-driven decision-making are needed at scale." (anthropic.com/research/building-effective-agents, Dec 2024)

---

## Section 2: Orchestration Patterns Taxonomy

### 2.1 Single-Agent Tool Loop (Willison Minimalist)

**Definition:** One LLM, one system prompt, N tools, a while-loop that terminates when the model stops calling tools or hits a max-iteration cap.

**When it applies:** Tasks where the model can self-direct; single-domain problems; developer tooling.

**Failure mode:** Loop never terminates (model keeps calling tools without progress); no mechanism for self-correction; tool errors propagate as LLM hallucination in the next turn.

**Canonical implementation:** Claude Code, Aider in `code` mode, any `Runner.run()` in OpenAI Agents SDK with a single agent and no handoffs.

**Why it works:** No coordination overhead. The full context window is dedicated to the task. Source overhead is minimal. When a task is truly single-domain, this beats multi-agent by a wide margin.

---

### 2.2 ReAct (Reasoning + Acting)

**Definition:** Interleaved generation of explicit thought traces and action calls. The format is: `Thought: ... Action: ... Observation: ...` repeated until done.

**Origin:** Yao et al. 2023, arXiv 2210.03629. "ReAct: Synergizing Reasoning and Acting in Language Models." Google Brain + Princeton.

**Why it mattered:** Pre-ReAct, models either reasoned (chain-of-thought) or acted (API calls). ReAct proved that interleaving the two outperformed both separately on knowledge-intensive tasks (HotpotQA, FEVER) and interactive decision-making tasks (AlfWorld, WebShop).

**Mechanism:** The `Thought:` step is free-form reasoning in natural language — it is not parsed, it just gives the model a place to "think aloud" before committing to an action. The observation after each action updates the model's belief state.

**When it applies:** Tasks where intermediate reasoning needs to be explicit and inspectable. Standard implementation in most tool-using LLMs today — GPT, Claude, Gemini all default to something ReAct-shaped.

**Failure mode:**
- Thought steps can be post-hoc rationalization rather than genuine reasoning
- Long action chains consume context; observations pile up
- Model can get stuck in thought-action-thought-action loops with no real progress ("hallucination of progress")

**Canonical implementation:** Nearly every framework that calls tools implicitly uses ReAct. LangChain's `create_react_agent`, LangGraph `ToolNode`, Claude's native tool-use loop.

---

### 2.3 Plan-and-Execute

**Definition:** Two-phase execution. Phase 1 (planner): decompose the goal into an ordered list of subtasks. Phase 2 (executor): execute each subtask deterministically, one at a time.

**When it applies:** Tasks with a clear decomposition structure; when you want to show the user a plan before taking irreversible actions; when subtasks are largely independent.

**Failure mode:**
- Plan quality is not verified before execution begins; a bad plan produces a lot of wasted work
- Plans go stale: an early subtask's result invalidates later subtask assumptions, but the plan doesn't update
- "Plan freeze": the executor is forced to execute a subtask that no longer makes sense given updated state

**Canonical implementation:** LangChain's `PlanAndExecute` agent (deprecated in favor of LangGraph), DeerFlow's `TodoListMiddleware` in plan mode (tracks task list across the thread), OpenHands Planning Mode beta (separate planning session before execution session).

**Key insight:** The planner and executor should use different prompts, and ideally different models. The planner benefits from maximum reasoning capacity; the executor benefits from maximum instruction-following precision. This is why Anthropic's Planner-Generator-Evaluator pattern uses three roles.

---

### 2.4 Reflexion (Self-Critique + Retry)

**Definition:** After a failed attempt, the agent generates a verbal critique of what went wrong, stores this critique in an episodic memory buffer, and retries with the critique as additional context.

**Origin:** Shinn et al. 2023, arXiv 2303.11366. "Reflexion: Language Agents with Verbal Reinforcement Learning." Princeton + MIT.

**Key result:** Reflexion achieved 91% pass@1 on HumanEval coding benchmark vs GPT-4's 80% at the time, without any weight updates. The improvement came from multi-trial verbal feedback alone.

**Mechanism:** Three roles: Actor (does the task), Evaluator (scores the outcome), Reflector (generates verbal lesson from failure). The reflective text is stored in a short episodic buffer, not just discarded. Subsequent trials see prior reflections.

**When it applies:** Tasks with binary or scalar feedback signals (code: tests pass or fail; math: answer correct or not); tasks where "trying again smarter" is cheaper than gradient descent.

**Failure mode:**
- Hallucinated reflection: the model convinces itself it failed for the wrong reason, stores a misleading lesson, and retries in the wrong direction
- Context creep: episodic buffer grows; eventually dominates the context
- No hard convergence guarantee; may iterate fruitlessly

**Canonical implementation:** Custom harness pattern; no single dominant library. The loop is: `attempt → evaluate → if failed: reflect + append to buffer → retry`.

---

### 2.5 State Machine / DAG (LangGraph)

**Definition:** Encode the workflow as an explicit directed graph. Nodes are LLM calls or tool calls; edges are transitions. State is typed and persisted at each node via checkpoints.

**When it applies:** Complex workflows with branching logic, parallel execution, human-in-the-loop gates, long-running sessions that must survive restarts.

**Failure mode:**
- Over-engineering: simple tasks don't need graph model; adds boilerplate and debugging complexity
- LangChain officially acknowledges: "use LangGraph for agents, not all LLM apps" (from prior G1 research)
- Graph topology becomes a bottleneck when task structure is not known at design time

**Canonical implementation:** LangGraph. DeerFlow 2.0's architecture wraps LangGraph as its agent runtime: `LangGraph Server (Port 2024) - Agent Runtime, Thread Mgmt, SSE Streaming, Checkpointing`. ThreadState extends LangGraph's AgentState with DeerFlow-specific fields (sandbox, artifacts, todos, viewed_images). (source: bytedance/deer-flow `backend/docs/ARCHITECTURE.md`)

**LangGraph specifics worth knowing:**
- **Checkpoints** persist the full TypedDict state after each node. This enables resume after failure and human interrupt.
- **Interrupt** mechanism: a node can call `interrupt(value)` to pause execution, surface state to the user, and resume only after human input is received. This is the canonical HITL implementation.
- **Conditional edges** are the branching primitive: a Python function inspects state and returns the next node name.

---

### 2.6 Hierarchical Multi-Agent (DeerFlow Lead + Sub)

**Definition:** A lead agent receives the goal, decomposes it, dispatches subtasks to specialized sub-agents, and synthesizes results. Sub-agents are not aware of the overall goal — only their assigned subtask.

**When it applies:** Tasks requiring diverse specialized capabilities (search + code + writing); tasks where parallel execution across sub-agents produces wall-clock speedup; tasks exceeding single-context limits.

**Failure mode:**
- Lead agent loses track of sub-agent results; synthesis quality degrades as the number of sub-agents grows
- Sub-agents operate with partial context and make locally rational but globally inconsistent decisions
- "Phone game" degradation: each handoff loses fidelity

**Canonical implementation:** DeerFlow 2.0. The `make_lead_agent` entry point in `packages/harness/deerflow/agents/lead_agent/agent.py` dispatches to configured sub-agents. The architecture also explicitly lists sub-agents in `config.yaml`. (source: bytedance/deer-flow architecture docs)

**Note from 00_master_synthesis:** Source analysis shows single agent + good tools outperforms multi-agent in pure coding scenarios. Multi-agent earns its cost only when sub-tasks are genuinely heterogeneous and can truly parallelize.

---

### 2.7 Handoff Pattern (OpenAI Agents SDK)

**Definition:** Agent A hands control to Agent B by calling a tool named `transfer_to_<agent_b>`. The calling agent's context is passed (with optional filtering) to the receiving agent. The receiving agent picks up from there.

**Mechanism:** Handoffs are represented as tools to the LLM — so the decision to hand off is itself a model-generated action. The `handoff()` function in the SDK allows: custom tool descriptions, input schemas (structured payload from A to B), input filters (scrub or reshape context), and `on_handoff` callbacks (e.g., kick off data fetching the moment a handoff is invoked). (source: openai.github.io/openai-agents-python/handoffs/)

**When it applies:** Customer-support triage; multi-domain systems where each domain is cleanly separable; when you want each agent to have a narrow, well-specified purpose.

**Failure mode:**
- Handoff storms: agent A hands to B, B hands to C, C hands back to A — infinite loop
- Context loss: if input_filter is too aggressive, the receiving agent lacks necessary background
- Model chooses the wrong handoff target because tool descriptions are ambiguous

**Key design principle:** Each agent should have a clear `handoff_description` that tells the triage model when — and only when — to route to it.

---

## Section 3: Planner / Executor Separation — Deep Dive

### Why separation matters

When a single agent plans and executes simultaneously, it conflates two cognitively distinct operations:
1. **Strategic reasoning**: What is the right decomposition of this goal? What might go wrong?
2. **Tactical execution**: Given this specific subtask, what is the exact sequence of tool calls?

Mixing these in one prompt is like asking an architect to also lay bricks — the context for one contaminates the other. The planner needs high-level world knowledge and goal understanding; the executor needs precise instruction-following and error recovery.

**Anthropic's Planner-Generator-Evaluator (PGE) framework** formalizes this into three roles:
- **Planner** (also called Orchestrator): high-level decomposition, task assignment
- **Generator** (also called Worker/Executor): executes one subtask with tools
- **Evaluator**: checks the Generator's output against criteria; triggers retry if needed

This pattern appears independently across multiple production systems — convergence C from 00_master_synthesis.

### Aider Architect Mode — Concrete Implementation

Aider has four chat modes: `code`, `ask`, `architect`, `help`. (source: aider.chat/docs/usage/modes.html)

In `architect` mode: "An architect model will propose changes and an editor model will translate that proposal into specific file edits."

Practically:
- **Architect model** (typically a larger, more reasoning-capable model): receives the change request + repo map, produces a high-level description of what changes are needed across which files
- **Editor model** (typically a faster, instruction-following model): receives the architect's description + actual file contents, produces the diff

The two models run in sequence. The architect never sees raw diffs; the editor never reasons about architecture. This separation is not just about cost (routing cheap tasks to cheap models) — it is about **prompt specialization**: each model's context is optimized for its role.

**Key insight from Aider:** The architect model's output is not code — it is a structured natural-language description of intent. This keeps the architect's context small and reasoning-focused. The editor's context can be large (full file contents) because it needs no reasoning, only precision.

### OpenHands Planning Mode (Beta, March 2026)

OpenHands introduced an explicit "planning mode" separate from execution. In planning mode, the agent generates a structured task list and presents it to the user for approval before executing. This is the HITL checkpoint at the planning stage — the highest-leverage intervention point because it catches errors before any irreversible action is taken.

Source: OpenHands release notes / blog (March 2026) — direct fetch failed, status INDIRECT based on master synthesis reference.

### When NOT to separate

Separation has overhead: two LLM calls instead of one, context formatting between phases, latency increase. Do not separate when:
- The task has 2-3 steps that can be enumerated trivially
- The task is in a single domain (one tool, one file)
- You are in an interactive REPL where the user provides replanning on each turn
- Context is tight (small models, small windows)

Rule of thumb: if you can write the plan in one sentence, the planner is free overhead.

### Open question: plan quality assessment

How do you judge a plan before executing it? There is no consensus. Options in practice:
1. **LLM-as-judge**: a second model evaluates plan quality against criteria (but this doubles cost before a single action is taken)
2. **Schema validation**: require the plan to be structured JSON and validate against a schema (catches format errors, not reasoning errors)
3. **Human approval**: the most reliable but the least scalable (OpenHands Planning Mode does this)
4. **Canary execution**: execute the first step of the plan and check for early signals before committing to the rest

This is an open engineering problem. There is no free lunch.

---

## Section 4: Tool System Design

### Why tool descriptions are the highest-leverage text you write

The LLM decides which tool to call based almost entirely on the tool's name and description. A bad description is a miscommunication that happens silently on every invocation. Anthropic states this is a core principle: "Carefully craft your agent-computer interface (ACI) through thorough tool documentation and testing." (anthropic.com/research/building-effective-agents)

**Common anti-patterns:**
- **Vague names:** `do_thing()` vs `search_arxiv_by_keyword()`
- **Missing parameter contracts:** not specifying expected format, units, or constraints for each parameter
- **No boundary statement:** not saying when the tool should NOT be used (forces the model to guess)
- **Overlapping tools:** two tools that seem interchangeable; model picks arbitrarily
- **Missing error behavior:** not saying what the tool returns on failure

**What good descriptions contain:**
1. What the tool does (one sentence)
2. When to use it (trigger conditions)
3. When NOT to use it (anti-triggers)
4. Parameter semantics: format, units, constraints
5. Return value semantics: shape, what null/empty means

### The problem of tool count vs accuracy

Accuracy degrades as tool set size grows. The widely cited data point in the field: with 300+ tools, accuracy drops to ~62% even with the best available models. (Note: this figure circulates in the practitioner community but the primary source is an internal Berkeley / scale-up study; treat as directionally correct, not precisely citable.)

The mechanism: when the tool list is large, the model's token budget for "scanning" available tools competes with its reasoning budget. The model is more likely to mis-select a tool or hallucinate a non-existent one.

**Solutions in production:**
1. **Progressive disclosure / lazy loading:** don't expose all tools upfront. Load a directory of tool metadata; the model requests the full spec for tools it wants to use. OpenAI Agents SDK's `ToolSearchTool` implements this explicitly: "The ToolSearchTool lets the model load deferred tools, namespaces, or..." (openai.github.io/openai-agents-python/tools/)
2. **Tool namespacing:** group tools into domains; expose only the relevant domain's tools per agent
3. **Routing first:** a cheap classifier decides which toolset is relevant before the main agent sees any tool

### MCP vs Function Calling vs Anthropic Skills: Three Models for Tool Exposure

| Dimension | Function Calling (OpenAI/Anthropic native) | MCP (Model Context Protocol) | Anthropic Claude Code Skills |
|---|---|---|---|
| **Who defines tools** | Developer in code | MCP server operator | Skill author in markdown |
| **Discovery** | Static — listed in the API call | Dynamic — MCP server exposes tool list at connect time | Directory scan at session start |
| **Runtime** | In-process | Separate process (stdio or HTTP) | Sub-agent / skill invocation |
| **Composability** | Per-call | Protocol-level (multiple servers) | File-based composition |
| **Best for** | Tightly integrated, low-latency tools | Cross-application tool sharing, third-party integrations | Persona-based specialized agents |

**MCP (Model Context Protocol, modelcontextprotocol.io):** A client-server protocol where the MCP server maintains tool definitions and the harness acts as a client. DeerFlow 2.0 supports MCP via `extensions_config.json` — MCP tools are one of three sources alongside built-in tools and `config.yaml` tools. The key MCP value proposition is that the same tool can be exposed to multiple harnesses without re-implementing it for each.

**Key architectural question:** MCP is network-transparent — the server can be remote. This introduces latency and reliability concerns that in-process function calling does not have. For high-frequency tools (called dozens of times per agent run), in-process function calling wins on latency. For ecosystem tools (e.g., GitHub, Slack, JIRA integrations), MCP wins on reuse.

### Tool result post-processing: why raw returns are wrong

When a tool returns 50,000 characters of JSON, or a 300-line stack trace, the raw return floods the context window. Every subsequent LLM call in the same thread carries this dead weight.

**Why this matters practically:**
- LLM attention degrades with distance from the current turn; a large observation from 10 turns ago is nearly invisible
- Large observations push newer context out of the window in sliding-window scenarios
- Verbatim error messages often contain internal details that confuse rather than help the model

**Solutions:**
1. **Structured truncation:** take the first N lines, or the last N lines, depending on whether you care about head or tail of the result
2. **Summarization at tool boundary:** a lightweight LLM call that turns raw output into a structured summary before it enters the agent's context
3. **Typed extraction:** parse the JSON response and extract only the fields the agent needs; discard the rest
4. **Error normalization:** convert all tool errors to a single `{error: string, code: int, retryable: bool}` schema so the agent has consistent failure handling

DeerFlow's `SummarizationMiddleware` (part of its middleware chain) does exactly this — it reduces context before it reaches the agent core.

### "Tools that don't exist yet" — hallucinated tool names

When the model invokes a tool name that does not exist, two things can happen:
1. **Hard crash:** the harness throws an exception; the agent run aborts
2. **Silent error:** the harness returns an error string to the model; the model either retries or hallucinates a "successful" result

The harder problem: the model may be inventing a tool it legitimately needs, and the tool should be built. Hallucinated tool names are sometimes a signal that the tool inventory is incomplete.

**Handling strategies:**
1. **Strict mode:** reject unknown tool names immediately; surface to user/developer
2. **Fuzzy match + confirmation:** find the closest matching tool, ask the model to confirm it meant that one
3. **Graceful degradation:** return `{"error": "tool not found", "available_tools": [...]}` and let the model recover

The signal should always be logged. Repeated hallucination of the same tool name is a strong indicator to build that tool.

---

## Section 5: Control Flow Specifics

### Retry strategies

Exponential backoff is the right primitive for **rate limits and transient network errors**. It is NOT the right primitive for **LLM reasoning failures**.

The distinction:
- If `tool_call` fails because of a 429 rate limit, retry with backoff is correct — the error is external and temporary
- If `tool_call` fails because the model passed the wrong argument, retrying immediately with the same input will fail again
- If the model generates a bad plan, no amount of retrying will fix it without new information

**LLM-specific retry pattern:**
```
attempt → failure → classify failure type:
  - External (rate limit, timeout): exponential backoff + retry
  - Model error (bad argument, wrong tool): enrich context with error message + retry once
  - Reasoning error (wrong approach): Reflexion cycle or HITL checkpoint
  - Irrecoverable: abort + surface to user
```

The number of retries must be bounded. Unbounded retry loops are the most common cause of runaway costs in production agents.

### Interrupts and HITL Handoff (LangGraph)

LangGraph's `interrupt()` primitive pauses graph execution at a node, persists the current state via checkpoint, and waits for external input. The implementation:

1. Node calls `interrupt(value)` — `value` is what to show the human
2. LangGraph serializes the current `ThreadState` to persistent storage
3. The run returns with a `INTERRUPTED` status
4. The harness surfaces the interrupt value to the user via UI/API
5. User provides input via `update_state()` call
6. The run resumes from the checkpoint with the human's input injected into state

This is the production-grade pattern for approval gates. Every irreversible or high-stakes action (file deletion, API write calls, financial transactions) should be preceded by an interrupt.

**HITL trigger heuristics:**
- Action is irreversible
- Action has external side effects (email, webhook, database write)
- Agent confidence score (if available) is below threshold
- Task has been running for more than N iterations without a terminal signal

### Parallel Tool Execution: When Safe

Multiple tools can execute in parallel when they have no data dependencies between them — each tool call does not need the result of the other to produce its own result.

**Safe for parallel:** independent web searches, reading multiple files, calling multiple read-only APIs

**Unsafe for parallel:** sequential writes to the same resource, tool B needs tool A's output, tool execution order affects the environment's state

Anthropic notes parallelization is useful for: "sectioning" (independent subtasks run in parallel) and "voting" (same task multiple times for confidence). (anthropic.com/research/building-effective-agents)

OpenAI Agents SDK supports agents-as-tools, which means a sub-agent can be called in parallel as a tool call alongside other tools — the orchestrating model fires multiple tool calls in one completion and they execute concurrently.

### Long-Running Operations: Architecture Implications

Tasks that take minutes to hours (deep research, large codebase refactors, multi-source report generation) break several assumptions of synchronous agent runs:

1. **Context window exhaustion:** a 200k token context fills up in a long run; mid-task context reset destroys reasoning continuity
2. **Connection timeout:** HTTP/SSE connections time out before the task completes; the client loses the result
3. **No resumability:** if the process crashes at minute 47, work is lost

**Architecture patterns for long-running tasks:**

| Problem | Solution |
|---|---|
| Context exhaustion | Progressive summarization (DeerFlow's `SummarizationMiddleware`); explicit memory writes at checkpoints |
| Connection timeout | Async task queue + polling / webhook notification; DeerFlow uses SSE streaming with LangGraph Server on Port 2024 |
| No resumability | LangGraph checkpointing: every node's completion is persisted; restart from last checkpoint |
| Cost runaway | Hard iteration cap; soft cost cap with user notification |

DeerFlow's deployment sizing guide is instructive: for long-running multi-agent runs, "long-running server / `make up`: 8 vCPU, 16 GB RAM, 40 GB free SSD" (bytedance/deer-flow README). The implication: long-running tasks are a resourcing problem, not just a code architecture problem.

---

## Section 6: Patterns vs Anti-Patterns

| Pattern | Anti-Pattern | Why the anti-pattern fails |
|---|---|---|
| Separate planner and executor | Single LLM does plan + execute simultaneously | Strategic and tactical reasoning interfere; errors in one contaminate the other |
| Bounded retry loops | Unbounded retry on any failure | Cost explosion; hallucination loops; false progress |
| Typed state with explicit transitions (LangGraph) | Implicit state via appended messages | State becomes unauditable; impossible to resume from checkpoint |
| Tool descriptions with trigger + anti-trigger | Tool names only, no descriptions | Model guesses usage; wrong tool called silently |
| Progressive tool loading (ToolSearchTool / skills directory) | All 300+ tools in every system prompt | 62% accuracy ceiling; context bloat on every call |
| Post-process tool output before it enters context | Pass raw tool output directly to next LLM call | Context poisoning; attention degradation; window overflow |
| HITL interrupts at irreversible actions | HITL "whenever possible" | HITL overhead kills UX; should be reserved for high-stakes moments |
| Handoffs via explicit transfer tool | Implicit context injection | Model has no clear signal to switch agents; context bleed between agents |
| Classify failure type before retry | Blanket exponential backoff on all errors | LLM reasoning failures are not network transients; backoff does not help |
| Hard termination condition (max_iterations + success signal) | Hope the model stops naturally | Open-ended loops consume infinite tokens; no production agent should be boundless |

---

## Section 7: Four Concrete Failure Scenarios

### Scenario A: The Runaway Loop

**Symptom:** Agent makes 200 tool calls, burns $50 in tokens, produces no result. Dashboard shows "running" indefinitely.

**Execution-layer cause:** No termination condition. The model's ReAct loop keeps calling `search()` because each search result feels incomplete — there is always more to find. No max_iterations cap. No "good enough" signal.

**Fix:**
1. Add hard `max_iterations=25` (or appropriate number for the task)
2. Add a soft check: after N iterations, inject a message "You have made N tool calls. Summarize what you have and provide a final answer, even if incomplete."
3. Monitor: alert if cost per run exceeds threshold

**Who discussed it:** Anthropic "building effective agents" — "it's also common to include stopping conditions (such as a maximum number of iterations) to maintain control."

---

### Scenario B: Plan Staleness in Plan-and-Execute

**Symptom:** Agent executes step 3 of a 5-step plan. Step 3 reveals the file structure is different from assumptions. Steps 4-5 reference files that do not exist. Agent fails on step 4 with a confusing error.

**Execution-layer cause:** Plan was generated once at the start based on incomplete information. Plan-and-execute does not re-plan when new information invalidates assumptions. The planner's world model is frozen.

**Fix:**
1. Add a re-planning gate: after each step, ask "does this result change the plan? If yes, produce an updated plan."
2. Alternatively, use an orchestrator-workers pattern (Anthropic) instead of plan-and-execute: the orchestrator dynamically breaks down tasks and adjusts based on worker results
3. Mark plan steps as "conditional" with explicit branching conditions

**Who discussed it:** Anthropic — "the key difference from parallelization is its flexibility — subtasks aren't pre-defined, but determined by the orchestrator based on the specific input."

---

### Scenario C: Tool Description Ambiguity Cascade

**Symptom:** Agent is supposed to search internal documents but keeps calling the web search tool instead. Internal results are never consulted.

**Execution-layer cause:** `web_search()` description says "search for information." `internal_docs_search()` description says "search internal documentation." When the task says "find information about X," the model picks `web_search` because the trigger is more generic and the description does not specify when internal search is preferred.

**Fix:**
1. Add anti-trigger to `web_search`: "Use this for publicly available information. Do NOT use this if the query is about internal company processes, policies, or proprietary data."
2. Add trigger to `internal_docs_search`: "Use this FIRST for any query that may relate to internal systems, processes, policies, team information."
3. Ordering matters: list preferred tools first in the tool list (models exhibit position bias)

**Who discussed it:** Anthropic Appendix 2 "Prompt Engineering your Tools" — thorough documentation and testing of the agent-computer interface.

---

### Scenario D: Context Poisoning from Raw Tool Output

**Symptom:** Agent successfully retrieves a large JSON API response (15,000 tokens). All subsequent reasoning is degraded. The model starts making errors it wouldn't make on a fresh context.

**Execution-layer cause:** The raw 15,000-token JSON is appended to the conversation history. It occupies a large fraction of the context window. The model's effective attention to the task description and prior reasoning drops. Recency bias means the model treats the noisy JSON as the most important context.

**Fix:**
1. Post-process tool output: extract only relevant fields from the JSON before returning to the model
2. Add a summarization step: "You have received a large API response. Here are the 5 most relevant fields: ..."
3. Use DeerFlow's `SummarizationMiddleware` pattern: reduce context size as part of the middleware chain, not ad hoc in the tool itself

**Who discussed it:** DeerFlow architecture docs (`SummarizationMiddleware` - Context reduction); convergence D from 00_master_synthesis (progressive disclosure / on-demand loading).

---

## Section 8: What a Learner Should Internalize

### Mental Model 1: The Loop Is the Atom

Everything is an elaboration of: `observe → reason → act → observe`. Before adding any architectural complexity, ask: is my loop broken? A loop with a bad termination condition, a loop without error classification, a loop without context management — these are the 90% case. Fix the loop first.

### Mental Model 2: Separation of Concerns Scales, Conflation Does Not

The reason Planner/Executor separation recurs across Anthropic, Aider, DeerFlow, and OpenHands independently is not fashion — it is engineering necessity. Every time you ask a single prompt to do two distinct cognitive operations, you degrade both. The right question is not "should I separate?" but "where is the cognitive boundary in my specific task?"

### Mental Model 3: Tools Are an API Contract, Not Code

Tool descriptions are not documentation for humans — they are the interface the LLM uses to decide what to call. Bad tool descriptions are bugs. They are silent bugs: the wrong tool is called, no exception is raised, and the agent produces a subtly wrong result. Write tool descriptions with the same care as function signatures in a typed language.

### Mental Model 4: Control Flow Is a Spectrum, Not a Binary

"Deterministic graph" and "open loop" are poles, not categories. In practice, every production system is a hybrid: a state machine with LLM-driven transitions, or an LLM loop with a hard-coded approval checkpoint. The skill is knowing where to add determinism (around irreversible actions, at quality gates) and where to allow flexibility (within execution subtasks, in tool selection).

### Mental Model 5: Failures Have Types, and Type Determines Response

Network failures → retry with backoff. Bad model arguments → enrich context and retry once. Bad plan → replan or HITL. Reasoning loop → Reflexion or abort. Treating all failures as "retry" is the single most common source of runaway cost and confusing behavior in production agents.

---

## Section 9: Further Reading with Ratings

| Source | What it teaches | Rating | URL |
|---|---|---|---|
| Anthropic "Building Effective Agents" (Dec 2024) | Canonical taxonomy: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer; tool engineering best practices | ★★★★★ Essential | anthropic.com/research/building-effective-agents |
| ReAct paper (Yao et al. 2023) | Original interleaved reasoning+acting; benchmark evidence; still the theoretical foundation for most tool-use implementations | ★★★★ Important | arxiv.org/abs/2210.03629 |
| Reflexion paper (Shinn et al. 2023) | Verbal reinforcement learning; no gradient updates; episodic reflection buffer; 91% HumanEval | ★★★★ Important | arxiv.org/abs/2303.11366 |
| DeerFlow 2.0 Architecture docs | Production-grade hierarchical multi-agent with LangGraph; middleware pattern; sandbox isolation; SSE streaming | ★★★★ Highly practical | github.com/bytedance/deer-flow (backend/docs/ARCHITECTURE.md) |
| OpenAI Agents SDK (handoffs, tools docs) | Handoff as tool; input filters; agents-as-tools; HITL approval gates; ToolSearchTool for deferred loading | ★★★★ Highly practical | openai.github.io/openai-agents-python/ |
| Aider chat modes docs | Architect mode: concrete planner/executor separation in a shipping product | ★★★ Good illustration | aider.chat/docs/usage/modes.html |
| Lilian Weng "LLM Powered Autonomous Agents" (2023) | Original taxonomy: Planning / Memory / Tools; CoT, ToT, ReAct, Reflexion overview; still the best survey | ★★★★ Survey reference | lilianweng.github.io/posts/2023-06-23-agent/ |
| LangGraph docs (checkpointing, interrupt) | Graph execution model; checkpoint persistence; interrupt() for HITL; thread state management | ★★★★ Essential for graph-based builds | docs.langchain.com/oss/python/langgraph/ |
| MCP specification | Protocol spec for cross-harness tool sharing; how servers expose tool lists; client implementation | ★★★ Good for ecosystem tools | modelcontextprotocol.io/introduction |

---

## Section 10: Source Reliability Notes

| URL | Status | Notes |
|---|---|---|
| anthropic.com/research/building-effective-agents | **DIRECT** | Full page retrieved; text extracted; extensively quoted |
| arxiv.org/abs/2210.03629 (ReAct) | **DIRECT** | Abstract and metadata retrieved; paper content available via PDF link |
| arxiv.org/abs/2303.11366 (Reflexion) | **DIRECT** | Full abstract retrieved and quoted verbatim; results confirmed |
| github.com/bytedance/deer-flow (README) | **DIRECT** | Full README retrieved; DeerFlow 2.0 architecture confirmed |
| github.com/bytedance/deer-flow (backend/docs/ARCHITECTURE.md) | **DIRECT** | Full architecture doc retrieved; component diagrams, middleware chain, tool sources confirmed |
| aider.chat/docs/usage/modes.html | **DIRECT** | Full page retrieved; architect mode description confirmed |
| openai.github.io/openai-agents-python/handoffs/ | **DIRECT** | Page retrieved; handoff mechanism, input filters, callbacks confirmed |
| openai.github.io/openai-agents-python/tools/ | **DIRECT** | Page retrieved; tool categories, ToolSearchTool, agents-as-tools confirmed |
| lilianweng.github.io/posts/2023-06-23-agent/ | **DIRECT** | Page retrieved; Planning/Memory/Tools taxonomy, ReAct/Reflexion discussion confirmed |
| langchain-ai.github.io/langgraph/ | **INDIRECT** | Redirects to docs.langchain.com; redirect confirmed; content behind JS render; details derived from DeerFlow architecture docs (which use LangGraph) + prior G1 research |
| modelcontextprotocol.io/introduction | **INDIRECT** | Page loads as Next.js app; JS-rendered content not extractable via curl; spec details derived from DeerFlow extension config references and OpenAI Agents SDK MCP tool documentation |
| OpenHands Planning Mode (March 2026) | **FAILED** | No direct fetch; existence confirmed via 00_master_synthesis reference and B2 specification; treat as INDIRECT |

**Source stats summary:** 9 URLs attempted. DIRECT: 8. INDIRECT: 2. FAILED: 1.

---

*B2 建造完毕。B3（质量层：Evals / Constraints / Recovery）是下一块。*
