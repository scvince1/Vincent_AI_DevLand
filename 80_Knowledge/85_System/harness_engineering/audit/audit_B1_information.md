---
id: audit_B1_information
title: B1 信息层审计报告
tags: [harness, knowledge, audit, information-layer, intent-memory]
status: confirmed
last_modified: 2026-04-15
summary: MeowOS 信息层（Intent+Memory+Context）审计报告
---
# B1 信息层审计报告
**审计人:** Audit-B1
**审计日期:** 2026-04-14
**标尺文件:** `85_System/harness_engineering/00_master_synthesis.md` + `layers/B1_information_layer.md`
**审计范围:** IMPACT 的 Intent + Memory，以及 Context 管理机制

---

## 1. 状态总表

| 维度 | 状态 | 证据（文件路径 + 关键位置） |
|------|------|--------------------------|
| **Intent 质量 — Computational Guide 程度** | PARTIAL | `CLAUDE.md` 第 34-60 行有明确行为规则（shell-runner 委派、禁止行为列表、意图模糊先确认）；但第 1-7 行的角色描述（"来自喵星的女王喵"、"傲娇气质"）是装饰性 persona，无可验证输出 |
| **Intent 优先级顺序** | MISSING | `CLAUDE.md` 60 行全文无任何优先级声明；禁止行为（第 56-60 行）与工作流规则（第 27-35 行）之间发生冲突时无解决机制 |
| **Memory — 三类状态分离** | PARTIAL | Long-term 有 `80_Knowledge/`；Session state 隐含在 context；Task state 没有独立位置——`00_Dump/` 是 dump 输入仓，不是 task state 容器；`Dashboard.md` Todo 混合了 task 和 long-term |
| **Memory — Filesystem 原则** | EXISTING | `80_Knowledge/` 362 个文件，完全 filesystem-based，无向量库；与 master_synthesis Section 3（收敛 A）完全对齐 |
| **Memory — 目录索引文件** | PARTIAL | `81_Identity/_manifest.md`、`82_Projects/_manifest.md`、`86_AI_Systems/_manifest.md`、`88_Learned/_index.md` 存在；但 `83_Observations/`、`84_Fitness/`、`85_System/`、`87_People/` 均无索引文件 |
| **Cross-session 记忆防断裂** | PARTIAL | 有 MEMORY.md（61 条条目）+ `habits.md` + `_staging.md`；但 Task state 跨 session 断裂——见 Section 3.3 失败场景 B |
| **Prompt Caching 结构** | MISSING | `CLAUDE.md` 没有 cache breakpoint 标注；Permanent / Sticky / Ephemeral 三层未物理分离；内容混合在一个文件中 |
| **分层 System Prompt** | PARTIAL | 逻辑上有分层意图（CLAUDE.md = permanent，Dashboard = sticky，工具输出 = ephemeral）；但物理上 CLAUDE.md 把 Permanent + 部分 Sticky（路径表）混在一起 |
| **Context 压缩策略** | MISSING | 无滚动摘要机制；无 structured compaction；无明确触发条件（B1 Section 2.3 的 context rot 应对缺失）；`improvement-queue.md` 第 14 行有"暂存区超 200 行提示"的候选，但尚未审批写入 |
| **Context Reset 协议** | MISSING | 无明确的 session 任务边界定义；无"什么时候应该开新 session"的 computational rule |

---

## 2. 前三大风险

### 风险 1：规则冲突时无优先级 → 不确定行为
**证据：**
- `CLAUDE.md` 第 56 行禁止"不在主 session 直接读写文件"
- `CLAUDE.md` 第 34-35 行的 shell-runner 原则里包含"所有文件读写委派 shell-runner subagent"
- `CLAUDE.md` 第 40-43 行 ACE 机制要求主动写入 `_staging.md`——与上条禁止规则存在张力（ACE 触发时主 session 应该委派 shell-runner 还是自己写？逻辑混）
- `B1_information_layer.md` 第 285-295 行（反模式 2、3）：矛盾规则 + 无优先级是最高风险项

