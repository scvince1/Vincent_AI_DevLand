---
id: github_ecosystem_2026-04
title: Harness Engineering Ecosystem — GitHub Research Report
tags: [harness, knowledge, ecosystem, github, agent-frameworks]
status: confirmed
last_modified: 2026-04-15
summary: Agent/harness engineering 领域主要 GitHub 项目 star 数与活跃度核查
---
# Harness Engineering Ecosystem: GitHub Research Report

**Source:** G1 scout agent
**Date:** 2026-04-14
**Scope:** Major GitHub projects in the agent/harness engineering ecosystem, star counts and activity verified via live API calls.

---

## Tier-1 Projects (Must-Know, High Impact)

### LangGraph
- **Repo:** https://github.com/langchain-ai/langgraph (~29.3K ⭐; LangChain parent ~97K ⭐)
- **Positioning:** Graph-based stateful agent orchestration; de facto standard for deterministic, auditable multi-step workflows.
- **Layers:** Execution orchestration (primary), Context (checkpointing), Memory & state, Constraints & recovery (interrupts + HITL + retry)
- **Recent:** v1.0 GA Oct 2025; currently v1.1.7a2 (Apr 2026). Added graph lifecycle callback handlers; CLI remote build. LangChain publicly redirects users: "use LangGraph for agents, not LangChain."
- **Why matters:** Most battle-tested framework for workflows needing explicit state transitions, checkpointing, and HITL interrupts. langchain-ai/deepagents demonstrates harness pattern built on top.

### Microsoft AutoGen
- **Repo:** https://github.com/microsoft/autogen (~57.1K ⭐)
- **Positioning:** Most-starred Python agent framework; multi-agent conversational.
- **Layers:** Execution orchestration, Tool system (MCP), Memory & state (RedisMemory), Constraints (approval_func)
- **Recent:** Being merged with Semantic Kernel into unified Microsoft Agent Framework (GA Q1 2026). Released Microsoft Agent Governance Toolkit April 2026.

### OpenHands (formerly OpenDevin)
- **Repo:** https://github.com/OpenHands/OpenHands (~71.2K ⭐)
- **Positioning:** Leading open-source autonomous software-engineering agent; full sandboxed execution.
- **Layers:** All six (orchestration + tools + constraints + eval via SWE-bench integration)
- **Recent:** v1.6.0 (Mar 30 2026) added Kubernetes support + Planning Mode beta (agent produces plan, requests approval before execution). $18.8M Series A.

### modelcontextprotocol/servers (MCP)
- **Repo:** https://github.com/modelcontextprotocol/servers (~83.7K ⭐)
- **Positioning:** Official MCP server implementations; emerging standard protocol for Tool System layer.
- **Recent:** Adopted by OpenAI, Google, Microsoft, Amazon. 1,200+ community servers. 2026 roadmap targets production gaps: authorization, lifecycle management, multi-server composition.

### mem0 (Universal Memory Layer)
- **Repo:** https://github.com/mem0ai/mem0 (~53K ⭐)
- **Positioning:** Drop-in production memory layer for any agent framework.
- **Layers:** Memory & state (primary) -- short-term, long-term, cross-session, user/task/agent state
- **Recent:** v1.0.3 (Jan 2026) added project-level memory config. Cassandra support added. Benchmarked 91% lower p95 latency vs full-context retrieval (1.44s vs 17.12s).

### Cline
- **Repo:** https://github.com/cline/cline (~60.3K ⭐)
- **Positioning:** Most-starred open-source IDE-native autonomous coding agent (VS Code).
- **Layers:** Orchestration, Tools, Context (visible token management), Constraints (every step requires explicit user approval = hard HITL)
- **Note:** Spawned Roo-Code (Roo-Cline) fork. The permission-step HITL model is its defining harness design choice.

