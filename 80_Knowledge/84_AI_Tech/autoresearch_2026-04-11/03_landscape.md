---
id: 03_landscape
title: Landscape — Autonomous Research Agents State of the Art
tags: [ai-tech, knowledge, autonomous-research, landscape, deepresearch]
status: confirmed
last_modified: 2026-04-15
summary: 自主研究 Agent 领域全景对比，聚焦知识持久性
---
# Landscape: Autonomous Research Agents — State of the Art
**Fetch date:** 2026-04-11  
**Task:** Track 3 of 3 — Landscape & Alternatives to Karpathy's `autoresearch`  
**Primary lens:** Knowledge persistence — which tools remember what they read, which discard it?

---

## Source URLs

| Source | URL | Fetched |
|--------|-----|---------|
| OpenAI Deep Research intro | https://openai.com/index/introducing-deep-research/ | 2026-04-11 |
| OpenAI Deep Research API docs | https://platform.openai.com/docs/guides/deep-research | 2026-04-11 |
| OpenAI o3-deep-research model | https://platform.openai.com/docs/models/o3-deep-research | 2026-04-11 |
| OpenAI Cookbook: Deep Research intro | https://cookbook.openai.com/examples/deep_research_api/introduction_to_deep_research_api | 2026-04-11 |
| Gemini Deep Research docs | https://ai.google.dev/gemini-api/docs/deep-research | 2026-04-11 |
| Gemini Deep Research overview | https://gemini.google/overview/deep-research/ | 2026-04-11 |
| Gemini DR in production (Medium) | https://medium.com/google-cloud/how-to-use-the-gemini-deep-research-api-in-production-978055873a39 | 2026-04-11 |
| Perplexity Deep Research intro | https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research | 2026-04-11 |
| Perplexity Sonar Deep Research model | https://docs.perplexity.ai/docs/sonar/models/sonar-deep-research | 2026-04-11 |
| Grok 3 / DeepSearch announcement | https://x.ai/news/grok-3 | 2026-04-11 |
| Grok DeepSearch guide | https://www.tryprofound.com/blog/understanding-grok-a-comprehensive-guide-to-grok-websearch-grok-deepsearch | 2026-04-11 |
| Anthropic Claude Managed Agents | https://siliconangle.com/2026/04/08/anthropic-launches-claude-managed-agents-speed-ai-agent-development/ | 2026-04-11 |
| GPT-Researcher GitHub | https://github.com/assafelovic/gpt-researcher | 2026-04-11 |
| GPT-Researcher on Tavily Docs | https://docs.tavily.com/examples/open-sources/gpt-researcher | 2026-04-11 |
| Stanford STORM GitHub | https://github.com/stanford-oval/storm | 2026-04-11 |
| Co-STORM research page | https://storm-project.stanford.edu/research/co-storm/ | 2026-04-11 |
| LangChain Open Deep Research blog | https://blog.langchain.com/open-deep-research/ | 2026-04-11 |
| LangChain ODR GitHub | https://github.com/langchain-ai/open_deep_research | 2026-04-11 |
| smolagents HuggingFace docs | https://huggingface.co/docs/smolagents/en/index | 2026-04-11 |
| smolagents GitHub | https://github.com/huggingface/smolagents | 2026-04-11 |
| Tongyi DeepResearch blog | https://tongyi-agent.github.io/blog/introducing-tongyi-deep-research/ | 2026-04-11 |
| Tongyi DeepResearch GitHub | https://github.com/Alibaba-NLP/DeepResearch | 2026-04-11 |
| Survey: Deep Research Systems (arXiv 2506.12594) | https://arxiv.org/abs/2506.12594 | 2026-04-11 |
| Survey: Deep Research Agents Roadmap (arXiv 2506.18096) | https://arxiv.org/abs/2506.18096 | 2026-04-11 |
| Survey: Autonomous Research Agents (arXiv 2508.12752) | https://arxiv.org/abs/2508.12752 | 2026-04-11 |
| A-MEM: Agentic Memory (arXiv 2502.12110) | https://arxiv.org/abs/2502.12110 | 2026-04-11 |
| Zep: Temporal KG Memory (arXiv 2501.13956) | https://arxiv.org/abs/2501.13956 | 2026-04-11 |
| Mem0: Production AI Memory (arXiv 2504.19413) | https://arxiv.org/abs/2504.19413 | 2026-04-11 |
| DeepResearch Bench leaderboard | https://github.com/Ayanami0730/deep_research_bench | 2026-04-11 |
| LLM agent frameworks comparison | https://dev.to/ultraduneai/eval-004-ai-agent-frameworks-langgraph-vs-crewai-vs-autogen-vs-smolagents-vs-openai-agents-sdk-190l | 2026-04-11 |
| Karpathy autoresearch GitHub | https://github.com/karpathy/autoresearch | 2026-04-11 |
| Karpathy autoresearch DataCamp guide | https://www.datacamp.com/tutorial/guide-to-autoresearch | 2026-04-11 |
| Graph-based agent memory survey (arXiv 2602.05665) | https://arxiv.org/html/2602.05665v1 | 2026-04-11 |

