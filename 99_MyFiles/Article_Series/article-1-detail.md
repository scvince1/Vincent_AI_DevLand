---
title: "Article 1 Detail — Building an LLM-Native Knowledge System"
parent: 82_Projects/article-series.md
last_modified: 2026-04-17
---

# LLM-Native Knowledge System — Article 1 Detail

Two-part article series. Article 1 outline locked and ready to write.

## Key Parameters

| Decision | Value |
|---|---|
| Language | English |
| Audience | Technically-minded general readers (understand LLMs, not necessarily engineers) |
| System names in article | Horsys / NovelOS / LifeOS (never MeowOS) |
| Author framing | History of Technology, MA, University of Chicago |
| POV | First-person; personal but not confessional |
| Tone | Technical practitioner; clear but not simplified |
| Tacit knowledge anchor | Polanyi's Paradox — "We know more than we can tell" |
| Cost numbers | Include actual figures |
| Intel white paper | Cite as contrast: same problem, different mechanism |
| Karpathy reference | https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f |

## Article 1 — Locked Outline

**Working title:** "Building an LLM-Native Knowledge System: A Practical Deployment"
**Target:** ~3,000–3,500 words

| Section | Key Content |
|---------|------------|
| 1. Introduction | RAG limitations (velocity, accuracy, maintenance); Polanyi's Paradox frame; author background; Karpathy as starting point |
| 2. Sparse Indexing | index.md as navigation; why it works at ~100 sources; where it breaks at scale |
| 3. The Dump | Zero-friction ingestion philosophy; Orchestrator → specialist agents → Archive Agent → KB pipeline; raw files preserved in Done/ |
| 4. Folder Structure | First retrieval decision layer; encodes domain ontology; shared mental model for human + AI |
| 5. FrontMatter + Tags | Schema design: human vs AI proposals (delta = tacit knowledge); Tag List discipline (compare before creating); bloat pruning |
| 6. QueryAgent | 4-level read strategy (folder → index → FrontMatter → body); tag-based expansion; human checkpoint; LLM prior violation edge case |
| 7. Manifest Alternative | Sparse index = navigation (where to look); Manifest = compression (pre-digested summary); comparison table by use case |
| 8. Three Live Systems | Horsys (high accuracy, financial consequences); NovelOS (highest accuracy, creative contradictions, Pending Terms folder); LifeOS (approximate awareness, supervisor layer) |
| 9. Practical Notes | Token savings ~10%; random-walk discovery benefit; failure modes (deprecated contamination, FrontMatter bloat, tag chaos); R&D cost ~$100 cold start, hundreds total, stabilized at tens/month; 1,000x per-query cost reduction |
| 10. Closing | Polanyi partially resolved via schema comparison process; human as schema designer not data clerk; brief enterprise closing |

## Article 2 — Scope Only

**Working title:** "Scaling LLM Knowledge Systems: From Personal to Enterprise"
Three-tier model: Personal KB → Initiative KB (file-system during active work, embedded to company RAG at close) → Company RAG (updated at initiative start/close only)
Key contrast: Intel Context Atlas (scale problem) vs personal system (relationship problem)
References: Intel white paper (Pulsipher 2025), Polanyi The Tacit Dimension (1966)

## Writing Session Handoff

- Start fresh context; load this file + full article outline at session open
- Anonymization pass required before publish: remove entity names, registration numbers, financial figures (keep approved cost figures)
- FrontMatter example: horse entity from Horsys — remove id, registration_number, purchase_price_usd, primary_trainer_id values; keep structural fields
- Do not use "revolutionary" or any equivalent
- Diagrams: suggest placement in prose; writer produces or commissions
