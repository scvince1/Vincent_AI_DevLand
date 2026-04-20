# Article Outline: LLM-Native Knowledge System (Two-Part Series)

Generated: 2026-04-07
Status: Locked outline — ready for writing session

---

## Locked Decisions

| Decision | Value |
|---|---|
| Language | English |
| Target audience | Technically-minded general readers (understand LLMs, not necessarily engineers) |
| System names | Horsys / NovelOS / LifeOS (never MeowOS) |
| Author framing | History of Technology, MA, University of Chicago |
| Personal info OK | UChicago background, MA program, role as operator/architect of systems |
| Personal info NOT OK | Business entity names, employer/partner names, unpublished novel content/concepts, specific ongoing personal events |
| Cost numbers | Include actual figures |
| Tacit Knowledge framing | Polanyi's Paradox as anchor — "We know more than we can tell" |
| Enterprise section | Brief closing thought in Article 1, full treatment in Article 2 |
| Intel white paper | Cite as contrast: same problem named, different mechanism |
| Karpathy reference | Cite directly: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f |
| Diagrams | Suggest placement per section (writer to produce or commission) |
| Writing POV | First-person; personal but not confessional |

---

## Article 1

**Working title:** "Building an LLM-Native Knowledge System: A Practical Deployment"
**Target length:** ~3,000–3,500 words
**Tone:** Technical practitioner; first-person; clear but not simplified

### Section 1 — Introduction

- The problem: knowledge management at personal scale, across multiple heterogeneous domains
- Why RAG doesn't work here:
  - High-velocity content: re-embedding every new draft is untenable
  - High-accuracy requirement: approximate vector similarity is not enough for exact creative/legal/financial retrieval
  - Maintenance burden: vector databases require continuous upkeep
- Introduce Polanyi's Paradox as the conceptual frame: the hardest part of building these systems is articulating what you actually need — and you often can't until you've tried
- Brief author framing: came to this from History of Technology, not engineering; humanists have something to say about how knowledge systems are designed
- Reference Karpathy's LLM Wiki as the starting point this work builds on

**Diagram suggestion:** None needed here — let the problem statement breathe.

---

### Section 2 — The Foundation: Sparse Indexing

- What Karpathy proposes: a persistent, compounding wiki maintained by the LLM
- Core mechanism: `index.md` as central navigation file — LLM reads it first on every query, then decides which documents to read
- Why this works at moderate scale (~100 sources, hundreds of pages)
- Where it breaks: index becomes too long; field proliferation makes it unreadable by humans; maintenance becomes impossible at scale

**Diagram suggestion:** Simple flow — Query → Read index.md → Identify target files → Read files → Answer

---

### Section 3 — The Dump: Drop-Everything Ingestion

- Design philosophy: zero pre-sorting friction; anything goes in
- Psychological effect: removes cognitive switching cost; single interface (Obsidian or VS Code — no tab switching)
- Pipeline: file dropped into Dump → Orchestrator reads and classifies → routes to specialist agents → Archive Agent writes structured knowledge to KB
- Raw files preserved in `Done/` subfolder after processing; original drafts are treated as irreplaceable
- Personal note: as someone who spends a significant portion of every day on text work, preserving original drafts is a non-negotiable habit

**Diagram suggestion:** Flowchart — Dump folder → Orchestrator → [Finance Agent / Marketing Agent / Knowledge Agent / etc.] → Archive Agent → KB

---

### Section 4 — Folder Structure as Navigation Layer

- The folder tree is not just organization — it is the first retrieval decision layer
- Designed by human up front; Archive Agent can extend it (new subfolders) based on emerging content needs
- The structure encodes domain ontology — e.g., `02_Knowledge/01_World/01_Natural/` communicates both location and category simultaneously
- Acts as a shared mental model: when the folder structure is well-designed, both human and AI can navigate without a map
- Example: show simplified tree from one of the live systems (anonymized as needed)

**Diagram suggestion:** Annotated folder tree for one system — highlight the semantic layering

---

### Section 5 — FrontMatter + Tag System