---

## Section 1: Commercial Products

### 1.1 OpenAI Deep Research
**Builder:** OpenAI  
**Release:** February 2025 (ChatGPT); API availability mid-2025  
**Underlying model:** o3-deep-research (now also o4-mini-deep-research for lightweight version)

**Architecture:**  
Deep Research runs a four-phase pipeline driven by a reasoning model trained end-to-end via reinforcement learning on browsing + research tasks:

1. **Planning** — task decomposition and research strategy formulation  
2. **Query Generation** — designing targeted queries per sub-question  
3. **Web Exploration** — searching, reading hundreds of sources (text, images, PDFs)  
4. **Report Generation** — synthesizing into a cited, structured report

The PromptLayer blog explains: "During training, OpenAI used end-to-end reinforcement learning on complex browsing and reasoning tasks, placing the model in simulated research environments with access to tools and giving it real-world tasks requiring multi-step problem solving, through which it learned to plan and execute multi-step search trajectories, backtrack when paths are unfruitful, and pivot strategies based on new information."

The OpenAI API Cookbook notes: "The output includes a listing of web search calls, code interpreter calls, and remote MCP calls made to get to the answer. Every output is fully documented, with clear citations and a summary of its thinking."

**Execution time:** 5-30 minutes per research task.

**Knowledge persistence:** NONE between sessions. Deep Research performs research within a single run. Each invocation starts from scratch. The model's "memory" is confined to the context window of the current run. No cross-session knowledge accumulation.

**Notable quirks:**  
- The RL training approach means the model has internalized research strategies as weights, not as accessible data  
- o3-deep-research is a specialized derivative of o3, not a general-purpose model  
- The API uses an async polling pattern (background task queue) because runs can take up to 30 minutes  

---

### 1.2 Google Gemini Deep Research
**Builder:** Google DeepMind  
**Release:** Late 2024, API available 2025  
**Underlying model:** Gemini 3.1 Pro (2026 current)

**Architecture:**  
Gemini DR is described as "an agentic workflow where a single request triggers an autonomous loop of planning, searching, reading, and reasoning." From the API docs:

> "Unlike standard chat requests where a request leads to one output, a Deep Research task is an agentic workflow where a single request triggers an autonomous loop of planning, searching, reading, and reasoning."

Three stages: (1) research plan generation (shown to user for optional editing), (2) autonomous search and browsing using `google_search` and `url_context` tools, iterative reading and reasoning, (3) comprehensive report synthesis.

A distinctive feature: Gemini DR can access **Gmail, Drive, and Chat** for enterprise users in addition to public web, enabling research across private organizational knowledge.

Context window: up to **1 million tokens** (from the arXiv 2506.18096 survey: "Google's Gemini DR supports a context window of up to one million tokens, supplemented by a RAG setup").

Maximum research time: 60 minutes.

**Knowledge persistence:** NONE between sessions. The 1M context window is a very large "working memory" for a single session but all of it is discarded at session end. What persists is only the output report.

**Notable quirks:**  
- The async Interactions API requires a `background=True` parameter, polling-based, similar to a job queue  
- The plan is shown to the user before execution — the only deep research tool with this human-in-the-loop planning step at the start  
- Private data access (Gmail/Drive) makes it uniquely positioned for enterprise "internal research"  

---

### 1.3 Perplexity Deep Research (Sonar Deep Research)
**Builder:** Perplexity AI  
**Release:** Early 2025  
**Underlying model:** Proprietary sonar-deep-research (128K context)

