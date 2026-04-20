# Sample Dossier (Fictional)

This is a reference output showing the PART 1 / PART 2 structure, source attribution conventions, and dimension usage. Subject is fictional.

File path: `people/mark.chen/mark.chen.md`

---

```md
# Mark Chen (mark.chen@acme-corp.com)

**Last updated**: 2026-04-16

---

## PART 1: FACTS
_外部可验证 + 用户确认。下游默认读这里。对外输出用这里。_

### 1. Profile meta
- Name: Mark Chen
- Slug: mark.chen
- Company: Acme Corp
- Role: Chief of Staff to CEO
- Level: VP
- Department: Office of CEO
- Source: Org directory (2026-04-16)

### 2. 身份
- Role: Chief of Staff to CEO
  - Source: Org directory (2026-04-16)
- Start date in current role: 2025-09-05
  - Source: Org directory (2026-04-16)
- Manager chain: CEO (direct) → Board
  - Source: Org directory (2026-04-16)

### 5. 表达 DNA
- "Let's regroup Monday, no decisions before we have numbers in hand."
  - Source: Email 2026-04-08 to leadership-team
- "Pre-reads under 5 pages, otherwise nobody reads."
  - Source: Email 2026-01-22 to executive-assistants
- "Push that one to next sprint, current sprint is overloaded."
  - Source: Email 2026-03-14 to eng-leads
- "When in doubt, ask for the 3-scenario analysis first."
  - Source: Email 2025-12-03 to strategy-team
- "This is not the priority this quarter, please defer."
  - Source: Email 2026-02-11 to product-leads

### 10. 职责范围
- Owns: Office of CEO operations, executive calendar, strategic initiatives pipeline
  - Source: Org directory (2026-04-16)
- Co-owns: M&A evaluation pipeline (with CFO)
  - Source: Email 2026-03-28 internal memo
- Not responsible for: salary design, performance review calibration
  - Source: Email 2026-03-22 (target explicitly scoped out)

### 14. 经验知识库
- "When budget is uncertain, I always require 3-scenario analysis before greenlight."
  - Source: Transcript (q4-all-hands-2025-10-08)
- "Pre-reads under 5 pages, otherwise nobody reads them fully before meetings."
  - Source: Email 2026-01-22

### 15. 诚实边界
- Public source coverage: LinkedIn profile, 2 industry interviews (Podcast X 2025-Q3, Podcast Y 2025-Q4)
- Private source coverage: email 60 days, Teams 90 days (DM + 3 relevant channels), 4 meeting transcripts
- Information cutoff: 2026-04-16
- Primary-source ratio: 72% of inferences in PART 2 backed by verbatim source
- Knowledge gaps:
  - #11 技术规范: N/A (non-technical role)
  - #8 心智模型: only 2 frameworks reached threshold; 3 more in staging
  - #12 工作流程 for incident handling: insufficient observations (fewer than N=3)
- Per-dim override: none active
- Supersede log: none this cycle

---

## PART 2: INFERENCE
_模型推测。不供对外输出。需用户确认后移到 PART 1。_

### 2. 身份
- MBTI 推测: ISTJ
  - Source: Derived from email decision rhythm + data-first preferences
- 文化影响推测: west-coast startup culture blended with east-coast corporate
  - Source: Based on prior company history (Acme Corp trajectory) + communication style

### 3. 核心人格规则
- 决策前先问时间窗口
  - Source: Observed 4 times across Email (2026-02-28, 2026-03-15, 2026-04-06, 2026-04-11)
- 答复关键邮件附 ISO 时间戳，暗示时间管理纪律
  - Source: Observed 6 times across Email (2026-02-10 onward)
- 被质疑时先沉默 10 秒再答（transcript 中停顿明显）
  - Source: Observed 3 times across Transcript (q4-allhands, q1-review, product-strategy)

### 4. 决策
- 优先级排序: customer experience > process compliance > 内部协调
  - Source: Observed 5 times across Email + Transcript (Q1 2026)
- Push 时倾向反问 "你有多少时间" 而非直接答应或拒绝
  - Source: Observed 3 times across Teams
- 跨团队冲突时偏向推进小范围试点而非大规模改动
  - Source: Observed 4 times across Email + Transcript

### 5. 表达 DNA
- Style: Short sentences, direct openings, minimal preamble. Frequent use of time-bounded commitments ("by Monday" / "end of week"). Low confidence-language usage (prefers "I think" over "I believe" or "definitely"). No emoji in work email; occasional emoji in Teams DMs.
  - Source: Derived from 38 email samples + 42 Teams messages over 60 days

### 6. 人际
- 对上级（CEO）: frames updates as options with recommendations rather than requests for direction
  - Source: Observed 5 times across Email + Transcript
- 对下级: delegates with clear success criteria; checks in weekly; avoids micromanaging
  - Source: Observed 4 times across Email
- 对平级（other VPs）: prefers 1-on-1 alignment over group meetings
  - Source: Observed 3 times across Email (all scheduling 1-on-1s before group meetings)
- 压力下: turnaround time stays consistent, but replies become shorter and more decision-oriented
  - Source: Observed during Q1 release crunch across Email

### 8. 心智模型
- **3-Scenario Analysis**: requires worst / base / best case for any significant commitment
  - Description: Not proceed with commitment until three scenarios mapped
  - Evidence: transcript (q4-all-hands), Email (2026-01-22, 2025-12-03)
  - Application: resource allocation, M&A decisions, quarterly planning
  - Limits: over-engineers fast-moving operational decisions
- **Time-Boxed Decisions**: frames every decision with a time window before discussion starts
  - Description: First question on any topic is "how long do we have?"
  - Evidence: Email (2026-02-28, 2026-03-15, 2026-04-06, 2026-04-11), Teams 2026-04-02
  - Application: meeting kick-offs, email triage, escalation response
  - Limits: may prematurely scope ambiguous problems that need exploration

### 13. 输出风格
- Format preference: Pre-reads under 5 pages. Bulleted structure when >2 decisions involved. Prose paragraphs for rationale, bullets for options.
  - Source: Observed 7 times across Email (explicit preference stated), 4 times across Transcript (references existing pre-read style)
- Information progression: Conclusion-first, evidence following. Rarely buries the ask.
  - Source: Observed 12 times across Email
- Detail density: medium. Rarely cites specific numbers unless decision-critical.
  - Source: Observed consistently across Email samples
```