**具体失败场景：** 某次 session 中 ACE 机制触发，主 session 自己尝试写 `_staging.md`，违反 shell-runner 原则。或者反过来，shell-runner 委派延迟导致 ACE 暂存丢失。这种歧义已经发生——`improvement-queue.md` 第 34 行的 Digest Pipeline 诊断发现"ACE 暂存和 habits 写入存在偏差"。

### 风险 2：Task State 跨 session 断裂 → Amnesia Loop
**证据：**
- `80_Knowledge/` 目录结构中无 task state 专属容器（`00_Dump/` 是输入 dump，不是任务进度追踪）
- `Dashboard.md` 的 Todo 表（第 54-163 行）混合了长期待办和临时任务状态，但 Todo 是"人读"的，不是"凌喵读"的结构化 task state
- `B1_information_layer.md` 第 210-220 行（失败场景 B）：Task state 没有跨 session 持久化是 cross-session amnesia 的根因
- MEMORY.md 有 61 条条目，但全部是 long-term 的偏好/行为规则，没有任务进度状态

**具体失败场景：** Vincent 在 session A 里让凌喵协助推进某个多步任务（如 SharkNinja 面试准备）。session B 开始时凌喵读 Dashboard 但 Dashboard 只有 Todo 标记，不知道已执行了哪些步骤、哪些路径失败过，重复问题或走已排除的路径。

### 风险 3：Context Rot 无对抗机制 → 长 session 指令飘移
**证据：**
- `CLAUDE.md` 第 45-51 行的 ACE 触发范围非常宽——"只要出现就写，不等用户提示"，会引发大量暂存操作，主 session 轮次增加
- 没有 compaction 触发条件（`B1_information_layer.md` 第 29-35 行的 Context Pollution / Context Rot 对应 fix 在 MeowOS 完全缺失）
- `B1_information_layer.md` 第 317-328 行（失败场景 A）："Agent 在长对话中逐渐忽略系统提示里的关键约束"——这和 MeowOS 的"主 session context 保持干净"目标直接冲突
- `improvement-queue.md` 第 14 行的暂存区积压（493 行/4 天未消化）是已发生的信号

**具体失败场景：** 一个涉及健身 + 营养 + 日程安排的复合 session，工具调用轮次超过 20 轮后，凌喵开始在主 session 直接读文件（违反 shell-runner 原则），或者忽略了早在 session 头部声明的"先确认意图再执行"规则。

---

## 3. Gap 逐条改进候选

### Gap 1：CLAUDE.md 无规则优先级

**Gap:** 10 条行为规则（禁止行为 + ACE + shell-runner 等）之间没有显式优先级，冲突时模型依赖训练偏差打破平衡。

**Candidate A（Redirective - 利用现有 improvement-queue 机制）：**
在 CLAUDE.md 现有禁止行为段落（第 56-60 行）之前，插入一个 3 行的优先级声明块：
```
## 规则优先级（冲突时依此顺序）
1. 禁止行为列表（硬约束，不可覆盖）
2. shell-runner 委派原则（操作约束）
3. ACE 暂存机制（记录约束）
4. 工作流规则（流程约束）
```
改动极小，利用现有 improvement-queue + 系统诊断 session 审批流程写入，不需要新机制。

**Candidate B（Reframing）：**
质疑"把所有规则都放在 CLAUDE.md"这个假设。考虑把不同层级的规则物理分离：只把硬约束留在 CLAUDE.md（永久层），把 ACE 触发细则移到 `90_Agents/` 下的一个 `_rules.md`，按需读取。这样冲突概率降低，而不是靠优先级声明来"打补丁"。

**推荐:** Candidate A。优先级声明是最小改动、最高信噪比的修复。Reframing 有价值但改动大，放入 improvement-queue 做下一步诊断。

**优先级:** 高 | **工期:** 1小时

---

### Gap 2：Task State 没有独立持久化容器

**Gap:** Session / Task / Long-term 三类状态中，Task State（任务进度、失败历史、中间结果）没有物理独立存储位置，跨 session 状态丢失。

