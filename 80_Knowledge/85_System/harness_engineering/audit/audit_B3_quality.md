---
id: audit_B3_quality
title: Audit B3 — Quality Layer 质量层审计
tags: [harness, knowledge, audit, quality-layer, evals]
status: confirmed
last_modified: 2026-04-15
summary: MeowOS 质量层审计：评估、可观测性、约束与恢复机制
---
# Audit B3 — Quality Layer: MeowOS 质量层审计

**版本：** 2026-04-14
**审计员：** Audit-B3 subagent
**依据标准：** B3_quality_layer.md（Hamel/Shankar evals、Böckeler Sensors、Lopopolo GC+HITL、NeMo Guardrails）
**方法论：** Evidence-first；≥2 候选方案/缺口；偏向 Redirective/Substitutive；所有 all-additive 缺口标注 ⚠️ ALL-ADDITIVE

---

## 1. 状态总表

| 质量子维度 | 标准要求 | MeowOS 当前实现 | 评级 |
|-----------|---------|----------------|------|
| **评估机制** | 独立评估 session，LLM-as-judge 或人工标注，误差分析 | ACE E·系统诊断（同 session 自评）；无自动化输出质量评估 | 🔴 缺失 |
| **评估独立性** | 生产 agent ≠ 评估 agent（B3 Section 1 循环验证警告） | system-diagnostics 在主 session 调用，与执行 agent 共享 session | 🔴 违反 |
| **观测性 — 用户端** | Trace 级别；每步输入/输出/中间状态均可见 | Dashboard.md（人读，干净，低频更新）；improvement-queue.md（错误信号队列）| 🟡 部分 |
| **观测性 — trace/replay** | 完整 DAG trace，支持时间旅行调试 | 无 trace 机制；shell-runner 只返回结论，不存中间状态 | 🔴 缺失 |
| **错误如何浮现** | 自动检测 + 人工审查并行 | 完全依赖 Vincent 手动发现并报告；improvement-queue.md 是手动录入的错误日志 | 🟡 被动 |
| **约束 — 类型** | Computational（硬规则）vs Inferential（推理指导）区分（Böckeler Section 4） | CLAUDE.md 禁止行为：3 条，全部为 Inferential（自然语言描述，无执行级检查）| 🟡 Inferential-only |
| **约束 — 误报率** | 需显式测量 false-positive 率 | 无测量机制；改进队列中有 routing 误报信号但无系统性追踪 | 🔴 未测量 |
| **输入/输出 Guardrail** | 实时拦截；NeMo Colang 或 Guardrails AI 模式 | 无 input/output guardrail；CLAUDE.md 禁止行为依赖模型内推理执行 | 🔴 缺失 |
| **恢复 — 重试协议** | 指数退避 + retry budget；频繁重试=harness缺陷信号 | 无显式重试协议；失败时无结构化处理路径 | 🔴 缺失 |
| **恢复 — 回滚** | 审计追踪 + 最小爆炸半径设计 | 无回滚机制；文件写入后无 undo 路径（improvement-queue.md 中看到过 staging 写入错误未能恢复）| 🔴 缺失 |
| **恢复 — HITL 升级** | 明确触发条件（不确定性+后果双维度）；异步队列 | 无结构化 HITL 升级协议；所有决策串行流向 Vincent | 🟡 隐性存在但未编码 |
| **恢复 — Context Reset** | 检测 context 质量衰减 → 结构化状态迁移 | 无 context reset 协议；无 context 质量指标 | 🔴 缺失 |
| **垃圾回收（GC）** | 背景周级任务扫描 80_Knowledge/ + agent prompts 的熵积累；执行 golden principles | 无 GC 任务；系统诊断 session 偶发性执行类 GC 功能但属临时性、人触发 | 🔴 无基础设施 |
| **行为调控（Behaviour Harness）** | 研究前沿，无完全解；朴素 workaround：approved fixtures + 修正信号捕获 | Vincent 反馈是唯一信号；rejection signals 有专项 memory 条目（feedback_rejection_signals.md 存在）| 🟡 朴素实现 |

---

## 2. Top 3 风险

