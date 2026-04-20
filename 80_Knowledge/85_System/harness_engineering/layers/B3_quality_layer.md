---
id: B3_quality_layer
title: "B3 - Quality Layer: Evaluation, Observability, Constraints and Recovery"
tags: [harness, knowledge, quality-layer, evals, observability]
status: confirmed
last_modified: 2026-04-15
summary: 质量层：Böckeler Sensors 映射，Hamel/Shankar evals，NeMo Guardrails
---
# B3 — Quality Layer: Evaluation, Observability, Constraints & Recovery

**Version:** 2026-04-14
**Scope:** Quality Layer — what happens when things go wrong, and how we know they went wrong
**Böckeler mapping:** Sensors side of the Guides-Sensors 2x2
**Sources used:** Hamel + Shankar Evals FAQ (Jan 2026), Hamel Evals-Skills (Mar 2026), Shankar EvalGen arXiv:2404.12272, NeMo Guardrails architecture README, Guardrails AI GitHub, Langfuse tracing docs, LangGraph persistence docs, F1 (Lopopolo/Symphony), F2 (Böckeler taxonomy)

---

## Section 1: Conceptual Foundation

### Why evaluation is the hardest harness layer

Hamel Husain calls this "the revenge of the data scientist." Every other layer of the harness — context, tools, orchestration, memory — has a clear build/don't-build decision and a verifiable output. Evaluation does not. There is no clean abstraction boundary: you cannot write a unit test to verify your unit tests.

The difficulty has three roots:

**1. Domain specificity crushes generic metrics.** ROUGE, BERTScore, accuracy against a held-out set — these work for NLP benchmarks. They fail for business agents because "quality" is defined by the business problem, not by surface similarity to reference text. As Hamel puts it: "The most important activity in evals is error analysis. It ensures that the evaluation metrics you develop are supported by real application behaviors instead of counter-productive generic metrics (which most platforms nudge you to use)." (hamel.dev/blog/posts/evals-faq/, Jan 2026)

**2. Requirements are not pre-specifiable.** Shankar's EvalGen study (arXiv:2404.12272, Apr 2024) identified "criteria drift": users need criteria to grade outputs, but grading outputs helps users define criteria. This is a chicken-and-egg loop, not a bug in the process. It means evaluation criteria for a new product literally cannot be written before observing model behavior. This destroys the standard software QA assumption of specifiable requirements.

