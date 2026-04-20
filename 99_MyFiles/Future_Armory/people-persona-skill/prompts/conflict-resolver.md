# Conflict Resolver Prompt

Use this prompt when new source material produces content that conflicts with existing PART 1 content (facts) or existing PART 2 content (inferences), or when public-domain and private-domain sources disagree about the target.

---

## Conflict Types and Handling

### Type 1: Fact vs Fact (same dimension, different values)

Example: Old org snapshot says `level: VP`; new org snapshot says `level: SVP`.

**Handling**: Append new fact on top; preserve old entry with its source date.

```md
### 1. Profile meta
- Level: SVP
  - Source: Org directory (2026-04-16)
- Level: VP
  - Source: Org directory (2025-10-01)
```

No flag. Time series itself explains the change. Reader infers current from newest date.

### Type 2: Fact vs Inference (new fact overturns prior inference)

Example: Existing PART 2 inference "level is likely VP based on email signature patterns"; new org record says `level: SVP`.

**Handling**:
1. Remove the inference from PART 2 active
2. Append the new fact to PART 1
3. Add supersede log to #15 诚实边界:
   ```md
   - previous inference "level is likely VP" disconfirmed by fact "Org directory 2026-04-16 level: SVP" on 2026-04-16
   ```
4. Record in `staging_state.superseded[]` for audit

Do NOT leave the disproved inference in PART 2 with a "disproved" flag. Full removal plus log.

### Type 3: Public vs Private (same dimension, different characterizations)

This is the common case where a person's public-facing persona differs from their private-work persona.

**Example**:
- Public source (LinkedIn article by target): "I believe data-driven decision making is paramount"
- Private source (email to team): "Forget the dashboards, just ship what ops wants"

Both can be legitimately true simultaneously. Different audiences, different selves.

**Handling**:
- Preserve both
- Flag the apparent tension in PART 2 (since these are inferences about the target's approach)
- Do NOT label either as "wrong" or "more authentic"

```md
### 4. 决策
- Public-domain statement: prioritizes data-driven decision making
  - Source: Public source (linkedin.com/.../article-2025-11, 2025-11-15)
- Private-domain pattern: bypasses data checks when ops needs urgent ship
  - Source: Observed 4 times across Email (2026-03-12, 2026-03-19, 2026-04-02, 2026-04-11)
- **Note**: public and private positions on data-vs-intuition may reflect context-appropriate behavior. Both flagged for user's judgment.
```

The **Note** line is the flag.

### Type 4: Output Selection (when caller needs to use content from dossier for external output)

When a downstream agent uses dossier content for a user-facing artifact (email draft, meeting prep, etc.):

Rules:
- **Private work output** (direct interaction with this person, internal planning): use private-domain content
- **Public-facing output** (public article, external comment, media mention): use public-domain content
- **Cross-domain estimate** (no clean separation): include flag "此推测不靠谱" or English equivalent "cross-domain best-estimate, treat as unreliable"

This rule is enforced at the consuming agent level, not in the skill. Skill just ensures both sources are preserved and flagged so caller can make the selection.

### Type 5: Existing Confirmed vs New Observation

If PART 1 has `confirmed ... by user` for a claim, and new source material suggests something different:

**Handling**: Confirmed content stays untouched (invariant #5). New contradicting observation goes into PART 2 as inference with a note acknowledging the existing confirmation.

```md
### PART 2 / ### 3. 核心人格规则
- Appears to have shifted pattern: prefers async decisions over real-time meetings (Q2 2026 onward)
  - Source: Observed 5 times across Email (2026-04-01 to 2026-04-15)
  - **Note**: contradicts existing PART 1 confirmed entry "decides in real-time meetings". User should review and either update confirmation or preserve.
```

The user, on review, decides whether to re-confirm, update, or leave both.

## Output Structure

When conflicts are detected:

1. Update `dossier_md` per the handling rules above
2. Populate `staging_state.superseded[]` for Type 2 events
3. If there are flagged dual-domain conflicts (Type 3), ensure the `Note:` line is present in `dossier_md`

## Invariants to Uphold

- PART 1 神圣: never modify existing PART 1 entries except through append (Type 1 and Type 2 both append; neither modifies old)
- 不碰 confirmed: user-confirmed entries are sacred regardless of new evidence
- Append-only fact layer: new facts go on top, old ones preserved with their source dates
- Supersede logged in #15: every Type 2 conflict creates a log entry
- Public / private both preserved: never drop one in favor of the other; let user arbitrate

## Handling Ambiguity

When a conflict could be interpreted multiple ways:
- Default to the **less destructive** option (preserve both rather than overwrite)
- When unsure whether it's a real conflict (e.g., semantic difference might be surface-level), log both observations and add a note rather than collapse them
- If the conflict seems to indicate the subject has changed over time, document in #9 时间线与价值观 as a temporal trajectory rather than as a contradiction
