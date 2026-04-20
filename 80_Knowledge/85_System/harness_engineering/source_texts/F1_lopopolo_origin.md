---
id: F1_lopopolo_origin
title: "F1 - Lopopolo Origin Texts: Harness Engineering"
tags: [harness, knowledge, source-text, lopopolo, openai]
status: confirmed
last_modified: 2026-04-15
summary: Lopopolo (OpenAI) harness engineering 原始文本编译
---
# F1 — Lopopolo Origin Texts: Harness Engineering

**Compiled:** 2026-04-14
**Researcher:** F1 subagent

---

## Source Reliability Notes

| Source | Status | Notes |
|--------|--------|-------|
| https://openai.com/index/harness-engineering/ | **DIRECT** | Full HTML retrieved and parsed. Published Feb 11, 2026 by Ryan Lopopolo. All article sections extracted. |
| https://www.latent.space/p/harness-eng | **DIRECT** | Full HTML retrieved and parsed. "Extreme Harness Engineering for Token Billionaires" podcast + transcript, Apr 7, 2026. Ryan Lopopolo interviewed by swyx and Vibhu. |
| https://www.infoq.com/news/2026/02/openai-harness-engineering-codex/ | **FAILED** | Page returned only title (JS-rendered or paywalled). Not usable. |
| https://web.archive.org/web/*/openai.com/index/harness-engineering* | **NOT ATTEMPTED** | Primary source was directly accessible; archive not needed. |

---

## 1. Definition

Per Lopopolo's Feb 11 article, harness engineering is the discipline of designing the *environment*, *feedback loops*, and *control systems* that enable coding agents to do reliable, large-scale software work. The key reframe: engineering work shifts from writing code to "design environments, specify intent, and build feedback loops that allow Codex agents to do reliable work." (OpenAI article)

In the podcast (Latent Space, Apr 7), Lopopolo describes the harness as "the box" — the scaffolding infrastructure around the model. The model reasons within it; the engineer builds and maintains it. He says: "It's done all the wiring and lets you just communicate in prompts." The harness is not the model, not the agent, not the task — it is the structured environment that makes agent output predictable and improvable.

The term emerged from a deliberate personal constraint: Lopopolo refused to write any code himself for five months, forcing every engineering problem to be resolved by improving the environment rather than by direct human coding.

Scope per Lopopolo:
- Tools and abstractions the agent uses
- Repository-embedded knowledge and docs structure
- CI, testing, observability pipelines wired to agent perception
- Skills (short, reusable capability scripts)
- Feedback loops that encode "engineering taste" as mechanical checks
- Escalation and rework protocols

---

## 2. Symphony Case Study

**Scale:**
- ~1 million lines of code (application logic, infra, tooling, docs, internal utilities)
- ~1,500 pull requests opened and merged over 5 months
- 3 engineers initially, scaled to 7; throughput increased as team grew
- Average: 3.5 PRs/engineer/day (rising to 5-10/day/engineer with GPT-5.2+)
- 0 lines of manually-written code; 0% human code review before merge (post-merge review only)
- Product shipped to internal beta users + external alpha testers with daily active users

**What "0 human code" means operationally:**
- Every line — application logic, tests, CI config, docs, observability tooling, internal dev tools, dashboard definitions — written by Codex
- Humans interact via prompts only; Codex pulls review feedback, responds inline, squashes and merges its own PRs
- Review is agent-to-agent; humans review post-merge at most
- When a PR is not mergeable, Symphony moves it to "rework" state: the Elixir service trashes the entire worktree and PR and restarts from scratch, treating the failure as a signal to improve the harness

**Symphony specifically:**
Symphony is OpenAI's internal Elixir-based multi-agent orchestration layer. It:
- Spins up, supervises, reworks, and coordinates large numbers of Codex agents across tickets and repos
- Uses Elixir/BEAM for native process supervision and concurrency (one gen_server daemon per task)
- Manages the "rework state" loop: propose PR → escalate to human → if not mergeable, trash worktree and restart
- Allows humans to review work asynchronously (opening app twice a day, approving/rejecting) rather than sitting at terminals
- Is itself distributed as a "ghost library" — a reference spec (by Alex Kotliarskyi) rather than shared source code, so others can re-implement it from the specification