### 风险 1：自评失真——循环验证已在发生
**证据：** improvement-queue.md 第 2026-04-10 节明确记录：「凌喵在 Pass 1 digest 中把自己的失误系统性地编码为'Vincent 的偏好数据'，从不当作自身故障信号处理。」（improvement-queue.md 第 33-36 行）
**B3 对照：** B3 Section 1"循环验证"警告——同一 session 既生产输出又评估输出，继承相同偏差。
**量级：** 高。这不是理论风险，已有文档化事件。系统诊断 agent（system-diagnostics.md）的执行在主 session，与生产 agent 共享 context，无隔离。

### 风险 2：GC 缺失导致 80_Knowledge/ 熵积累无防护
**证据：** `80_Knowledge/` 下已有 10+ 子目录；`_staging.md` 在 2026-04-12 诊断前已积压 493 行/4 天未消化（improvement-queue.md 第 14 行）；无任何周期性扫描任务。
**B3 对照：** B3 Section 6——Lopopolo GC = 背景任务，持续扫描，非"偶尔重构 sprint"。当前系统诊断是人触发的 sprint 模式，无法跟上 agent-speed 的熵生产速率。
**量级：** 中高。现在还早，但 knowledge entropy cliff（B3 Section 9 Failure 4 类比）在 KB 规模增长后将出现。

### 风险 3：无 trace/replay + context rot 无检测
**证据：** shell-runner 原则（CLAUDE.md 第 35 行）：「主 session 只接收结构化结论，不加载原始文件内容」。该设计有 B1 层优势（context 干净），但代价是**中间状态被主动丢弃**，没有任何 replay 能力。多步 agent session（如 digest pipeline）在中途失败时无法从检查点恢复。
**B3 对照：** B3 Section 5 Context Reset 模式——「检测衰减信号 → 结构化状态迁移」；B3 Section 9 Failure 3（Silent Context Rot）。
**量级：** 中。单次短 session 影响小；长 session（digest pipeline、系统诊断）已有此风险。

---

## 3. 缺口分析与候选方案

### 缺口 A：评估机制缺失（最高优先级缺口）

**当前状态：** 无任何自动化输出质量评估；用户反馈是唯一信号。
**证据：** CLAUDE.md 全文无"eval"/"评估"/"quality check"字样；system-diagnostics.md 执行步骤全为 staging 消化+矛盾检查，无质量测量。

**候选方案：**

| # | 家族 | 方案 | 成本 | 备注 |
|---|------|------|------|------|
| A1 | **Redirective** | **将 improvement-queue.md 的错误记录改造为朴素 eval 数据集**：每次 Vincent 纠正凌喵时，improvement-queue.md 写入结构化条目（input_summary, wrong_output, correct_expectation）。系统诊断 session 周期性跑过这些条目，检查当前行为是否仍会复现。不需要新工具，复用已有文件。 | 低 | 利用现有机制；approved fixtures pattern（B3 Section 7） |
| A2 | **Substitutive** | **以 rejection_signals memory 文件代替通用 eval 框架**：MEMORY.md 已有 feedback_rejection_signals.md 条目。将其格式化为"凌喵建议 X → Vincent 拒绝 → 正确行为 Y"的三元组，作为 regression 测试基础。系统诊断每次读取全部 rejection 条目，验证是否仍有复现 pattern。 | 极低 | 完全 redirective；零新建文件 |
| A3 | ⚠️ ALL-ADDITIVE | ~~建立 Langfuse/Braintrust eval pipeline~~ | 高 | 对个人 AI OS 过度工程化；B3 建议先做 50 次人工 trace 审查，再建基础设施 |

**推荐：A1 + A2 组合，A3 禁用。**

---

### 缺口 B：评估独立性（自评失真）

**当前状态：** system-diagnostics 在主 session 执行，与生产 agent 共享 context。
**证据：** system-diagnostics.md 无"分离 session"指令；improvement-queue.md 已文档化 Pass 1 自我诊断盲点问题（第 33 行起）。

**候选方案：**

