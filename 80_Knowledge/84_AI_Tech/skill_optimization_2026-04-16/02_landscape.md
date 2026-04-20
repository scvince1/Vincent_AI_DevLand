# Skill Optimization & Agent Self-Improvement: Landscape Scan
**Fetch date:** 2026-04-16
**Scope:** All major frameworks EXCEPT darwin-skill (covered in 01_darwin_skill.md by parallel agent)
**Coverage:** Evolutionary skill systems, prompt optimization frameworks, auto-growing skill libraries, 2025-2026 survey papers

---

## Source URLs (all fetched 2026-04-16)

| Source | URL |
|---|---|
| Voyager arXiv | https://arxiv.org/abs/2305.16291 |
| Voyager project | https://voyager.minedojo.org/ |
| JARVIS-1 arXiv | https://arxiv.org/abs/2311.05997 |
| PromptBreeder arXiv | https://arxiv.org/abs/2309.16797 |
| AFlow arXiv | https://arxiv.org/abs/2410.10762 |
| ADAS arXiv | https://arxiv.org/abs/2408.08435 |
| GPTSwarm arXiv | https://arxiv.org/html/2402.16823v3 |
| DSPy GitHub | https://github.com/stanfordnlp/dspy |
| DSPy docs | https://dspy.ai/learn/optimization/optimizers/ |
| TextGrad arXiv | https://arxiv.org/abs/2406.07496 |
| OPRO arXiv | https://arxiv.org/abs/2309.03409 |
| APE arXiv | https://arxiv.org/abs/2211.01910 |
| EvoPrompt arXiv | https://arxiv.org/abs/2309.08532 |
| PromptWizard arXiv | https://arxiv.org/abs/2405.18369 |
| PromptWizard MSFT Blog | https://www.microsoft.com/en-us/research/blog/promptwizard-the-future-of-prompt-optimization-through-feedback-driven-self-evolving-prompts/ |
| SAMMO arXiv | https://arxiv.org/html/2404.02319v1 |
| Anthropic Agent Skills | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |
| Anthropic Skills GitHub | https://github.com/anthropics/skills |
| Agent Skills Survey arXiv | https://arxiv.org/abs/2602.12430 |
| SoK Agentic Skills arXiv | https://arxiv.org/html/2602.20867v1 |
| SAGE RL arXiv | https://arxiv.org/abs/2512.17102 |
| SkillX arXiv | https://arxiv.org/html/2604.04804v1 |
| Darwin Goedel Machine | https://sakana.ai/dgm/ |
| Darwinian Evolver GitHub | https://github.com/imbue-ai/darwinian_evolver |
| darwin-skill GitHub | https://github.com/alchaincyf/darwin-skill |
| SkillsBench arXiv | https://arxiv.org/html/2602.12670v1 |

---

## 1. Foundational Taxonomy: What Is a Skill?

The SoK paper (arXiv:2602.20867, 2026) provides the most rigorous formalization. A skill is a 4-tuple S = (C, pi, T, R) where:
- C = applicability condition (when skill applies)
- pi = executable policy (how to act)
- T = termination condition (when to stop)
- R = reusable interface (callable signature)

Verbatim: "A skill carries its own applicability conditions, termination criteria, and callable interface, making it a first-class unit of procedural knowledge."

Distinguishes skills from:
- **Tools**: "A tool is an atomic primitive (e.g., a web-search API or a file-write function) with a fixed interface and no internal decision-making." Tools lack applicability logic.
- **Plans**: "one-time, session-scoped, and not directly executable without further interpretation"
- **Memory**: skills encode procedural knowledge (how to act); episodic memory stores declarative knowledge (what happened)
- **Prompt Templates**: lack "applicability conditions, termination logic, and callable interfaces"

The SoK identifies seven design patterns for skill systems:
1. Metadata-driven disclosure (compact metadata + on-demand full load)
2. Code-as-skill (executable Python/scripts)
3. Workflow enforcement (hard-gated procedural sequences)
4. Self-evolving libraries (autonomous quality assessment and updates)
5. Hybrid NL+code macros
6. Meta-skills (skills that create other skills)
7. Plugin/marketplace distribution (versioned, packaged skill ecosystems)

