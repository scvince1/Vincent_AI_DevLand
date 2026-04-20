---
id: F2_bockeler_taxonomy
title: F2 — Birgitta Bockeler Harness Engineering Taxonomy
tags: [harness, knowledge, source-text, bockeler, taxonomy]
status: confirmed
last_modified: 2026-04-15
summary: Bockeler (Martin Fowler blog) harness engineering taxonomy 直接来源
---
# F2 — Birgitta Böckeler's Harness Engineering Taxonomy
**Compiled:** 2026-04-14
**Primary source:** https://martinfowler.com/articles/harness-engineering.html (2026-04-02, DIRECT)
**Secondary source:** https://martinfowler.com/articles/exploring-gen-ai/harness-engineering-memo.html (2026-02-17, DIRECT)
**Background source:** https://openai.com/index/harness-engineering/ (2026-02-11, DIRECT — Ryan Lopopolo, the article that originally prompted Böckeler's analysis)

---

## 1. Böckeler's Core Framework

### The "Guides-and-Sensors" Framing

Böckeler's central organizing metaphor treats the coding agent harness as a **cybernetic governor**: a system of feedforward and feedback controls that steers agent behaviour toward desired codebase states.

> "A well-built outer harness serves two goals: it increases the probability that the agent gets it right in the first place, and it provides a feedback loop that self-corrects as many issues as possible before they even reach human eyes."
> — https://martinfowler.com/articles/harness-engineering.html

The two mechanisms:

- **Guides (feedforward controls):** Anticipate the agent's behaviour and steer it *before* it acts. Increase probability of first-attempt success.
- **Sensors (feedback controls):** Observe *after* the agent acts and help it self-correct. Most powerful when producing signals optimized for LLM consumption (e.g. linter messages with embedded remediation instructions).

Neither alone is sufficient: "Separately, you get either an agent that keeps repeating the same mistakes (feedback-only) or an agent that encodes rules but never finds out whether they worked (feed-forward-only)."

### Three Jobs Böckeler Identifies (derived from her Regulation Categories)

Böckeler does not name exactly "three jobs" as a formal list; she describes three **regulation categories** that together cover the jobs of a harness:

| Category | What it regulates | Harnessability today |
|---|---|---|
| **Maintainability harness** | Internal code quality, style, structure | Highest — extensive pre-existing tooling |
| **Architecture fitness harness** | Architectural characteristics, fitness functions | Medium — custom linters + structural tests |
| **Behaviour harness** | Functional correctness | Lowest — major open problem |

This maps to the three-category breakdown Böckeler herself abstracted from the **OpenAI/Lopopolo article**, which she reads as: (1) context engineering, (2) architectural constraints, (3) garbage collection. The maintainability + architecture categories roughly correspond to (1)+(2), while the behaviour harness is a gap neither framework fully addresses.

### Relation to the Popular "6-Layer" Framework

Böckeler does not directly engage with a 6-layer framework in the article. She explicitly frames harness engineering as a subset and specific form of **context engineering**: "Context engineering provides us with the means to make guides and sensors available to the agent. Engineering a user harness for a coding agent is a specific form of context engineering." She treats context engineering as the supply layer and harness engineering as the structural/regulatory layer on top.

---

## 2. Guides in Detail

**Definition:** Feedforward controls that steer agent behaviour proactively, before the agent acts.

**Two execution types:**

- **Computational guides** — Deterministic, fast. Type checkers, linters, bootstrap scripts, code-mod tools (e.g. OpenRewrite recipes). Run by CPU.
- **Inferential guides** — Semantic, AI-based. AGENTS.md files, Skills, instructions written in natural language for the agent to internalize. Run by GPU/NPU; slower, non-deterministic but allow rich semantic guidance.

**Forms and examples (from article):**

| Type | Direction | Example |
|---|---|---|
| Inferential | Feedforward | AGENTS.md, Skills with coding conventions |
| Both | Feedforward | Skill with instructions + a bootstrap script |
| Computational | Feedforward | A tool with access to OpenRewrite recipes |
| Inferential | Feedforward | Architecture fitness requirements described in Skills |

