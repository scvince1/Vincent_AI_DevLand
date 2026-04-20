---
id: audit_B2_execution
title: Audit-B2 — 执行层审计报告
tags: [harness, knowledge, audit, execution-layer, planning]
status: confirmed
last_modified: 2026-04-15
summary: MeowOS 执行层（Planning+Control Flow+Tools）审计报告
---
# Audit-B2：执行层审计报告
**审计日期：** 2026-04-14
**审计对象：** MeowOS 执行层（Planning + Control Flow + Tools）
**标准来源：** `harness_engineering/layers/B2_execution_layer.md`
**审计人：** Audit-B2 subagent

---

## 1. 状态总表

| 维度 | 评级 | 关键证据 |
|------|------|---------|
| **Planning — 持久化规划** | 🔴 缺失 | 无跨 session 的计划层；improvement-queue.md 承担了部分规划功能但不是 planning layer |
| **Planning — 计划质量评估** | 🔴 缺失 | 无 plan 质量 gate；所有 agent prompt 直接执行，无评估步骤 |
| **Control Flow — shell-runner 委派** | 🟢 强 | CLAUDE.md L34-35；01_Routing.md L51；所有 agent prompts 均包含委派声明 |
| **Control Flow — agent 间状态传递** | 🟡 弱 | 仅靠 `cross_agent_required` flag（01_Routing.md L38-40）；无结构化 payload schema |
| **Control Flow — HITL 触发点** | 🟡 部分 | scheduler.md L33 / dump-processor.md Step 2-3 有显式确认门；其余 agent 无系统性 HITL 约束 |
| **Control Flow — 并行 agent 调度** | 🟡 散乱 | digest-pipeline.md 中有 Pass 1 × N Opus subagent（串行）、Pass 2-3 单次；其余 agent 无并行模式 |
| **Control Flow — 失败恢复** | 🟡 局部 | digest-pipeline.md 有显式失败恢复逻辑（L60-65）；其余 agent 无失败恢复协议 |
| **Control Flow — context reset 协议** | 🔴 缺失 | 无任何文件描述 context 耗尽时的处理方式 |
| **Tools — 工具数量 / 暴露管理** | 🟡 中等 | settings.json 有 160+ WebFetch 域名白名单 + 1 MCP；技术上工具数可控，但无 progressive disclosure |
| **Tools — 工具描述质量** | 🟢 良好 | 各 agent prompt 对工具调用有明确触发词和禁止声明；符合 B2 Section 4 规范 |
| **Tools — MCP 配置** | 🟢 受控 | settings.json L285-294：仅 ms365 一个 MCP server；未过度暴露 |
| **Tools — 工具结果后处理** | 🔴 缺失 | 无 SummarizationMiddleware 类机制；shell-runner 返回原始内容 |
| **Orchestration — 模式识别** | 🟡 混合 | 主要是 Single-Agent Tool Loop + 手动 Handoff；有 Plan-Execute 影子但无正式 Planner/Executor 分离 |
| **Orchestration — Planner/Executor 分离** | 🔴 缺失 | system-diagnostics agent（L1-55）同时做诊断+建议+执行，三角色未分离 |

---

## 2. Top 3 风险

### 风险 1：持久化规划层缺失 — 多 session 目标漂移

**为什么是最高风险：** MeowOS 的高价值工作（文章系列 HBR/LinkedIn、求职、BaseOS 设计）全部是多 session 跨度项目。当前规划状态只存在于 session-level TodoWrite，session 结束即消失。改进队列（improvement-queue.md）承担了部分"积压项目"功能，但它是待审批列表，不是执行计划。

**具体后果：**
- job-search.md 有状态追踪（82_Projects/job-search.md），但计划层（下一步是什么、何时执行）不持久
- 文章系列无任何跨 session 可见的进度 + 下一步指针
- 系统诊断 session 执行后，被确认的改进项无执行计划分解，只有"写入对应文件"这一步

