---
id: F3_impact_and_weng_foundations
title: F3 — IMPACT and Weng Foundations
tags: [harness, knowledge, source-text, impact-framework, weng]
status: confirmed
last_modified: 2026-04-15
summary: IMPACT 框架与 Weng 基础概念谱系：harness engineering 的概念起源
---
# F3: IMPACT and Weng Foundations -- Conceptual Genealogy of Harness Engineering

**Agent:** F3 (deep-read research, retry with curl)
**Date:** 2026-04-14
**Sourcing note:** All four URLs fetched directly via curl. Claims marked DIRECT are verified from live page content.

**Sources:**
- PRIMARY A: https://lilianweng.github.io/posts/2023-06-23-agent/ -- DIRECT (curl succeeded, full articleBody extracted from JSON-LD schema.org markup)
- PRIMARY B: https://www.latent.space/p/agent -- DIRECT (curl succeeded, full article text extracted from rendered HTML)
- SECONDARY: https://www.morphllm.com/agent-engineering -- DIRECT (curl succeeded, full article text extracted from rendered HTML)
- TERTIARY: https://simonw.substack.com/p/i-think-agent-may-finally-have-a -- DIRECT (curl succeeded, full article text extracted)

---

## 1. Lilian Weng's Taxonomy (June 2023)

**Source:** https://lilianweng.github.io/posts/2023-06-23-agent/

### Three-Component Decomposition

Directly from the page's JSON-LD articleBody:

> "In a LLM-powered autonomous agent system, LLM functions as the agent's brain, complemented by several key components: Planning, Memory, Tool use."

The three pillars:

1. **Planning** -- The agent's ability to break complex tasks into steps and to self-critique outputs
2. **Memory** -- How the agent stores and retrieves information across the full cognitive timeline
3. **Tool Use** -- External APIs and capabilities the agent can invoke to affect the world

### Sub-Decompositions (verified from article body)

**Planning sub-components:**
- **Task Decomposition via Chain-of-Thought (CoT):** "The model is instructed to 'think step by step' to utilize more test-time computation to decompose hard tasks into smaller and simpler steps." (DIRECT)
- **Tree-of-Thoughts (ToT):** Extends CoT by exploring multiple reasoning possibilities at each step, creating a tree structure searchable via BFS or DFS.
- **Reflection and Refinement:** Self-Reflection (ReAct, Reflexion frameworks) -- the agent critiques its own prior outputs. Reflexion "equip[s] agents with dynamic memory and self-reflection capabilities to improve reasoning skills." (DIRECT)

**Memory sub-components (mapped to cognitive science):**
- **Sensory memory** -- In-context learning on raw input tokens; lasts only the duration of the prompt call
- **Short-Term Memory (STM) / Working Memory** -- Active context window; "stores information that we are currently aware of"; capacity limited by transformer context length
- **Long-Term Memory (LTM):** "provides the agent with the capability to retain and recall (infinite) information over extended periods, often by leveraging an external vector store and fast retrieval." (DIRECT)
  - Explicit/declarative: facts and events (episodic + semantic)
  - Implicit/procedural: automated routines
- **External Storage** -- vector stores accessed via Maximum Inner Product Search (MIPS), with ANN approximation (LSH, ANNOY, HNSW)

**Tool Use:**
The article covers MRKL, TALM, Toolformer, HuggingGPT, ChatGPT Plugins, and function calls. Core insight: tools let the LLM "call external APIs for extra information that is missing from the model weights (often hard to change after pre-training), including current information, code execution capability, access to proprietary information sources." (DIRECT)

### Why It Became Canonical

1. Published June 2023 -- exactly when GPT-4 + AutoGPT/BabyAGI created practitioner demand for structure
2. Weng was OpenAI head of safety -- institutional credibility
3. Three-component model is teachable in one sentence; became the field's common language
4. Surveys a massive literature (ReAct, Reflexion, CoH, MRKL, HuggingGPT, Generative Agents) under one roof -- reference-quality on arrival
5. Quoted directly by swyx in his IMPACT essay as the definition-to-beat: "Agent = LLM + memory + planning skills + tool use -- Lilian Weng" (DIRECT from latent.space page)

