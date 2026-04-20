# Dream Mode 研究 & MeowOS 应用方案

> 来源：[clawdecode.net](https://www.clawdecode.net/) — Claude Code 源码泄露分析
> 日期：2026-04-09
> 用途：供另一个 session 的记忆模式增强讨论参考

---

## 一、Dream Mode 原始设计

### 概述

Dream Mode 是 Claude Code 的**空闲时段记忆维护系统**，四阶段串行执行。核心设计哲学：

- 纯 markdown 文件，不用向量数据库 / RAG
- `ENTRYPOINT.md` 作索引，硬限 25KB、单条 ≤150 字符
- 记忆按类型分：user（偏好/角色）、feedback（纠正）、project（进行中工作）、reference（外部指针）
- 每日日志层级存储：`logs/YYYY/MM/YYYY-MM-DD.md`
- Session transcripts 存为大 JSONL 文件，只做定向查询

### Phase 1: Orient（定位）

- 列出 memory 目录内容，理解现有结构
- **完整读取** ENTRYPOINT.md 索引
- 浏览已有的主题文件，识别已覆盖的话题
- 目的：**防止创建重复记忆**

### Phase 2: Gather（采集）

- 检查 daily logs 里最近漂移/演化的记忆
- **窄范围 grep** JSONL transcript 文件
- 关键原则：**"Don't exhaustively read transcripts. Look only for things you already suspect matter"**
- 识别值得整合到持久记忆的具体事实

### Phase 3: Consolidate（整合）

- 将新发现信息合并到已有记忆文件
- 所有相对日期 → 绝对日期（"yesterday" → "2026-04-08"）
- 识别并删除被推翻/取代的事实
- 将相关信息综合成连贯叙述
- 维护组织良好、持久的记忆结构

### Phase 4: Prune（修剪）

- 强制执行索引大小限制（25KB + 最大行数）
- 删除指向过时信息的死链
- 通过仔细比对解决记忆文件之间的矛盾
- 删除已过期或不再相关的引用

### 关键约束

| 约束 | 规则 |
|------|------|
| 索引上限 | ENTRYPOINT.md ≤ 25KB |
| 单条长度 | ≤ 150 字符 |
| Transcript 策略 | 窄 grep，不全读 |
| 日期处理 | 一律转绝对日期 |
| 矛盾处理 | 删旧留新 |

---

## 二、MeowOS 现状对照

| Dream Mode 概念 | MeowOS 对应 | 差距 |
|---|---|---|
| ENTRYPOINT.md | `MEMORY.md`（auto memory 索引） | 有 200 行截断规则，但没有主动 prune 机制 |
| 四类记忆（user/feedback/project/reference） | auto memory 完全一致 | ✅ 已对齐 |
| Daily logs | 无 | 没有按天归档的对话日志 |
| JSONL transcripts | `99_MyFiles/Normalized_Session_History/` 有部分 | 存在但没被系统性利用 |
| Orient 阶段 | 系统诊断时没有标准化的"先看全貌"步骤 | ❌ 缺失 |
| Gather 阶段 | `_staging.md` 承担了一部分 | 但没有从 transcript 主动采集的能力 |
| Consolidate 阶段 | 系统诊断在做，但没有日期转换和矛盾检测 | ⚠️ 部分覆盖 |
| Prune 阶段 | **基本没做** | ❌ 缺失 |
| 25KB 硬限 | 无 | ❌ 缺失 |
| 空闲时段自动执行 | 需要 Vincent 手动喊"系统诊断" | ❌ 被动触发 |

---

## 三、建议应用方向

### 3.1 系统诊断标准化为四阶段

改 `system-diagnostics` agent prompt，把四阶段写成强制步骤：

**Orient →** 读 `MEMORY.md` 索引 + `_staging.md` + `habits.md` 目录，建立全貌，识别已有条目避免重复

**Gather →** 从 `_staging.md` 提取高信号条目；可选：窄 grep `Normalized_Session_History/` 里的近期 transcript

**Consolidate →** 合并到 `habits.md` / 对应 Knowledge 文件；相对日期→绝对日期；发现矛盾删旧留新

**Prune →** 清空已处理的 `_staging.md`；删 `MEMORY.md` 死链；删 Knowledge 文件过期条目

### 3.2 索引 Prune 硬规则

- `MEMORY.md` 超过 150 行 → Prune 阶段必须砍到 120 行以内
- 每条 memory 文件可加 `last_verified` 字段，系统诊断时删超过 60 天没被触发的
- "死链"定义：memory 文件指向的路径/资源已不存在

### 3.3 Transcript 利用（可选增强）

Dream Mode 的 Gather 阶段会 grep JSONL transcript 找高信号信息。MeowOS 的 `Normalized_Session_History/` 和 digest pipeline 已经有部分基础设施。可以在系统诊断时加一步：窄范围 grep 最近 3 天的 transcript，找 `_staging.md` 可能遗漏的观察。

### 3.4 自动触发（依赖 KAIROS/schedule 能力）

Dream Mode 在"空闲时段"自动跑。如果 MeowOS 未来有 schedule/cron 能力，可以设一个每天凌晨 4:00 的 trigger 自动执行一次四阶段整合，不需要 Vincent 手动喊"系统诊断"。

---

## 四、核心 takeaway

1. **Anthropic 自己选了纯 markdown 路线**，不用向量库——验证了 MeowOS 的方向
2. **关键差距不在存储格式，在维护纪律**——四阶段流程 + prune 硬规则才是 Dream Mode 的真正价值
3. **"Don't exhaustively read, grep for what you suspect matters"** 这条原则可以直接偷——系统诊断不需要全量读所有文件