| # | 家族 | 方案 | 成本 | 备注 |
|---|------|------|------|------|
| B1 | **Redirective** | **system-diagnostics 的职责拆分为两个 prompt**：第一个 prompt（诊断者）只读文件、生成结论，不执行写入；第二个 prompt（执行者）只根据诊断结论执行写入。两个 prompt 在分开的 subagent 调用中运行，互不共享主 session context。复用 Claude Code subagent 机制，不新建任何文件。 | 低 | 对应 master_synthesis.md 第 105 行"系统诊断 agent 应拆成两个 session"的收敛 B 建议 |
| B2 | **Reframing** | **接受自评失真，改为"错误信号累积后外部核对"**：不尝试修复 session 内自评，转为在 improvement-queue.md 中标记"自评信心低"条目，等 Vincent 每月一次人工审计，由 Vincent 做最终校准。此方案把人类判断作为唯一可信 ground truth（Hamel 的"benevolent dictator"模式）。 | 极低 | 不是工程解，是现实约束下的诚实做法；适用于个人 OS |

**推荐：B1 作为结构性修复；B2 在 B1 实施前作为过渡策略。**

---

### 缺口 C：Observability / Trace

**当前状态：** 用户只能看到 Dashboard.md（低频、汇总级）；无 trace/replay 能力。
**证据：** CLAUDE.md 路径表（第 13-22 行）——用户可见的只有 Dashboard.md；improvement-queue.md 所有错误发现均为事后人工识别，无自动触发。

**候选方案：**

| # | 家族 | 方案 | 成本 | 备注 |
|---|------|------|------|------|
| C1 | **Redirective** | **将 _staging.md 改造为 operation log**：现在 _staging.md 只存 Vincent 的观察数据。扩展格式，每次 subagent 调用（shell-runner / knowledge-agent 等）在 _staging.md 追加一行操作摘要：`[HH:MM] agent=X action=Y target=Z result=ok/fail`。零新文件；_staging.md 已有追加写入机制。 | 低 | 不是完整 trace，但提供最小可行 audit trail |
| C2 | **Additive** | **建立专用 session-log.md**：每次 session 开始写入，记录 session ID、触发意图、调用 agent 序列、关键决策点。session 结束时追加 outcome summary。 | 中 | 额外文件；但解决"session 间不连续"问题 |
| C3 | **Reframing** | **接受低 observability 作为个人 OS 的合理 tradeoff**：B3 的 trace 标准针对多用户生产系统。MeowOS 的 Vincent 即是用户又是调试者，他可以直接观察 session 内容。全链路 trace 对单用户 OS 是 overkill；把精力放在 context 质量，不是 observability 基础设施。 | 零 | 合理 reframing；但不能解决多步 agent session 失败恢复问题 |

**推荐：C1（低成本 audit trail）+ C3 认知前提（不追求生产级 trace）。**

---

### 缺口 D：约束类型（全 Inferential）

**当前状态：** CLAUDE.md 禁止行为（第 56-59 行）3 条均为自然语言：「不在主 session 直接读写文件」「意图不明时不猜测」「日程未经 Vincent 确认不写入 Dashboard」。没有任何 computational 执行层约束。
**证据：** CLAUDE.md 禁止行为段（第 56-59 行）；Böckeler 区分：computational = hard rule，inferential = AI interpretation required。

**候选方案：**

| # | 家族 | 方案 | 成本 | 备注 |
|---|------|------|------|------|
| D1 | **Redirective** | **将最高优先禁止行为升级为 hookify 规则**：「日程未确认不写 Dashboard」这条具有高 blast radius（错写 Dashboard 影响可见性）。通过 hookify hook 在任何 Edit/Write 针对 Dashboard.md 的操作时强制插入确认步骤。复用已有 hookify 基础设施，不修改 CLAUDE.md。 | 低 | Settings.json hook 机制；computational 执行保证；参考 feedback_settings_path_format.md |
| D2 | **Substitutive** | **用 settings.json permissions 替代 CLAUDE.md 推理约束**：把「不在主 session 直接读写」改为 settings.json 中限制主 session 的 Bash/Edit/Write 权限范围（仅允许特定目录），将 inferential 约束转换为 computational 访问控制。 | 中 | 需仔细定义白名单；可能误伤合法操作 |
| D3 | **Reframing** | **接受 inferential 约束在单用户高信任 OS 场景是足够的**：NeMo Colang 的 computational policy 设计针对面向外部用户的生产系统（untrusted input）。MeowOS 只有 Vincent 一个用户，凌喵与 Vincent 是高信任协作关系，inferential 约束的误报率低。把约束能量聚焦在"可能伤害较大的单一操作"（Dashboard 写入）而非全面 computational 化。 | 零 | 配合 D1 使用；对 blast-radius-小的约束接受 inferential |