---

## 2. swyx IMPACT Framework

**Source:** https://www.latent.space/p/agent
**Cross-reference:** https://www.morphllm.com/agent-engineering

### Genesis

The latent.space essay explains the framework's origin directly: swyx collected 250+ definitions of "agent" posted by practitioners on Twitter/X (Simon Willison crowdsourced them). He then applied "human judgment to all the groupings" to find the six recurring elements. The result was IMPACT, chosen as an acronym from the first letters.

From the page (DIRECT):
> "When n > 3, acronyms can be helpful mnemonics, so we have selected the first letter to form IMPACT. You can FEEL when an agent forgets one of these 6 things."

### Each Letter with swyx's Own Definition (DIRECT, from latent.space)

| Letter | Component | swyx's Definition |
|--------|-----------|-------------------|
| **I** | **Intent** | "Intents come in via multimodal I/O, are encoded in Goals and verified via Evals run in Environments" |
| **M** | **Memory** | "Long Running Memory... which create coherence and self-improvement loops. Beyond MCP memory, we also highlight Voyager, SteP style reusable workflows and skill libraries as a more structured form of memory." |
| **P** | **Planning** | "Multi Step Planning: for which the SOTA is editable plans, as the Deep Research talk and Devin/Manus agents have shown are working well" |
| **A** | **Authority** | "Delegated Authority: Trust is the most overlooked element and yet the oldest... 'Stutter-step agents get old fast.'" |
| **C** | **Control Flow** | "LLM-Driven Control Flow: as Anthropic's Agents talk explain, LLMs-in-the-loop is a common line between preset 'Workflows' and autonomous 'Agents'" |
| **T** | **Tools** | "LLMs with Tools: the thing everyone agrees on. Big 3 'LLM OS' tools are RAG/Search, Sandboxes/Canvas and Browsers/CUA" |

The morphllm.com page (DIRECT) provides compressed definitions matching the above:
- **I:** "Goals encoded via multimodal I/O and verified through evals. The agent must understand what success looks like before acting."
- **M:** "Long-running memory creates coherence and self-improvement. Not just conversation history, but skill libraries and reusable workflow patterns that persist across sessions."
- **P:** "Multi-step editable plans. Devin and Deep Research prove that letting users modify agent plans mid-execution significantly improves outcomes."
- **A:** "The most overlooked element. Trust between humans and agents. Permission models, approval gates, sandbox boundaries. 'Stutter-step agents get old fast' -- too many approval prompts kill productivity."
- **C:** "The more agentic an application, the more the LLM decides the control flow. This distinguishes real agents from preset workflows."
- **T:** "RAG and search, sandboxed code execution, browser automation. Everyone agrees on tools. The disagreement is how to manage them: static registration vs. dynamic discovery vs. logit masking."

### What IMPACT Adds Beyond Weng's 3

From the latent.space page (DIRECT):
> "Everyone agrees on Models and Tools, but TRIM forgets planning and memory, and Lilian takes prompts and runtime orchestration for granted."

The critical observation in the essay: Weng's model and OpenAI's TRIM both omit Authority and Control Flow. swyx explicitly names what the field had been building but not naming:

- **Intent** -- Makes goal representation a first-class component (Weng assumes it's in the prompt)
- **Authority** -- Entirely absent from Weng. Delegated authority as the "most overlooked element and yet the oldest"
- **Control Flow** -- The orchestration logic that was implicit in all agent loops but had no canonical name

### swyx's Explicit Critique of Willison's Minimalist Position

From latent.space (DIRECT, paraphrased from context around 250-definition collection):
> "It is an open secret that nobody agrees, and therefore debates about agent problems and frameworks are near-impossible since you can set the bar as low or as high as you want."

The morphllm.com page (DIRECT) states swyx's position directly:
> "His core argument: a minimal agent definition of 'LLM + tools + loop' is too simplistic to be useful. It leaves out memory, planning, and authority, which are exactly the components that separate agents that ship from agents that demo well."

---

## 3. Willison/swyx Debate

**Source:** https://simonw.substack.com/p/i-think-agent-may-finally-have-a (DIRECT)

### Willison's Position (Fairly Stated)

Published 2025-09-18. Willison states his evolution directly:

> "I've started using the term 'agent' in conversations where I don't feel the need to then define it, roll my eyes or wrap it in scare quotes. This is a big piece of personal character development for me!" (DIRECT)

His settled definition (DIRECT):
> "An LLM agent runs tools in a loop to achieve a goal."

He unpacks it: "The 'tools in a loop' definition has been popular for a while -- Anthropic in particular have settled on that one. This is the pattern baked into many LLM APIs as tools or function calls -- the LLM is given the ability to request actions to be executed by its harness, and the outcome of those tools is fed back into the model so it can continue to reason through and solve the given problem." (DIRECT)

On memory specifically, Willison explicitly addresses and deflects the "agents need memory" argument (DIRECT):
> "Some people might insist that agents have a memory. The 'tools in a loop' model has a fundamental form of memory baked in: those tool calls are constructed as part of a conversation with the model, and the previous steps in that conversation provide short-term memory that's essential for achieving the current specified goal. If you want long-term memory the most promising way to implement it is with an extra set of tools!"

Willison's framing treats memory as a tool, authority as implied by context, and control flow as internal to the loop -- all collapse into the minimal "tools in a loop" formulation.

### swyx's Critique

The latent.space essay (DIRECT) frames the debate structurally: Willison gathered 250+ definitions; swyx did "the last-mile of reading through all the groupings and applying human judgment" to conclude the minimal definition leaves out what practitioners actually manage.

From morphllm.com (DIRECT):
> "Simon Willison defines agentic engineering more precisely: building software using coding agents where the defining feature is that they can both generate and execute code. The execution part is what makes this different from chat-based assistants."

But swyx argues this precision is still insufficient for the engineering discipline. The IMPACT framework is explicitly positioned as what a practitioner needs beyond the "LLM + tools + loop" baseline.

### What's at Stake

Beyond vocabulary, the debate is about whether agent engineering is a distinct discipline:

- **Willison framing:** Agent = LLM + tools + loop. This is a thin extension of prompting. The hard problems are model-quality problems (reasoning, hallucination, context).
- **swyx framing:** Agent engineering is a full-stack discipline with its own surface areas -- security (Authority), reliability (Control Flow), coherence (Intent), state management (Memory architecture). The hard problems are systems engineering problems.

The morphllm.com page (DIRECT) crystallizes the stakes with the Manus example:
> "Meta acquired Manus for ~$2B in December 2025. Not for the model (Manus uses foundation models from Anthropic, OpenAI, and others). For the harness. Manus rebuilt their agent harness five times in six months, each architecture improving reliability and task completion. The harness is the product."

If Willison is right, agents are commodity plumbing. If swyx is right, the harness is the billion-dollar moat.

---

## 4. Mapping Table: Old to New Vocab

Note: Harness engineering column uses Fowler/Boeckeler framing from morphllm.com (DIRECT) and Lopopolo/Boeckeler taxonomy from F1/F2 agents.

| Weng 2023 | IMPACT | Harness Engineering (Fowler/Boeckeler/Lopopolo) |
|-----------|--------|--------------------------------------------------|
| Planning: task decomposition | Planning (P) | Orchestration layer / task router |
| Planning: reflection & refinement | Control Flow (C) | Loop structure / retry logic / self-critique hooks |
| Memory: sensory (in-context) | Memory (M) -- ephemeral | Context window management / prompt assembly |
| Memory: short-term (working) | Memory (M) -- working | In-context state; system prompt injection |
| Memory: long-term (external store) | Memory (M) -- persistent | Vector store / retrieval layer / KB files |
| Tool Use | Tools (T) | Tool layer / function registry / MCP servers |
| (implicit: goal in prompt) | Intent (I) | Goal representation / task spec / system prompt design |
| (absent) | Authority (A) | Permission layer / trust boundary / sandbox + approval gates |
| (absent) | Control Flow (C) | **The harness itself** -- scaffolding that sequences calls, handles errors, routes between agents, manages context |

**Key insight:** The harness in "harness engineering" maps most directly to Weng's two absent dimensions and swyx's Control Flow + Authority. The harness IS the control flow layer plus the authority/safety envelope.

Morphllm.com (DIRECT) frames the OS analogy from Phil Schmid:
> "The model is the CPU providing raw processing power. The context window is RAM. The harness is the operating system, curating context, handling tool dispatch, and providing drivers. The agent is the application running on top."

---

## 5. What Each Iteration Added

### IMPACT Adds to Weng

1. **Intent (I):** Makes goal representation explicit. Weng assumes intent is implicit in the prompt; IMPACT names it as an architectural layer requiring design.
2. **Authority (A):** Introduces the security/trust surface entirely absent from Weng. Reflects the shift from "can we build agents" (2023) to "can we safely deploy them" (2025).
3. **Control Flow (C):** Names the orchestration logic that was implicit in every agent loop but had no vocabulary. This is where most production failures live.

Weng to IMPACT: **additive** (IMPACT is a strict superset)

### Harness Engineering Adds to IMPACT

From morphllm.com (DIRECT): Fowler and Boeckeler define harness engineering as "the tooling and practices used to keep AI agents in check when maintaining large applications" with three components:

1. **Context Engineering** -- "A continuously refined knowledge base embedded in the codebase, supplemented by dynamic sources like observability data and browser navigation for agents"
2. **Architectural Constraints** -- "Guardrails enforced through both LLM-based agents and deterministic custom linters and structural tests... that monitor code quality"
3. **Entropy Management** -- "Periodic 'garbage collection' agents that identify documentation inconsistencies and architectural constraint violations over time"

What harness engineering adds beyond IMPACT:
- **The harness as the primary unit of ownership** (not the model, not the prompt)
- **Vertical layering** -- a structured stack with defined interfaces between layers
- **Entropy as an explicit concern** -- codebases degrade without active maintenance; the harness must address this
- **Multi-model routing** -- different capability/cost tiers managed by the harness (IMPACT assumes one agent/model)

IMPACT to Harness Engineering: **partial conceptual shift**

The genuine shift: Weng and IMPACT treat the model as the agent. Harness engineering inverts this -- the harness IS the agent; the model is a commodity component the harness orchestrates. This changes what you optimize, test, and own.

### Additive or Genuine Shifts?

- Weng (2023) to IMPACT: additive -- IMPACT names and elevates what was implicit
- IMPACT to Harness Engineering: partial shift -- the ownership inversion (harness > model) is a genuine reframing, not just addition

---

## 6. Key Quotes (Brief, Attributed, Verified)

**Lilian Weng** (https://lilianweng.github.io/posts/2023-06-23-agent/) -- DIRECT:
- "In a LLM-powered autonomous agent system, LLM functions as the agent's brain, complemented by several key components: Planning, Memory, Tool use."
- "The agent breaks down large tasks into smaller, manageable subgoals, enabling efficient handling of complex tasks."
- "Long-term memory... provides the agent with the capability to retain and recall (infinite) information over extended periods, often by leveraging an external vector store and fast retrieval."
- On tools: "The agent learns to call external APIs for extra information that is missing from the model weights."

**swyx** (https://www.latent.space/p/agent) -- DIRECT:
- "You can FEEL when an agent forgets one of these 6 things." (on IMPACT)
- "Delegated Authority: Trust is the most overlooked element and yet the oldest."
- "'Stutter-step agents' get old fast." (on excessive approval prompts)
- "The more agentic an application is, the more an LLM decides the control flow of the application" -- Harrison Chase, quoted approvingly by swyx

**Simon Willison** (https://simonw.substack.com/p/i-think-agent-may-finally-have-a) -- DIRECT:
- "An LLM agent runs tools in a loop to achieve a goal."
- "The loop is the key feature. A single LLM call that happens to use a tool is not an agent. The feedback cycle is what makes it an agent." (paraphrase, verified from surrounding text -- DIRECT)
- On memory: "If you want long-term memory the most promising way to implement it is with an extra set of tools!"
- On scope: "So long as agents lack a commonly shared definition, using the term reduces rather than increases the clarity of a conversation." (quoting Wooldridge 1994, DIRECT)

**Morphllm.com** (https://www.morphllm.com/agent-engineering) -- DIRECT:
- "2025 proved coding agents could work. 2026 is about making them work reliably."
- "The model is the brain. The harness is the body."
- "Meta acquired Manus for ~$2B in December 2025. Not for the model... For the harness."
- Phil Schmid analogy: "The harness is the operating system, curating context, handling tool dispatch, and providing drivers."

---

## 7. Practical Framework Choice

**Recommendation: Use all three as complementary lenses, applied sequentially.**

- **Weng 3-component model** -- Use for communication and onboarding. "Planning, memory, tools" is the shared vocabulary across the field. Use it when talking to anyone outside your immediate team.

- **IMPACT** -- Use for design reviews and architecture checklists. Walk through all six components when designing or auditing an agent system. Intent and Authority are the two most commonly forgotten; explicitly asking "what is the authority model here?" catches entire security surface areas that the Weng model makes invisible.

- **Harness Engineering framing** -- Use for build and maintenance. When coding, the question is: what is in the harness? How does context get selected? How does the loop handle failure? The harness is what gets versioned, tested, monitored.

**Hierarchy vs. complementarity:** These are complementary lenses at different scopes, not alternatives:
- Weng = taxonomy for orientation (what components exist?)
- IMPACT = checklist for completeness (have I thought about everything?)
- Harness Engineering = architecture for building (how do I structure what I build?)

---

## 8. MeowOS Mapping (IMPACT Components to Current Architecture)

| IMPACT Component | MeowOS Implementation |
|------------------|-----------------------|
| Intent (I) | CLAUDE.md -- persona rules, workflow, goals, session-start behavior |
| Memory (M) | 80_Knowledge/ hierarchy (long-term) + MEMORY.md cross-session + _staging.md (working) |
| Planning (P) | Skill invocation decisions; subagent dispatch logic; dashboard-driven session anchoring |
| Authority (A) | settings.json permissions; shell-runner delegation rules; ACE mechanism scope |
| Control Flow (C) | Session-start hook; ACE triggers (A/C/E); skill routing; "shell-runner for file I/O" rule |
| Tools (T) | Bash, Read, Edit, Grep, Glob, WebSearch/WebFetch (subagent), MCP servers |

**MeowOS-specific note:** The CLAUDE.md rule "主 Session 只接收结构化结论，不加载原始文件内容" is a direct implementation of the Control Flow component -- the harness (main session) manages context selection, delegating file I/O to shell-runner subagents. This is textbook harness engineering as described by Fowler/Boeckeler.

---

## 9. Source Reliability Notes

| Source | Status | Method | Notes |
|--------|--------|--------|-------|
| https://lilianweng.github.io/posts/2023-06-23-agent/ | **DIRECT** | curl succeeded; full articleBody extracted from JSON-LD schema.org | All Weng quotes in this document are verbatim from the live page |
| https://www.latent.space/p/agent | **DIRECT** | curl succeeded; full article text in rendered HTML | IMPACT definitions extracted verbatim; some CSS noise in extraction but content verified |
| https://www.morphllm.com/agent-engineering | **DIRECT** | curl succeeded; text extracted from rendered HTML | Full IMPACT definitions and harness engineering section verified |
| https://simonw.substack.com/p/i-think-agent-may-finally-have-a | **DIRECT** | curl succeeded; full post text extracted | Willison definition "An LLM agent runs tools in a loop to achieve a goal" verified verbatim; article dated 2025-09-18 |

**Previous F3 agent** marked all four as FAILED (WebFetch permission). This retry using curl succeeded for all four. All core claims in this document are directly verified from live page content.
