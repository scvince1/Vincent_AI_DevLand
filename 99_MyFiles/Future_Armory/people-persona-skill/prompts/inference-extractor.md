# Inference Extractor Prompt

Use this prompt to generate **inference-layer** content: personality patterns, decision heuristics, style descriptions, interpersonal models, mental models. All go into PART 2 unless promoted by user confirmation.

---

## Task

Given source materials about a target person, derive characterizations that:

1. Are **not verbatim** (they are your synthesis from observed behaviors)
2. Appear in **multiple independent observations** (≥3, per staging threshold)
3. Are **flagged** as inference in output
4. Do **not** invent content beyond what evidence supports

## Staging Discipline

Before surfacing an inference into PART 2 active list, verify:

- **N ≥ 3**: same pattern observed in ≥3 distinct message / meeting / event instances
- **T ≤ 90 days**: observations within a 90-day rolling window
- **Per-dim override**: if the target's #15 诚实边界 explicitly relaxes to N=2 for a specific dimension (e.g., sparse data), honor it

If the threshold isn't met, the observation stays in `staging_state.observations[]` (counter incremented) and does NOT appear in `dossier_md` output. Skill returns updated `staging_state` for caller to persist.

## What to Extract per Dimension

### 3. 核心人格规则 (IF-THEN behavioral rules)

Not adjectives ("thoughtful"). Concrete behavioral rules:
- "When questioned, counter-asks rather than explains"
- "Before accepting new work, asks for time windows explicitly"
- "Replies to critical messages within 2 hours; non-critical within 24"

Derive from observed consistent behaviors across contexts.

### 4. 决策 (priorities + heuristics)

Two sub-clusters:
- **Situational priorities**: ordered preferences (e.g., "customer experience > process compliance")
- **Abstract maxims**: declarative rules (e.g., "Ship small changes frequently; hold large changes for review")

### 5. 表达 DNA (style)

Inference portion (fact verbatim portion handled separately):
- Sentence patterns (short / long / nested / direct)
- Rhythm (pauses, confidence language like "I suspect" vs "definitely")
- Openings / closings
- Humor style
- Formality shifts by context

### 6. 人际

Patterns by relationship class:
- With superiors: how they escalate / push back / defer
- With subordinates: how they delegate / coach / correct
- With peers: how they collaborate / disagree / yield
- Under pressure: how behavior changes

NOT specific individuals.

### 7. 主体边界

What they consistently refuse:
- Request types they decline
- Topics they don't engage with
- Channels they avoid

### 8. 心智模型

Theoretical frameworks (3-7 total). Each with:
- **Framework name** (concise)
- **Description** (1-2 sentences)
- **Evidence** (source citations)
- **Application scenario** (when applied)
- **Limits** (where fails)

Triple validation gate:
- Cross-domain reproducibility: appears in ≥2 fields of discussion
- Generative power: predicts stance on novel questions
- Exclusivity: not universal / generic (avoid "he thinks systematically")

### 11. 技术规范 (tech roles only)

Stack preferences, code style, naming, CR focus. Omit if not a technical role.

### 12. 工作流程

Task intake patterns, proposal structure, incident response rhythm.

### 13. 输出风格

Document structure, information progression, detail density, tone.

## Output Format per Item

```md
- {inference content}
  - Source: Observed N times across {channel list}
```

Where `Source:` summarizes the evidence behind this inference. Example:

```md
### 3. 核心人格规则
- 被质疑时先沉默 10 秒再答
  - Source: Observed 4 times across Teams (2026-03-14, 2026-03-22, 2026-04-02, 2026-04-09)
- 决策前先问时间窗口
  - Source: Observed 3 times across Email (2026-02-28, 2026-03-15, 2026-04-06)
```

## Invariants to Uphold

- NEVER promote an inference below threshold. Stays in `staging_state`.
- NEVER replace or delete existing PART 2 entries from `existing_record`; only append new promotions.
- NEVER touch PART 1 content (sacred).
- NEVER invent rules / heuristics / frameworks not grounded in observable evidence.
- When in doubt, prefer declaring a gap in #15 over speculation.
- Mark every inference with source-count evidence in the `Source:` line.

## Fallback and Sparse-Data Handling

If evidence is insufficient for a dimension (N<3, no observations, or only N=2 for non-critical dims):

- Option A: Omit the dimension entirely from output
- Option B: If the dimension is crucial and data allows N=2, declare override in #15 诚实边界:
  ```
  - Per-dim override: #3 relaxed to N=2 due to limited source materials
  ```
  Then include the dim in PART 2 with `Source: Observed 2 times ...`

Option A is preferred. Option B is a deliberate choice to communicate a tentative observation.

## Handling of Fact Overturning Inference

If new fact evidence directly contradicts an existing PART 2 inference:

1. Remove the inference from PART 2 active
2. Add supersede log to #15 诚实边界:
   ```
   - previous inference "{X}" disconfirmed by fact "{Y}" on {YYYY-MM-DD}
   ```
3. Record the supersede event in `staging_state.superseded[]` for audit

Do NOT leave the disconfirmed inference in PART 2 with a "disproved" flag. Full removal + log.

## Register and Tone

- Write inferences in neutral-analytical register
- Use third-person about the subject
- No judgmental language ("wisely" / "unfortunately" / "stupidly")
- No guesses about the subject's motivations beyond what evidence directly supports
- Specific > general ("prefers bullet points over prose in status updates" > "is concise")