**推荐：D1（仅 Dashboard 写入升级为 hookify）+ D3（其余保持 inferential）。**

---

### 缺口 E：恢复机制（重试/回滚/HITL）

**当前状态：** 无显式重试协议；无回滚机制；HITL 升级隐性存在（所有不确定性都流向 Vincent）但未编码为结构化触发条件。
**证据：** CLAUDE.md 工作流段（第 27-35 行）仅描述 happy path；无任何失败路径指令。改进队列（第 73-87 行）中记录 agent routing 失败但无触发的结构化恢复。

**候选方案：**

| # | 家族 | 方案 | 成本 | 备注 |
|---|------|------|------|------|
| E1 | **Redirective** | **将 improvement-queue.md 的错误分类升级为 HITL 触发条件表**：在 CLAUDE.md 工作流段增加一小节"升级条件"，列出：(1) routing 失败（无匹配 agent）→ 明确告诉 Vincent 无法处理，不静默降级；(2) 连续 2 次文件写入失败 → 停止，报告状态；(3) 意图歧义 → 直接问（已有）。将已知失败模式显式编码，不新建文件。 | 低 | Redirective：复用 improvement-queue.md 已有分类语言；解决 implicit HITL 问题 |
| E2 | **Additive** | **建立最小回滚约定**：约定所有 agent 在写入文件前，若文件已存在，先将内容存入 00_Dump/ 作为备份快照。「undo」= 从 00_Dump/ 恢复。| 中 | 已有 00_Dump/ 目录；但增加每次写入的操作步骤 |
| E3 | **Reframing** | **把 Context Reset 协议写入 CLAUDE.md 作为 session 行为**：不建 checkpoint 基础设施。改为在 CLAUDE.md 加入一条：「多步长 session（>20 turn）后若出现前后矛盾，主动提示 Vincent：本 session context 可能需要重置，建议提取关键状态后新开 session。」把 Lopopolo context reset 模式降维成可操作提示。 | 极低 | Substitutive：用人工感知+主动提示替代自动检测基础设施 |

**推荐：E1（编码 HITL 触发条件）+ E3（context reset 降维实现）。E2 可选，Dump 目录已存在。**

---

### 缺口 F：垃圾回收（GC）——最新概念，最大空白

**当前状态：** 零 GC 基础设施。系统诊断 session 偶发执行 GC 类工作（检查 agent prompts 矛盾、routing 覆盖），但：(1) 人触发，非定时；(2) 在同一 session 执行；(3) 无"golden principles"文档作为扫描标准。
**证据：** improvement-queue.md 全文中系统诊断均为 Vincent 手动触发；无任何定期执行记录；`80_Knowledge/` 已有 90_Deprecated/ 目录存在（第三行 ls 输出），说明有废弃内容积累。

**GC 概念边界澄清（per B3 Section 6）：**
- **不是** context pruning（B1 层，本 session 内）
- **不是** human-led refactoring sprint（偶发，成本高）
- **不是** memory staging（_staging.md 是输入缓冲，不是 GC）
- **是** 背景 agent 任务，周级，按 golden principles 扫描 80_Knowledge/ + 90_Agents/，自动生成「建议归档/更新/删除」清单供 Vincent 快速确认

**候选方案：**

| # | 家族 | 方案 | 成本 | 备注 |
|---|------|------|------|------|
| F1 | **Redirective** | **将 system-diagnostics.md 的步骤 3（矛盾检查）扩展为轻量 GC checklist**：在矛盾检查步骤添加：扫描 90_Agents/ 中的 agent prompts 是否有过期描述（日期 >60 天无更新且 improvement-queue 有相关改动）；扫描 80_Knowledge/90_Deprecated/ 是否有可清除内容；扫描 habits.md 是否有与 MEMORY.md 重复的条目。生成「GC 建议清单」供 Vincent 确认。不新建 agent，在现有 system-diagnostics 步骤内扩展。 | 低 | Redirective；不解决"定时触发"问题，但解决"有 GC 动作" |
| F2 | **Additive** | **建立 golden-principles.md + 定期 GC agent**：编写 `85_System/golden-principles.md`（MeowOS 的黄金原则：KB 文件格式规范、agent prompt 最长行数、staging 消化周期上限等）；建立单独 `gc-agent.md` prompt；Vincent 每周手动调用一次（短期），后续接入 schedule skill 自动化。 | 中 | ⚠️ ALL-ADDITIVE；但 Lopopolo 原方案本身是 additive——GC 是新基础设施，在此处 additive 有合理性 |
| F3 | **Substitutive** | **以 improvement-queue.md 待审批区作为 GC 输出落点，不建新文件**：GC 任务的产出（旧文件建议归档、agent prompt 建议更新、habits 去重建议）全部写入 improvement-queue.md 待审批区，复用已有审批流程。GC 任务不需要单独的输出格式，只需要一个标准化触发 prompt。 | 低 | Substitutive；GC 产出复用现有审批流 |