**Architecture:**  
Perplexity DR uses a "retrieval-reasoning-refinement cycle" with three core components: a planner (decomposes query into subtopics), a retriever (fetches via Perplexity's search API, hundreds of sources per run), and a synthesizer (compiles insights). The key proprietary mechanism is described as "Test Time Compute (TTC) expansion, which enables the systematic exploration of complex topics through a sophisticated process that mimics human cognitive processes."

Perplexity performs "dozens of searches, reads hundreds of sources" and "refining its research plan as it learns more about the subject areas."

Augmented with coding capabilities for quantitative data analysis.

**Execution time:** 2-4 minutes (fastest of the major commercial tools).

**Benchmark:** 21.1% on Humanity's Last Exam — notably higher than Gemini Thinking, o3-mini, o1, and DeepSeek-R1 at the time of reporting.

**Knowledge persistence:** NONE between sessions. Single-run processing. The 128K context window is the outer bound of what can be held during a single research session.

**Notable quirks:**  
- Speed is the differentiator: 2-4 minutes vs 5-30 for OpenAI DR  
- TTC expansion appears to be a form of test-time compute scaling applied to the search/retrieval strategy selection  
- Launched as Sonar Deep Research model accessible via API  

---

### 1.4 Grok DeepSearch (xAI)
**Builder:** xAI  
**Release:** February 2025 (with Grok 3)

**Architecture:**  
DeepSearch is described by xAI as "xAI's first agent — a lightning-fast AI agent built to relentlessly seek the truth across the entire corpus of human knowledge." It is built on Grok 3, "trained on xAI's Colossus supercluster with 10x the compute of previous state-of-the-art models."

DeepSearch "allows Grok 3 to browse the internet, verify sources and synthesize real-time information before generating a final answer." The reasoning capabilities are "refined through large scale reinforcement learning" allowing it to "think for seconds to minutes, correcting errors, exploring alternatives."

Key differentiator: **Speed**. "While ChatGPT's full Deep Research mode can take up to 17 minutes to generate an in-depth report, Grok DeepSearch completed a similar task in approximately 36 seconds." This speed-depth tradeoff is explicit — Grok prioritizes rapid synthesis over exhaustive research.

**Knowledge persistence:** NONE between sessions. Standard context-window bounded single-run approach.

**Notable quirks:**  
- 36-second completion is order-of-magnitude faster than competitors — reflects a different quality/depth target  
- Positioned more as "DeepSearch" (fast, synthesis-focused) than "Deep Research" (exhaustive, report-focused)  
- xAI emphasizes "reason about conflicting facts and opinions" — adversarial source evaluation is a stated design goal  

---

### 1.5 Anthropic (Claude) Research Agent Features
**Builder:** Anthropic  
**Release:** Claude Managed Agents launched April 2026; Claude Cowork (macOS) January 2026 research preview  

**Architecture:**  
Anthropic has not released a standalone "Deep Research" product. Their agent features are:

- **Claude Managed Agents**: Cloud service for building AI agents, with two features in research preview: (1) an agent that can spin up sub-agents for complex tasks, and (2) automatic prompt quality refinement. The announcement (April 8, 2026): "shortens the development workflow from months to weeks."  
- **Claude Cowork**: MacOS desktop application with plug-ins targeting enterprise departments (finance, legal, HR), launched enterprise tier April 2026.  
- **Agent Skills**: (skills-2025-10-02 beta) "organized folders of instructions, scripts, and resources that Claude loads dynamically to perform specialized tasks" — this is the Claude Code skills system being formalized.

Anthropic's positioning is **infrastructure for building research agents** rather than a turn-key deep research product. The Managed Agents service enables the multi-agent spawn-subagent pattern that other systems (like OpenAI's) have baked in.

**Knowledge persistence:** Session-only by default. The skills system can load persistent context, but no native cross-session research knowledge accumulation equivalent to STORM's mind map or GPT-Researcher's source tracking.

---

## Section 2: Open-Source Frameworks

### 2.1 GPT-Researcher
**Builder:** Assaf Elovic (assafelovic)  
**Release:** 2023 (GitHub); Deep Research variant 2025  
**License:** Apache 2.0  
**GitHub:** https://github.com/assafelovic/gpt-researcher

**Architecture:**  
GPT-Researcher uses a **planner-executor-publisher** pattern. From the README: "The core idea is to utilize 'planner' and 'execution' agents. The planner generates research questions, while the execution agents gather relevant information."

Five-step workflow:
1. Generate task-specific research questions  
2. Deploy crawler agents per research question (parallel)  
3. Summarize and track sources for each resource  
4. Filter and aggregate summaries  
5. Compile into final research report (2,000+ words, 20+ sources)

The system "maintains memory and context throughout research" — but this is within a single session, not cross-session. A key feature is support for local document processing (PDF, CSV, Excel, Markdown, Word) alongside web scraping and MCP integrations.

Advanced implementations use a **tree-like exploration pattern**: "breadth exploration generating multiple search queries, depth diving recursively into subtopics, and concurrent processing utilizing async/await patterns." This recursive depth-breadth structure is the closest to a knowledge graph walk in the open-source web-research space — but it's computed fresh each run.