- Archive Agent generates FrontMatter on ingestion; can add new fields dynamically
- Field discipline: only include fields that correspond to actual query use cases — fields the QueryAgent will actually filter on
- The setup process:
  1. Whiteboard or paper-sketch the domain knowledge first
  2. Take a small sample of representative documents
  3. Human proposes a schema; AI proposes a schema independently
  4. Compare, discuss, merge — the delta between the two proposals is where tacit knowledge lives
- Polanyi moment: AI-suggested FrontMatter fails in two directions simultaneously — adds fields no one will ever query, misses fields the human knows matter but can't articulate why until they're absent
- Tag List: controlled vocabulary file maintained alongside the KB
  - Before adding a new tag, Archive Agent must compare against existing Tag List
  - If an existing tag is close enough, reuse it; only create new tags for genuinely novel content
  - Tags with high query reuse rate have their descriptions auto-pruned (signals stability)
  - Dual function: Obsidian knowledge graph browsing + concept-level search outside Obsidian
- FrontMatter bloat is real: ongoing pruning is part of the workflow; random-walk review sessions catch useless fields

**Diagram suggestion:** Annotated FrontMatter block (use horse entity structure, anonymized — remove registration numbers, financial figures; keep structural fields like entity_type, discipline, relationships, workbook_path)

---

### Section 6 — The QueryAgent: Hierarchical Retrieval

Four-level read strategy:

1. **Folder structure** — determine which branch of the KB is relevant
2. **Index file(s)** — read `index.md` in the identified branch(es); narrow to candidate documents
3. **FrontMatter** — read FrontMatter of candidates; if fields don't match query, do not read body — return title, location, and FrontMatter summary to user for manual judgment
4. **Body** — read full document only for confirmed matches

Additional mechanism: **Tag-based scope expansion**
- After reading FrontMatter of primary matches, check tag overlap across candidates
- If multiple candidates share a tag cluster, broaden search to include other documents with those tags
- Prevents over-precision: sparse indexing optimizes for accuracy; tags provide a controlled way to expand scope when needed

Human checkpoint:
- In months of use, manual judgment required approximately twice
- Trigger: FrontMatter fields ambiguous relative to query; AI cannot determine relevance above threshold
- Resolution: AI returns the ambiguous document's metadata; user decides in seconds whether to retrieve body

Edge case — concepts that violate LLM priors:
- Some domain-specific terminology (particularly in a creative project with invented concepts) uses vocabulary that contradicts LLM training data
- Index summaries generated for these concepts are lower quality
- Fix: manual annotation of the index entry for those specific terms
- This is the one maintenance task that cannot be fully automated

**Diagram suggestion:** Decision tree — query in → folder selection → index read → FrontMatter filter (branch: match → read body; branch: ambiguous → return to human; branch: no match → skip)

---

### Section 7 — The Manifest Alternative

Key distinction:
- **Sparse indexing** = navigation mechanism — tells the LLM *where to look*, not *what is there*; always requires a second read of the underlying document
- **Manifest** = compression mechanism — pre-digested summary of a cluster; can directly answer queries without reading underlying files

These are not competing approaches — they serve different retrieval patterns:
- Sparse index + QueryAgent: for high-accuracy domains where the answer must come from the exact document (NovelOS, Horsys)
- Manifest: for approximate-awareness domains where project management context is sufficient (LifeOS)

How Manifests work in LifeOS:
- Active initiatives are broken into clusters (logical groupings of related tasks/projects)
- Each cluster has an AI-generated and AI-maintained Manifest: a compressed summary of current state
- QueryAgent reads Manifest first; if sufficient, no further retrieval needed
- If insufficient, falls back to folder structure + FrontMatter approach for that cluster

When to use which:
| Criterion | Sparse Index | Manifest |
|---|---|---|
| Accuracy requirement | High | Moderate |
| Content velocity | High | Moderate |
| Query type | Exact retrieval | Status/awareness |
| KB size | Hundreds of files | Dozens of clusters |
| Maintenance cost | Lower (structure) | Higher (summaries need updating) |

