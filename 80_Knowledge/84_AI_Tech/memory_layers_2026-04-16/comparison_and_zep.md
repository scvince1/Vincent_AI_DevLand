# Zep / Mem0 / A-MEM — Agent Memory Layer Comparison

**Fetch date:** 2026-04-16
**Persistence note:** Originally assigned to background subagent; Write tool was blocked in that session, so content was saved from main session using the agent's full report.

**Sources:**
- Zep: arXiv 2501.13956 — https://arxiv.org/abs/2501.13956 ; https://www.getzep.com ; Graphiti OSS on GitHub
- Mem0: arXiv 2504.19413 — https://arxiv.org/abs/2504.19413 ; https://mem0.ai
- A-MEM: arXiv 2502.12110 — https://arxiv.org/abs/2502.12110

---

## Judgment Call: DIFFERENCES ARE SIGNIFICANT

Each solves a meaningfully different problem. They are not cosmetic variants.

---

## Phase 1: 5-Dimension Comparison

| Dimension | Zep (Graphiti) | Mem0 | A-MEM |
|-----------|---------------|------|-------|
| **Core data structure** | Temporal knowledge graph. Nodes = entities, edges = facts. 4 timestamps per edge. Backends: Neo4j, FalkorDB, Kuzu, Neptune. | Hybrid: vector store + optional graph layer + rerankers. Primary index is embeddings. | Vector store (ChromaDB) + Zettelkasten-style note network. Each memory has tags, keywords, category, context metadata. |
| **Update mechanism** | Invalidation-not-deletion. Conflicts set `invalid_at` on old edge; history preserved. Explicit delete removes edge. 4 edge timestamps: `created_at`, `valid_at`, `invalid_at`, `expired_at`. | Extract-and-consolidate via Memory Compression Engine. Merges or supersedes prior memories with versioned timestamps. Not natively bi-temporal. | Retroactive evolution. New memory triggers re-indexing and attribute updates on *existing* memories. No explicit invalidation — old memories enriched, not timestamped out. |
| **Query/retrieval** | Hybrid: semantic embeddings + BM25 keyword + graph traversal, reranked by graph distance. Time-travel queries ("what was true at T?"). Sub-200ms P95. | Semantic search (primary) over vector store. Graph layer for relational queries in graph variant. Returns relevance scores + categories. | Semantic search via ChromaDB. Note links enable associative traversal but retrieval is primarily vector-similarity. |
| **Production readiness** | Production-grade. SaaS (getzep.com): SOC 2 II, HIPAA BAA, BYOC/BYOK/BYOM. Graphiti is Apache-2.0 OSS, Docker self-host. Python/TS/Go SDKs. REST + MCP server. Pricing: Free / $25 / $475 / Enterprise per mo. | Production-grade. SaaS (mem0.ai): SOC 2 II, GDPR, on-prem enterprise tier. Python/JS SDKs. `pip install mem0ai`. Pricing: Free / $19 / $249 / Enterprise per mo. | Research-grade. MIT OSS only. No managed service, no pricing tier, no enterprise path. OpenAI + Ollama backends. Minimal production guidance. |
| **Target use case** | Multi-session agents + enterprise data integration. Temporal reasoning over evolving facts. Cross-session synthesis and factual history. | Conversational personalization at scale. High-throughput, low-latency recall of user preferences. Multi-hop and temporal Q&A over long dialogue histories. | Research / agent self-improvement. Agents iteratively building domain knowledge across tasks. Single-agent, not multi-user production. |

---

## Phase 2: Why the Differences Are Significant

**1. Zep** is a temporal fact store built around a knowledge graph. The bi-temporal edge model is architecturally foundational — every fact independently tracks when it was true in the world and when the system learned about it. This enables point-in-time historical queries that Mem0 and A-MEM simply cannot do. Target: enterprise agents reasoning over evolving real-world state (product histories, user relationship changes, compliance timelines).

**2. Mem0** is a memory compression and retrieval service optimized for conversational personalization at scale. Its graph layer is additive, not foundational — the primary operation is extract-consolidate-index over dialogue. Right tool for high-throughput, low-latency recall across large user bases where you need "what does this user prefer now" not "what did they prefer in Q3 2023." Claims 91% latency reduction and >90% token cost reduction vs full-context approaches.

**3. A-MEM** is a research prototype with a genuinely distinct mechanism: adding new memories retroactively enriches existing ones (the Zettelkasten influence). Knowledge compounds rather than just accumulates. Interesting for solo research-assistant agents but has zero production deployment story, no multi-user support, and no validation at scale.

The three differ on data model (graph vs vector vs associative notes), update semantics (invalidate vs compress vs retroactively enrich), and production maturity (enterprise vs scalable SaaS vs research). This is a selection decision, not a "which implementation of the same idea" decision.

---

## Selection Matrix

| Scenario | Best Pick | Why |
|----------|-----------|-----|
| Agent tracking when facts changed over time | Zep | Only system with bi-temporal edges + point-in-time queries |
| High-volume conversational AI, tight token budget | Mem0 | 91% latency cut, 90% token reduction; production-hardened SaaS |
| Single agent doing iterative research | A-MEM | Retroactive enrichment; no infra overhead |
| **Challenge 5 bootstrap** (scrape → sentiment → prediction) | ChromaDB / A-MEM pattern | Lightweight; don't add graph DB before pipeline exists |
| **Challenge 5 production** (failure-mode timeline tracking) | Zep | Temporal tracking of failure modes across product generations and review date windows |
| MeowOS KB augmentation | Graphiti OSS | Files ingested as episodes; MCP server gives Claude direct graph queries |

