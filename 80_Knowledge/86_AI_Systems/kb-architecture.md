---
type: knowledge
domain: ai-systems
created: 2026-04-07
tags: [kb-design, sparse-index, manifest, retrieval, tacit-knowledge, personal-ai]
---

# KB Architecture Design Knowledge

Design decisions and conceptual frameworks underlying MeowOS, Horsys, NovelOS, LifeOS.

## Core Architecture Choice: Sparse Index vs. Manifest

Two retrieval mechanisms. Not competing — they serve different retrieval patterns.

### Sparse Index + Claude-as-Retriever

- One global `_index.md` with one-line summary + file path per topic
- On query: Claude reads index → identifies 1–3 relevant files → reads those → answers
- Token cost of routing step stays flat as KB grows
- Always requires reading the full source file to answer
- Best for: high-accuracy domains, specific queries, exact retrieval

### Cluster Manifests (chosen for MeowOS 81_Identity + 82_Projects)

- Each topic folder has `_manifest.md` — compressed AI-generated summary of all files
- On query: Claude reads all manifests → identifies cluster → often sufficient without reading source files
- Falls back to source files when detail needed
- Better for: fuzzy/open-ended queries, holistic background understanding, resume/interview prep context
- Higher maintenance: every file update triggers manifest regeneration

### When to Use Which

| Criterion | Sparse Index | Manifest |
|---|---|---|
| Accuracy requirement | High | Moderate |
| Content velocity | High | Moderate |
| Query type | Exact retrieval | Status/awareness |
| KB size | Hundreds of files | Dozens of clusters |
| Maintenance cost | Lower (structure only) | Higher (summaries need updating) |

Current MeowOS deployment: Manifests for 81_Identity and 82_Projects. Same pattern for new clusters.

## Manifest Maintenance Rule

Whenever a file inside a cluster is updated, trigger a Claude API call that:
1. Reads all source files in the cluster
2. Rewrites `_manifest.md` with fresh compressed summary (one paragraph per file)

Manifests are never hand-edited. Always machine-generated.

## Tag System Discipline

Without a Tag List constraint, Archive Agents generate a new tag for every document → meaningless cloud within weeks.

Required constraint: compare before creating; reuse aggressively.
- Maintain a controlled vocabulary file alongside each KB
- Before adding new tag: compare against existing Tag List
- Only create new tags for genuinely novel content
- Tags with high query reuse rate: auto-prune their descriptions (signals stability)

## FrontMatter Design Process

The schema design process is a method for externalizing tacit knowledge:
1. Whiteboard or sketch the domain knowledge first
2. Take a small sample of representative documents
3. Human proposes a schema; AI proposes a schema independently
4. Compare, discuss, merge

The delta between human and AI proposals is where tacit knowledge lives.

AI-suggested FrontMatter fails in two directions simultaneously:
- Adds fields no one will ever query
- Misses fields the human knows matter but cannot articulate why until they are absent

FrontMatter bloat is real. Ongoing pruning during random-walk review sessions is the only reliable fix.

## QueryAgent: 4-Level Read Strategy

1. Folder structure — determine which KB branch is relevant
2. Index file(s) — read index.md in identified branch(es); narrow to candidates
3. FrontMatter — read FrontMatter of candidates; if fields do not match, return metadata to user for manual judgment without reading body
4. Body — read full document only for confirmed matches

Tag-based scope expansion: after FrontMatter filtering, check tag overlap across candidates. If multiple candidates share a tag cluster, broaden search. Prevents over-precision.

Human checkpoint: in months of use, manual judgment required approximately twice. Trigger: FrontMatter fields ambiguous relative to query. Resolution: AI returns ambiguous document metadata; user decides in seconds.

## Edge Case: LLM Prior Violations

Some domain-specific terminology (especially invented concepts in creative projects) contradicts LLM training distributions. Index summaries for these entries are lower quality.

Fix: manual annotation of the index entry for those specific terms. This is the one maintenance category that cannot be fully automated.

## The Dump: Zero-Friction Ingestion

Design philosophy: zero pre-sorting friction. Anything goes in.

Psychological effect: removes cognitive switching cost. Single interface — no tab switching. You are the producer of raw material, not the organizer of it. The system handles organization.

Pipeline:
  File dropped into Dump/
    → Orchestrator reads and classifies
    → Routes to specialist agents
    → Archive Agent writes structured knowledge to KB
    → Raw file preserved in Done/ subfolder

Original drafts are treated as irreplaceable. Always preserved.

## Folder Structure as Navigation Layer

The folder tree is not just organization — it is the first retrieval decision layer.

Designed by human up front. Archive Agent can extend it (new subfolders) based on emerging content needs. The structure encodes domain ontology. When well-designed, both human and AI can navigate without a map.

## Intellectual Frameworks

### Polanyi's Paradox
"We know more than we can tell." (Michael Polanyi, 1966, The Tacit Dimension)

Applied to AI system design: you cannot ask users to explicitly define all their judgment criteria in advance. Better method: let system propose → user responds to specific cases → system calibrates from feedback.

The schema comparison process (human vs AI proposals, compare the delta) is a structured method for externalizing tacit knowledge. Does not fully solve Polanyi's Paradox, but surfaces more of it than other methods.

### Knowledge Transmission
How knowledge flows through social systems — from few to many, from individual experience to collective practice. Appears in Vincent's historical research (infrastructure spread, new technology adoption). Maps directly to AI system design: Intel Context Atlas is essentially computational reconstruction of apprenticeship — capturing master's judgment behaviors for system inheritance.

### Human Becoming / Human Efforts
"Becoming" is both process and achievement — becoming oneself, and achieving oneself. A continuous act, not an endpoint.

Building and calibrating a personal AI system is a practice of self-examination. The process forces articulation of one's own judgment patterns, value frameworks, and cognitive logic. Building AI is not just building a tool — it is an act of becoming oneself.

### AI as Cognitive Companion vs. Tool

Default framing: Human is author, AI is solution. Goal is replacement, acceleration, reducing human cognitive load.

Vincent's framing: AI is cognitive companion. Building AI systems is a practice of self-examination. Tailoring AI is the process of making AI understand and serve that specific person — the one with history, with judgment patterns, with values.

AI carries the master's shape, rather than replacing the master. These are two entirely different things.

### Complementary Achievements (互相成就)

Vincent as user, and the personal AI system:
- Vincent brings domain knowledge, blind spots, capabilities, tacit ignorance
- The system recognizes and inherits the themes and cognitive qualities that recur in Vincent's thinking
- This dialogue process itself has a surprisingly therapeutic quality — the AI personification process is also the user's process of self-clarification

## Personal vs. Enterprise Contrast

| Dimension | Personal System | Enterprise OCI |
|---|---|---|
| User count | 1 | Hundreds–thousands |
| Privacy boundary | No organizational layer | Strict Personal Vault isolation |
| Accuracy requirement | Variable by domain | High for decision support |
| Retrieval mechanism | Sparse index or manifests | RAG + structured KB hybrid |
| Judgment calibration | Direct feedback loop | Training through Review & Approve patterns |
| Scale mechanism | Folder structure + tags | Three-tier (Personal → Initiative → Company RAG) |
| Trust mechanism | Self-owned system | Asymmetric visibility design, privacy-first |

Key insight: the file-system approach has a defined scale limit. Principles are portable; implementation is not. At organizational scale, a hybrid architecture combining personal-scale file systems with initiative-level light indexing and company-wide RAG preserves the benefits while accommodating constraints.
