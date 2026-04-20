# Dimension Specification

15 dimensions organized as: Profile meta (1) + Persona dimensions covering behavior / thinking / interpersonal (2-9) + Work dimensions (10-14) + Dossier-meta (15).

## Dimension Table

| # | Dimension | Default Tier | Source Preference | Content Summary |
|---|---|---|---|---|
| 1 | Profile meta | Fact only | Org directory | name / slug / company / level / role / gender / MBTI (inferred OK) / personality tags / culture tags / impression |
| 2 | 身份 | Mixed | Org + email / transcript | Fact: role / level / dept from org. Inference: MBTI / 文化影响 / 印象 |
| 3 | 核心人格规则 | Inference default | Email + IM + transcript | IF-THEN behavioral rules. Concrete observable behaviors, not adjectives |
| 4 | 决策 | Inference default | Email + IM + transcript | Priorities + heuristics + pushback response |
| 5 | 表达 DNA | Fact + Inference | **Email only** for fact verbatim | 5+ verbatim quotes + style. IM / transcript only as fallback when email sparse |
| 6 | 人际 | Inference default | Email + IM + transcript | Relationship patterns by class: superior / peer / subordinate + pressure response. NOT specific-person |
| 7 | 主体边界 | Inference default | Email + IM + transcript | Subject's refusal patterns, avoided topics |
| 8 | 心智模型 | Inference default | Transcript + public web | 3-7 frameworks with evidence + application + limits |
| 9 | 时间线与价值观 | Mixed | All sources | Fact: timestamped events. Inference: values, pursuits, rejections. Absorbs origin-story content |
| 10 | 职责范围 | Fact only | Org + email | Scope + ownership + explicit boundaries |
| 11 | 技术规范 | Inference default | Email + IM (tech roles only) | Stack / style / naming / CR focus |
| 12 | 工作流程 | Inference default | Email + IM + transcript | Task intake / proposal / incident handling |
| 13 | 输出风格 | Inference default | Email primary | Doc format / detail density / tone |
| 14 | 经验知识库 | Fact (verbatim) | Email + transcript | Verbatim lessons / technical conclusions with source |
| 15 | 诚实边界 | Meta | N/A | Gap declarations, source coverage, cutoffs, supersede logs, per-dim N-overrides |

---

## Dimension Details

### 1. Profile meta (Fact only)

Structured fields at the top of output.

Fields:
- `name`: display name
- `slug`: filesystem-safe identifier
- `company`: current company
- `level`: internal level designation
- `role`: job title
- `gender`: when authoritatively known
- `MBTI`: must be marked inferred unless user confirmed
- `personality_tags`: array of inferred traits
- `culture_tags`: array of inferred company-culture identifiers
- `impression`: freeform, user-provided

### 2. 身份 (Mixed)

**Fact portion**: role, level, department from org directory.
**Inference portion**: MBTI prediction, cultural-background effects on communication, user's freeform impression.

### 3. 核心人格规则 (Inference)

Concrete observable behaviors in IF-THEN form. Not traits ("thoughtful") but rules ("when questioned, counter-asks rather than explains"). Derived from consistent behavioral observations across email / IM / transcript.

Target: 3-7 rules per person. Each must pass staging threshold (N=3).

### 4. 决策 (Inference)

Two sub-clusters unified:
- Situational priorities (e.g., "customer experience > process compliance")
- Abstract decision maxims (e.g., "fund people not ideas"-style)

Both are if-then decision rules at different abstraction levels.

### 5. 表达 DNA (Fact + Inference)

Hybrid. Requires ≥5 verbatim samples from email (fact) plus style characterization (inference):
- Sentence patterns (length, structure)
- High-frequency words / catchphrases
- Rhythm and confidence language (e.g., "I suspect" vs "definitely")
- Emoji habits
- Formality shifts by context
- Opening / closing patterns

Email-only for verbatim because email is higher-stakes communication. Teams and transcript samples only when email data is insufficient; note fallback explicitly in #15.

### 6. 人际 (Inference)

Patterns by relationship class:
- With superiors (upward)
- With subordinates (downward)
- With peers (lateral)
- Under pressure (crisis / tight deadline / conflict)

NOT about interactions with specific named individuals.

### 7. 主体边界 (Inference)

What the subject refuses or avoids:
- Request types they decline
- Topics they don't engage with
- Communication channels they avoid
- Meetings / interactions they systematically skip

Distinct from #15 (which concerns dossier's own limitations).

### 8. 心智模型 (Inference)

3-7 theoretical frameworks the person uses to reason about the world. Each includes:
- Framework name
- Brief description
- Evidence (citations from source materials)
- Application scenario
- Limits (where it fails)

Triple validation gate:
- Cross-domain reproducibility: appears in ≥2 fields of discussion
- Generative power: predicts stance on novel questions
- Exclusivity: not universal / generic

### 9. 时间线与价值观 (Mixed)

Two sub-parts:
- Key events shaping cognition (dated, fact-layer)
- Values / pursuits / rejections (inference-layer)

Absorbs "origin story" content. Events listed chronologically. Values articulated as pursuit-vs-rejection contrasts.

### 10. 职责范围 (Fact only)

From org directory plus email signatures:
- Systems / modules / business lines owned
- Documentation maintained
- Explicit boundaries (what they don't own)

### 11. 技术规范 (Inference, tech roles only)

For subjects with technical responsibilities. Derived from code review comments, technical discussions, decision records:
- Tech stack preferences
- Code style conventions
- Naming conventions
- Code review focus areas

Omitted for non-tech roles.

### 12. 工作流程 (Inference)

Inferred patterns for:
- How they take on new tasks
- How they write proposals
- How they handle production incidents
- Their CR or approval process

### 13. 输出风格 (Inference)

Inferred from email and document drafts:
- Document format preferences (memo / bullets / prose)
- Information progression (conclusion-first vs buildup)
- Detail density
- Communication tone (formal / casual / direct / diplomatic)

### 14. 经验知识库 (Fact verbatim)

Verbatim lessons learned and technical conclusions. Each with source attribution.

Format: `- "quoted text"` with source sub-bullet.

### 15. 诚实边界 (Meta)

About the dossier itself, not the subject:
- Public source coverage (which web sources informed this)
- Private source coverage (email / IM / transcript windows used)
- Information cutoff date
- Primary-source ratio (target ≥50% of inferences backed by verbatim source)
- Knowledge gaps (dimensions without sufficient evidence)
- Per-dim N-overrides (e.g., "#11 relaxed to N=2 due to sparse data")
- Supersede logs (when facts overturned prior inferences)