**B2 标准锚点：** B2 Section 3（Plan-and-Execute）；B2 Section 2.3 收敛 B（Planner/Executor 拆分）

---

### 风险 2：agent 间状态传递无结构化协议 — "电话游戏"降级

**为什么严重：** 01_Routing.md 定义了 `cross_agent_required` flag，但无 payload schema。dump-processor → dashboard-updater 的 handoff 通过"调用 dashboard-updater agent + 传入参数"实现，参数格式隐含在各 agent 的文字描述里而非结构化 schema。scheduler.md L35-39 中 `replace_schedule` 和 `table` 字段也是约定而非合约。

**B2 标准锚点：** B2 Section 2.7（Handoff Pattern）——"Model chooses the wrong handoff target because tool descriptions are ambiguous"；B2 Section 6 Pattern vs Anti-Pattern（Handoffs via explicit transfer tool vs implicit context injection）

---

### 风险 3：工具结果无后处理 — context poisoning 潜在风险

**为什么严重：** shell-runner 读取文件后将原始内容返回主 session。当 job-search agent 读取 5 个知识文件时，fitness-coach 读取 7 个文件时，原始文本直接进入 context 窗口。当前文件体量尚可，但随系统增长（更多知识文件、更长 state.md）这是明确的恶化路径。

**B2 标准锚点：** B2 Section 4（Tool result post-processing）；Scenario D（Context Poisoning from Raw Tool Output）；DeerFlow SummarizationMiddleware 模式

---

## 3. Gap-by-Gap 候选方案

### Gap 1：持久化规划层缺失

**已知：** 仅 session-level TodoWrite，无跨 session 持久化计划

| Family | 方案 | 说明 |
|--------|------|------|
| **Redirective** | **R1：improvement-queue.md 扩展为 planning tracker** | 现有文件已有表格结构。在"待审批"之外增加"执行中"区块，每个审批通过的改进项在执行中区块展开为步骤+负责 agent+目标完成时间。零新文件，零新 agent。 |
| **Redirective** | **R2：82_Projects/ 文件夹标准化为 planning 层** | job-search.md 已经是有效的项目追踪文件。将 article-series.md、baseos-plan.md 等同样建立在 82_Projects/ 下，作为"跨 session 可见的执行计划"，各 agent prompt 读取对应 project 文件作为规划上下文。 |
| **Additive** | A1：新增 planning agent，专职维护跨 session 计划 | 增加 planner.md，在 system-diagnostics 之前运行，生成结构化计划 → 送 executor 执行。成本较高，引入新 agent 维护负担。**偏 Additive，标注。** |

**推荐：R2（Redirective）** — 82_Projects/ 已存在且结构已验证（job-search.md 证明有效），扩展比新建风险低。

---

### Gap 2：Planner/Executor 未分离（system-diagnostics）

**已知：** system-diagnostics.md 同时做"读取→分析→建议→执行"四步，违反 Planner/Executor 分离原则（B2 Section 3）；ACE 自评失真风险（master_synthesis.md L120-121）

| Family | 方案 | 说明 |
|--------|------|------|
| **Redirective** | **R3：system-diagnostics 加入 HITL 门作为 plan quality gate** | 当前第 4 步"生成改进建议"后已有"批量审批流程"。将此步骤明确标注为 Planner-phase 结束 + Executor-phase 开始，审批 = plan quality gate。文本修改，无新文件。 |
| **Substitutive** | S1：system-diagnostics 拆为 diagnostics-planner.md 和 diagnostics-executor.md | Planner 只做读取+分析+输出建议列表；Executor 只在审批通过后写入文件。两个 agent 职责分离，但需要更新 routing。 |
| **Reframing** | RF1：当前设计其实是 PGE 的"Human 作 Evaluator"变体 | Vincent 的审批本质上就是 Evaluator 角色。已有的批量审批流程（system-diagnostics.md L35-55）已经是 Plan-Evaluate-Execute 模式。真正的 gap 是 Planner 生成的计划质量无验证，不是结构缺失。 |