**Design principles:**
- Guides encode human developer experience as explicit, machine-readable rules
- Inferential guides are especially valuable for conventions that require semantic judgment
- Greenfield teams can design harnessability in from day one; legacy teams face the harder retrofit problem
- Böckeler coins the term **"harness templates"** — bundles of guides (and sensors) codified for common service topologies, the potential successor to service templates

**Ambient affordances:** Her colleague Ned Letcher's term for "structural properties of the environment itself that make it legible, navigable, and tractable to agents operating within it." Strongly-typed languages, clear module boundaries, opinionated frameworks all act as implicit guides.

---

## 3. Sensors in Detail

**Definition:** Feedback controls that observe what the agent produced and trigger self-correction.

**What they monitor:**

- Structural violations (duplicate code, cyclomatic complexity, missing coverage, architectural drift, style)
- Semantic issues (semantically duplicate code, redundant tests, brute-force fixes) — partially, via inferential sensors
- Architecture drift — running continuously against the codebase *outside* the change lifecycle
- Runtime signals — degrading SLOs, log anomalies, response quality sampling

**Execution types:**

- **Computational sensors:** Deterministic, fast, cheap enough to run on every commit. Pre-commit hooks, structural tests (e.g. ArchUnit), linters, mutation testing. Catch structural problems reliably.
- **Inferential sensors:** AI code review, "LLM as judge." More expensive and non-deterministic but can handle semantic judgment. Must be placed at appropriate lifecycle stages.

**Recovery triggers and "positive prompt injection":**
Böckeler emphasizes that sensors are most powerful when their output is **optimized for LLM consumption** — custom linter error messages that include remediation instructions become a form of positive prompt injection that guides self-correction.

**Timing / lifecycle distribution:**

| Stage | What belongs here |
|---|---|
| Pre-commit / before integration | Linters, fast test suites, basic code review agent |
| Post-integration / pipeline | Mutation testing, broader code review, slow structural checks |
| Continuous / outside change lifecycle | Dead code detection, test coverage quality, dependency scanners |
| Runtime monitoring | SLO degradation detection, log anomaly flagging |

**Limits:** Neither computational nor inferential sensors reliably catch: misdiagnosis of issues, overengineering, misunderstood instructions. "Correctness is outside any sensor's remit if the human didn't clearly specify what they wanted in the first place."

---

## 4. "Garbage Collection" — the Novel Concept

This concept originates in the **OpenAI/Lopopolo article** (Feb 2026), not Böckeler's own coinage. Böckeler adopts and analyses it as one of the three organizing principles she extracts from Lopopolo's framework.