**Problems the harness had to solve in practice:**
- Context overload: "one big AGENTS.md" failed; replaced with a 100-line table-of-contents AGENTS.md and a structured `docs/` hierarchy
- Build loop speed: agent required under-1-minute builds; team iterated through Make → Bazel → Turbo → NX to achieve this
- Agent observability: wired Chrome DevTools Protocol, LogQL, PromQL, ephemeral per-worktree local observability stacks (Prometheus/Victoria Metrics)
- Entropy/drift: recurring "garbage collection" Codex tasks scan for deviations from "golden principles," update quality grades, and open targeted refactor PRs
- Multi-human coordination: 45-minute daily standups for knowledge sync; rigid 500-npm-package architecture to prevent trampling
- Model generation transitions: each new model version (GPT-5, 5.1, 5.2, 5.3, 5.4) required harness adaptation (e.g., 5.3 added background shells, requiring full build system retool)

---

## 3. Harness Components per Lopopolo

Lopopolo does not present a single canonical numbered taxonomy in the OpenAI article. The Latent Space podcast host swyx attempts a 6-layer framing ("policy, configuration, coordination, execution, integration, observability") — Lopopolo confirms it's reasonable but treats it as approximate, not prescriptive.

**From the OpenAI article, the functional components are:**

1. **Repository knowledge structure** — Short AGENTS.md as map; `docs/` hierarchy as system of record (design-docs, exec-plans, product-specs, references, quality scores). Enforced by linters and CI.

2. **Skills** — Short, reusable scripts embedded in the repo that give agents specific capabilities (e.g., DOM snapshots via CDP, log querying, navigation). Team uses only ~6 skills total; new capability is encoded into existing skills before creating new ones.

3. **Observability stack** — Ephemeral per-worktree local stack: logs queryable via LogQL, metrics via PromQL, traces via Jaeger. Agent can reproduce bugs and validate fixes without human QA.

4. **Application legibility layer** — App bootable per git worktree; Chrome DevTools Protocol wired to agent runtime; rasterized UI images for layout understanding.

5. **Golden principles + garbage collection** — Opinionated mechanical rules encoded in the repo; background Codex tasks continuously scan and enforce; "human taste captured once, enforced continuously."

6. **Execution plans as first-class artifacts** — Lightweight plans for small changes; structured exec-plan docs with progress/decision logs for complex work; active/completed/debt all versioned.

7. **Rework loop / escalation protocol** — Ralph Wiggum Loop: agent self-reviews, requests agent reviews, iterates until reviewers satisfied, then merges. If human rejects, Symphony trashes worktree and restarts.

**Comparison to popular 6-layer framework (context/tools/orchestration/memory/eval/recovery):**
Lopopolo's framing maps partially but differs in emphasis:
- Context → his "repository knowledge" + progressive disclosure architecture
- Tools → his "skills" (narrowly scoped, CLI-first, ~6 total)
- Orchestration → Symphony (explicit, Elixir-based, rework-as-first-class)
- Memory → docs/ as system of record + exec-plans; no explicit memory layer separate from repo
- Eval → quality scores, golden principles, CI linters — baked into repo, not a separate eval system
- Recovery → rework state in Symphony; "fix the harness, not the prompt" as the recovery philosophy

Key divergence: Lopopolo treats "agent legibility" (making the entire codebase, UI, and logs readable by the agent) as a first-class layer that the 6-layer framework doesn't name explicitly. Also, his "skills" are explicitly minimal (6 total), contrasting with frameworks that encourage richer tool libraries.

---

## 4. Core Claims (Non-Obvious Theses)

1. **The bottleneck shifts to human attention, not compute.** "The only fundamentally scarce thing is the synchronous human attention of my team." Tokens are cheap and parallelizable; human time is not. Engineering discipline should optimize for human attention first. (OpenAI article; Latent Space)