---

## 2. Evolutionary / Self-Improving Skill Systems

### 2.1 Voyager (Wang et al., NVIDIA/MineDojo, May 2023)
arXiv: 2305.16291 | Environment: Minecraft

**What skill means here:** Executable code (JavaScript programs) implementing complex behaviors. Verbatim: "temporally extended, interpretable, and compositional."

**Architecture:**
- Automatic curriculum that maximizes exploration
- Ever-growing skill library (code stored + indexed by embedding)
- Iterative prompting mechanism incorporating environment feedback, execution errors, and self-verification

**Update mechanism:** Verbatim: "A new iterative prompting mechanism that incorporates environment feedback, execution errors, and self-verification for program improvement." GPT-4 writes new skills or patches failing ones based on runtime errors.

**Local vs. Global:** Global accumulation. Verbatim: "Voyager is able to utilize the learned skill library in a new Minecraft world to solve novel tasks from scratch, while other techniques struggle to generalize."

**Persistence model:** External code store + embedding retrieval. Not baked into model weights. Library transfers across worlds.

**Evaluation:** Verbatim: "3.3x more unique items, travels 2.3x longer distances, and unlocks key tech tree milestones up to 15.3x faster than prior SOTA."

**Key limitation:** Environment-specific skills. Self-verification is GPT-4 checking its own output -- no independent oracle.

---

### 2.2 JARVIS-1 (Wang et al., Nov 2023)
arXiv: 2311.05997 | NeurIPS 2023

**What skill means here:** Memories of successful trajectories and plan templates, stored as multimodal (text + image) entries. Goal-plan-observation triples, not raw code.

**Architecture:** Built on multimodal language models with "multimodal memory" storing visual observations paired with textual plans. Self-instruct loop: agent proposes its own exploration tasks, executes, writes back successful plans.

**Update mechanism:** Verbatim: "JARVIS-1 is able to self-improve following a life-long learning paradigm thanks to growing multimodal memory, sparking a more general intelligence and improved autonomy."

**Local vs. Global:** Global accumulation across gameplay sessions.

**Persistence model:** External memory store (text + screenshots), retrieved at planning time.

**Evaluation:** Verbatim: "capable of completing over 200 different tasks... surpasses the reliability of current state-of-the-art agents by 5 times" on ObtainDiamondPickaxe.

**Key distinction from Voyager:** Memory is declarative plans, not executable code.

---

### 2.3 PromptBreeder (Fernando et al., DeepMind, Sept 2023)
arXiv: 2309.16797

**What skill means here:** Task-prompts (NL instructions governing LLM approach to a problem class). Mutation-prompts are meta-level operators evolving task-prompts.

**Architecture:** Two-layer evolutionary system: population of task-prompts + population of mutation-prompts. Both evolve simultaneously, fitness-evaluated against training set.

**Self-referential key innovation:** Verbatim: "Promptbreeder is not just improving task-prompts, but it is also improving the mutation-prompts that improve these task-prompts." Mutation operators themselves subject to selection pressure.

**Update mechanism:** Evolutionary loop: generate -> evaluate fitness -> select survivors -> repeat.

**Persistence model:** Evolved prompt population. Historically expensive: 18,600 API calls on BBII dataset (per PromptWizard comparison).

**Evaluation:** Verbatim: "outperforms state-of-the-art prompt strategies such as Chain-of-Thought and Plan-and-Solve Prompting on commonly used arithmetic and commonsense reasoning benchmarks."

---

### 2.4 ADAS -- Automated Design of Agentic Systems (Hu et al., UBC, Aug 2024)
arXiv: 2408.08435 | ICLR 2025

**What skill means here:** Entire agentic system designs represented as code. Building blocks include "Chain-of-Thought, Self-Reflection, Toolformer" and novel combinations.

**Architecture (Meta Agent Search):**
Verbatim: "a meta agent iteratively programs interesting new agents in code based on previous discoveries"
Verbatim: "instruct a meta agent to iteratively create interestingly new agents, evaluate them, add them to an archive that stores discovered agents, and use this archive to help the meta agent in subsequent iterations create yet more interestingly new agents."