**Diagram suggestion:** Side-by-side comparison — Query path through sparse index vs. query path through Manifest

---

### Section 8 — Three Live Systems

Brief domain sketches showing how retrieval requirements shape architecture:

**Horsys** (equine import business operations)
- Knowledge types: contacts/relationships, horse profiles, financial records, competition history, legal/regulatory
- Retrieval requirement: high accuracy — a wrong financial figure or wrong contact detail has real consequences
- Architecture choice: sparse index + full QueryAgent pipeline
- Notable: finance workflow fully automated; no manual Excel interaction required; the system pulls data from the workbook, processes transactions, generates reports

**NovelOS** (long-running sci-fi novel and game project)
- Knowledge types: world-building, character profiles, plot structure, design decisions, deprecated concepts, pending/unresolved contradictions
- Retrieval requirement: highest accuracy — creative contradictions are costly; collaborators also query the system
- Architecture choice: sparse index + full QueryAgent pipeline + Tag System
- Notable: Pending Terms folder as deliberate contradiction-parking mechanism; semantic search advantage over RAG for identifying deprecated content contamination

**LifeOS** (personal life operating system)
- Knowledge types: schedule, initiatives, cross-system coordination, learning notes
- Retrieval requirement: low-to-moderate — approximate awareness is sufficient
- Architecture choice: Manifest-first; sparse index as fallback
- Notable: supervisor layer — has read access to Horsys and NovelOS KBs; those systems have no awareness of LifeOS

---

### Section 9 — Practical Notes

**Trade-offs**

Token savings: approximately 10% reduction in search token usage, based on observation rather than precise measurement. The saving is not dramatic — reading the final documents still costs the same. The real saving is maintenance cost: this system does not require re-embedding on every new document. The marginal ingestion cost is low.

Unexpected benefit — random walking: because the KB is organized as readable Markdown, the human operator can browse it without AI assistance. Reviewing archived knowledge without a specific query in mind consistently produces new connections and revisions. The KB develops a recognizable authorial quality — not identical to the author's voice, but close enough that reading it is comfortable rather than alienating.

Edge failure — LLM prior violations: certain domain-specific concepts (particularly invented terminology in a creative project) use vocabulary that contradicts LLM training distributions. Index summaries for these entries are lower quality. Resolution: manual annotation. This is the one category of maintenance that resists automation.

**Failure Modes**

Deprecated content contamination: when earlier versions of a concept are not moved to the `90_Deprecated/` folder, they pollute later KB entries. In a creative project with multiple revision cycles (e.g., a religious system overhauled several times), old descriptions persist across many files. Cleanup is difficult.

Advantage of semantic search over RAG in cleanup: because this system uses LLM semantic understanding rather than vector similarity, it can locate contamination by concept — including terminology that has been deliberately removed from the active vocabulary. RAG would not find what is no longer in the embedding space.

Pending Terms as contradiction infrastructure: the `90_Pending_Terms/` folder began as a naming question ("Spirit or Soul?") and evolved into a deliberate mechanism for parking genuine design contradictions. Contradictions are not resolved immediately; they are labeled, stored, and often resolve themselves as adjacent design work produces new context. Occasionally a single contradiction forks into two independent design directions that coexist productively.

Early Tag chaos: without a Tag List, the Archive Agent generates a new tag for every document, producing a meaningless cloud within weeks. The Tag List constraint — compare before creating, reuse aggressively — is not optional; it is the mechanism that makes the Tag System functional.

FrontMatter bloat: Archive Agents, left unconstrained, generate impressive-looking FrontMatter with fields that correspond to no real query use case. Ongoing pruning during random-walk review sessions is the only reliable fix. Schema discipline must be actively maintained.

**What Surprised Me**

Build speed: the first system took several hours to understand and configure. By the third and fourth system, a new deployment from scratch took under ten minutes and was functional immediately. The key enabler: a standardized System Spec document format, iterated across deployments. When starting a new system, the Spec is handed to the AI, differences are negotiated, and the agent generates all configuration.