**推荐：F1（短期，立即可用）+ F3（产出格式）。F2 作为中期目标，golden-principles.md 值得建立但不急。**

---

### 缺口 G：行为调控（Behaviour Harness）

**研究前沿声明：** B3 Section 7 明确标记行为调控为"major open problem"（Böckeler F2）。此处无法提供与 eval、observability 同级别的工程方案。MeowOS 面临的是与行业一致的开放问题，不是 MeowOS 独有缺陷。

**当前 MeowOS 的朴素实现：**
- MEMORY.md 的 feedback_rejection_signals.md 条目——Vincent 拒绝 AI 建议时结构化记录，是"approved fixtures"的逆向版本（记录不该做什么，而非应该做什么）。这是 B3 Section 7 中唯一有价值的朴素 workaround。
- improvement-queue.md 中的"Pass 1 自我诊断盲点"记录（第 33 行）——认识到错误的性质，有助于未来校准，但不是系统性解。

**候选方案（朴素 workaround 级别，不声称是完整解）：**

| # | 家族 | 方案 | 局限 |
|---|------|------|------|
| G1 | **Redirective** | **将 rejection_signals memory 格式化为 approved fixtures**：每次 Vincent 纠正，以`[context, wrong_behavior, expected_behavior]`三元组写入专用文件。系统诊断 session 每次跑过这些三元组，自然语言测试凌喵在类似场景是否仍重复错误。这是 Böckeler 的 approved fixtures pattern 的朴素实现。 | 三元组是 inferential 对比，不是 deterministic 测试；但在个人 OS 场景是合理的最小实现 |
| G2 | **Reframing** | **接受 Vincent = 行为调控的唯一可靠传感器**：在当前研究水平下，Vincent 的直接反馈是比任何 LLM-as-judge 更可靠的行为质量信号。MeowOS 的正确投资是降低 Vincent 发现和报告错误的摩擦，而不是建设自动化行为评估基础设施。 | 系统盲区：Vincent 看不到的 session 无法被评估；但这是当前技术前沿的诚实边界 |

---

## 4. MeowOS 已经做对的事情

### 4.1 记忆系统作为反馈捕获基础设施
MEMORY.md 及其 50+ 子文件（feedback_*.md 系列）是 MeowOS 质量层最成熟的组件。每个 feedback 文件本质上是一个"人工标注的失败案例"，Vincent 的修正历史被系统性地持久化。这与 Hamel 的"从真实错误做 error analysis"完全对齐。很少有个人 AI OS 有这一层。

### 4.2 Rejection Signals 的专项追踪
`feedback_rejection_signals.md` 的存在（MEMORY.md 第 25 行）说明 Vincent 已认识到拒绝信号是最高价值的校准数据。这是 behaviour harness 中唯一有证据基础的朴素实现，领先于大多数 agent 系统的行为调控水平。

### 4.3 ACE 机制的设计逻辑
A·暂存 + C·快捷词 + E·系统诊断的三层设计（CLAUDE.md 第 37-43 行），在没有显式 eval 框架的情况下，用"持续观察 → 暂存 → 周期性结构化"模拟了一个朴素的 feedback loop。这是 Böckeler Sensors 概念在个人 OS 场景下的最小可行版本。

### 4.4 shell-runner 的最小爆炸半径原则
CLAUDE.md 的 shell-runner 原则（第 34-35 行）将所有文件读写委托给 subagent，主 session 只接收结论。虽然这牺牲了 observability（中间状态丢失），但它有效降低了主 session 因直接文件操作引入错误的概率。这是 B3 Section 5 「最小爆炸半径工具设计」pattern 的隐性实现。