**Update mechanism:** Meta-agent programming loop. Verbatim: "Given that programming languages are Turing Complete, this approach theoretically enables the learning of any possible agentic system."

**Local vs. Global:** Global -- archive accumulates across iterations. Verbatim: "agents maintain superior performance even when transferred across domains and models."

**Persistence model:** Archive of discovered agent code.

---

### 2.5 AFlow (Zhang et al., FoundationAgents/MetaGPT lab, Oct 2024)
arXiv: 2410.10762 | ICLR 2025 Oral

**What skill means here:** Operators -- verbatim: "predefined, reusable combinations of nodes representing common agentic operations (e.g., Ensemble, Review and Revise)." Workflows are compositions of operators.

**Architecture:** Reformulates workflow optimization as search over code-represented workflows. LLM-invoking nodes connected by edges. MCTS navigates workflow space.

**Update mechanism:** Verbatim: "Iteratively refining workflows through code modification, tree-structured experience, and execution feedback."

**Local vs. Global:** Per-benchmark-run optimization. No mechanism for cross-task knowledge transfer described.

**Evaluation:** Verbatim: "5.7% average improvement over state-of-the-art baselines." "smaller models to outperform GPT-4o on specific tasks at 4.55% of its inference cost."

---

### 2.6 GPTSwarm (Zhuge et al., ICML 2024 Oral)
arXiv: 2402.16823

**What skill means here:** Graph nodes -- each is an LLM operation or tool call. Agents are subgraphs; multi-agent systems are composed graphs.

**Architecture:**
Verbatim: "unifies human-designed prompt engineering techniques by describing LLM-based agents as computational graphs, where nodes implement functions to process multimodal data or query LLMs, and edges describe the information flow between operations."

Two optimization types: node optimization (refines node-level LLM prompts) + edge optimization (modifies graph connectivity).

**Local vs. Global:** Per-task graph optimization. Improvements persist as optimized graph structure.

---

### 2.7 Darwin Goedel Machine (Sakana AI, 2025)
Source: https://sakana.ai/dgm/

**What skill means here:** The agent entire codebase is the skill set.

**Architecture:**
Verbatim: "read and modify its own Python codebase to try to self-improve (e.g., adding a new tool, or suggesting a different workflow)"

Three components: (1) foundation model proposes code modifications, (2) empirical validation on benchmarks, (3) archive-based evolution sampling from diverse pool -- not pure hill-climbing from best.

Verbatim on discovered improvements: "a patch validation step, better file viewing, enhanced editing tools, generating and ranking multiple solutions to choose the best one, and adding a history of what has been tried before."

**Local vs. Global:** Global -- discovered improvements are actual code changes, persisted in archive.

**Evaluation:** SWE-bench: 20.0% -> 50.0%. Polyglot: 14.2% -> 30.7%.

---

### 2.8 SAGE -- RL for Self-Improving Agents with Skill Libraries (Dec 2024)
arXiv: 2512.17102

**What skill means here:** Procedural subroutines discovered during task execution, formalized into reusable units stored in a library.

**Architecture:** Skill Augmented GRPO for self-Evolution (SAGE). Two innovations:
1. Sequential Rollout: verbatim: "iteratively deploys agents across a chain of similar tasks for each rollout. Skills generated from previous tasks accumulate in the library and become available for subsequent tasks."
2. Skill-integrated Reward: verbatim: "complements the original outcome-based rewards" to incentivize generating reusable skills.

**Local vs. Global:** Explicitly global. Cross-task accumulation within rollout chains.

**Persistence model:** Skill library grows during RL training; fixed post-training.

**Evaluation:** Verbatim: "8.9% higher Scenario Goal Completion while requiring 26% fewer interaction steps and generating 59% fewer tokens."

---

## 3. Prompt / Program Optimization Frameworks

### 3.1 APE -- Automatic Prompt Engineer (Zhou et al., ICLR 2023)
arXiv: 2211.01910

**What skill means here:** A single natural language instruction string.

**Architecture:** (1) generate candidate instructions via LLM from output demonstrations, (2) improve best candidates via Monte Carlo search. Verbatim: "The instruction generation problem is framed as natural language synthesis addressed as a black-box optimization problem."