Maintenance cost: surprisingly low. The system mostly runs.

Upgrade and debug cost: surprisingly high. Optimizing context management and token usage requires significant trial and error. The architecture is legible, but its failure modes are not always obvious.

R&D cost: the cold start of the first full system cost approximately $100 in a single evening — archiving roughly twenty documents (a few hundred words to a few thousand words each) into a new KB. Total R&D spend to reach a stable, optimized state: several hundred dollars over several months.

Current state: stabilized at tens of dollars per month. For Horsys and NovelOS specifically, per-query cost has dropped by approximately 1,000x compared to the initial architecture. The cost reduction did not reduce usage — it enabled much higher intensity use than would have been feasible otherwise.

---

### Section 10 — Closing

- This is not reinventing the wheel: mature tools, workflows, and skills exist that produce similar outputs. The difference is not in tooling — it is in the 1% of architectural and design philosophy decisions that determine whether the system actually fits the operator's cognitive model. A mismatch at that level is extremely difficult to detect and extremely difficult to correct after deployment.

- Polanyi resolved, partially: the design process — whiteboarding the schema, comparing human and AI proposals, pruning fields through use — is a structured method for externalizing tacit knowledge. It does not fully solve Polanyi's Paradox (some knowledge remains inarticulate), but it surfaces more of it than any other method the author has used.

- Capital H Human: the role is schema designer, not data entry clerk. The AI handles bookkeeping — Karpathy's framing is exactly right. The human handles judgment: which contradictions to park, which fields matter, which index entries need manual correction. These are genuinely human moments, and the system is designed to protect them rather than automate them away.

- Enterprise closing thought: this architecture has a clear scale limit — it is designed for individual or small-team use. At organizational scale, a different approach is needed. A three-tier model — personal KB, initiative KB, and company-wide RAG — preserves the principles while accommodating the constraints. That is the subject of a separate piece.

---

## Article 2 (Scope Only)

**Working title:** "Scaling LLM Knowledge Systems: From Personal to Enterprise"
**Status:** Scoped, not outlined — write outline in separate session

### Core argument
The file-system approach described in Article 1 has a defined scale boundary. The principles are portable; the implementation is not. A hybrid architecture combining personal-scale file systems with initiative-level light indexing and company-wide RAG can preserve the benefits (low maintenance, human legibility, tacit knowledge capture) while accommodating organizational constraints.

### Key content blocks
1. Where the personal approach breaks: context window limits, file count at scale, multi-user write conflicts, compliance constraints
2. Three-tier model:
   - Personal KB: habits, relationships, judgment, tacit knowledge of the individual
   - Initiative KB: lightweight during active work (file-system approach); embedded into company RAG at project close
   - Company RAG: traditional vector database; updated at initiative start and close, not continuously
3. Initiative lifecycle: start → active use → close + embed → archived
4. Information alignment as enterprise value: aligning "what each person knows" vs. "what the organization knows" — and managing the gap
5. Individual KB as tacit knowledge capture: not replacement of the employee, but externalization of judgment over time
6. Contrast with Intel "Capturing Tacit Knowledge through Generative AI" (Context Atlas approach): same problem framed differently; different mechanism; trade-offs

### References for Article 2
- Intel white paper: *Capturing Tacit Knowledge through Generative AI* (Dr. Darren W. Pulsipher)
- Polanyi, Michael. *The Tacit Dimension.* (1966)
- Additional enterprise knowledge management literature: TBD in writing session

---

## Session Handoff Notes

For the writing session:
- Start fresh context; load this document at session open
- Article 1 diagrams: writer should either commission or describe in prose — do not attempt ASCII art
- Anonymization pass required before publish: remove any remaining specific entity names, registration numbers, financial figures (other than the explicitly approved cost figures)
- FrontMatter example to use: horse entity structure from Horsys — remove id value, registration_number value, purchase_price_usd value, primary_trainer_id value; keep structural fields
- Tone check: article should read like a thoughtful practitioner piece, not a product demo
- Do not use the word "revolutionary" or any equivalent