---

## Notes on This Sample

### Why this structure

- PART 1 contains only externally-verifiable or user-confirmed content. Every item has a `- Source:` sub-bullet.
- PART 2 contains derived characterizations. Every inference has `Source: Observed N times across {channels}` showing staging was met.
- #15 诚实边界 is present and declares gaps (dim 11 N/A, dim 8 limited, dim 12 insufficient).
- Several dimensions are omitted (e.g., #7, #9, #12) because they had no content passing staging threshold. No empty placeholders.

### Key conventions demonstrated

- Fact source attributions specify channel + date (or date range)
- Verbatim quotes are exact strings in PART 1 #5
- Inferences in PART 2 always show observation count and channels
- No mixing of fact and inference in same section
- No emoji-laden language; neutral-analytical register throughout
- Time-series implicitly preserves chain (if old Level: VP later appears, new Level: SVP would append on top)

### What this sample does not show

- A user-confirmed entry (would appear in PART 1 with `Source: confirmed YYYY-MM-DD by user`)
- A supersede log entry in #15 (would appear as `previous inference "X" disconfirmed by fact "Y" on DATE`)
- A public-vs-private conflict flag in PART 2
- A per-dim N=2 override declaration in #15

Those variants demonstrated individually in `prompts/conflict-resolver.md`.
