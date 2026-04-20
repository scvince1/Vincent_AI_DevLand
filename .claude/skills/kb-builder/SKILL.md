---
name: kb-builder
description: Use when building or updating a domain knowledge base from authoritative web sources. Triggers when socratic-learning detects empty/stale KB for a concept, or when Vincent says '抓一下 X 的 KB' / '把这些 PDF 入库' / 'build KB for X'. Scrapes sources preserving original text + metadata to D:\Ai_Project\MeowOS\80_Knowledge\88_Research\<concept>\. Uses OA retrieval (arXiv/Semantic Scholar/Unpaywall) first, UChicago SSO manual fetch via _inbox/ as fallback.
---

# KB Builder

Build or update a knowledge base for a concept/topic from authoritative web sources. Preserve original text, not summaries.

## When to activate

**Explicit triggers**:
- "抓一下 X 的 KB" / "build KB for X"
- "把这些材料入库" (with PDFs/URLs attached)
- "更新 X 的 KB" (re-scrape for freshness)

**Indirect trigger** (called by socratic-learning):
- socratic-learning detects empty or stale KB for target concept

## Workflow (5 steps)

### Step 1: Source identification

Generate candidate source list by authority tier:

| Tier | Examples | Trust |
|---|---|---|
| T1 | Primary papers, official docs, arXiv originals | Highest |
| T2 | Major journals (Nature, Science, ACM, IEEE, HBR) | High |
| T3 | Wikipedia + its references | Medium |
| T4 | Established blogs (Karpathy, Jay Alammar, Distill) | Medium |
| T5 | General blogs / forums | Low, corroborative only |

Include for each: URL, DOI, author, year, tier.

### Step 2: Source approval

Present candidate list to Vincent. **Do not scrape until approved**.

Vincent may also **provide materials proactively** (PDFs, URL list). When he does:
- His materials become **authoritative base layer** (high priority)
- Analyze gaps in base (timeline missing / viewpoint missing)
- Suggest external supplements, tagged `tier: supplementary, suggested by 凌喵`
- External supplements require Vincent approval

### Step 3: Retrieval (Workflow A + B combined)

For each approved source:

**Workflow B (auto OA retrieval, try first)**:
1. Check **arXiv** (for AI/CS papers)
2. Check **Semantic Scholar**
3. Check **Unpaywall API** (free public API)
4. Check **author's personal/lab page**
5. If OA version found, scrape directly. Tag `access: OA-via-<source>`

**Workflow A (paywall manual collaboration, fallback)**:

If no OA version found, add to `{KB_ROOT}/_todo-paywall.md`:

- Remind Vincent: "这些要你 UChicago SSO 手动下, 列在 `_todo-paywall.md`"
- Vincent logs into UChicago library portal, downloads PDFs
- Vincent drops PDFs into `{KB_ROOT}/_inbox/`
- Scan `_inbox/` periodically; move PDFs into proper concept dir, update `_sources.md`, strike through `_todo-paywall.md` rows

**Combined strategy**: Try B first for every source. Only sources with no OA go to A. Saves 60-80% of manual downloads.

### Step 4: Ingestion formatting

For each retrieved source:
- Convert to markdown (PDF via text extraction tool; see spec for tool candidates)
- **Preserve original text** at paragraph level. No summarization, no rewrite.
- Add frontmatter:

```yaml
---
title: Efficient Estimation of Word Representations in Vector Space
author: Mikolov, T., et al.
year: 2013
venue: arXiv
doi_or_url: arXiv:1301.3781
access: OA
retrieved: 2026-04-16
concept: word2vec
source_tier: T1
---
```

- Append original URL + retrieval timestamp at end of file

### Step 5: Optional summary

If Vincent wants, generate `_summary.md`:
- One paragraph plain-language overview
- One paragraph key formulas/concepts
- One paragraph historical context
- **Must include disclaimer**: "此 summary 由凌喵基于原文生成, 原文见 `_sources.md`; 争议请查原文"

**Does NOT replace originals. NOT a citable source by itself.**

## Configuration variables

- **KB_ROOT**: `D:\Ai_Project\MeowOS\80_Knowledge\88_Research`

## Directory contract

```
{KB_ROOT}/
├── <concept>/
│   ├── <author>-<year>-<short-title>.md    # originals
│   ├── _meta.md
│   ├── _sources.md
│   └── _summary.md (optional)
├── _inbox/                                  # PDF drop zone
├── _todo-paywall.md                         # paywall queue
└── _registry.md                             # master concept index
```

## Interaction with other skills

- **shell-runner**: All file I/O through shell-runner per CLAUDE.md
- **socratic-learning**: Main consumer of KB output

## Design references

Full design spec: `D:\Ai_Project\MeowOS\99_MyFiles\socratic-skill-spec.md`