### LiteLLM
- **Repo:** https://github.com/BerriAI/litellm (~43.3K ⭐)
- **Positioning:** Universal LLM proxy/gateway; infrastructure layer beneath all agent frameworks.
- **Layers:** Tools (routing/fallback), Context (caching/cost), Constraints (rate limiting, project guardrails)
- **Recent:** 140+ provider support; A2A protocol handling, project-level guardrails, tag-based routing.

### Langfuse
- **Repo:** https://github.com/langfuse/langfuse (~24.9K ⭐)
- **Positioning:** #1 open-source LLM observability; self-hostable.
- **Layers:** Evaluation & observation (distributed tracing, session replay, LLM-as-judge eval)

### DeerFlow (ByteDance)
- **Repo:** https://github.com/bytedance/deer-flow (~61.5K ⭐)
- **Positioning:** Production-grade open-source "SuperAgent harness"; the most explicit use of "harness" as an architectural term in a major repo.
- **Layers:** All six -- explicitly structured as a harness.
- **Recent:** DeerFlow 2.0 released Feb 27 2026 as a ground-up rewrite. Hit #1 on GitHub Trending within 24 hours. Internal package named `deerflow-harness`, explicitly publishable as standalone agent framework. Built on LangGraph + LangChain.
- **Why matters:** Most direct reference implementation of "Agent = Model + Harness" in production codebase.

---

## Tier-2 Projects (Worth Tracking)

| Project | Repo | Stars | Primary Layers | Note |
|---------|------|-------|---------------|------|
| CrewAI | crewAIInc/crewAI | ~48.9K | Orchestration, Tools | Most beginner-friendly multi-agent; some migrate away as complexity grows |
| Google ADK | google/adk-python | ~19K | Orchestration, Tools (A2A), Eval | Google Cloud first-party SDK |
| OpenAI Agents SDK | openai/openai-agents-python | ~20.8K | Orchestration (handoffs), Constraints, Tools | Successor to Swarm; minimal handoff pattern reference |
| Mastra | mastra-ai/mastra | ~23K | Orchestration, Context, Memory, Tools | TS-native; Mastra Studio IDE; from Gatsby team |
| Pydantic-AI | pydantic/pydantic-ai | ~16.4K | Tools (type-safe), Context (DI), Orchestration | Best for Python teams wanting strict types |
| A2A Protocol | a2aproject/A2A | ~23.2K | Agent-to-agent routing | Google-donated to Linux Foundation; v0.3 gRPC support |
| AG-UI Protocol | ag-ui-protocol/ag-ui | ~13K | Constraints (HITL), Tools (streaming to frontend) | Third protocol edge: agent ↔ frontend |
| Composio | ComposioHQ/composio | ~27.8K | Tools (250+ SaaS integrations, OAuth) | MCP catalog for business apps |
| Playwright-MCP | microsoft/playwright-mcp | ~30.8K | Tools (browser automation via a11y tree) | Accessibility tree > screenshots = order-of-magnitude less token |
| Aider | Aider-AI/aider | ~43.3K | Context (git diff), Orchestration (architect mode) | Two-agent planner/executor split reference |
| Langroid | langroid/langroid | ~4K | Orchestration (message-passing) | Lighter than LangGraph/AutoGen |
| DSPy | stanfordnlp/dspy | ~33.7K | Context (prompt compilation), Eval | Prompts as programs; self-improving harness direction |
| NeMo Guardrails | NVIDIA-NeMo/Guardrails | ~6K | Constraints (Colang DSL), Observability | Most complete Constraints layer impl |
| Arize Phoenix | Arize-ai/phoenix | ~9.3K | Eval & observation | Between Langfuse (tracing) and Braintrust (evals) |
| Promptfoo | promptfoo/promptfoo | ~20.1K | Eval (YAML regression), Constraints | Acquired by OpenAI Mar 9 2026; remains OSS |
| Agno (ex-PhiData) | agno-agi/agno | ~39.4K | Orchestration, Tools, Memory | "No graphs, no chains, pure Python" -- lightweight alt to LangGraph |
| Outlines | dottxt-ai/outlines | ~13.7K | Tools (structured output via constrained sampling) | JSON Schema / regex / CFG at token-level |