**Candidate A（Redirective - 复用 00_Dump 结构）：**
`00_Dump/` 已经是任务临时输入的容器，在同目录建立 `00_Dump/Tasks/` 子目录，每个进行中的多步任务一个文件（`job-search-sharkninja.md`），包含进度、失败路径、当前状态。`dump-processor` agent 已有读写 `00_Dump/` 的能力，可以直接扩展。不需要新 agent，不需要改主架构。

**Candidate B（Additive）：**
在 `80_Knowledge/` 下新建 `89_Tasks/` 目录，专门存放任务状态文件，带 frontmatter 标注任务生命周期（active/paused/done）。

**推荐:** Candidate A。直接复用 `00_Dump/` 容器和 `dump-processor` agent，避免在 `80_Knowledge/` 增加一个新的长期管理目录。Task state 本来就是有时效性的，放在 Dump 结构下也更直观。

**注意:** Candidate B 是纯 additive，如果 Candidate A 经过验证不合适再考虑。

**优先级:** 高 | **工期:** 2-3小时（包含 dump-processor 的小幅更新）

---

### Gap 3：Prompt Caching 无结构支撑

**Gap:** `CLAUDE.md` 无 cache breakpoint 标注；Permanent/Sticky/Ephemeral 三层物理混合；每次请求可能重新计算整个 system prompt。

**Candidate A（Redirective - 拆分注入顺序，不改 CLAUDE.md 内容）：**
在 session 开始的 hook 里，按 Permanent → Sticky → Ephemeral 顺序注入，而不是一次性传整个 CLAUDE.md。路径表（Sticky 内容）改为 session 开始时由 shell-runner 动态读取后注入，而不是硬编码在 CLAUDE.md 里。这样 CLAUDE.md 本身只含 Permanent 内容，缓存命中率提高。

**Candidate B（Reframing）：**
MeowOS 是单用户、低频请求的个人系统，每次 session 的 system prompt 重新计算成本相对较低。问的是：prompt caching 的投入回报比是否值得在当前规模投入工程资源？如果 Vincent 每天 session 数量有限，优先级可以降低。

**推荐:** Candidate B 的 Reframing 优先。当前规模下 caching 优化不是迫切问题。但 Candidate A 的"把 Sticky 内容移出 CLAUDE.md"作为副产品有助于降低 CLAUDE.md 的 kitchen sink 风险，值得作为其他改进的附带动作执行。

**优先级:** 低 | **工期:** 4-6小时（如果做）

---

### Gap 4：Context Rot 无压缩协议

**Gap:** 长 session（>20 轮）无 compaction 触发，无 context reset 触发条件，指令飘移风险随 session 长度递增。

**Candidate A（Redirective - 复用现有 shell-runner 委派原则）：**
在 CLAUDE.md 工作流段落中加入一条 computational rule：
```
当 session 超过 15 轮工具调用时，在下一轮回复前主动告知 Vincent：
"当前 session 轮次较多，建议开启新 session 继续，我会提供状态摘要。"
```
这是在现有"主 session context 保持干净"原则的基础上加一个触发条件，不需要新机制。摘要由主 session 生成，状态写入 `00_Dump/Tasks/`（即 Gap 2 的方案）。

**Candidate B（Reframing）：**
"凌喵怕麻烦"（CLAUDE.md 第 28 行）是设计原则，换言之 MeowOS 的 session 应该天然短。问的是：MeowOS 是否真的会产生"长 session"？如果 shell-runner 委派有效执行，主 session 实际上只处理高层决策，轮次自然受控。Context Rot 可能是个被夸大的风险。

**推荐:** 两者并行。Candidate B 的 reframing 先验证（观察近期 session 是否真的超 15 轮）；如果有，再执行 Candidate A。

**优先级:** 中 | **工期:** 1小时（若验证后需要写入）

---

### Gap 5：部分知识目录缺少索引文件

**Gap:** `83_Observations/`、`84_Fitness/`、`85_System/`、`87_People/` 四个目录无 `_manifest.md` 或 `_index.md`，agent 无法快速定向导航。`B1_information_layer.md` 第 311 行明确标注"渐进式披露"需要 metadata 层作为前置。

