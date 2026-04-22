---
id: 88-research-registry
title: 88_Research Own Registry
tags: [meta, research, registry]
status: active
last_modified: 2026-04-21
---

# 88_Research 本地注册表

> **协议**: 此 registry 与全局 `Knowledge_Index.md` **互补不竞争**:
> - 全局 `Knowledge_Index.md` 负责 ID 检索（id/type/name/folder/key_info 列）
> - 本 registry 负责 research 生命周期（concept/tier/freshness/sources 列）
>
> 所有 88_Research/ 下的 non-meta 文件须同时出现在两处。如发现偏差，以 knowledge-agent 的 registry rebuild 为准。

---

# KB Registry

Master index of all concepts in `{KB_ROOT}` = `D:\Ai_Project\MeowOS\80_Knowledge\88_Research`.

## By Concept (A-Z)

| Concept | Tier | Last Updated | Sources Scraped | Summary | Notes |
|---|---|---|---|---|---|
| corporate_consumer_signal_roles | T2 | 2026-04-17 | 6 synthesis files produced (primary: LinkedIn / careers.sharkninja.com / trade press) | yes (00_synthesis.md) | Challenge 5 target-user research, SharkNinja-specific |
| memory-layers | T2 | 2026-04-16 | 1 synthesis (arXiv 2501.13956 / 2504.19413 / 2502.12110 + vendor docs) | yes (comparison_and_zep.md) | Zep / Mem0 / A-MEM 三家对比；Graphiti MCP 集成建议 |
| skill-optimization | T2 | 2026-04-16 | 2 synthesis files (darwin-skill repo + 17 papers/frameworks) | yes (01_darwin_skill.md + 02_landscape.md) | darwin-skill 深挖 + 全景扫描，并发 subagent 产出 |
| vibe-kanban | T2 | 2026-04-19 | 1 synthesis (GitHub + DeepWiki + 官方 blog) | yes (vibe-kanban-architecture.md) | BloopAI repo 逆向；公司已关闭转社区维护 |
| word2vec | slow | 2026-04-16 | 0 / 5 primary + 0 / 4 secondary | yes (from Session 1 narrative) | First seed concept; source scrape pending |

## By Recency

| Last Updated | Concept |
|---|---|
| 2026-04-19 | vibe-kanban |
| 2026-04-17 | corporate_consumer_signal_roles |
| 2026-04-16 | memory-layers |
| 2026-04-16 | skill-optimization |
| 2026-04-16 | word2vec |

## By Freshness Tier

**fast** (re-scrape every ~2 months): _(none yet)_

**T2** (default research material, re-check quarterly): corporate_consumer_signal_roles, memory-layers, skill-optimization, vibe-kanban

**slow** (stable, no regular re-scrape): word2vec
