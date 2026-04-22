# DevLand 路由规则 v1.0
_同步自 MeowOS v2.0 — 裁剪版 | 更新: 2026-04-21_

## 意图分类

| 触发词 / 意图 | 路由目标 |
|-------------|---------|
| `系统诊断` / `系统增强` / `system diagnostic` / `system enhancement` | → system-diagnostics |
| `读了…` / `想聊聊…` / `记一下这个概念` / `整理一下XX` / `这个想法` / `入库` / `knowledge` / `知识归档` / `read ...` / `think about ...` / `log this concept` / `archive knowledge` | → knowledge-agent |
| `聊聊身边的人` / `聊聊身边的事` / `跟你说说身边的人` | → people-interview skill |
| `记住这个` / `obs:` / `remember this` | → 主入口直接处理（写入 83_Observations/habits.md） |
| `日历` / `calendar` / `日程查看` / `添加日程` | → 主入口直接处理（调用 calendar MCP tools） |
| `同步外部系统` / `跨系统同步` | → 主入口直接处理（强制读取外部文件，刷新跨系统概览） |
| 意图不明 / Ambiguous intent | → 主入口直接问 Vincent 确认意图，不猜测 |

> ⚠️ `早 / check / 收工` / `安排 / 排日程` 等 daily 语境触发词暂空（等待 dashboard 模块按 DevLand 需求实现）

## Claude 主 session 自动调用（非关键词触发）

以下 agent 由主 session 在识别到相关语境时**自动召唤**，Vincent 通常不直接触发：

| agent | 自动触发语境 |
|---|---|
| knowledge-agent | 80_Knowledge/ 下**结构化条目**写入（single-writer，见下）；reading/writing person profiles；cross-category queries across `80_Knowledge/` |

## 知识库写入路由（single-writer 原则）

**结构化写入 → knowledge-agent 独占**:
- `87_People/` 人物档案
- `88_Learned/` 外部知识卡片
- `88_Research/` 研究库（除 `_inbox/`）
- `82_Projects/` 项目追踪
- `{Knowledge,Entity,Meta}_Index.md` 全局索引重建
- 其他 `80_Knowledge/` 下带 frontmatter 的结构化 md

**Raw append log → shell-runner 直写**（需首行声明 `[raw_log_write=true, path=<精确路径>]`）:
- `83_Observations/_staging.md`
- 其他符合 raw log 语义的文件

**shell-runner 对 `80_Knowledge/` 写入有硬性 scope guard**（见 `shell-runner.md`）:
- 未带 `[raw_log_write=true]` 标记的写入被拒绝
- knowledge-agent 不通过 shell-runner 写文件，自己用 Write/Edit 工具

## Cross-agent 编排规则

- 某 agent 输出 `cross_agent_required` flag 时，主 session 按 flag 的 `target` **顺序调用**目标 agent（纵向编排）
- **禁止** agent 之间横向直接 call 其他 agent（防止嵌套调用失控、难调试）
- 主 session 综合多 agent 结论后再向 Vincent 呈现
- 常见编排路径:
  - knowledge-agent 写入 `88_Research/_inbox/` → 触发 `inbox_archive` 归档流程

## 冲突规则

- 多意图信号 → 逐一处理，告知 Vincent 顺序

## 文件操作原则

- 所有读写操作（除 knowledge-agent 自身）委派 shell-runner subagent，不在主 session 直接调用 Read/Edit/Grep/Glob
- **knowledge-agent 是例外**: 它是独立 subagent，自己拥有 context，直接使用 Write/Edit 工具操作 `80_Knowledge/`，不再转派 shell-runner（见 `knowledge-agent.md`）

**Exceptions to shell-runner delegation (direct tools are fine):**
1. Vincent explicitly asks for direct file operations.
2. The session is dedicated to coding / development / using the `complex-system` skill.
