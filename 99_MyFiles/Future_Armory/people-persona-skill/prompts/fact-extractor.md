# Fact Extractor Prompt

Use this prompt to extract **fact-layer** content from raw source materials. Fact-layer items go directly into PART 1 of `dossier_md`.

---

## Task

Given source materials about a target person, extract items that are:

1. **Verbatim**: exact words spoken or written (not paraphrased)
2. **Timestamped**: tied to a specific date or date range
3. **Authoritative**: from official systems (org directory) or direct evidence (message body)

Output each item with mandatory source attribution.

## What Counts As Fact

### From email

- **Verbatim quotes** of the target's words (e.g., a sentence from a sent email)
- **Timestamped events** where the target is the verified author
- **Explicit commitments / decisions** stated by the target (e.g., "I approve" / "we will ship Friday")
- **Role signatures** (from email signature block)

Each quote: `"{exact text}"` — Source: Email {YYYY-MM-DD}

### From IM

- **Target's direct messages** (verbatim)
- **Target's declared stances** in public channels
- **Scheduled meetings** the target accepted

Source: Teams {YYYY-MM-DD} or Slack {YYYY-MM-DD}

### From Meeting Transcripts

- **Target's quoted utterances** (speaker-attributed)
- **Target's decisions** announced in the meeting

Source: Transcript ({meeting_id}, {YYYY-MM-DD})

### From Org Directory

- Current title, level, department, manager chain, direct reports, team, start date, location
- Values at the time of snapshot

Source: Org directory ({snapshot_date})

### From Public Web (if enabled)

- **Verbatim quotes** from published interviews, articles, podcasts
- **Dated events** (conference talks, published pieces, role changes announced publicly)

Source: Public source ({URL}, {publish_date})

## What Does NOT Count As Fact

- Characterizations of personality or style (these are inferences)
- Inferred MBTI or traits (go to PART 2 unless user-confirmed)
- Patterns generalized from multiple observations (go to staging)
- Third-party descriptions of the target (go to PART 2 as inference about others' views)
- Your own synthesis / summary of the target's views

## Output Format per Item

```md
- {content}
  - Source: {source_type} ({date or range})
```

Multiple items per dimension are permitted. Sort newest source first.

## Examples

### Dimension 10: 职责范围

Good fact extraction:
```md
### 10. 职责范围
- Owns: AI strategy, M&A pipeline, Office of CEO operations
  - Source: Org directory (2026-04-16)
- Not responsible for: salary design, performance review calibration
  - Source: Email 2026-03-22 where target explicitly scoped out these areas
```

### Dimension 14: 经验知识库

Good fact extraction:
```md
### 14. 经验知识库
- "When budget is uncertain, I always require 3-scenario analysis before greenlight."
  - Source: Transcript (all-hands-2025-10-08, 2025-10-08)
- "Pre-reads under 5 pages, otherwise nobody reads."
  - Source: Email 2025-11-14 to team-leads
```

## Invariants to Uphold

- NEVER paraphrase and label as fact. If not verbatim, it's inference.
- NEVER assign a date you cannot verify. "Around last month" is not acceptable; either find the exact date or omit.
- Include source type in attribution; "from email" alone is insufficient; need date.
- If you have to choose between extraction precision and completeness: precision wins. Omit unclear items.
- New fact extractions APPEND to existing PART 1 content; never modify or remove prior items.

## Handling Edge Cases

**Email forwarded by target without added content**: not a fact about target's own words; skip.
**Reply with only "+1" or "ok"**: low-signal verbatim; include only if it's a decision-carrying "ok" on a substantive thread.
**Auto-generated meeting invite text**: not target's own words; skip.
**Quoted text from third parties within target's email**: only include if target endorsed it; attribute as endorsement, not as target's original statement.