**推荐：RF1 + R3 组合** — 先在文档层明确"审批=Evaluator gate"语义，再在提示词中加入 plan quality 自检 checklist，成本最低，不引入新文件。

---

### Gap 3：agent 间 handoff 无结构化 payload

**已知：** dump-processor → dashboard-updater、scheduler → dashboard-updater 的参数传递是约定而非 schema

| Family | 方案 | 说明 |
|--------|------|------|
| **Redirective** | **R4：各 agent prompt 的"调用下游 agent"段改为结构化 JSON template** | 在 dump-processor.md Step 3、scheduler.md Step 4 中，将"调用 dashboard-updater"的描述改写为显式 JSON payload template（action / section / item 等字段）。已有字段名，只需格式化为合约。零新文件。 |
| **Redirective** | R5：在 01_Routing.md 的 cross-agent 编排规则段加入 payload schema 规范 | 当前 L38-40 描述了编排逻辑，加入标准 payload schema（source_agent / target_agent / action / params）作为所有 cross-agent call 的强制格式。 |
| **Additive** | A2：建立 agent-contracts.md，为每个 agent 定义 input/output schema | 参考 knowledge-agent.md 的返回格式定义（L66-69）将其推广。成本高，但一致性最强。**偏 Additive，标注。** |

**推荐：R4（Redirective）** — 改写现有描述段，约定升级为合约，修改量最小。

---

### Gap 4：工具结果无后处理

**已知：** shell-runner 原始返回进入 context；随知识文件增多风险上升

| Family | 方案 | 说明 |
|--------|------|------|
| **Redirective** | **R6：在各 agent prompt 的 Step 1 读取段加入 summary 指令** | 给 shell-runner subagent 的 prompt 中加入：读取文件后先提取关键字段（state、rule、constraint 类）再返回，非关键原文不传回主 session。在 fitness-coach.md、job-search.md 等高文件负载 agent 中先试行。 |
| **Redirective** | R7：shell-runner 本身加入 output budget 约束 | 在 CLAUDE.md 或 shell-runner 子 agent prompt 中加入通用规则："单次文件读取返回不超过 500 字符原文；超过则提取结构化摘要"。全局生效，一处配置。 |
| **Additive** | A3：新建 context-compressor agent，专职压缩长 context | 参考 DeerFlow SummarizationMiddleware。MeowOS 规模下过重，不推荐。**全 Additive，标注此 gap 下 A3 是孤立 additive 方案，优先选 redirective。** |

**推荐：R7（Redirective）** — CLAUDE.md 一条规则，全局覆盖，不需要改每个 agent prompt。

---

### Gap 5：路由语义覆盖不足（已知问题）

**已知：** improvement-queue.md L73-87 记录了"晚上爬了墙"未路由到 fitness-coach 的 bug；01_Routing.md 触发词为字面串

| Family | 方案 | 说明 |
|--------|------|------|
| **Redirective** | **R8：CLAUDE.md 加入语义域兜底规则（即 improvement-queue 选项 C）** | 加入硬约束：主 session 在字面触发词失配时，按语义主题域（具身活动/饮食/身体状态）路由到对应 agent。已有 improvement-queue 中的建议 C，直接采纳即可。 |
| **Substitutive** | S2：01_Routing.md 触发词扩展为正则/语义等价集合 | 用扩展词表替代字面串（爬墙/跑步/打球 → fitness-coach）。维护成本高，覆盖不完整。 |
| **Reframing** | RF2：路由失配本质是 intent parsing 失败，不是触发词不够多 | 解法不是加触发词，而是给主 session 加一步"意图 → 语义域分类"推理，分类后再查路由表。更健壮但需要 prompt 工程。 |