---

## Zep / Graphiti Deep Dive

### Bi-Temporal Edge Model

Every edge (fact) carries four temporal fields:

- `created_at`: when Zep first recorded this fact (database time)
- `valid_at`: when the fact became true in the real world
- `invalid_at`: when the fact stopped being true in the real world
- `expired_at`: when Zep learned the fact was no longer valid (database time)

Two independent time axes — world time (valid_at / invalid_at) and database time (created_at / expired_at). This separation handles late-arriving data correctly. A product failure mode documented in 2022 reviews, ingested in 2025, gets `valid_at=2022` and `created_at=2025`. A query for "failure modes that existed in 2022" returns it correctly.

From docs verbatim: "When new data invalidates a prior fact, the time the fact became invalid is stored on that fact's edge in the knowledge graph."

### Invalidation vs Deletion

**Invalidation** (default when contradictions arrive): sets `invalid_at` on the superseded edge. Edge remains in graph; historical queries find it. Example: user changes shoe preference from Adidas to Puma — Adidas edge gets `invalid_at` set; Puma edge created.

**Deletion** (explicit): removes the edge entirely. No historical record. Requires explicit API call; not triggered automatically by contradictions.

Default behavior is append-with-invalidation. Graph grows monotonically unless explicitly pruned.

### Contradiction Handling Flow

1. New episode arrives
2. LLM compares new content against existing edges to detect contradictions
3. Contradicting edges get `invalid_at` set to the episode's `reference_time`
4. New edge created with updated fact
5. Both old and new edges preserved with respective validity windows
6. All edges trace back to source episodes (full provenance chain)

No summarization step — original episode text is ground truth.

### Query Semantics

- Current facts: edges where `invalid_at IS NULL AND valid_at <= now`
- Point-in-time T: edges where `valid_at <= T AND (invalid_at IS NULL OR invalid_at > T)`

### API Surface

Graphiti Python (OSS):
```python
from graphiti_core import Graphiti
graphiti = Graphiti("bolt://localhost:7687", "neo4j", "password")

await graphiti.add_episode(
    name="review_batch_1",
    episode_body="Users report motor failure in model X after 18 months.",
    source_description="scraped_review",
    reference_time=datetime(2023, 6, 15)
)
results = await graphiti.search("motor failure reports for model X")
```

Zep managed SDK: `client.thread.add_messages(thread_id, messages)` and `client.context.create_context_template(...)`

API resource categories: Thread, User, Context, Graph (nodes/edges/episodes/ontology), Project, Task, Community (experimental).

REST: FastAPI-based, mirrors SDK. MCP Server: ships with Graphiti OSS; connects Claude Code or any MCP client directly to the running graph.

### Deployment Model

SaaS tiers:

| Tier | Price | Credits/mo | Rate limit |
|------|-------|-----------|-----------|
| Free | $0 | 1,000 | Variable, low priority |
| Flex | $25/mo | 20,000 + auto-topup | 600 req/min |
| Flex Plus | $475/mo | 300,000 + auto-topup | 1,000 req/min |
| Enterprise | Custom | Custom | Guaranteed SLA |

Credit model: 1 episode = 1 credit. Episodes >350 bytes billed in multiples. Storage not charged separately. Enterprise: BYOC, BYOK, BYOM. SOC 2 II, HIPAA BAA.

Self-hosted (Graphiti OSS): Apache 2.0; Docker Compose with Neo4j or FalkorDB; Python 3.10+; LLM API key required for entity extraction; Windows via Docker only; MCP server included.

### Known Limitations

- Entity extraction requires LLM call per episode (latency + cost at ingestion scale)
- Graph DB dependency (Neo4j or FalkorDB must run continuously)
- Windows: Docker only, no native installer
- Credit accumulation on SaaS at high episode volume
- Community detection is experimental, not production-stable
- Contradiction detection quality is LLM-dependent

---

## Integration Notes: Graphiti + MeowOS File-Based KB

MeowOS KB at `D:\Ai_Project\MeowOS\80_Knowledge\` is markdown files. Clean integration pattern:

**Files remain canonical truth.** Graphiti runs as a derived read-optimization layer:

1. Sync agent monitors KB markdown files for changes
2. On change: ingest file as Graphiti episode with file path as source reference
3. Graphiti extracts entities and facts automatically; nodes/edges created with temporal windows
4. Claude queries graph via MCP server at inference time (no full file loads into context)
5. Graph state is never primary: if conflict, markdown file wins
6. File deletions propagate as explicit edge deletions

Advantages: relational cross-file queries ("projects involving Joyce with deadline this month") without loading multiple full files; temporal tracking of role/status changes; sub-200ms retrieval.

Constraints: Docker + graph DB must run; sync agent adds operational overhead; LLM costs for initial ingestion; two truth representations require discipline.

**Recommendation: do not implement now.** Current MeowOS KB scale does not justify the infrastructure. Revisit when: (a) relational cross-file queries become context-load bottlenecks, or (b) temporal tracking of evolving facts is needed at query time without loading full history.