**Candidate A（Redirective - 复用现有 manifest 模板）：**
`81_Identity/_manifest.md` 和 `86_AI_Systems/_manifest.md` 已有 frontmatter 模板（type/cluster/last_updated）。直接复制这个模板为 `83_Observations/_manifest.md`、`84_Fitness/_manifest.md` 等创建索引，内容列出该目录的文件功能摘要。这是纯文件创建，无 agent 改动。

**Candidate B（Reframing）：**
`84_Fitness/` 下的 `_rules.md` 和 `_state.md` 本质上已经起到了"索引 + 入口"的功能（`fitness-coach.md` 第 14-18 行明确列出读取文件清单）。Agent 已经通过 prompt 硬编码了导航，`_manifest.md` 可能只是多余的文档层。问的是：缺少 manifest 的目录，有没有 agent 因为"不知道读什么文件"而失败过？

**推荐:** Candidate A 对 `83_Observations/` 和 `87_People/` 优先执行（这两个目录没有 agent prompt 内的硬编码导航）；`84_Fitness/` 和 `85_System/` 用 Candidate B 的 reframing——agent prompt 已覆盖。

**优先级:** 中 | **工期:** 1-2小时

---

### Gap 6：_staging.md 写入触发范围过宽，缺少去重/合并步骤

**Gap:** `CLAUDE.md` 第 45-51 行的 ACE 触发范围覆盖"只要出现就写"，但写入后没有合并/去重机制（`B1_information_layer.md` 第 200-202 行指出 MeowOS 的"合并/去重步骤没有显式化"）。`improvement-queue.md` 第 34 行已记录"ACE 暂存存在偏差"的诊断。

**Candidate A（Redirective - 用 system-diagnostics 的现有步骤 2 扩展）：**
`system-diagnostics.md` 第 18-23 行已有"消化暂存区 → 判断是否可提炼 → 更新 habits.md → 清空 staging"的流程。在该 agent 的步骤 2 中，加入一个 diff 步骤：写入 `habits.md` 前检查是否与现有条目冲突或重复，并区分"Vincent 纠正凌喵（凌喵错误信号）"和"Vincent 表达偏好（用户习惯）"。这直接修复 `improvement-queue.md` 第 34 行已记录的已知缺陷。

**Candidate B（Additive）：**
新建一个 staging-merge agent，负责定期（每 3 天或超过 100 行时）运行去重和合并。

**推荐:** Candidate A。system-diagnostics 已有完整的步骤框架，diff 步骤是 3-4 行的 prompt 扩展，不是新 agent。Additive 的 Candidate B 引入了管理开销。

**优先级:** 高 | **工期:** 1小时

---

### Gap 7：MEMORY.md 与 habits.md 边界模糊，同类信息双写

**Gap:** MEMORY.md（Claude 自动记忆，61 条）和 `habits.md`（MeowOS 显式维护，凌喵读）存在内容重叠。例如"Nocturnal Productivity Peak"在两个地方都有。没有明确的分工协议。

**Candidate A（Reframing）：**
质疑这是否是一个问题。两个系统有不同的读者和不同的维护机制：MEMORY.md 是 Claude 跨项目自动维护的（不受 MeowOS 控制），`habits.md` 是凌喵主动维护的（更可靠、更细粒度）。重叠是有意冗余（redundancy），在一个系统失效时另一个兜底。问的是：重叠是否导致了实际的错误行为？

**Candidate B（Redirective - 在 CLAUDE.md 中声明分工）：**
在 `CLAUDE.md` 路径表中加一行说明：
```
| MEMORY.md 边界 | 跨项目通用偏好（Claude 自维护）；会话特定细节不写入 MEMORY.md，只写 habits.md |
```
这不是技术修复，是认知边界的显式化，防止未来出现"该写哪里"的判断歧义。

**推荐:** Candidate A 的 reframing 先验证（查是否有实际冲突案例）；如果没有，接受现状。Candidate B 作为低成本的文档改进可以附带执行。

**优先级:** 低 | **工期:** 30分钟（若做 Candidate B）