**Key finding:** Verbatim: "APE discovers a better zero-shot CoT prompt than the human engineered Let us think step by step prompt."

**Historical role:** Direct ancestor of EvoPrompt, OPRO, PromptBreeder, DSPy instruction optimizers. First paper to frame prompt optimization as search with LLMs doing the searching.

---

### 3.2 OPRO -- LLMs as Optimizers (Yang et al., DeepMind, Sept 2023)
arXiv: 2309.03409

**What skill means here:** Instructions/prompts described in natural language.

**Architecture:** Verbatim: "In each optimization step, the LLM generates new solutions from the prompt that contains previously generated solutions with their values, then the new solutions are evaluated and added to the prompt for the next optimization step." Optimization history embedded in the prompt itself -- a meta-prompt with trajectory of (solution, score) pairs.

**Update mechanism:** In-context trajectory extrapolation. No external memory.

**Local vs. Global:** Per-run. No cross-run persistence described.

**Evaluation:** Verbatim: "best prompts optimized by OPRO outperform human-designed prompts by up to 8% on GSM8K, and by up to 50% on Big-Bench Hard tasks."

---

### 3.3 EvoPrompt (Guo et al., ICLR 2024)
arXiv: 2309.08532

**What skill means here:** Discrete natural language prompt strings.

**Architecture:** Population of prompts. Verbatim: "EvoPrompt starts from a population of prompts and iteratively generates new prompts with LLMs based on the evolutionary operators, improving the population based on the development set." Implements both Genetic Algorithm (crossover + mutation) and Differential Evolution (DE) variants.

**Key difference from PromptBreeder:** EvoPrompt does NOT evolve the mutation operators themselves -- uses fixed GA/DE operators. PromptBreeder additionally evolves the mutation-prompts (self-referential).

**Evaluation:** Verbatim: "up to 25% on BBH." Tested on 31 datasets.

---

### 3.4 DSPy -- Declarative Self-improving Python (Khattab et al., Stanford, 2022-present)
GitHub: https://github.com/stanfordnlp/dspy

**What skill means here:** Modules -- composable Python objects wrapping LLM calls with typed Signatures. A Signature declares input/output types (e.g., question -> reasoning, answer). The whole pipeline is a composition of Modules.

**Architecture:**
Verbatim: "the framework for programming -- rather than prompting -- language models"

**Optimizer catalog:**
- BootstrapFewShot: verbatim: "The bootstrapping process employs the metric to validate demonstrations, including only those that pass the metric in the compiled prompt."
- MIPROv2: three-stage -- bootstrap traces, draft grounded instructions, discrete search via Bayesian Optimization
- COPRO: verbatim: "Generates and refines new instructions for each step, and optimizes them with coordinate ascent"
- SIMBA: stochastic mini-batch sampling, identifies challenging examples, generates self-reflective improvement rules
- GEPA: reflection on program trajectories, proposes improved prompts
- BootstrapFinetune: verbatim: "Distills a prompt-based DSPy program into weight updates"
- BetterTogether: alternates prompt and weight optimization

**Persistence model:** Verbatim: "plain-text JSON format containing all the parameters and steps in the source program."

**Key distinction:** Only framework treating the full multi-module pipeline as optimization target, not just a single prompt string.

---

### 3.5 TextGrad (Yuksekgonul et al., Stanford/CZ Biohub, June 2024)
arXiv: 2406.07496 | Published in Nature

**What skill means here:** Any variable in a computation graph -- prompts, code snippets, molecule structures, reasoning chains.

**Architecture:**
Verbatim: "TextGrad backpropagates textual feedback provided by LLMs to improve individual components. LLMs provide rich, general, natural language suggestions to optimize variables in computation graphs."

PyTorch-like API. Textual gradients are natural language criticism propagated backward through the computation graph.

**Key difference from DSPy:** DSPy optimizes at module/pipeline level with discrete search; TextGrad optimizes at variable level with LLM-gradient propagation. TextGrad can optimize structures (molecules, treatment plans) DSPy cannot.

**Evaluation:** GPT-4o zero-shot accuracy on GPQA: 51% -> 55%. LeetCode-Hard coding: 20% relative performance gain.

---