2. **Failure signals are harness deficits, not model deficits.** "When something failed, the fix was almost never 'try harder.'" Every model failure is a missing capability, missing context, or missing structure — and the fix is to build it into the harness, not reprompt. (OpenAI article)

3. **Software must be written for the model as much as for the engineer.** "Agent legibility is the goal." Architecture, naming, docs, and structure should be designed so the agent can navigate without humans copying and pasting context. Code is increasingly context/prompt. (OpenAI article; Latent Space)

4. **Entropy is a first-class engineering problem in agent-generated codebases.** Agents replicate patterns including bad ones; "AI slop" accumulates. Garbage collection via recurring Codex cleanup tasks and "golden principles" is necessary infrastructure, not optional hygiene. (OpenAI article)

5. **Ghost libraries and spec-driven distribution change how software is shared.** A high-fidelity specification — rather than shared source code — can allow a coding agent to reproduce a complex system. Symphony is distributed this way. This suggests software distribution itself changes when code generation is cheap. (Latent Space, ~31:00-35:00)

---

## 5. Key Quotes

All attributed to Ryan Lopopolo.

1. "Humans steer. Agents execute." — OpenAI article, core framing sentence.

2. "The discipline shows up more in the scaffolding rather than the code. The tooling, abstractions, and feedback loops that keep the codebase coherent are increasingly important." — OpenAI article, closing section.

3. "Give Codex a map, not a 1,000-page instruction manual." — OpenAI article, on AGENTS.md design.

4. "Human taste is captured once, then enforced continuously on every line of code." — OpenAI article, on golden principles + garbage collection.

5. "The harnesses are there enough where they're isomorphic to me in capability and the ability to do the job." — Latent Space transcript, on why the zero-code constraint was viable.

6. "My job is to figure out ways to funnel text from one agent to the other." — Latent Space transcript, ~43:00, on the fundamental nature of the coordination work.

7. "Put the agent in a box. Just make sure the box has everything it needs." — Latent Space transcript (paraphrase synthesizing his exchange with swyx ~42:44); Lopopolo: "Context and tools."

8. "It's been fun to feel like we've defined the discourse in some sense." — Latent Space transcript, ~01:30, on the HE article's reception.

---

## 6. Open Questions / Gaps in the Argument

1. **Long-term architectural coherence is unproven.** Lopopolo explicitly acknowledges: "What we don't yet know is how architectural coherence evolves over years in a fully agent-generated system." The experiment is 5 months old; drift at 2-5 year timescales is an open question.

2. **Generalizability beyond OpenAI's resource context.** The team has no internal rate limits and runs ~1B tokens/day (~$2-3K/day at market rates). The harness engineering discipline as described may not transfer to teams with token budget constraints.

3. **Zero-to-one product creation remains human-dependent.** Lopopolo notes models "still need humans" for "hard and new" problems — pure white-space product creation and deep architectural refactors. The framework doesn't describe how to harness-engineer these.

4. **Symphony's coordination layer is described but not fully specified.** The ghost library/spec distribution is referenced, but the exact supervisory primitives, failure escalation logic, and state machine structure are not detailed in either source. The Elixir implementation is internal.

5. **The "no human review before merge" claim needs scrutiny.** Lopopolo says most review is "post-merge" and that fundamentally the review is "did it ship and break things." This works for an internal beta but the article doesn't address compliance, security review, or regulated environments.

6. **Skills vs. MCP friction trade-off is underexplored.** Lopopolo is explicitly bearish on MCPs ("forcibly injects all those tokens in the context... they mess with auto compaction"). The alternative (custom CLI shims) scales to a 7-person team but his own skepticism about generalizing skills to other teams suggests the primitives are not fully settled.

---

*Sources consulted:*
- OpenAI article (DIRECT): https://openai.com/index/harness-engineering/
- Latent Space podcast + transcript (DIRECT): https://www.latent.space/p/harness-eng
- InfoQ (FAILED): https://www.infoq.com/news/2026/02/openai-harness-engineering-codex/
