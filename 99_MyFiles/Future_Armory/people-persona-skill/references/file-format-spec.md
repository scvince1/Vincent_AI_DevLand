# File Format Specification

## Location

Caller writes output to:
```
people/{slug}/{slug}.md
```

Single file per person. `slug` is filesystem-safe identifier derived from name or email. For Chinese names use pypinyin to generate. Examples:
- `Mark Chen` → `mark.chen`
- `Sarah Kim` → `sarah.kim`
- `李青云` → `li-qingyun`

## Top-Level Structure

```md
# {Display Name} ({email})

**Last updated**: YYYY-MM-DD

---

## PART 1: FACTS
_外部可验证 + 用户确认。下游默认读这里。对外输出用这里。_

### 1. Profile meta
...

### (only dimensions with content appear)

---

## PART 2: INFERENCE
_模型推测。不供对外输出。需用户确认后移到 PART 1。_

### 2. 身份
...

### (only dimensions with content appear)
```

## Conventions

### Section Headings

Dimension numbers are preserved across both PARTs for alignment:
- `### 1. Profile meta` — Only in PART 1 (fact-only dimension)
- `### 3. 核心人格规则` — Can appear in PART 1 (confirmed) and PART 2 (inferred) simultaneously, same number in both

Empty dimensions are OMITTED. Do not list a dimension heading with "暂无" placeholder.

### Source Attribution

Every item has a `- Source: ...` sub-bullet (indented 2 spaces):

```md
### 3. 核心人格规则
- 答复邮件始终附 ISO 时间戳
  - Source: 观察自 2026-03-12 起 14 封邮件
- 决策前先问时间窗口
  - Source: confirmed 2026-04-10 by user
```

### Source Types

- `Org directory (YYYY-MM-DD)`
- `Email (YYYY-MM-DD to YYYY-MM-DD)` or `Email YYYY-MM-DD`
- `Teams (YYYY-MM-DD to YYYY-MM-DD)` or `Teams YYYY-MM-DD`
- `Transcript (meeting_id)`
- `Public source ({URL}, YYYY-MM-DD)`
- `confirmed YYYY-MM-DD by user` (for user-promoted inferences)
- `Observed N times across {channels}` (for staged-promoted inferences)

### Time-Series Ordering

Within a dimension, entries are newest-first. Old entries preserved, new ones appended on top:

```md
### 10. 职责范围
- Owns: AI strategy + M&A pipeline
  - Source: Org directory (2026-04-16)
- Owns: Office of CEO operations + executive calendar
  - Source: Org directory (2025-10-01)
```

Reader sees the latest-dated entry at top = current state.

### Confirmed vs Fact Within PART 1

Both treated as authoritative. Differentiation is at the source line:
- `- Source: Org directory (YYYY-MM-DD)` — external fact
- `- Source: confirmed YYYY-MM-DD by user` — user-promoted inference

No separate subsections in PART 1. Mix is fine in same dimension.

## Templates

### Full Dossier Template

```md
# {Display Name} ({email})

**Last updated**: {YYYY-MM-DD}

---

## PART 1: FACTS
_外部可验证 + 用户确认。下游默认读这里。对外输出用这里。_

### 1. Profile meta
- Name: {name}
- Company: {company}
- Role: {role}
- Level: {level}
- Source: Org directory ({date})

### 5. 表达 DNA
- "{verbatim quote 1}"
  - Source: Email {date}
- "{verbatim quote 2}"
  - Source: Email {date}

### 10. 职责范围
- Owns: {scope description}
  - Source: Org directory ({date})

### 14. 经验知识库
- "{lesson quoted verbatim}"
  - Source: Transcript ({meeting_id}, {date})

### 15. 诚实边界
- Public source coverage: {list or "none"}
- Private source coverage: email {days} days, IM {scope}, transcripts {count}
- Information cutoff: {date}
- Primary-source ratio: {percent}
- Knowledge gaps: {list of dimensions with insufficient evidence}
- Supersede log: {list of "previous inference X disconfirmed by fact Y on DATE" entries, if any}

---

## PART 2: INFERENCE
_模型推测。不供对外输出。需用户确认后移到 PART 1。_

### 3. 核心人格规则
- {rule 1}
  - Source: Observed N times across {channels}
- {rule 2}
  - Source: Observed N times across {channels}

### 4. 决策
- {heuristic 1}
  - Source: Observed N times across {channels}

### 5. 表达 DNA
- Style: {description of sentence patterns / rhythm / confidence language}
  - Source: Derived from {N} email samples over {period}

### 8. 心智模型
- **{framework name}**: {description}
  - Evidence: {citations}
  - Application: {when}
  - Limits: {where it fails}
```

## Reader's Mental Model

- Top of PART 1 / any dimension = current authoritative state
- Scroll through PART 1 for what's trusted
- Scroll through PART 2 for speculation (flagged, use with caution)
- #15 tells you what's missing and what's been overturned