### 3.6 PromptWizard (Microsoft Research, May 2024)
arXiv: 2405.18369

**What skill means here:** Task instruction + in-context examples, jointly optimized.

**Architecture:** Two sequential stages: (1) instruction refinement via iterative critique-and-synthesis, (2) joint instruction + example optimization. Verbatim: "a self-evolving and self-adaptive mechanism, where the LLM iteratively generates, critiques, and refines prompts and examples in tandem."

**Key efficiency vs. PromptBreeder:** PromptBreeder: 18,600 API calls, 1,488k tokens. PromptWizard: 69 calls, 24k tokens -- 270x fewer calls, 62x fewer tokens.

**Evaluation:** Verbatim: "rigorously evaluated on over 45 tasks." "using just five examples, the framework achieved only a 5% accuracy drop compared to 25 examples."

---

### 3.7 SAMMO -- Structure-Aware Multi-Objective Metaprompt Optimization (Schnabel & Neville, Microsoft, Apr 2024)
arXiv: 2404.02319 | EMNLP 2024 Findings

**What skill means here:** Structured metaprompts -- prompts treated as programs with modifiable components.

**Architecture:**
Verbatim: "SAMMO represents these metaprompts as function graphs, where individual components and substructures can be modified to optimize performance, similar to the optimization process that occurs during traditional program compilation."

**Key innovation:** Structure-awareness. Unlike OPRO/APE treating prompts as flat strings, SAMMO understands tree structure and rewrites sub-components independently. Supports verbatim: "rewrite operations targeting specific stylistic objectives."

**Multi-objective:** Simultaneously optimizes for accuracy AND efficiency (prompt compression).

**Evaluation:** Verbatim: "10-100% in instruction tuning, 26-133% in RAG tuning, and over 40% in prompt compression in performance."

---

## 4. Skill / Agent Libraries That Auto-Grow or Compose

### 4.1 Anthropic Agent Skills (Claude skills-2025-10-02 beta)
Docs: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

**What skill means here:** Packaged bundle of instructions, metadata, and optional resources (scripts, templates, documentation). Stored as folder with SKILL.md file (YAML frontmatter + instructions).

**Architecture -- progressive disclosure:**
Verbatim: "Skills employ a progressive disclosure architecture where metadata loads (~100 tokens) as Claude scans available Skills to identify relevant matches, full instructions (<5k tokens) load when Claude determines the Skill applies, and bundled resources are files and executable code that load only as needed."

Admin deployment workspace-wide shipped December 18, 2025.

**Auto-grow mechanism:** Community contribution -- the ecosystem grows, not individual skills. Skills are static files; they do not self-modify.

**Persistence model:** Filesystem-based. Verbatim: "Custom Skills in Claude Code are filesystem-based and do not require API uploads."

**Evaluation gap:** No built-in eval loop in the spec. Quality control is manual or tool-mediated (darwin-skill fills this gap).

**Security concern:** Agent Skills Survey found verbatim: "26.1% of community-contributed skills contain vulnerabilities."

---

### 4.2 SkillX (Apr 2026)
arXiv: 2604.04804

**What skill means here:** Three-level hierarchy:
- Planning skills: compressed successful trajectories, ordered abstract steps (exploration/backtracking filtered out)
- Functional skills: reusable tool-based subroutines with name, docs, and invocation pattern
- Atomic skills: execution-oriented usage patterns for individual tools, including verbatim: "constraints and common failure modes"

**Architecture:** Three phases: (1) rollout extraction via backbone agent executing training tasks, (2) iterative refinement via Skills Merge + Skills Filter, (3) Exploratory Expansion targeting verbatim: "under-explored or failure-prone tools to improve sample efficiency."

**Auto-grow:** Yes -- "Experience Guiding Exploration" proactively expands the skill space by targeting gaps.

**Persistence model:** Plug-and-play skill knowledge base stored externally, retrieved at inference time.

---

### 4.3 LangChain / LangGraph Skills (2024-2025)

LangChain v1 (late 2025): deprecated all old chains/agent abstractions, LangGraph becomes verbatim: "the foundational runtime for durable, stateful, orchestrated execution." Skills installable via npx skills for agents supporting the Agent Skills specification. No auto-grow mechanism.