A 2025 update added a NextJS UI allowing users to "chat with research results, deepen research, and connect MCPs directly from the UI."

**Knowledge persistence:** NONE across sessions. Memory is contextual within the session. The system tracks sources and maintains research continuity during execution but does not maintain cross-session knowledge bases.

**Notable quirks:**  
- Average research task: ~3 minutes, ~$0.10 cost  
- Heavy prompt engineering focus (criticized for "inconsistent report quality" in comparison articles)  
- Supports AG2 and LangGraph backends for multi-agent orchestration  
- Broadest developer customization options among open-source tools  

---

### 2.2 Stanford STORM and Co-STORM
**Builder:** Stanford OVAL Lab  
**Release:** STORM 2024; Co-STORM 2024-2025  
**License:** MIT  
**GitHub:** https://github.com/stanford-oval/storm

**Architecture:**  
STORM is uniquely opinionated: it targets **Wikipedia-style article generation** as its output format. Two-stage pipeline:

1. **Pre-writing stage**: "The system conducts Internet-based research to collect references and generates an outline."  
2. **Writing stage**: "The system uses the outline and references to generate the full-length article with citations."

The key technique is **perspective-guided question asking**: "given the input topic, STORM discovers different perspectives by surveying existing articles from similar topics and uses them to control the question-asking process." This is implemented as a simulated conversation between a "Wikipedia writer" and a "topic expert" — the LLM plays both roles, using the dialogue structure to force coverage across multiple perspectives.

Multi-LM design with specialized roles:
- Conversation simulator LM (cheaper/faster model — handles query splitting and answer synthesis)
- Question asker LM (identifies research gaps)
- Outline generation LM (organizes hierarchically)
- Article generation LM (produces verified content)
- Article polishing LM (refines presentation)

Implemented in **DSPy**, enabling modular component replacement.

**Co-STORM extensions:**  
Co-STORM introduces "a collaborative discourse protocol with LLM experts that generate answers grounded on external knowledge sources and/or raise follow-up questions based on the discourse history, and a Moderator agent that generates thought-provoking questions inspired by information discovered by the retriever but not directly used in previous turns."

The key knowledge persistence innovation: **a dynamic updated mind map** that "organizes collected information into a hierarchical concept structure, aiming to build a shared conceptual space between the human user and the system." This mind map persists and updates during the session and represents STORM's answer to knowledge organization.

**Knowledge persistence:**  
- STORM: Structured outline + collected references + full article — all persist as OUTPUT files (not a live knowledge base)  
- Co-STORM: Mind map persists DURING SESSION as a hierarchical knowledge structure. Between sessions, the mind map can be saved and reloaded. This is the most deliberate knowledge organization of any research tool.  
- No cross-session learning or accumulation — each topic is a fresh project.

**Notable quirks:**  
- The perspective-guided approach produces more comprehensive coverage than keyword-focused search  
- Co-STORM's mind map is the closest thing in the research agent space to a lightweight knowledge graph  
- Output format is fixed: Wikipedia-style article, not flexible reports  
- The simulated expert dialogue is architecturally distinct from all other tools — it forces diverse coverage by design  

---

### 2.3 LangChain Open Deep Research (ODR)
**Builder:** LangChain  
**Release:** 2025  
**License:** MIT  
**GitHub:** https://github.com/langchain-ai/open_deep_research

**Architecture:**  
Built on LangGraph. Uses a **supervisor-researcher** multi-agent design:

> "A multi-agent approach allows multiple sub-agents to run in parallel, and each is dedicated to an independent, focused task. The system uses multi-agent for only the research task itself, performing writing after all research was done."

From LangChain's tweet: "Uses a supervisor architecture to coordinate research sub-agents... Supports your own LLMs, tools, and MCP servers."

Three conceptual parts: scoping, research, final report. The supervisor agent, "given the brief and using reflection, spawns multiple research sub-agents on demand, each with a dedicated sub-task, and each sub-agent receives a dedicated topic, performs research on it, and returns a summary to the supervisor."

The framework is explicitly model-agnostic, search-tool-agnostic, and MCP-compatible — designed for developer customization.

**Benchmark performance:** Ranked #6 on Deep Research Bench Leaderboard with RACE score 0.4344.