**推荐：R8（Redirective）** — 最短路径，已有 improvement-queue 建议 C 直接可用。

---

### Gap 6：context reset 协议缺失

**已知：** 无任何文件描述 context 耗尽的处理方式；digest-pipeline 的 Pass 1 串行设计可能部分解决了这个问题但未显式声明

| Family | 方案 | 说明 |
|--------|------|------|
| **Redirective** | **R9：在 CLAUDE.md 工作流段加入 context budget 自监控规则** | 当主 session 使用 ≥70% context 时，主动向 Vincent 提示"context 接近上限，建议开新 session 并告知我续接点"。利用已有的 CLAUDE.md 规则机制。 |
| **Redirective** | R10：long-running task 的子 agent 加入 checkpoint 写入约定 | 参照 digest-pipeline.md 的失败恢复设计（L60-65），要求所有多步 agent 在中间步骤写入 checkpoint 文件。现有 digest-pipeline 已是最佳实践，需推广为通用约定。 |
| **Additive** | A4：新建 session-handoff.md template，标准化跨 session 续接格式 | 定义续接文件格式（当前进度 / 待执行步骤 / context 摘要）。可行但增加维护成本。**偏 Additive，标注。** |

**推荐：R9 + R10 组合（均为 Redirective）** — R9 预防，R10 恢复；均利用已有机制。

---

### Gap 7：并行 agent 调度缺乏明确控制

**已知：** digest-pipeline.md Pass 1 为严格串行（L27 "严格串行，等完成再派下一个"）——此设计有理由（rate limit 控制）；其余 agent 无并行/串行策略声明

| Family | 方案 | 说明 |
|--------|------|------|
| **Redirective** | **R11：为各 agent prompt 加入"并行安全声明"** | 在每个 agent prompt 中加入一行：独立只读操作可并行；涉及同一文件写入必须串行。沿用 digest-pipeline 的设计模式，推广为规范。 |
| **Reframing** | RF3：MeowOS 规模下并行调度不是瓶颈 | 当前日均 agent 调用量小，串行够用。控制并行的价值在 high-volume 场景。现在过度设计此 gap。待规模扩大后再处理。 |

**推荐：RF3（Reframing）** — 当前规模不构成实际问题，标注为"观察中"而非立即行动项。

---

## 4. MeowOS 执行层已经做对的事情

### 4.1 shell-runner 原则 — 强
**证据：** CLAUDE.md L34-35；01_Routing.md L51；dump-processor.md L44；knowledge-agent.md L54；scheduler.md L52；job-search.md L122；dashboard.md L43
主 session context 隔离是跨所有 agent 一致执行的原则，覆盖率接近 100%。这是 MeowOS 执行层最突出的工程优势，与 B2 Section 4（工具结果后处理）方向一致，且早于研究结论独立实现。

### 4.2 HITL 确认门 — 日程/Dump 场景覆盖良好
**证据：** scheduler.md L32-34（"必须等 Vincent 确认"）；dump-processor.md Step 2-3（逐条询问）；dashboard.md L46（"日程未经 Vincent 确认不写入"）
高风险写入（Dashboard 日程修改、Todo 归属）均有 HITL 门，与 B2 Section 5（HITL trigger heuristics）的"不可逆动作前停止"原则匹配。

### 4.3 失败恢复 — digest-pipeline 是最佳实践样本
**证据：** digest-pipeline.md L60-65（明确的 5 步失败恢复树）
这是 MeowOS 内唯一实现了 B2 Section 5（Retry strategies + Failure classification）的组件，且分类精细（pending Pass 1 未完成 / Pass 2 未跑 / Pass 3 未跑 / update_watermark 未跑 — 四种独立状态）。可作为其他 agent 的 failure recovery 模板。