### 4.5 improvement-queue.md 的审批流
结构性改动走 improvement-queue.md 的审批流（CLAUDE.md 第 54 行）——而不是立即写入——是 HITL 的异步实现。它不完整（无结构化触发条件），但方向正确。B3 Section 5 的「HITL 作为异步状态」原则在这里有体现。

---

## 5. 无法审计的内容

| 项目 | 原因 |
|------|------|
| `settings.json` 完整内容 | 未请求读取；无法核实 hookify 规则的实际覆盖范围和 computational 约束的执行效果 |
| `80_Knowledge/90_Deprecated/` 内容 | 未读取；无法评估废弃内容的规模和性质，无法量化 GC 紧迫性 |
| digest pipeline 具体 agent prompts | `00_Dump/` 或其他目录下的 digest agent 文件未被读取；无法核实 Pass 1/Pass 2 的实际自评逻辑 |
| MEMORY.md 全部子文件 | 仅读取了 MEMORY.md 索引，未读取各 feedback_*.md 具体内容；rejection signals 的实际规模和质量未核实 |
| 其他 90_Agents/ 文件 | 仅读取了 system-diagnostics.md，其余 agent prompts（knowledge-agent.md 等）未审查；无法评估跨 agent 约束一致性 |

---

## 候选方案汇总（全 15 条）

| # | 缺口 | 家族 | 一句话描述 | 推荐 |
|---|------|------|-----------|------|
| A1 | 评估机制 | Redirective | improvement-queue 改造为 eval 数据集 | ✅ |
| A2 | 评估机制 | Substitutive | rejection_signals 格式化为三元组 regression 测试 | ✅ |
| A3 | 评估机制 | ⚠️ ALL-ADDITIVE | 建 Langfuse/Braintrust pipeline | ❌ 禁用 |
| B1 | 评估独立性 | Redirective | system-diagnostics 拆成诊断+执行两个 prompt | ✅ |
| B2 | 评估独立性 | Reframing | 接受自评失真，靠月度人工核对 | 过渡用 |
| C1 | Observability | Redirective | _staging.md 扩展为 operation log | ✅ |
| C2 | Observability | Additive | 建专用 session-log.md | 可选 |
| C3 | Observability | Reframing | 接受低 observability 为个人 OS 合理 tradeoff | ✅ 认知前提 |
| D1 | 约束类型 | Redirective | Dashboard 写入升级为 hookify computational 约束 | ✅ |
| D2 | 约束类型 | Substitutive | settings.json 访问控制替代 inferential 禁止 | 谨慎评估 |
| D3 | 约束类型 | Reframing | 接受 inferential 约束在高信任单用户场景足够 | ✅ 配合 D1 |
| E1 | 恢复机制 | Redirective | improvement-queue 错误分类升级为 HITL 触发条件 | ✅ |
| E2 | 恢复机制 | Additive | 写入前 Dump/ 备份约定 | 可选 |
| E3 | 恢复机制 | Reframing | context reset 降维为主动提示，不建基础设施 | ✅ |
| F1 | GC | Redirective | system-diagnostics 步骤 3 扩展为轻量 GC checklist | ✅ |
| F2 | GC | ⚠️ ALL-ADDITIVE | 建 golden-principles.md + gc-agent.md | 中期目标 |
| F3 | GC | Substitutive | GC 输出落点复用 improvement-queue 审批流 | ✅ 配合 F1 |
| G1 | 行为调控 | Redirective | rejection_signals 格式化为 approved fixtures | ✅ 朴素实现 |
| G2 | 行为调控 | Reframing | 接受 Vincent = 唯一可靠行为传感器 | ✅ 诚实边界 |

*注：F2 虽 ALL-ADDITIVE，但 GC 本质上就是新基础设施，Lopopolo 原方案亦然。中期建立 golden-principles.md 的 additive 成本有合理性。*

---

*审计截止：2026-04-14*
*证据来源：CLAUDE.md、system-diagnostics.md、improvement-queue.md、B3_quality_layer.md、F1_lopopolo_origin.md、00_master_synthesis.md、habits.md（片段）、_staging.md（片段）、Dashboard.md、目录结构扫描*