**Knowledge persistence:**  
- LangGraph state allows file persistence within a conversation thread  
- A `CompositeBackend` pattern routes `/memories/` to persistent `StoreBackend` while scratch files remain ephemeral  
- This enables cross-turn (within a session) accumulation but is not automatic cross-session research knowledge  
- The framework offers the MOST FLEXIBLE persistence options of any open-source tool, but persistence requires deliberate developer configuration  

**Notable quirks:**  
- The most "infrastructure" of the open-source options — not a product, a framework  
- Explicitly positioned as the open-source alternative to commercial deep research products  
- LangGraph's StateGraph model makes the research workflow inspectable and debuggable  

---

### 2.4 smolagents (HuggingFace)
**Builder:** HuggingFace  
**Release:** Late 2024  
**License:** Apache 2.0  
**GitHub:** https://github.com/huggingface/smolagents

**Architecture:**  
smolagents is a minimalist framework — "~1,000 lines of code." Two core agent types:

- **CodeAgent**: "writes its actions in code (as opposed to agents being used to write code) to invoke tools or perform computations." The LLM generates code snippets that call tools as functions, assign results to variables, and can loop, branch, and compose logic. Operates on the **ReAct framework**.
- **ToolCallingAgent**: standard JSON/text-based tool-calling for traditional patterns.

Research backing: "Executable Code Actions Elicit Better LLM Agents" — code agents use 30% fewer steps and achieve higher performance on difficult benchmarks.

smolagents supports LiteLLM integration (OpenAI, Anthropic, etc.) and sandboxed execution via Modal, Blaxel, E2B, or Docker. MCP integration is built-in.

**Knowledge persistence:** None built-in. smolagents is a framework, not a research product. It provides the execution substrate; persistence is the developer's responsibility.

**Notable quirks:**  
- The code-as-action paradigm is architecturally distinct: the agent can write loops, conditionals, and function compositions rather than only calling predefined tools  
- 26K+ GitHub stars — widely adopted as a lightweight agent substrate  
- Framework velocity slowed compared to LangGraph/CrewAI in 2025-2026 per framework comparison analyses  

---

### 2.5 Tongyi DeepResearch (Alibaba)
**Builder:** Alibaba, Tongyi Lab  
**Release:** September 2025  
**License:** Open-source (model weights available)  
**GitHub:** https://github.com/Alibaba-NLP/DeepResearch

**Architecture:**  
Tongyi DeepResearch-30B-A3B is a **30B MoE model** (only ~3B active parameters per token) specifically trained for deep research as an agentic task. This is architecturally distinct from all other tools: instead of using a general-purpose LLM with a research orchestration layer, Tongyi baked the research behavior into the model weights via a three-stage training pipeline:

1. **Agentic Continual Pre-training (CPT)**: Pre-trains on agentic data patterns  
2. **Supervised Fine-Tuning (SFT)**: Using a fully automated synthetic data pipeline (no human labels)  
3. **Reinforcement Learning (RL)**: GRPO optimization for research task reward

Two inference modes:
- **ReAct**: Standard "reason-act" loop for evaluating core capabilities  
- **IterResearch** ("Heavy" mode): Test-time scaling strategy for maximum performance ceiling

Benchmark performance:
- 32.9 on Humanity's Last Exam  
- 43.4 on BrowseComp  
- 75 on xbench-DeepSearch

Described as "the first fully open-source Web Agent to achieve performance on par with OpenAI's DeepResearch across a comprehensive suite of benchmarks."

**Knowledge persistence:** NONE across sessions. Single-run inference. The model's research capability is in weights, not in an external knowledge store.

**Notable quirks:**  
- The fully automated training pipeline (no human labels) is a significant contribution — demonstrates that synthetic data + RL can produce competitive research agents  
- 128K context window, dual inference modes  
- Powers real Alibaba products: Gaode Mate (navigation agent) and Tongyi FaRui (legal research agent)  
- The "DeepSeek moment for agents" framing in VentureBeat coverage — open-source matching closed-source  

---

### 2.6 AutoGen / Microsoft Agent Framework
**Builder:** Microsoft Research  
**Release:** AutoGen 2023; merged with Semantic Kernel → Microsoft Agent Framework (GA targeted Q1 2026)  

**Architecture:**  
Microsoft merged AutoGen (multi-agent patterns) with Semantic Kernel (enterprise orchestration) into a unified framework. The merged framework supports:
- Agent-to-Agent (A2A) protocol  
- MCP for tool integration  
- Enterprise-grade orchestration patterns

For research tasks, AutoGen's contribution was the "conversational programming" pattern — agents that communicate via structured dialogues to decompose and solve tasks collaboratively.

**Knowledge persistence:** Not natively built for research knowledge persistence. External database integration required.