### 4.4 工具描述质量 — 符合 B2 规范
**证据：** 所有 agent prompt 均包含：触发词（when to use）、禁止行为（when NOT to use）、返回格式（return semantics）；knowledge-agent.md L66-69 有完整 return schema
符合 B2 Section 4（"What good descriptions contain"）的 5 个要素中的 4 个（缺失 error behavior 声明为弱项）。

### 4.5 路由层 — 明确的 intent → agent 映射
**证据：** 01_Routing.md 覆盖 20+ 触发词 + cross-agent 编排规则 + 冲突解决规则（L47-49）
相比无路由层的系统，MeowOS 的单一路由文件将调度逻辑集中管理，减少了散布在 CLAUDE.md 中的 if-else 式规则积累。符合 B2 Section 2.7（Handoff Pattern）中"每个 agent 应有清晰的 handoff_description"原则。

### 4.6 MCP 暴露极度克制
**证据：** settings.json L285-294：仅 ms365 一个 MCP server
与 B2 Section 4（"300+ tools → 62% accuracy"）形成对比，MeowOS 的 MCP 选择精准，避免了工具泛滥问题。

---

## 5. 无法审计的内容

| 项目 | 原因 |
|------|------|
| **00_Dump/Done/ 中的 session artifacts** | 目录存在但无法获取文件列表（bash 输出为空），无法检查实际 orchestration 产物 |
| **shell-runner subagent 实际执行一致性** | shell-runner 是约定而非代码实现；无法验证每次实际调用是否遵循委派原则，存在"声明合规但执行偏移"的风险 |
| **skill 文件完整集合** | 仅读取了 dashboard.md / digest-pipeline.md / wa-sync.md；dream-walking / people-interview 目录未详读，可能有额外执行层特性 |
| **agent 调用频率与真实 context 消耗** | 无实际 session log 样本（Done/ 目录不可读），无法评估 context 压力的实际水位 |
| **ms365 MCP 实际使用范围** | settings.json 配置了 ms365 MCP 但未找到任何 agent prompt 描述何时使用它，可能存在未记录的使用方式 |

---

## 候选方案汇总索引

| ID | Family | Gap | 推荐度 |
|----|--------|-----|--------|
| R1 | Redirective | Gap 1（规划持久化） | 备选 |
| **R2** | **Redirective** | **Gap 1（规划持久化）** | **首选** |
| A1 | Additive | Gap 1 | 低（⚠️ 孤立 Additive 待检）|
| R3 | Redirective | Gap 2（Planner/Executor）| 推荐组合之一 |
| S1 | Substitutive | Gap 2 | 备选 |
| **RF1+R3** | **Reframing+Redirective** | **Gap 2** | **首选组合** |
| **R4** | **Redirective** | **Gap 3（handoff schema）** | **首选** |
| R5 | Redirective | Gap 3 | 备选 |
| A2 | Additive | Gap 3 | 低（⚠️ 偏 Additive）|
| **R7** | **Redirective** | **Gap 4（工具后处理）** | **首选** |
| R6 | Redirective | Gap 4 | 备选 |
| A3 | Additive | Gap 4 | 低（⚠️ 孤立 Additive，不推荐）|
| **R8** | **Redirective** | **Gap 5（路由语义）** | **首选** |
| S2 | Substitutive | Gap 5 | 备选 |
| RF2 | Reframing | Gap 5 | 备选 |
| **R9+R10** | **Redirective** | **Gap 6（context reset）** | **首选组合** |
| A4 | Additive | Gap 6 | 低（⚠️ 偏 Additive）|
| RF3 | Reframing | Gap 7（并行调度）| 当前规模推荐 |
| R11 | Redirective | Gap 7 | 规模扩大后考虑 |

**总计：** 19 个候选方案；其中 Additive 3 个（A1/A2/A3），均已标注 ⚠️。Redirective 为主要推荐家族（10 个），符合审计偏向原则。

---

*audit_B2_execution.md — Audit-B2 subagent — 2026-04-14*