**What it means (Lopopolo's original description, from https://openai.com/index/harness-engineering/):**

In a fully agent-generated codebase, the agent replicates existing patterns — including suboptimal ones — causing continuous **entropy accumulation** (what the team called "AI slop"). OpenAI's solution: encode "golden principles" (opinionated mechanical rules for legibility/consistency) directly into the repo, then run **background Codex tasks on a recurring cadence** that scan for deviations, update quality grades, and open targeted refactoring PRs.

> "This functions like garbage collection. Technical debt is like a high-interest loan: it's almost always better to pay it down continuously in small increments than to let it compound and tackle it in painful bursts. Human taste is captured once, then enforced continuously on every line of code."
> — Lopopolo, https://openai.com/index/harness-engineering/

**Why separate from ordinary context pruning:**
Garbage collection is not about managing context window size — it is about **continuously fighting codebase entropy** that accumulates from agent replication of imperfect patterns. It operates at the *codebase level* over time, not at the *session level* during a single agent run.

**Concrete examples (from OpenAI article):**
- Prefer shared utility packages over hand-rolled helpers (keeps invariants centralized)
- Validate data boundaries / use typed SDKs instead of YOLO-style data probing
- Background jobs scanning for structural deviations from golden principles
- Auto-generated refactoring PRs that can be reviewed in under a minute and automerged

**Böckeler's reading (from memo, https://martinfowler.com/articles/exploring-gen-ai/harness-engineering-memo.html):**
She groups this as distinct from context engineering and architectural constraints — it is a *maintenance loop* rather than a setup step. She notes it is an iterative, ongoing engineering practice, not one-time configuration.

---

## 5. Comparison to Other Frameworks

### Böckeler's Framework vs. Lopopolo's 3-Category Framework

Lopopolo organizes his harness implicitly around:
1. Context engineering (knowledge base, AGENTS.md as table of contents, observability access)
2. Architectural constraints (custom linters, structural tests, layered domain enforcement)
3. Garbage collection (periodic entropy-fighting agents)

Böckeler's abstraction directly references these three and maps them onto her own guides/sensors framework:
- Context engineering → primarily guides (inferential feedforward)
- Architectural constraints → both guides (rules) and sensors (linters as feedback)
- Garbage collection → a type of continuous sensor running outside the change lifecycle

**What Böckeler adds that Lopopolo doesn't address:**
- The computational/inferential distinction across all controls
- Timing/lifecycle distribution of controls (keep quality left)
- The behaviour harness gap (Lopopolo's framework is entirely about internal quality/maintainability, not functional correctness)
- Harnessability as a codebase property
- The "ambient affordances" concept
- Harness templates as organizational infrastructure

### vs. swyx IMPACT Framework

Böckeler does not reference IMPACT (Intent / Memory / Planning / Authority / Control Flow / Tools) in either article. Her framework operates at a different level: IMPACT describes the **architecture of a single agent session**, while Böckeler's guides-and-sensors model describes the **outer engineering harness** that wraps agent usage over a continuous development lifecycle. They are complementary, not competing. IMPACT is session-level; Böckeler is codebase-level and time-extended.

### Unique Insights vs. Shared Ground

| Shared with common discourse | Böckeler's distinctive contributions |
|---|---|
| AGENTS.md / context engineering | Computational vs. inferential distinction applied to both guides AND sensors |
| Tests and linters as feedback | Timing framework (keep quality left) |
| AI code review | Behaviour harness as unsolved problem, explicitly named |
| Context engineering matters | Harnessability as a first-class design property |
| Harness = everything except model | Harness templates as org-level infrastructure evolution |
| | Positive prompt injection via sensor error messages |
| | Ashby's Law of Requisite Variety as formal justification for topology constraints |

---

## 6. Practical Implementation Advice

**Starting point / adoption steps:**
1. Audit what you already have: pre-commit hooks, linters, structural tests. "What is your harness today?"
2. Add computational feedforward guides (linters, type checkers configured to your conventions)
3. Layer in inferential guides (AGENTS.md, Skills) for convention-heavy / semantic rules
4. Build computational feedback sensors and place them as far left as the cost/speed tradeoff allows
5. Add inferential sensors (AI code review) at integration or pipeline stage
6. Establish continuous drift sensors for architecture health
7. Implement garbage collection cadence for entropy fighting
8. Iterate on the harness itself when issues recur ("the steering loop")

**Anti-patterns:**
- Feedback-only: the agent keeps repeating the same mistakes
- Feedforward-only: rules encoded but never verified
- One monolithic AGENTS.md: crowds context, rots quickly, can't be verified mechanically (Lopopolo's lesson)
- Expecting sensors to catch correctness problems that stem from underspecified requirements
- Treating harness engineering as one-time configuration rather than ongoing practice
- Over-engineering the behaviour harness before solving the maintainability harness

**Harnessability as prerequisite:**
Not all codebases are equally amenable. Greenfield teams should design harnessability in from day one. Legacy/high-debt codebases face retrofitting costs. Technology choices (strongly-typed languages, clear module boundaries, opinionated frameworks) determine how governable the codebase will be.

**Tool stance:**
- Böckeler does not prescribe specific tools; she mentions LangGraph, MCP, and custom linters only as examples in passing
- She explicitly references LSP and code intelligence as computational feedforward guides gaining traction
- Structural testing frameworks (ArchUnit) are named as underused computational sensors now having a resurgence
- The article was authored with Claude and Claude Code assistance (explicitly noted in acknowledgements)

---

## 7. Key Quotes

1. "A well-built outer harness serves two goals: it increases the probability that the agent gets it right in the first place, and it provides a feedback loop that self-corrects as many issues as possible before they even reach human eyes." — Böckeler, primary article

2. "Sensors... are particularly powerful when they produce signals that are optimised for LLM consumption, e.g. custom linter messages that include instructions for the self-correction — a positive kind of prompt injection." — Böckeler, primary article

3. "Harnesses are an attempt to externalise and make explicit what human developer experience brings to the table, but it can only go so far." — Böckeler, primary article

4. "A good harness should not necessarily aim to fully eliminate human input, but to direct it to where our input is most important." — Böckeler, primary article (also in memo intro)

5. "Building a coherent system of guides and sensors and self-correction loops is expensive, so we have to prioritise with a clear goal in mind." — Böckeler, primary article

6. "Its goal is to raise the conversation above the feature level — from skills and MCP servers to how we strategically design a system of controls that gives us genuine confidence in what agents produce." — Böckeler, primary article

7. "Our most difficult challenges now center on designing environments, feedback loops, and control systems." — Lopopolo (OpenAI), quoted approvingly by Böckeler in both articles

8. "Building this outer harness is emerging as an ongoing engineering practice, not a one-time configuration." — Böckeler, primary article

---

## 8. Gaps / What's Underspecified

1. **Behaviour harness is openly unsolved.** Böckeler acknowledges this is "the elephant in the room" — how to verify functional correctness well enough to reduce manual testing. The "approved fixtures pattern" is mentioned as a partial answer, but she says it's not a wholesale solution.

2. **Harness coherence at scale.** As the harness grows, guides and sensors may contradict each other. No methodology provided for maintaining coherence or resolving conflicts.

3. **Harness coverage and quality measurement.** "If sensors never fire, is that a sign of high quality or inadequate detection mechanisms?" — no answer given. Böckeler calls for tooling analogous to code coverage for harness evaluation.

4. **Harness templates versioning problem.** Service templates already suffer from forking and synchronization challenges; harness templates with non-deterministic inferential components will be harder to test and sync. The problem is named but not solved.

5. **Trust calibration for inferential sensors.** How much to weight AI code review vs. human review, especially when both are non-deterministic? Mentioned but not quantified.

6. **Agent trade-off handling.** "How far can we trust agents to make sensible trade-offs when instructions and feedback signals point in different directions?" — open question.

7. **Inferential guide/sensor testing.** How do you test whether an inferential guide (a piece of AGENTS.md) is actually effective? No methodology discussed.

8. **Multi-year coherence.** Lopopolo's article itself acknowledges "We don't yet know how architectural coherence evolves over years in a fully agent-generated system."

---

## 9. Source Reliability Notes

| Source | Status | Notes |
|---|---|---|
| https://martinfowler.com/articles/harness-engineering.html | **DIRECT** | Full text fetched and parsed; primary Böckeler article dated 2026-04-02; complete and current |
| https://martinfowler.com/articles/exploring-gen-ai/harness-engineering-memo.html | **DIRECT** | Full text fetched and parsed; original Feb 17 2026 memo; URL now redirects to primary article per Böckeler's own note, but content still accessible at original path |
| https://openai.com/index/harness-engineering/ | **DIRECT** | Page is a Next.js SPA; prose extracted from embedded JSON data (`__next_f.push` script chunks); core sections (garbage collection, architecture enforcement) fully recovered; some diagram alt-text captured instead of figures |
| Martin Fowler commentary / X posts | **NOT FETCHED** | Not required; Böckeler's own writing on martinfowler.com is the authoritative source; Fowler's role is publisher/editor |
| swyx IMPACT framework | **NOT DIRECT** — framework referenced for comparison from existing knowledge; not cited in Böckeler's articles |