---

### 2.7 CrewAI
**Builder:** CrewAI  
**Release:** 2024  
**License:** MIT (core)

**Architecture:**  
Role-based collaboration model. A "Crew" is a container for multiple agents each with defined roles. Research crews typically have: Researcher role (web search, source gathering), Analyst role (synthesis), Writer role (report drafting). CrewAI v1.10 added A2A protocol support and native MCP tool loading.

**Knowledge persistence:** None built-in for cross-session research. Session-scoped context only.

---

## Section 3: Knowledge Persistence Ecosystem (Adjacent Infrastructure)

### 3.1 Zep (Temporal Knowledge Graph for Agent Memory)
**Paper:** arXiv 2501.13956, January 2025  
**Architecture:** Three-layer temporal knowledge graph:
- Episode subgraph (raw messages/JSON, non-lossy)
- Semantic entity subgraph (extracted entities + relationships)  
- Community subgraph (clustered entities with summaries)

Core innovation: bi-temporal edge modeling. Each relationship edge carries four timestamps — system creation time, system expiry time, fact valid time, fact invalid time. From the paper: "When the system identifies temporally overlapping contradictions, it invalidates the affected edges by setting their tᵢₙᵥₐₗᵢ𝒹 to the tᵥₐₗᵢ𝒹 of the invalidating edge." Facts are never deleted, only invalidated.

**Performance:** Reduces average context tokens from 115,000 to 1,600 tokens while improving accuracy 18.5% on temporal reasoning tasks. DMR benchmark: 94.8%.

**Relevance to research agents:** Zep is primarily designed for conversational memory (enterprise chatbots, customer-facing agents) rather than research agents. But the temporal KG architecture is directly applicable: it would allow a research agent to track how its understanding of a topic evolves over multiple sessions, with contradictions flagged rather than silently overwritten.

### 3.2 Mem0
**Paper:** arXiv 2504.19413  
**Architecture:** Two variants:
- **Base Mem0**: Extracts, evaluates, and manages salient information via dedicated extraction and update modules  
- **Mem0g (Graph-Based)**: Directed labeled graph with entities as nodes, relationships as edges

**Performance:** 26% relative improvement in LLM-as-a-Judge metric over OpenAI; 91% lower p95 latency; 90% token savings.

Designed specifically for production deployment — handles "the fixed context window challenge by dynamically extracting, consolidating, and retrieving salient information from ongoing conversations."

### 3.3 A-MEM (Agentic Memory)
**Paper:** arXiv 2502.12110  
**Architecture:** Applies **Zettelkasten principles** to agent memory. From the abstract: generates comprehensive notes for new memories containing "multiple structured attributes, including contextual descriptions, keywords, and tags," then identifies relevant historical memories and establishes connections. New memories "can trigger updates to the contextual representations and attributes of existing historical memories."

This is **bidirectional memory evolution**: new information refines the understanding of old information. Rather than a static accumulation of notes, the knowledge network actively reorganizes as new evidence arrives.

**Critical insight for research agents:** A-MEM's architecture would allow a research agent to not just collect sources but to maintain a living knowledge graph where reading a new paper can retroactively update the interpretation of earlier papers. None of the current deep research tools do this.

### 3.4 AgentRxiv (referenced in arXiv 2506.18096)
A system described in the deep research roadmap survey as operating "akin to arXiv for storing and retrieving relevant outcomes from other agents." Agents "collaboratively share and access a centralised repository of prior research outputs, simulating an online-updating arXiv-like platform, which can be seen as a comprehensive case bank." This is the most developed form of **cross-agent persistent knowledge sharing** identified in the literature — agents publishing findings that other agents can retrieve.

---

## Section 4: Academic / Methodological Context

### Survey 1: "A Comprehensive Survey of Deep Research" (arXiv 2506.12594)
Analyzes 80+ commercial and non-commercial deep research implementations since 2023. Proposes four-dimensional taxonomy:
1. Foundation models and reasoning engines  
2. Tool utilization and environmental interaction  
3. Task planning and execution control  
4. Knowledge synthesis and output generation

Five architectural patterns: Monolithic, Pipeline-Based, Multi-Agent, Hybrid, Emerging Framework Ecosystems.

### Survey 2: "Deep Research Agents: A Systematic Examination And Roadmap" (arXiv 2506.18096)
This survey is the most detailed on architecture. Key findings:

**On knowledge persistence strategies:**
> "Systems like Manus and OWL utilise external file systems to store intermediate outcomes and historical data for subsequent retrieval. More sophisticated approaches employ vector databases to support scalable memory storage and fast similarity-based lookup."

