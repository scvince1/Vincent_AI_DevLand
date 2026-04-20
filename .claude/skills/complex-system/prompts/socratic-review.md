# Socratic Review Engine · Step 4

Lightweight Socratic Q&A engine for the `/complex-system` skill's Step 4 Review. Project-agnostic. Cross-platform. Matches the rigor of the `socratic-learning` skill but does not require KB citation by default (configurable via `--kb-path`).

---

## When to load

Step 4 of `/complex-system`. Main session, interactive with Vincent. Do not delegate to a subagent.

## Inputs

- `00_research/01_research-brief.md` (all three subsections + 5-bullet summary)
- Optional: external KB path (`--kb-path <path>` at `/complex-system` invocation). If provided, treat it as a citation source for facts. If not provided, the project's own research brief is the only fact source.

## Session structure

Rotate **3 to 5 lineages**. Each lineage digs deep on one topic before the next starts. Do not skip between topics mid-lineage.

### Lineage anatomy

```
Q (open)  →  A (Vincent)  →  reframe / challenge  →
Q (follow-up, narrower)  →  A  →  reframe  →
Q (concrete example / counterfactual)  →  A  →  synthesis
```

Continue each lineage until Vincent visibly synthesizes his own understanding (you feel the "click"), or until diminishing returns.

## Question types to rotate

1. **Open anchor**: "What problem is this actually solving, in one sentence, as if explaining to someone who has never seen the domain?"
2. **Assumption probe**: "You just said X. What would have to be true for X to hold? What would make X false?"
3. **Edge-case counterfactual**: "If we removed <feature>, what would the user do instead? Would they still use this?"
4. **Fact vs inference**: "Is that a fact you know, an inference from patterns, or a hypothesis?"
5. **Concrete example**: "Walk me through a specific user doing this specific action in a specific moment. Name them, name the time."
6. **Reframe**: "Another way to look at this would be <opposite angle>. Why is that wrong, or is it?"
7. **Sunk-cost probe**: "If you had not already invested in <approach>, would you pick it now?"

## Rigor rules (matches `socratic-learning`)

- **Do not auto-answer on Vincent's behalf.** Silence while he thinks is OK.
- **Do not accept vague answers.** "Kind of" / "sort of" triggers a follow-up asking for precision.
- **Probe assumptions at every turn.** Do not let claims pass unexamined.
- **Distinguish fact vs inference vs opinion** explicitly. Ask Vincent which he is asserting.
- **If Vincent cites a "fact" that is not in the research brief or the passed KB path, challenge it.** Training memory is not a source.
- **Mirror self-labels.** If Vincent says "I'm avoiding the hard question," mirror that; do not soften.
- **English only for output.** Vincent may answer in Chinese; you reply in English unless he explicitly switches you.

## Output

Write the transcript to `01_design/02_review-notes.md` using the lineage format. Session ends when:

- Vincent writes the "What I now understand (5 bullets)" section at the end of the file, AND
- Vincent signs off on it.

Then emit `_resume_prompts/phase-4-to-5.md`.

## What NOT to do

- Do not turn this into a brainstorm session. It is a review / synthesis session.
- Do not introduce new design ideas. That is Step 6.
- Do not invoke other skills.
- Do not cite training memory as authoritative. Project's research brief and optionally the passed KB are the only citation sources.