---

### 4.4 Cursor Rules / Skills (2025)

Two customization layers: Rules (static context) + Skills (dynamic, progressive disclosure). /Generate Cursor Rules command creates rules from conversation context. Team Rules enable org-level policy propagation. No auto-improvement loop.

---

## 5. Comparison Table

| Tool | Skill Representation | Improvement Mechanism | Local vs. Global | Persistence | Eval Approach |
|---|---|---|---|---|---|
| Voyager | Executable JS code | Iterative prompting + env feedback + self-verify | Global (cross-world library) | External vector DB + code files | Domain milestone metrics |
| JARVIS-1 | Multimodal plan trajectories | Self-instruct + memory write-back | Global (cross-session) | External multimodal store | Task completion rate |
| PromptBreeder | NL task-prompts + mutation-prompts | Evolutionary population (LLM mutator+evaluator) | Global (for task domain) | Evolved prompt population | Dev set fitness, benchmarks |
| ADAS | Agent system code | Meta-agent writes + archives + iterates | Global (ever-growing archive) | Archive of agent code | Cross-domain benchmark transfer |
| AFlow | Workflow DAG (code) | MCTS over workflow space | Local (per-benchmark run) | Optimized workflow code | 6 benchmark datasets |
| GPTSwarm | Computation graph (nodes + edges) | Node prompt + edge connectivity optimization | Local (per-task graph) | Optimized graph structure | Task benchmarks |
| Darwin Goedel Machine | Agent codebase | Open-ended code mutation + empirical validation | Global (archive of agent variants) | Codebase + archive | SWE-bench, Polyglot |
| SAGE | Procedural skill subroutines | RL (GRPO) + Sequential Rollout + Skill-integrated Reward | Global (cross-task RL rollouts) | Skill library (fixed post-training) | AppWorld goal completion |
| APE | NL instruction string | Monte Carlo search + LLM variant generation | Global (found prompt reused) | Single instruction string | 24 NLP benchmarks |
| OPRO | NL prompt/solution | In-context trajectory extrapolation | Per-run (no cross-run store) | Best found prompt | GSM8K, BBH |
| EvoPrompt | NL prompt string | GA/DE evolutionary operators (LLM as mutator) | Global for task domain | Evolved prompt population | 31 datasets, BBH |
| DSPy | Module pipeline (typed Signatures) | Compiler: discrete search over instructions + demos | Global (saved JSON program) | Optimized JSON program | User-defined scorer |
| TextGrad | Any variable (prompt/code/molecule) | Text backpropagation via LLM feedback | Per-optimization run | Optimized variable values | GPQA, LeetCode, molecule binding |
| PromptWizard | Instruction + in-context examples | Critique-and-synthesis loop (joint) | Global for task | Instruction + curated examples | 45+ tasks |
| SAMMO | Structured metaprompt (function graph) | Compile-time rewrite operations | Global for task | Optimized metaprompt structure | Instruction tuning, RAG, compression |
| Anthropic Skills | SKILL.md (metadata + NL + scripts) | Manual / community contribution | Global (workspace-wide) | Filesystem directories | Manual review; no built-in eval |
| SkillX | 3-level hierarchy (planning/functional/atomic) | Rollout extraction + merge/filter + exploration | Global (built KB for task env) | Plug-and-play KB | Downstream agent task performance |
| darwin-skill | SKILL.md files | Hill-climbing + 8-dim rubric + git versioning | Global (skills improved in-place) | Git-tracked SKILL.md files | 8-dim rubric + test prompt validation |

---

## 6. Gap Analysis: What Is NOT Being Done Well

### 6.1 Evaluation Without External Oracle
Almost every system uses the model-being-optimized as its own evaluator. The SkillsBench finding is damning -- verbatim: "self-generated skills average -1.3 pp relative to skill-free baselines" -- autonomous skill creation degrades performance without independent verification. Unit tests are the only reliable alternative, and they require human authorship.

### 6.2 Cross-Task, Cross-Domain Skill Transfer
ADAS and Darwin Goedel Machine show cross-domain transfer at agent-design level. But at the skill level, Voyager library is Minecraft-specific, JARVIS-1 memory is environment-specific, SAGE skills are AppWorld-specific. No system has demonstrated a general skill library accumulating across heterogeneous task environments.