> "Agentic Reasoning employs knowledge graphs to capture intermediate reasoning processes and thereby enhance the precision of information reuse."

Three strategies identified for managing extended contexts:
1. **Extended context windows** (Gemini: 1M tokens)
2. **Intermediate compression** (Search-o1's "Reason-in-Documents" — compress documents via language reasoning before adding to context)
3. **External structured storage** (file systems, vector DBs, knowledge graphs)

**On non-parametric continual learning:**
> "Rather than updating model weights, systems enable self-evolution through external mechanisms. Case-Based Reasoning (CBR) allows agents to 'retrieve, adapt, and reuse structured problem-solving trajectories from an external case bank dynamically.'"

**Seven identified gaps:**
1. Broaden information source (beyond crawlable web)
2. Fact checking (insufficient validation)
3. Asynchronous parallel execution
4. Tool-integrated reasoning
5. Benchmark misalignment with practical objectives
6. Parametric optimization of multi-agent architectures
7. Self-evolving language model agents

### Survey 3: "Deep Research: A Survey of Autonomous Research Agents" (arXiv 2508.12752)
Identifies four foundational modules: Planning, Question Developing, Web Exploration, Report Generation. Notes that current survey literature contains "no explicit discussion of knowledge persistence mechanisms" as a first-class concern — confirming that knowledge persistence is an **understudied gap** in the research agent literature.

---

## Section 5: Comparison Dimension Table

| Tool | Architecture | Knowledge Persistence | Output Format | Open/Closed | Maturity |
|------|-------------|----------------------|---------------|-------------|---------|
| OpenAI Deep Research | Single-agent RL-trained, multi-phase | None (session only) | Long-form cited report | Closed | Production |
| Gemini Deep Research | Single-agent agentic loop | None (1M token session only) | Long-form cited report | Closed | Production |
| Perplexity Sonar DR | Planner-retriever-synthesizer | None (session only) | Long-form cited report | Closed | Production |
| Grok DeepSearch | Single-agent RL (fast) | None (session only) | Synthesis answer | Closed | Production |
| Anthropic / Claude | Multi-agent infrastructure (not DR product) | Session + configurable skills | Configurable | Closed (API) | Beta |
| GPT-Researcher | Planner-executor-publisher | None (session only) | Long report | Open (Apache 2.0) | Stable |
| Stanford STORM | Perspective-guided multi-LM pipeline | Session outline + mind map (Co-STORM) | Wikipedia article | Open (MIT) | Stable |
| LangChain ODR | Supervisor-researcher multi-agent | Configurable (LangGraph Store) | Flexible | Open (MIT) | Active dev |
| smolagents | Code-action ReAct | None (dev responsibility) | Flexible | Open (Apache 2.0) | Stable |
| Tongyi DeepResearch | Trained MoE agent (ReAct + IterResearch) | None (session only) | Long-form report | Open (weights) | Stable |
| AutoGen / MS Agent | Conversational multi-agent | External DB required | Flexible | Open/Enterprise | Active dev |
| CrewAI | Role-based crew | Session only | Flexible | Open (MIT core) | Active dev |

---

## Section 6: Knowledge Persistence — The Detailed Picture

This is the dimension Vincent flagged as most important. The honest answer is: **almost nothing persists**.

### What every major tool does
Every major commercial deep research tool (OpenAI, Gemini, Perplexity, Grok) and every major open-source research framework (GPT-Researcher, Tongyi, smolagents, CrewAI, AutoGen) operates as a **read-process-discard pipeline**:

1. User submits query  
2. Agent reads hundreds of sources  
3. Sources are held in context window during the session  
4. Session ends: all read content is discarded  
5. Output report survives  

The report captures synthesized conclusions but not the underlying source material or the agent's intermediate reasoning paths. Next time a related query arrives, everything is re-fetched from scratch.

### The one exception: Co-STORM's mind map
Co-STORM's "dynamic updated mind map" is the only research-agent feature from any major tool that actively organizes the knowledge being accumulated during research. From the paper: it "organizes collected information into a hierarchical concept structure, aiming to build a shared conceptual space between the human user and the system." The mind map persists across the session and can be exported. But: it still resets per-topic, and there is no accumulation across research topics over time.

### What the adjacent infrastructure layer does
The knowledge persistence problem IS being solved — just not in the research agent layer. It's being solved in the **agent memory layer** (Zep, Mem0, A-MEM):

- **Zep**: Temporal knowledge graph with edge-level invalidation rather than deletion — full fact history preserved  
- **Mem0**: Graph-based extraction and update — 26% accuracy improvement, 90% token savings vs naive context  
- **A-MEM**: Zettelkasten-style interconnected notes where new memories retroactively update old ones  

None of these systems are natively integrated with any of the major research agent tools (as of April 2026). They exist as separate infrastructure packages.

### The architectural gap
The research agent layer (plan, search, read, synthesize → report) and the agent memory layer (persist, organize, retrieve, evolve) are currently **separate stacks**. No tool integrates them into a coherent "read once, know forever" system. A research agent that used Zep or Mem0 as its storage backend could in principle:
- Accumulate domain knowledge across research sessions  
- Retrieve relevant prior findings when starting a new related query  
- Track how its understanding of a topic evolved over time  
- Surface contradictions between sources read in different sessions  

This integration does not yet exist in any production research agent.

---

## Section 7: Gaps in the Landscape

1. **No persistent cross-session research knowledge accumulation** — every tool starts from zero. This is the most significant architectural gap.

2. **No knowledge graph output** — outputs are documents (reports, articles), not structured graphs of claims and relationships. The research might establish that "A caused B" and "B relates to C" but these relationships are buried in prose, not in a queryable graph.

3. **No contradiction management** — when two sources conflict, current agents either pick one or describe both, but don't maintain a persistent record of conflicting claims for future resolution.

4. **Textual monoculture** — from arXiv 2508.12752: "current pipelines are almost exclusively textual," excluding quantitative data, images, and structured databases as primary research sources.

5. **No research provenance** — there is no way to ask "where did this claim come from and was it corroborated?" against a persistent knowledge store. The cited reports provide URLs, but the claim-source mapping is not queryable.

6. **Single-task orientation** — all current tools are designed around answering a single question per run. There is no tool designed around the concept of ongoing research into a domain over weeks or months, with knowledge accumulation as a first-class concern.

7. **No reward signal from real-world use** — the RL training approaches (OpenAI, Tongyi) use simulated research environments. No tool learns from whether its reports were actually useful or accurate after the fact.

---

## Section 8: Where Karpathy's `autoresearch` Fits

Karpathy's `autoresearch` (released March 7, 2026; 21K+ stars within days) is architecturally orthogonal to all the tools above. Understanding why requires being precise about what it actually does.

`autoresearch` is not a web research tool. It is a **self-improving ML experimentation loop**:
- Domain: ML training code, specifically nanochat (single-GPU LLM training)
- The "research" is: try a code modification, measure val_bpb (bits-per-byte on validation set), keep if better
- Three contract files: `prepare.py` (immutable ground truth), `train.py` (modifiable), `evaluate.py` (metric computation)
- Loop: modify `train.py` → train for exactly 5 minutes → check metric → keep or discard → repeat
- Target throughput: ~12 experiments/hour, ~100 overnight

This is **experimental research in the ML lab sense**, not **information-gathering research in the literature-review sense**. The "knowledge" being accumulated is: which architectural and training choices improve performance on this task. That knowledge IS persistent — it lives in the best `train.py` that has been selected over hundreds of iterations.

In the landscape:
- It shares nothing architecturally with OpenAI/Gemini/Perplexity Deep Research (those do web information gathering)
- It is closer in spirit to AI Scientist (Sakana AI, 2024) — but AI Scientist targets academic paper generation from experiments, while `autoresearch` is tighter: pure optimization loop on a fixed task
- The "knowledge persistence" answer for `autoresearch`: **the winning code IS the knowledge**. There is no separate knowledge store — the evolved program is the artifact
- The comparison with Co-STORM is instructive: Co-STORM accumulates a mind map of what it knows about a topic; `autoresearch` accumulates empirically validated code that encodes what works

**The synthesis:** `autoresearch` represents a different epistemology from web-search-based deep research. Web deep research asks "what is known" and reads other people's work. `autoresearch` asks "what works" and generates its own empirical evidence. The knowledge persistence question is answered differently: web research tools discard everything (a waste, as Vincent notes); `autoresearch` preserves only what survives the fitness test (a very different form of knowledge selection).

The unexplored territory that would be genuinely novel: **a web research agent that applies the autoresearch loop concept** — iteratively refining a knowledge representation based on how well it answers test questions, rather than doing a single read-and-synthesize pass. That would combine the information-gathering capability of the commercial deep research tools with the self-improving persistence of `autoresearch`.

---

## KB File Path
`D:\Ai_Project\MeowOS\80_Knowledge\84_AI_Tech\autoresearch_2026-04-11\03_landscape.md`