**3. The data volume problem.** Human attention is scarce (Lopopolo's Claim 1). You need enough labeled examples to align automated evaluators, but labeling is expensive. Hamel reports teams spending 60-80% of development time on error analysis and evaluation. There is no shortcut that doesn't sacrifice calibration quality.

### The feedback loop problem: Circular validation

Using a model to evaluate its own outputs — or a similar model to evaluate them — creates circular validation. Shankar's frame is precise: "LLM-generated evaluators simply inherit all the problems of the LLMs they evaluate, requiring further human validation." (arXiv:2404.12272)

This does not mean LLM-as-judge is useless. It means it must be anchored to human ground truth. The calibration process is:
1. Generate candidate judge implementations (prompts or Python functions)
2. Have humans label a subset of real outputs
3. Select judge implementations that maximize agreement with human labels
4. Measure alignment using true positive rate / true negative rate (TPR/TNR), not just accuracy — because failure modes are often asymmetric (false negatives hurt differently than false positives)
5. Re-calibrate when distribution shifts

The circular danger is highest when the same model that generated outputs also grades them with minimal intermediate grounding.

### Why guardrails are not evaluation

These two concepts are commonly conflated. The functional difference is timing and purpose:

| | Guardrails | Evaluation |
|---|---|---|
| Timing | Real-time, per-request | Offline batch or async |
| Purpose | Block or transform bad outputs now | Measure quality to improve later |
| Action on failure | Reject, rewrite, escalate (live) | Log, report, trigger retrain cycle |
| Scope | Individual request | Distribution of many requests |
| Böckeler type | Computational/inferential Sensor (reactive) | Inferential Sensor (diagnostic) |

Hamel's FAQ makes the distinction explicit: "Evaluators tell you about quality trends across many examples. Guardrails act on individual outputs in real time." (hamel.dev/blog/posts/evals-faq/). A guardrail that fires frequently is a signal that evaluation found a real failure mode worth blocking — but the guardrail itself is not the evaluation.

---

## Section 2: Evaluation Methodology

### Three eval scenarios

**Scenario 1: Selection (which model/prompt is better?)**
Pairwise comparison. Present two outputs to a judge (human or LLM) and ask: which is better for this input? Pairwise is more reliable than absolute scoring because it avoids anchoring effects. Used when choosing between two versions of a system.

**Scenario 2: Improvement verification (did this change help?)**
Measure a score before and after a change on the same test set. Requires a stable test set and a calibrated judge. The risk here is test set overfitting — if you iterate enough against the same set, you optimize for the set rather than the underlying capability.

**Scenario 3: Regression prevention (did we break something that worked?)**
CI integration. Every code or prompt change runs the eval suite and gates merge. This requires fast evals (otherwise it slows development) and a test set with high coverage of known failure modes. Hamel recommends: "If you're passing 100% of your evals, you're likely not challenging your system enough." (hamel.dev/blog/posts/evals-faq/)

### Eval data construction

**From docs/specs:** Write test cases from your product requirements and known policies. These are deterministic (there is a right answer). Good for regression prevention but insufficient alone — they don't cover emergent behaviors.

**From production traces:** Run in production, log traces, identify failures via error analysis. This is the highest-value source because it reflects actual user behavior. Hamel: "Start with error analysis, not infrastructure. Spend 30 minutes manually reviewing 20-50 LLM outputs." Ground truth is expensive but worth it here.

**From synthetic generation:** When you have no production data (new product), generate diverse inputs from your docs and product spec. The risk is distribution mismatch — synthetic data reflects what you imagine users will say, not what they actually say. Use it to bootstrap, then replace with real data as fast as possible.

**Variant generation to prevent leakage:** Once a test set exists, generate paraphrases and variations of the test inputs using a separate model. This tests whether your system has learned the capability or memorized the specific phrasing. Relevant especially if prompts are tuned against the test set.

### LLM-as-judge: how it works and when it fails

**How it works:** A grader LLM receives (input, output, optional reference), and produces a Pass/Fail verdict with a critique. Hamel recommends binary Pass/Fail over Likert scales: "Binary evaluations are more reliable because they force a decision and reduce inter-rater inconsistency. Continuous scales introduce calibration variance between annotators and across time." (hamel.dev/blog/posts/evals-faq/)

**When it fails:**
- Judge is the same model family as the judged system (self-flattery bias documented empirically)
- Judge is given vague criteria ("was this helpful?") — criteria must be operational, not aspirational
- Judge is not calibrated against domain expert labels — high accuracy on easy cases, bad on edge cases
- Criteria drift: the criteria were written before observing enough real failures, so they don't cover the failure modes that actually occur (Shankar arXiv:2404.12272)
- Distribution shift: judge calibrated on Q1 data, production is now Q2 data with different user patterns

**How to align to human preferences (EvalGen protocol, Shankar):**
1. Run the system and collect real outputs
2. Have a domain expert ("benevolent dictator") make Pass/Fail judgments with written critiques for 50-100 examples
3. Generate multiple candidate judge prompts from those critiques
4. Measure each candidate's TPR and TNR against the human labels
5. Pick the candidate with the best aligned TPR/TNR profile for your use case
6. Check for bias: a judge with 95% accuracy but 40% TPR on failures is useless

### Pairwise vs absolute scoring

**Absolute:** "Grade this output 1-5." Fast to run, hard to calibrate across judges and sessions. Best for automated monitoring where consistency matters more than precision.

**Pairwise:** "Is A or B better?" More reliable for human preference capture. Required when you are doing model selection or A/B testing. Harder to aggregate into a single score for CI. Braintrust and LangSmith support pairwise eval modes.

### Why generic benchmarks fail for business use

Tau-Bench (tool use), SWE-Bench (code), MMLU (general knowledge) — these are useful for evaluating base model capability. They are not useful for evaluating whether your agent handles your customer support queue correctly.

The reason is specificity. SWE-Bench tests whether a model can fix GitHub issues in open-source repos. Your software agent is working on a proprietary codebase with company-specific patterns, internal APIs, and domain knowledge not in training data. A model that scores well on SWE-Bench can still fail badly on your task.

Hamel: "Don't use 'ready-to-use' evaluation metrics. They are optimized for the benchmark, not your product." (hamel.dev/blog/posts/evals-faq/) Generic benchmarks are useful for vendor comparison in procurement, not for production quality monitoring.

---

## Section 3: Observability in Production

### Tracing at agent granularity

Traditional APM (application performance monitoring) traces at request granularity: one HTTP request, one span. For LLM agents, one user message may trigger dozens of sub-operations: multiple LLM calls, tool invocations, retrieval steps, planning steps. Request-level tracing loses the causal structure.

Agent-level tracing captures the full DAG of operations. Hamel's FAQ defines a trace: "the complete record of all actions, messages, tool calls, and data retrievals from a single initial user query through to the final response... every step across all agents, tools, and system components in a session." (hamel.dev/blog/posts/evals-faq/)

This is not just a verbosity choice. If your agent fails at step 7 of 12, you need to know what state it was in at step 6. Without agent-level tracing, debugging is guesswork.

### What to log

The minimum viable trace includes:

- **Input:** The exact prompt sent to each LLM call (not just the user message)
- **Output:** The complete model response, including any structured outputs or tool calls
- **Intermediate states:** Memory reads/writes, tool selection decisions, planner outputs
- **Tool results:** The actual return value of every tool call, not just whether it succeeded
- **Timing:** Latency per step, total latency, wall clock timestamps
- **Metadata:** Model name, temperature, token counts, cost estimate

Langfuse's documentation emphasizes that tool calls and retrieval steps must be logged as first-class observations, not buried in raw text: "Application tracing records the complete lifecycle of a request as it flows through your system. Each trace captures every operation — LLM calls, retrieval steps, tool executions, and custom logic — along with timing, inputs, outputs, and metadata." (langfuse.com/docs)

### OpenTelemetry for LLMs (OpenLLMetry)

OpenTelemetry (OTEL) is the CNCF standard for distributed tracing. OpenLLMetry is the LLM-specific convention layer on top of OTEL, maintained by Traceloop. It defines span attributes for:
- `llm.vendor`, `llm.request.model`, `llm.response.model`
- `llm.usage.prompt_tokens`, `llm.usage.completion_tokens`
- `llm.prompts` (array of prompt messages), `llm.completions` (array of responses)

This matters because it enables interoperability: an OTEL-instrumented application can send traces to Langfuse, Phoenix, Datadog, or any OTEL-compatible backend without vendor lock-in. Langfuse explicitly supports OTEL ingestion alongside its own SDK.

The practical value: OTEL lets you bring your existing observability infrastructure (if you have one) and layer LLM-specific semantics on top, rather than adopting a fully separate tracing stack.

### Replay and debugging: Langfuse vs Phoenix vs Braintrust

Three tools dominate here as of 2026:

**Langfuse** (open source, self-hostable, 25k GitHub stars as of Apr 2026):
- Purpose-built for LLM applications
- Captures traces, sessions, observations (spans), prompt versions, evaluation scores
- Supports LLM-as-judge natively, dataset management, A/B experiments
- OTEL ingestion + native SDKs (Python, JS)
- Self-hosted or cloud; v4 released Apr 2026 ("Faster, Observations-First")
- Skill available: `github.com/langfuse/skills` for agent integration

**Phoenix** (Arize AI, open source):
- Strong on evaluation + tracing co-located
- Has an MCP server for agent integration
- Good for teams already using Arize for ML monitoring

**Braintrust** (commercial):
- Strong on pairwise eval, experiment tracking
- MCP server available
- More opinionated workflow (experiments are first-class)

**LangSmith** (LangChain, commercial):
- Tightly integrated with LangChain/LangGraph
- MCP server available
- Better choice if you're already on the LangChain stack

The key difference between Langfuse and the others is self-hostability and open source governance. For teams with data privacy constraints, Langfuse is the default choice.

### Privacy implications when observing user sessions

When you log every LLM input and output, you are storing user conversations. This has implications:

- **PII exposure:** User messages may contain names, health information, financial data. Traces must be scrubbed or access-controlled.
- **Consent:** Depending on jurisdiction (GDPR, CCPA), storing detailed conversation logs may require explicit consent or a legal basis.
- **Data retention:** Traces for debugging purposes need a retention policy. Langfuse supports configurable retention.
- **Internal access control:** Not all engineers should have access to all user conversations. Role-based access on the observability platform is not optional for production systems.

This is not a tooling problem — it is a policy problem. The tooling must support the policy (access controls, masking, retention), but the policy must be designed by humans.

---

## Section 4: Constraints and Guardrails

### Input guardrails (what the user can send)

Input guardrails intercept the user's message before it reaches the agent. Common types:

- **Prompt injection detection:** Attempts to override system prompt or hijack agent behavior
- **Jailbreak detection:** Attempts to elicit out-of-policy content
- **Topic scope:** Reject inputs outside the agent's intended domain ("This is a billing bot; I can't discuss politics")
- **PII detection:** Block or scrub user PII before it enters the LLM context (relevant when you don't want to log or process it)
- **Rate limiting / abuse detection:** Repeated malformed inputs from the same user

These are implemented as pre-processing validators that run before the agent processes the input. They should be fast (computational or small classifier model) to avoid adding latency to every request.

### Output guardrails (what the agent can produce)

Output guardrails intercept the agent's response before it reaches the user:

- **Factual grounding:** Does the output cite claims not present in the retrieved context? (hallucination detection)
- **Competitor mentions:** Block outputs that mention competitors by name (brand safety)
- **Toxic/harmful content:** Detect hate speech, harassment, dangerous instructions
- **Structured output validation:** Verify that JSON/code outputs conform to the expected schema
- **Regulatory compliance:** For financial or medical agents, flag outputs that constitute specific regulated advice

**Guardrails AI** (github.com/guardrails-ai/guardrails) implements this as a validator pattern. Each validator is a callable that receives the output and returns Pass or Fail with an action directive (`OnFailAction.EXCEPTION`, `OnFailAction.REASK`, `OnFailAction.FIX`). Multiple validators compose into a Guard:

```python
guard = Guard().use(
    ToxicLanguage(threshold=0.5, on_fail=OnFailAction.EXCEPTION),
    CompetitorCheck(["Competitor A"], on_fail=OnFailAction.REASK)
)
```

The `REASK` action is significant: it sends the output back to the LLM with the violation highlighted, asking for a rewrite. This is a form of automated self-correction that Böckeler would call "positive prompt injection via sensor output."

### Policy as code: NeMo Colang

NVIDIA's NeMo Guardrails (github.com/NVIDIA/NeMo-Guardrails) introduces Colang, a domain-specific language for encoding guardrail policies as flows:

```colang
define flow answer report question
  user ask about report
  bot provide report answer
  $accuracy = execute check_facts
  if $accuracy < 0.5
    bot remove last message
    bot inform answer unknown
```

The architecture is event-driven. Every user utterance becomes a `UtteranceUserActionFinished` event. The runtime:
1. Generates a canonical user intent via LLM + vector search on intent examples
2. Looks up pre-defined flows that match the intent
3. If no matching flow, uses LLM to generate the next step
4. Generates a bot utterance for any `BotIntent` events

This is more powerful than simple input/output validators because it can express multi-turn conditional policies: "if the bot says X, then check Y, and if Y fails, do Z." The DSL approach means policies are auditable, version-controlled, and can be reviewed by non-engineers.

**The tradeoff:** Colang adds latency (3 LLM calls minimum per turn: intent, next step, utterance). It is well-suited to regulated environments where policy auditability matters more than latency.

### The false-positive problem

The false-positive problem is the defining tension in guardrail design. An overly sensitive guardrail that blocks legitimate requests destroys user trust faster than an occasional policy violation. A study of production support bots shows that false-positive rates above ~2-3% cause significant user abandonment.

The correct calibration strategy:
1. Never tune guardrails on synthetic data only — real user inputs will find edge cases you didn't imagine
2. Measure false-positive rate explicitly, not just false-negative rate
3. For topic-scope guardrails specifically: users regularly ask edge-case questions that are topically adjacent but legitimate. A billing bot user asking "why does my subscription auto-renew?" is technically asking about subscription policy, not billing — but blocking it would be wrong.
4. Provide a graceful degradation path: when a guardrail fires, the agent should explain what it cannot help with and suggest an alternative, not just return an error.

### Guardrails AI validator pattern summary

The `OnFailAction` enum captures the three recovery options:
- `EXCEPTION`: Raise an exception, propagate to error handler — use for hard policy violations
- `REASK`: Return output to LLM with violation highlighted — use for fixable quality issues
- `FIX`: Apply a deterministic transformation (e.g., strip competitor names, replace with `[REDACTED]`) — use when the fix is mechanical

The validator hub at guardrailsai.com contains pre-built validators for common risks (toxic language, competitor mentions, PII, regex patterns, two-word constraints, etc.). Custom validators are Python callables following the validator interface.

---

## Section 5: Recovery Mechanisms

### Retry strategies (and when NOT to retry)

**When to retry:**
- Transient errors: API rate limits, network timeouts, 5xx errors from external services
- Non-deterministic LLM failures where re-sampling may produce a better output (e.g., malformed JSON that occasionally works)

**When NOT to retry:**
- Deterministic failures: if the LLM consistently produces the wrong output for this input, retrying produces the same wrong output at higher cost
- Guard failures that indicate a policy violation: retrying a jailbreak attempt doesn't make sense
- Context overflow: if the context is too long, retrying with the same context will fail again
- Budget exhaustion: retrying when you're already at the token or cost limit makes the problem worse

**Exponential backoff with jitter** is the standard for transient errors. The key parameter is the retry budget: how many retries are you willing to pay for before escalating? For production agents, 2-3 retries maximum before escalation is a reasonable ceiling.

**The deeper problem:** Hamel (via Lopopolo's frame) argues that if your agent needs to retry frequently, the root cause is usually a harness deficiency — missing context, unclear instructions, underspecified tool descriptions. The retry mechanism masks the underlying problem. Track retry rates as a harness quality metric, not just as infrastructure noise.

### Checkpointing (LangGraph)

LangGraph's persistence layer saves graph state as checkpoints at every "super-step" (one tick of the graph where all scheduled nodes execute). The design has four benefits:

1. **Human-in-the-loop:** A human can inspect state at any checkpoint, modify it, and resume — without restarting the entire graph from scratch
2. **Time travel debugging:** Replay the exact sequence of states that led to a failure
3. **Fork and explore:** Branch the state graph at any checkpoint to test alternative paths
4. **Fault tolerance:** If a node fails mid-execution, resume from the last successful checkpoint; nodes that completed in the same super-step don't re-execute

Implementation: compile a graph with a `checkpointer`, specify a `thread_id` in config. The checkpointer is pluggable (in-memory for development, PostgreSQL/Redis for production). LangGraph Agent Server handles checkpointing automatically if you use it.

This is most valuable for long-running agents (multi-step planning, research agents) where restarting from scratch on failure is expensive. For simple single-turn agents, the overhead is not worth it.

### Context Reset (Lopopolo pattern)

Distinct from LangGraph checkpointing. The context reset pattern applies when a long-running agent session has accumulated so much state and history that the model's attention is degraded by irrelevant earlier content.

The pattern (from Symphony/Lopopolo):
1. Detect signal: the agent starts making errors that seem unrelated to the current task, or task completion quality is declining
2. "Burn down": trash the current context window entirely (not compact, not summarize — trash)
3. Transfer essentials: extract only the structured state that the new session needs (current task state, key decisions made, current failure context)
4. Restart with clean context: new session, current state injected as structured context

**When to use Context Reset vs Compact:**
- **Compact:** When context is large but still mostly relevant. Keep the substance, compress the verbosity. Use when you need continuity of thought.
- **Reset:** When context has accumulated irrelevant or contradictory history that is actively confusing the model. Use when you need a clean slate with structured state transfer.

The decision heuristic: if re-reading the context would help a human understand the current task, compact. If re-reading would confuse a human, reset.

### Rollback (transactions for agents)

True rollback — the ability to undo agent actions as a unit, transactionally — is largely unsolved for agents that interact with external systems. The database analogy breaks down because:

- Agent actions are often irreversible (sent an email, charged a card, deleted a file)
- Agent actions happen across multiple systems with no shared transaction coordinator
- The "undo" action for many agent operations must itself be a new LLM call (undo is semantic, not mechanical)

What partial solutions exist:
- **Reversible actions:** Design agent tools to prefer reversible operations. "Move to trash" instead of "delete". "Draft email" instead of "send email". Require explicit confirmation for irreversible actions.
- **Audit trail:** Log every tool call with enough state to reconstruct what happened — even if you can't mechanically roll back, a human can manually remediate.
- **Staged execution:** Don't execute until a plan review step. LangGraph interrupts implement this: the graph pauses at a checkpoint before the irreversible step and waits for human approval.
- **Idempotency:** Design tools to be idempotent where possible, so "re-running" doesn't cause double-effects.

The honest assessment: for agents with write access to consequential systems, the architectural principle is "design for auditability and minimal blast radius," not "design for rollback." True transactional rollback for agent actions is a research problem.

### HITL escalation triggers

Human-in-the-loop escalation is triggered by uncertainty or consequence. The decision framework:

**Escalate based on consequence:**
- Irreversible action about to be taken (send, delete, pay, deploy)
- Action affects more than N records/users
- Financial amount exceeds threshold
- External communication to a customer or partner

**Escalate based on uncertainty:**
- Agent confidence is low (where "confidence" is estimated via judge, not just logprob)
- Guardrail fired but agent tried to continue anyway
- Retry budget exhausted
- Task has been running longer than expected without progress
- Internal state is contradictory (planned action conflicts with a known constraint)

**The minimum viable HITL interface:** The agent produces a structured decision request (what it wants to do, why, what the alternatives are, what happens if blocked). A human reviews asynchronously and responds with approve/reject/redirect. LangGraph interrupts + async checkpointing make this practical without blocking the agent synchronously.

**The Lopopolo pattern for HITL in Symphony:** Humans open the app twice a day, review pending decisions, approve or reject. The agent does not wait synchronously. The escalation is a state change in the task graph, not a blocking call. This decoupling is what makes asynchronous HITL scale.

---

## Section 6: Garbage Collection (Lopopolo Concept)

### Precise definition

Garbage collection (GC) in the Lopopolo/harness engineering sense is **not**:
- Context pruning (removing old messages from a context window)
- Memory management (deciding what goes to long-term memory)
- Refactoring sprints (developer-led cleanup sessions)

It **is**: recurring background agent tasks that run at a weekly or per-sprint cadence, scanning the codebase for deviations from "golden principles" and opening targeted refactoring PRs that can be reviewed in under a minute.

Lopopolo: "Human taste is captured once, then enforced continuously on every line of code." (OpenAI article, openai.com/index/harness-engineering/)

The problem GC solves: agent-generated codebases accumulate entropy. Agents replicate patterns — including bad ones. Every agent that writes a slightly different version of a utility function, or uses an older API pattern because it was in context, adds a unit of entropy. Without GC, this compounds. Lopopolo's team called this "AI slop."

### Concrete examples from Symphony

From F1 source (direct, OpenAI article):

- **Prefer shared utility packages:** When agent-written code rolls its own helper that duplicates an existing utility, a GC task detects the duplication and opens a PR to replace it with the canonical utility. This keeps invariants centralized.
- **Enforce typed SDK usage:** When agent-written code probes data structures without type assertions (YOLO-style access), GC flags it and proposes the typed version.
- **Golden principle enforcement:** The team encodes opinionated mechanical rules (naming conventions, module boundaries, error handling patterns) as scannable rules. GC tasks check compliance and auto-generate micro-PRs.
- **Quality grade tracking:** Each file or module has a quality grade. GC tasks update these grades and surface modules that have drifted below threshold.

### How Symphony handles it

Symphony (OpenAI's internal Elixir-based orchestration) runs GC as a separate class of Codex tasks — not prompted by a user request, but scheduled by the orchestration layer itself. These tasks:
1. Have read access to the entire codebase
2. Run against the "golden principles" encoded in the repo's docs/quality directory
3. Produce minimal, reviewable PRs (reviewed in under a minute — the goal is to make them easy to merge without deep inspection)
4. Run on a recurring cadence, not triggered by failures

The Elixir/BEAM implementation allows running many small GC tasks in parallel without managing concurrency manually — each is a lightweight process (gen_server) with its own lifecycle.

### Is this just "refactoring" rebranded?

**The case that it is:** Refactoring has always meant improving code structure without changing behavior. Linting and style enforcement are not new. Teams have always had "cleanup sprints." The concept of encoding style rules as linters exists in every mature codebase.

**The case that it is not:** Several things are genuinely new:

1. **Automation level:** Traditional refactoring requires a developer to write the fix. GC uses an agent to write the fix — the human only reviews. The cost of executing a refactor drops from 30 minutes to 2 minutes.
2. **Continuous cadence:** Traditional cleanup sprints happen when someone is frustrated enough to schedule one (roughly: never regularly). GC is infrastructure — it runs whether or not a human thought to schedule it.
3. **Scale:** 1,500 PRs over 5 months at Symphony were agent-generated. A human team cannot sustain that PR rate. The GC pattern is only viable at this scale because agents write the fixes.
4. **Entropy rate:** Human-generated codebases accumulate entropy at a human rate. Agent-generated codebases accumulate entropy at agent speed. Human-paced cleanup cannot keep up — GC as infrastructure is not optional.

**Verdict:** The concept of "continuous technical debt reduction" is not new. What is new is the automation level and the necessity imposed by agent-speed entropy generation. Calling it a new concept is partially marketing; calling it merely "refactoring" misses what's operationally different.

---

## Section 7: Behaviour Harness (The Unsolved Problem)

### Why maintainability and architecture fitness have solutions but behaviour doesn't

**Maintainability** (internal code quality, style, structure) has:
- Linters, formatters, type checkers — fully automated, fast, cheap
- Coverage metrics with clear interpretation
- GC tasks for drift management

**Architecture fitness** (architectural characteristics — coupling, layering, dependencies) has:
- Structural tests (ArchUnit, custom dependency checks)
- Fitness functions (measurable thresholds: cyclomatic complexity < N, fan-out < M)
- These are deterministic — pass or fail, no ambiguity

**Behaviour** (does the agent actually do the right thing for the user?) has:
- Nothing equivalent

The reason is fundamental: correctness is not specifiable in advance. As Böckeler writes: "Correctness is outside any sensor's remit if the human didn't clearly specify what they wanted in the first place." (F2, martinfowler.com/articles/harness-engineering.html)

For unit-tested software, "correct" means "matches spec." For LLM agents, the spec is often incomplete, ambiguous, or only articulable by observing failures. This is Shankar's criteria drift from the other direction: you don't know the full specification until you've seen enough failures.

### What "behaviour" means exactly (Böckeler's frame)

Böckeler distinguishes three regulation categories (F2):

| Category | Regulated by | Harnessability |
|---|---|---|
| Maintainability | Linters, type checkers, GC | High |
| Architecture fitness | Structural tests, fitness functions | Medium |
| Behaviour | ??? | Low — major open problem |

"Behaviour" here means functional correctness: does the agent's output correctly accomplish the user's goal for this input? Not: is the code syntactically valid? Not: does the architecture follow the correct layering? Does it actually work?

The distinction matters because many eval approaches claim to solve behaviour but only solve a proxy. "Judge says thumbs up" is not the same as "user's problem was solved."

### Partial solutions that exist

**1. LLM-as-judge (calibrated):** Covered in Section 2. It approximates human preference judgment at scale. The limitation: it measures outputs, not outcomes. An agent that gave a technically correct answer that the user couldn't act on passes the judge but fails the user.

**2. A/B testing in production:** Compare system A vs. system B on real user traffic. Measure downstream user actions (did the user follow the agent's recommendation? Did they escalate? Did they churn?). This is the most reliable signal but requires scale (enough traffic to reach statistical significance) and time.

**3. Slow rollout / canary deployment:** Roll out a changed agent to 5% of users first. Monitor downstream metrics before full rollout. Standard practice from software deployment, now applied to agent behaviour.

**4. Reputation systems:** Track quality scores per agent version over time. Downweight agents with declining scores. This is a lagging indicator — you learn about failure after it has happened at scale.

**5. Approved fixtures pattern (Böckeler):** Maintain a set of "golden" input-output pairs that have been manually approved by domain experts. The behaviour harness checks that the agent still produces approved outputs for these inputs. Limited because it only covers the explicitly approved cases.

**The honest assessment:** None of these is the equivalent of a comprehensive test suite. They are risk-reduction strategies, not quality guarantees. Böckeler explicitly flags the behaviour harness as the "elephant in the room" and "major open problem." (F2)

### Research frontier

The direction most likely to produce progress:
- **Outcome-grounded evaluation:** Measure user task completion, not output quality. Requires instrumentation of downstream user actions.
- **Procedural evaluation:** For agents with known execution patterns, verify that the procedure was correct (right tools called in right order), not just the final output.
- **Tau-Bench and similar:** Task-focused benchmarks where correctness is deterministic (the tool was called with the right arguments, the transaction completed correctly). These cover the "known-correct" subset of behaviour but miss open-ended reasoning tasks.

---

## Section 8: Patterns vs Anti-Patterns

| Pattern | Anti-Pattern | Why It Matters |
|---|---|---|
| **Error analysis before infrastructure:** Review 50 real traces before building any automated evaluator | **Infrastructure first:** Build eval pipeline, dashboards, and metrics before looking at data | Anti-pattern builds metrics for problems you haven't diagnosed; produces good-looking dashboards that measure the wrong things |
| **Binary (Pass/Fail) judge with critique:** Single decision + written reason | **Likert scale scoring (1-5):** Averaging over raters introduces calibration variance | Binary forces a decision; Likert scales produce mushy averages that hide disagreement between raters |
| **Domain expert as "benevolent dictator":** One expert per eval domain who resolves disagreements | **Democratic annotation:** Average all annotators' scores | Averaging hides signal; one calibrated expert is more valuable than five uncalibrated ones |
| **Calibrate judge against human labels (TPR/TNR):** Measure false-positive and false-negative rates separately | **Accuracy-only calibration:** Measure overall agreement rate | A judge with 95% accuracy but 20% TPR on failures is worse than useless — it misses most real problems |
| **Traces as first-class observability:** Log full agent DAG including intermediate states | **Response-only logging:** Log only final user-facing output | Can't debug failures without intermediate state; can't do root cause analysis |
| **Sensors optimized for LLM consumption:** Linter error messages that include remediation instructions | **Generic error codes:** Return numeric error codes or cryptic messages | The agent can self-correct from a descriptive error; it cannot infer what to do from error code 403 |
| **Checkpointing for long-running agents:** Persist state at super-step boundaries | **Stateless long-running agents:** No persistence, restart from scratch on failure | Hours of agent work lost on transient failures; no HITL possible without state |
| **GC as recurring infrastructure:** Scheduled background agent tasks for entropy fighting | **GC as sprint events:** "We'll do a cleanup sprint next quarter" | Quarterly sprints cannot keep pace with continuous agent-generated entropy |
| **Minimal blast radius tool design:** Prefer reversible operations, require confirmation for irreversible | **Full write access by default:** Agent can delete, send, pay without confirmation | Irreversible failures are unrecoverable; designing for reversibility is cheaper than incident response |
| **HITL as asynchronous state:** Agent continues with other work while awaiting human review | **Synchronous HITL blocking:** Agent waits in real time for human approval | Synchronous HITL means the agent is blocked and the human must respond immediately — doesn't scale |

---

## Section 9: Four Concrete Failure Scenarios

### Failure 1: The Self-Congratulatory Judge

**Scenario:** A support bot is deployed with an LLM-as-judge evaluator using the same model (GPT-4o) for both the bot and the judge. Post-launch monitoring shows a 94% pass rate. Customer satisfaction scores are declining.

**What went wrong:** The judge and the judged share the same biases, the same blind spots, and the same failure modes. The judge approves responses the bot produces confidently — including confidently wrong responses. This is the circular validation problem from Section 1.

**Fix:** Use a different model family for the judge (judge with Claude, generate with GPT, or vice versa). Calibrate the judge against a manually labeled set of 100 examples. Monitor TPR separately from overall accuracy.

### Failure 2: The Criteria Drift Trap

**Scenario:** A team writes 50 eval test cases based on their product spec before launch. All 50 pass. After three weeks in production, users are reporting that the bot gives unhelpful responses in a specific scenario the spec didn't cover.

**What went wrong:** The eval set was written from the spec (what the team imagined users would ask), not from real user behavior. Shankar's criteria drift: the team couldn't write the right criteria without observing the failures, but the failures only appeared in production.

**Fix:** Run error analysis on real production traces immediately after launch (Day 1, not Week 3). Add new test cases from real failure modes. Treat the initial eval set as a starting point, not a complete spec. Budget for regular eval set expansion from production data.

### Failure 3: The Silent Context Rot

**Scenario:** A research agent is running a multi-step investigation task (12 steps, ~2 hours wall time). Around step 8, the agent starts making decisions that contradict decisions it made in step 3. The final output is internally inconsistent. The user has no visibility until the end.

**What went wrong:** The agent's context window has accumulated enough history that early decisions are being "forgotten" or down-weighted by the model's attention. There was no context management strategy (no checkpointing, no context reset protocol, no intermediate state extraction).

**Fix:** Implement LangGraph checkpointing so state is preserved at each super-step. Add an intermediate state extraction step every N steps that summarizes key decisions into structured form and adds them to the active context as a structured reminder. Implement context quality monitoring: detect when output quality starts degrading mid-task.

### Failure 4: The Entropy Accumulation Cliff

**Scenario:** A team builds a codebase rapidly with a coding agent over 3 months. Everything works. In Month 4, making any change seems to break something else. The codebase has three different implementations of the same date utility. Authentication logic is inconsistently applied across modules. New agents onboarded to the codebase produce code that follows one of several conflicting patterns.

**What went wrong:** No garbage collection mechanism. The agent replicated patterns from whatever was in context at the time of each PR. Without GC, three implementations of the same utility diverged. Without GC, different sessions produced different patterns. The technical debt did not accumulate linearly — it compounded.

**Fix:** Implement GC from Month 1, not Month 4. Encode golden principles in the repo (canonical utilities, naming conventions, authentication patterns). Schedule weekly GC agent runs that scan for violations and open micro-PRs. Make the micro-PRs easy to approve (under 60 seconds to review). The cost in Month 1 is a few hours of setup; the cost in Month 4 is a rewrite.

---

## Section 10: What a Learner Should Internalize

**Mental model 1: Evaluation is a discipline, not a tool.**
You don't "add evals" to an agent — you build a continuous practice of error analysis, criteria development, and automated monitoring. The tooling (Langfuse, Braintrust, Promptfoo) supports the practice. Without the practice, the tooling is expensive infrastructure for measuring the wrong things.

**Mental model 2: Sensors are the feedback loop; Guides are the feedforward loop. You need both.**
Böckeler's insight is structural: a system with only Guides (rules, AGENTS.md, instructions) will repeat mistakes it's never told about. A system with only Sensors (linters, eval feedback) has no proactive steering and relies entirely on reactive correction. Both together create the self-correcting loop.

**Mental model 3: Guardrails reduce blast radius; evaluation measures trajectory.**
Guardrails prevent individual bad outputs from reaching users. Evaluation tells you whether the system is trending better or worse over time. Confusing them means either (a) building guardrails and thinking you've done quality assurance, or (b) measuring quality without protecting users from immediate harms.

**Mental model 4: Behaviour correctness is not yet a solved engineering problem.**
The urge to close the loop with automated eval is strong. Resist it. Automated evals measure proxies for correctness, not correctness itself. The honest answer — "we monitor closely, we A/B test carefully, and we escalate uncertainty to humans" — is more durable than a false sense of automated coverage.

**Mental model 5: Entropy is a budget, not a one-time cost.**
Agent-generated codebases don't have a fixed technical debt ceiling that you pay down once and hold steady. Entropy accrues continuously at the rate agents generate code. GC is not a cleanup — it is a continuous operating expense. Budget for it from the start.

---

## Section 11: Further Reading with Ratings

| Resource | Rating | Why |
|---|---|---|
| Hamel Husain + Shreya Shankar, "LLM Evals: Everything You Need to Know," hamel.dev/blog/posts/evals-faq/ (Jan 2026) | ★★★★★ | The most practically grounded eval guide available. Direct experience from 700+ engineers, 50+ companies. Binary judgments, error analysis emphasis, anti-generic-metrics stance. Required reading. |
| Shreya Shankar et al., "Who Validates the Validators?" arXiv:2404.12272 (Apr 2024) | ★★★★☆ | Academic; formally establishes criteria drift and circular validation problems. The EvalGen system is the concrete proposal. Less actionable than the FAQ but provides the theoretical grounding. |
| Hamel Husain, "Evals Skills for Coding Agents," hamel.dev/blog/posts/evals-skills/ (Mar 2026) | ★★★★☆ | Practical skill set for coding agents. The error-analysis skill, judge calibration skill, and eval-audit skill are directly usable. Complements the FAQ. |
| Birgitta Böckeler, "Harness Engineering," martinfowler.com/articles/harness-engineering.html (Apr 2026) | ★★★★★ | The Sensors section is the canonical theoretical treatment of quality controls in agent harnesses. The computational/inferential distinction and the behaviour harness open problem are unique contributions not found elsewhere. |
| Langfuse documentation, langfuse.com/docs | ★★★★☆ | Best reference for production tracing implementation. Open source, well-maintained, OTEL-compatible. The concepts section (traces, sessions, observations) is precise and interoperability-focused. |
| NeMo Guardrails Architecture, github.com/NVIDIA/NeMo-Guardrails/blob/main/docs/architecture/README.md | ★★★☆☆ | Good reference for Colang DSL and event-driven guardrail architecture. Useful if you need policy-as-code at the framework level. More complex than most teams need. |
| Guardrails AI, github.com/guardrails-ai/guardrails | ★★★☆☆ | Practical validator pattern. The Hub is a good source of pre-built validators. The framework is Pythonic and composable. Less architectural depth than NeMo, more immediately useful for most teams. |
| LangGraph Persistence docs, docs.langchain.com/oss/python/langgraph/persistence | ★★★★☆ | Definitive reference for checkpointing implementation. The super-step concept, thread model, and human-in-the-loop interrupt pattern are well-documented. Read if using LangGraph. |
| Ryan Lopopolo, "Harness Engineering," openai.com/index/harness-engineering/ (Feb 2026) | ★★★★★ | Primary source for GC concept, rework loop, and production harness case study. Already extensively summarized in F1 — this rating is for the original source value. |

---

## Section 12: Source Reliability Notes

| Source | Access Method | Reliability | Notes |
|---|---|---|---|
| hamel.dev/blog/posts/evals-faq/ | Direct HTML fetch, text extracted | **HIGH** | Full content accessible. Jan 2026. Authored by Hamel Husain + Shreya Shankar from direct practitioner experience. Not peer-reviewed but empirically grounded. |
| hamel.dev/blog/posts/evals-skills/ | Direct HTML fetch, full content | **HIGH** | Mar 2026. Short practical post, GitHub repo linked and verifiable. |
| arxiv.org/abs/2404.12272 | Direct HTML fetch, full abstract + metadata | **HIGH** | Peer-reviewed, ACM CHI 2024. Abstract fully recovered. Full paper not fetched but abstract contains the key claims. |
| github.com/NVIDIA/NeMo-Guardrails (architecture README) | Direct raw GitHub fetch | **HIGH** | Full markdown content fetched from main branch. Architecture description is authoritative. |
| github.com/guardrails-ai/guardrails (README) | Direct raw GitHub fetch | **HIGH** | Full README fetched. Code examples verified. API may have changed since README was last updated. |
| langfuse.com/docs | Direct HTML fetch, text extracted | **HIGH** | Content accessible. Tracing and get-started pages fetched. Open source; claims verifiable against GitHub (25k stars). |
| docs.langchain.com/oss/python/langgraph/persistence | Direct HTML fetch | **HIGH** | Full persistence/checkpointing doc fetched. LangGraph is well-documented and actively maintained. |
| F1 (Lopopolo) | Pre-fetched, stored in source_texts/F1_lopopolo_origin.md | **HIGH** | Two sources (OpenAI article + Latent Space transcript) fetched directly in prior session. Used here as secondary reference. |
| F2 (Böckeler) | Pre-fetched, stored in source_texts/F2_bockeler_taxonomy.md | **HIGH** | Primary article + memo fetched directly in prior session. Used here as secondary reference. |
| promptfoo.dev | NOT FETCHED | **UNVERIFIED** | Listed as priority source; site is JS-rendered and not directly fetchable without browser. Acquired by OpenAI Mar 2026. Core functionality (prompt testing, red-teaming) described from general knowledge — treat any Promptfoo-specific claims in this document as approximate. |
| Anthropic "Building reliable agents" post | NOT FETCHED | **UNVERIFIED** | Could not confirm canonical URL. General Anthropic guidance on agent reliability drawn from known public documentation. |

**Gap declaration:** Promptfoo is not covered with direct source evidence. This is a meaningful gap for Section 4 (Constraints) where Promptfoo's red-teaming capabilities are relevant. A follow-up fetch or a dedicated Promptfoo subagent would fill this gap for completeness.

---

*Estimated read time: 16-20 minutes*
*Layer scope: Sensors side of Böckeler's Guides-Sensors 2x2; covers Evaluation, Observability, Constraints, Recovery, Garbage Collection*
*Companion files: B1_info_layer.md (if created), B2_execution_layer.md (if created), 00_master_synthesis.md*