### 6.3 Unsupervised Skill Boundary Discovery
All systems assume task boundaries are given by benchmark structure or human curriculum. Verbatim from SoK: "Truly autonomous boundary detection remains unsolved." A skill library needs to know when to create a new skill vs. extend an existing one.

### 6.4 Skill Maintenance and Drift
Skills break when APIs, UIs, or conditions change. Verbatim from SoK: "Systematic approaches to skill maintenance and drift detection are lacking." darwin-skill git + rollback is the closest practical solution, but requires proactive re-runs.

### 6.5 Cost vs. Benefit Accounting
No framework tracks expected value of optimization (improvement per API call). PromptWizard surfaces the cost problem; nobody has solved the accounting.

### 6.6 The Plateau Problem
All hill-climbing approaches (OPRO, EvoPrompt, PromptWizard) plateau because they optimize from a fixed starting distribution. Darwin Goedel Machine open-ended archive sampling and PromptBreeder meta-mutation are the only approaches that escape local optima by design.

### 6.7 Security in Open Ecosystems
The ClawHavoc incident: verbatim: "nearly 1,200 malicious skills infiltrated a major agent marketplace, exfiltrating API keys, cryptocurrency wallets, and browser credentials at scale." Skill supply-chain security is essentially unsolved at scale.

---

## 7. Where a Darwin Evolutionary Skill Tool Fits

**The unoccupied niche:** Evolutionary optimization at the skill-bundle level -- targeting SKILL.md files as the optimization unit, using hill-climbing with empirical validation via test prompts, with git-backed version control for rollback safety.

Position in the landscape:
- Lower level than ADAS (not redesigning agent architecture)
- Higher level than EvoPrompt/PromptBreeder (optimizing a full skill bundle including metadata, workflow guidance, and instructions -- not just a prompt string)
- More focused than DSPy (targets SKILL.md format specifically, not a general LLM program)
- More grounded than OPRO (uses test-prompt validation, not in-context trajectory scoring)

**Architectural position in SoK taxonomy:** darwin-skill implements the "self-evolving libraries" design pattern for the Anthropic/Claude Code skill ecosystem. It adds the missing eval loop the skills spec lacks.

**Conceptual lineage:** Voyager (code-as-skill + iterative refinement) -> Karpathy autoresearch (LLM-driven self-improvement of research artifacts) -> darwin-skill (apply to SKILL.md files specifically). The darwin-skill README explicitly cites Karpathy autoresearch as inspiration.

**What darwin-skill does NOT do that the landscape shows is valuable:**
- Cross-skill library optimization (each SKILL.md optimized independently, no joint optimization across the library)
- RL-style sequential rollout (SAGE-style cross-task accumulation)
- Open-ended search via diverse archive sampling (Darwin Goedel Machine style)
- Automatic drift detection (reoptimize when skill degrades in production)

These represent the natural growth path for darwin-skill if it absorbs lessons from the broader landscape.

---

## 8. 2025-2026 Survey Papers (Key References)

1. "Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward" (arXiv:2602.12430, Feb 2026) -- most comprehensive field survey; covers SKILL.md spec, progressive disclosure, SEAgent, SAGE, SkillX, security

2. "SoK: Agentic Skills -- Beyond Tool Use in LLM Agents" (arXiv:2602.20867, Feb 2026) -- formal 4-tuple skill definition, 7 design patterns, ClawHavoc case study, gap analysis

3. "SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks" (arXiv:2602.12670, 2026) -- key finding: curated skills +16.2pp, self-generated skills -1.3pp

4. "How Well Do Agentic Skills Work in the Wild: Benchmarking LLM Skill Usage in Realistic Settings" (arXiv:2604.04323, Apr 2026) -- practical deployment benchmarking

5. "SkillX: Automatically Constructing Skill Knowledge Bases for Agents" (arXiv:2604.04804, Apr 2026) -- automated 3-level skill KB construction

---

KB file path: D:\Ai_Project\MeowOS\80_Knowledge\84_AI_Tech\skill_optimization_2026-04-16_landscape.md