---

### Gap 8：Agent prompts 缺少标准化 Intent 段落

**Gap:** `00_master_synthesis.md` 第 115 行建议"每个 Skill/Agent 都应有标准化 metadata（name + description）"。检查：`knowledge-agent.md` 第 1 行只有名称；`fitness-coach.md` 第 1 行有触发词但无正式 Intent 声明；`system-diagnostics.md` 第 3 行有职责描述。格式不一致，无标准化 metadata。

**Candidate A（Redirective - 复用 fitness-coach 的触发词格式做模板）：**
`fitness-coach.md` 的格式（触发词 + 更新日期 + 职责）是最完整的，把这个格式反向推广到其他 agent 作为最小标准。不需要新文件，在系统诊断 session 里作为"格式统一"任务批量执行。

**Candidate B（Additive）：**
建立 agent prompt 模板文件 `90_Agents/_template.md`，规定 Intent/触发词/知识文件/执行步骤/返回格式的标准结构。

**推荐:** Candidate A 短期，Candidate B 中期。先统一现有格式，再固化模板。

**优先级:** 中 | **工期:** 2小时

---

## 4. MeowOS 已做得好的事（对标 B1 标准）

1. **Filesystem memory 架构与行业收敛完全对齐。** 362 个文件、分层目录结构（`80_Knowledge/`）、无向量库，完全符合 master_synthesis 收敛 A 的论断。这不是偶然选择，是正确的工程判断。

2. **shell-runner 委派原则是高质量的 Context Pollution 对策。** `B1_information_layer.md` 第 31 行 Jason Liu 的实测数据：subagent 路径比 slash command 路径信噪比高 8 倍。MeowOS 的 shell-runner 原则（CLAUDE.md 第 34-35 行）独立实现了同样的设计，且在 `01_Routing.md` 第 51 行再次强化。

3. **improvement-queue + 系统诊断 session 的审批流程是有效的 GC 机制。** Lopopolo 主张 4 要求"持续的 garbage collection"，MeowOS 用 `improvement-queue.md` + 诊断触发词实现了人工审批版本。改动不自动写入、需要显式审批，符合"人类注意力是瓶颈"（master_synthesis 收敛 E）的设计原则。

4. **01_Routing.md 实现了渐进式披露的关键部分。** `00_master_synthesis.md` 收敛 D 建议"启动时只加载 metadata"。MeowOS 的路由表（`01_Routing.md` 第 1-60 行）正是这个结构：主 session 只持有路由规则，具体 agent 按需加载。知识文件也不进主 session context，由 shell-runner 按需读取。

5. **fitness-coach 的硬约束注入模式是 computational guide 的好例子。** `fitness-coach.md` 第 1-3 行在最开头（primacy 位置）放了一个 `[硬约束 · 日期边界]` 段落，明确触发条件和违反后果，完全符合 B1 Section 4.1 的 computational guide 标准。这个模式值得推广到其他 agent。

---

## 5. 无法充分审计的部分

1. **Prompt caching 实际命中率无法验证。** MeowOS 基于 Claude Code（API 层面），没有 cache hit/miss 的可观测数据。是否有 TTL 过期问题、是否因路径表频繁变动导致 cache miss，无法从文件层面得出结论。

2. **主 session 实际 context 长度分布未知。** shell-runner 委派是否在实践中真正执行（还是主 session 有时直接调用 Read）、实际轮次分布，没有 session 层面的遥测数据，只能从 improvement-queue 的观察信号（暂存积压）间接推断。

3. **88_Learned 目录规模和质量。** `_index.md` 存在但未读取全文，88_Learned 里的知识条目是否按 frontmatter 模板严格写入、是否存在无 frontmatter 的"孤立"条目，未做全面 audit。

4. **跨系统（Horsys/NovelOS）的状态同步机制正确性。** `01_Routing.md` 第 53-60 行有跨系统概览自动检测的规则，依赖 `LastWriteTime` 对比。该机制是否在实践中可靠触发，未验证。

---

*审计完成时间: 2026-04-14 · Audit-B1*