---

## Emerging / Surprise Finds

- **HKUDS/OpenHarness** (~9.6K ⭐, 13 days old) -- HKU/HippoRAG lab, explicitly named "harness". Recent additions: MCP HTTP transport, multi-provider auth, built-in personal agent "Ohmo".
- **AG-UI Protocol** (~13K ⭐, under 1 year) -- standardizes agent-to-frontend streaming (MCP and A2A don't cover this edge).
- **Playwright-MCP** (30.8K ⭐ in 13 months) -- accessibility-tree approach is a harness design lesson: tool output shape matters as much as capability.
- **Pydantic DeepAgents** (vstorm-co/pydantic-deepagents) -- Claude Code-style deep agent built as publishable harness library on Pydantic-AI.
- **OpenLLMetry** (traceloop/openllmetry, ~7K ⭐) -- semantic conventions for LLM calls as first-class OTel spans; signals observability is standardizing on OpenTelemetry.
- **LM Evaluation Harness** (EleutherAI, ~12.2K ⭐) -- the canonical few-shot eval framework; the word "harness" in its name is not coincidental.

---

## Ecosystem Observations

### Architectural patterns winning
1. **Graph-based state machines** for deterministic workflows (LangGraph)
2. **Planner/Executor split** (Aider architect, OpenHands Planning, DeerFlow lead/subagent)
3. **Protocol-first tool integration** (MCP winning; A2A + AG-UI extending)
4. **Memory as separate service** (mem0, Zep, Letta all chose this)
5. **Type-safe structured outputs** as first-class harness primitive (Pydantic-AI, Instructor, Outlines)

### Active debates
- LangGraph overhead vs power for simple workflows
- AG-UI long-running HITL tool call streaming (open bug)
- MCP 2026 roadmap: multi-server composition, authorization, lifecycle
- A2A governance post-Google donation
- Pydantic-AI #3179: integrate DSPy-style algorithmic optimizers?

### Losing momentum
- **LangChain core** -- LangChain company redirects users to LangGraph
- **LlamaIndex RAG-first framing** -- Jerry Liu publicly acknowledged erosion by coding agents + MCP + purpose-built SDKs
- **OpenAI Swarm** -- labeled "educational only"; Agents SDK is the production recommendation
- **Heavyweight 2023-era framework abstractions** -- frontier models handle native function calling at a level that makes many abstractions actively harmful to debuggability

### Consolidation
- Microsoft: AutoGen + Semantic Kernel → Microsoft Agent Framework (Q1 2026)
- OpenAI: acquired Promptfoo (Mar 2026)
- Linux Foundation: received A2A + Goose; becoming neutral home for agent infra standards
- LangChain ecosystem: LangGraph + LangSmith increasingly dominate production users (vendor-coupling risk)

---

## Recommended Deep-Dive Targets

If you want to understand harness design at source level, read these five:

1. **bytedance/deer-flow** -- Most explicit real-world layered harness. `deerflow-harness` package never imports from app layer. Start: `packages/harness/deerflow/`
2. **OpenHands/OpenHands** -- Most complete open-source six-layer implementation in one codebase. `software-agent-sdk` sub-package is the teachable version.
3. **langchain-ai/langgraph** -- Clearest state-machine orchestration source. Checkpointing, interrupt/resume, thread/run model.
4. **cline/cline** -- Most readable "every tool call requires approval" HITL. Transparent context management UX.
5. **modelcontextprotocol/servers + ag-ui-protocol/ag-ui** (pair) -- The boundary protocol stack. MCP = agent↔tool; AG-UI = agent↔frontend.

---

## Uncertainty flags
- Aider repo moved `paul-gauthier/aider` → `Aider-AI/aider` (old redirect may split third-party star counts)
- block/goose transferred to Linux Foundation's Agentic AI Foundation; primary repo may move
- Microsoft Agent Framework (AutoGen + SK merger) doesn't yet have single canonical OSS repo URL as of Apr 14 2026
- Braintrust is closed-source; no star count available
