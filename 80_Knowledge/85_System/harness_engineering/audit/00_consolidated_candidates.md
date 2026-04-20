---
id: 00_consolidated_candidates
title: 系统改进候选合并报告
tags: [harness, knowledge, audit, improvement, system-meta]
status: confirmed
last_modified: 2026-04-15
summary: 三层审计合并候选清单，待 Vincent 审批后写入 improvement-queue
---
# 00_consolidated_candidates.md
**版本：** 2026-04-14
**合成人：** Synthesis agent（独立 session，非凌喵主 session）
**依据：** audit_B1_information.md / audit_B2_execution.md / audit_B3_quality.md + 00_master_synthesis.md
**待 Vincent 审批后方可写入 improvement-queue.md**

---

## Section 1：Top-line Synthesis（≤200字）

三份审计集体呈现一个清晰模式：**MeowOS 的信息架构层（B1）是强项，执行层（B2）和质量层（B3）存在结构性空白，且两者的空白高度重叠**。

具体而言：filesystem memory、shell-runner 委派、improvement-queue 审批流、路由层集中管理——这四件事 MeowOS 独立做出了与行业收敛方向完全一致的选择，且早于研究结论。这是真实的工程判断优势，不是偶然。

但同一套设计在质量层暴露了代价：shell-runner 委派让主 session 干净，但中间状态被主动丢弃，replay 能力为零；ACE 机制设计精良，但触发范围过宽 + 无去重，导致 staging 积压；system-diagnostics 是 GC 的唯一出口，但诊断者和执行者是同一个 session，自评失真已有文档化证据。

核心结论：**MeowOS 的 harness 成熟度处于"设计意图超前、执行保障滞后"的状态**。最高价值修复全部是 redirective（调整已有机制），没有一项需要从零建设。

---

## Section 2：Cross-Layer Themes（跨层主题）

以下问题在 2 个或以上审计层中独立出现，是最高信号发现。

### Theme A：system-diagnostics 的"裁判+运动员"问题
- **B2** Gap 2：system-diagnostics 同时做诊断+建议+执行，违反 Planner/Executor 分离。
- **B3** 缺口B：system-diagnostics 在主 session 执行，与生产 agent 共享 context，循环验证已发生（improvement-queue.md 第33行：「凌喵把自己的失误编码为 Vincent 的偏好数据」）。
- **00_master_synthesis.md** 第120行收敛E直接点名：「MeowOS 的 ACE 自评机制存在自评失真风险，诊断和执行要分 session」。
- **结论：** 三层 + master_synthesis 四方独立收敛，这是最高优先级 cross-layer 问题。

### Theme B：Task State 跨 session 断裂
- **B1** Gap 2：Task State（任务进度、失败历史）无独立容器，跨 session 状态丢失。
- **B2** Gap 1：持久化规划层缺失，多 session 项目（HBR/LinkedIn、求职、BaseOS）目标漂移。
- **结论：** 两层从不同切角描述同一根因——任务中间状态没有持久化落点。

### Theme C：Context Reset 无协议
- **B1** Gap 4：长 session 无 compaction 触发，指令飘移风险随轮次递增。
- **B2** Gap 6：无 context 耗尽处理方式；context reset 协议完全缺失。
- **B3** 缺口E/风险3：shell-runner 丢弃中间状态，无 replay 能力；多步 session 失败无恢复路径。
- **结论：** 三层均覆盖，且有具体失败场景（digest pipeline 中途中断）。

### Theme D：ACE staging 写入无去重 + GC 缺位
- **B1** Gap 6：staging 写入触发范围过宽，无合并/去重步骤；improvement-queue 第14行已记录 staging 积压 493行/4天。
- **B3** 缺口F：零 GC 基础设施；系统诊断是唯一出口但属临时性人触发。
- **结论：** 已有文档化的熵积累证据，修复路径一致（扩展 system-diagnostics 步骤）。

### Theme E：HITL 触发点不均匀
- **B2** Gap 2/6：仅 scheduler 和 dump-processor 有 HITL 门，其余 agent 无系统性 HITL 约束。
- **B3** 缺口E：HITL 升级隐性存在但未编码为结构化触发条件；routing 失败时无明确上报路径。
- **结论：** 高风险写入（Dashboard）已有 HITL，但故障场景（routing 失败、文件写入失败）没有结构化上报协议。

---

## Section 3：Ranked Candidate List

> **已在 improvement-queue.md 的条目（不重复）：**
> - routing 语义兜底（选项C）— 已记录 2026-04-13
> - staging 积压频率提醒 — 已记录 2026-04-12
> - digest pipeline 中文切换 — 已记录 2026-04-11
> - Pass 1 自我诊断盲点（区分错误信号 vs 偏好数据）— 已记录 2026-04-10

---

### SYN-001
**Title：** system-diagnostics 拆分为诊断 subagent + 执行 subagent，解除自评失真
**Source：** Cross（B2 Gap2 + B3 缺口B + master_synthesis 收敛E）

**Gap：** system-diagnostics.md 当前在同一 session 内完成读取→分析→建议→写入全流程，与被评估的生产 agent 共享 context，自评失真已有文档化事件（improvement-queue.md 第33-36行：「凌喵把失误编码为 Vincent 偏好数据」）。master_synthesis.md 第105行明确建议拆成两个 session。

**Recommended Solution + Family（Redirective）：**
将 system-diagnostics.md 当前第4步"生成改进建议"处插入一个明确的 phase 边界：Phase 1（诊断 subagent）= 只读文件+生成候选清单，不执行写入；Phase 2（执行 subagent）= 只在 Vincent 审批后执行写入。两个 phase 以分开的 subagent 调用运行，利用 Claude Code 已有的 subagent 机制，不新建文件。

**Alternative Considered（Reframing）：**
B3 B2 方案——承认 Vincent 的审批本质上已是 Evaluator gate，当前设计是"Human 作 Evaluator"的变体，够用。局限：这个 reframing 无法解决 Pass 1 阶段的自评失真（审批发生在 Pass 1 之后，失真已经写入）。

**Why This One：** 已有文档化失败，不是理论风险。Phase 边界修复的是失真发生点（Pass 1），而非结果清理。Redirective：完全复用现有 subagent 机制，不新建文件。

**Priority：高**（已发生的文档化失败 + cross-layer + master_synthesis 直接点名）
**Effort：** 半天（修改 system-diagnostics.md prompt，拆分 phase 边界）
**Blast Radius：低**（只改 system-diagnostics 内部流程，不影响其他 agent）
**Evidence Strength：** 文档化失败（improvement-queue.md 第33-36行）

---

### SYN-002
**Title：** 82_Projects/ 标准化为跨 session 任务规划层，补齐 Task State 容器
**Source：** Cross（B1 Gap2 + B2 Gap1）

**Gap：** 三类状态（session/task/long-term）中 Task State 无独立容器。job-search.md 证明 82_Projects/ 格式有效（B2 Gap1 audit_B2_execution.md 第70行），但 article-series、BaseOS 等多 session 项目无等价规划文件，跨 session 进度不持久（B1 Gap2：Dashboard.md 的 Todo 混合了长期待办和临时状态，是人读而非凌喵读的结构）。

**Recommended Solution + Family（Redirective）：**
以 job-search.md 为模板，为当前活跃的多 session 项目（article-series、baseos-plan 等）在 82_Projects/ 下建立等价文件：包含进度、下一步指针、已排除路径。各 agent prompt 读取对应 project 文件作为规划上下文，不建新 agent，不建新目录。

**Alternative Considered（Redirective-B）：**
B1 Candidate A——复用 00_Dump/ 建 Tasks/ 子目录。局限：Dump 语义是"输入暂存"，Task State 语义是"执行追踪"，放在 Dump 会混淆目录职责。

**Why This One：** 82_Projects/ 已有验证案例（job-search.md），复用成熟模式比新建结构风险低。目录语义也更准确（Projects = 进行中的事情）。

**Priority：高**（多 session 核心工作全部受影响：求职、文章系列、BaseOS）
**Effort：** 2-3小时（为2-3个项目建初始文件 + 简单 agent prompt 更新）
**Blast Radius：低**（纯增量，不修改现有文件结构）
**Evidence Strength：** 观察信号（session 间规划状态断裂，无具体 incident 日期但系统性存在）

---

### SYN-003
**Title：** CLAUDE.md 加入规则优先级声明块，消除 shell-runner vs ACE 的规则冲突歧义
**Source：** B1 Gap1

**Gap：** CLAUDE.md 60行全文无优先级声明。禁止行为段（第56行）"不在主 session 直接读写文件"与 ACE 触发范围（第45-51行）"只要出现就写 _staging.md"之间存在规则张力——ACE 触发时主 session 应该自己写还是委派 shell-runner？逻辑歧义在实践中依赖模型训练偏差打破平衡（B1 audit_B1_information.md 第29-34行）。

**Recommended Solution + Family（Redirective）：**
在 CLAUDE.md 禁止行为段之前插入3行优先级声明：
```
## 规则优先级（冲突时依此顺序）
1. 禁止行为列表（硬约束，不可覆盖）
2. shell-runner 委派原则（操作约束）
3. ACE 暂存机制（记录约束）
4. 工作流规则（流程约束）
```
同时在 ACE 机制段加一句：「ACE 触发时，暂存操作通过 shell-runner subagent 执行，不由主 session 直接写入。」

**Alternative Considered（Reframing）：**
B1 Candidate B——把不同层级规则物理分离，只把硬约束留在 CLAUDE.md。改动更大，作为中期目标。

**Why This One：** 最小改动、最高信噪比。3行插入解决歧义，附带的 ACE 澄清句同时固化 shell-runner 对 staging 写入的覆盖。

**Priority：高**（规则冲突的不确定行为影响每次 session，无需等待事件发生才修）
**Effort：** 1小时
**Blast Radius：低**（仅 CLAUDE.md 文本变更，无架构影响）
**Evidence Strength：** 观察信号（improvement-queue.md 第34行：「ACE 暂存和 habits 写入存在偏差」）

---

### SYN-004
**Title：** system-diagnostics 步骤3扩展为轻量 GC checklist，补齐 ACE staging 去重 + KB 熵清理
**Source：** Cross（B1 Gap6 + B3 缺口F）

**Gap：** staging 写入无去重步骤（B1 Gap6），且 80_Knowledge/ 无任何定期清理机制（B3 缺口F）。improvement-queue.md 第14行已记录 staging 积压 493行/4天。system-diagnostics.md 第18-23行已有"消化暂存区"步骤但缺少 diff 检查和 KB 扫描。

**Recommended Solution + Family（Redirective）：**
在 system-diagnostics.md 步骤2（消化暂存区）中加入 diff 步骤：写入 habits.md 前检查是否与现有条目重复，并区分"Vincent 纠正凌喵（错误信号）"vs"Vincent 表达偏好（习惯数据）"。在步骤3（矛盾检查）末尾加入轻量 GC checklist：(1) 扫描 90_Agents/ 中日期 >60 天无更新且 improvement-queue 有相关改动的 agent prompt；(2) 扫描 80_Knowledge/90_Deprecated/ 可清除内容；(3) 检查 habits.md 与 MEMORY.md 重复条目。GC 建议写入 improvement-queue.md 待审批，不直接执行。

**Alternative Considered（Additive）：**
B3 F2——建立 golden-principles.md + 独立 gc-agent.md。作为中期目标合理，但当前 system-diagnostics 已有步骤框架，扩展比新建管理成本低。

**Why This One：** 两个 gap 共用同一个修复入口（system-diagnostics），一次 prompt 修改解决两个问题。GC 建议走现有 improvement-queue 审批流（B3 F3），不新建输出格式。

**Priority：高**（已有文档化积压证据；Pass1 错误信号问题已在 improvement-queue 记录但修复尚未执行）
**Effort：** 1-2小时（修改 system-diagnostics.md prompt）
**Blast Radius：低**（只改诊断 agent 步骤，不影响其他流程）
**Evidence Strength：** 文档化失败（improvement-queue.md 第14行积压证据 + 第33行错误信号偏差）

---

### SYN-005
**Title：** CLAUDE.md 加入 context 预警规则 + digest-pipeline 失败恢复模式推广为通用约定
**Source：** Cross（B1 Gap4 + B2 Gap6 + B3 风险3）

**Gap：** 无 context reset 协议；无 context 耗尽时的处理方式；长 session 指令飘移风险无对抗机制（三层均覆盖）。digest-pipeline.md 第60-65行已有 5 步失败恢复树作为最佳实践样本（B2 audit 第172行），但仅限该 agent，未推广。

**Recommended Solution + Family（Redirective）：**
双管齐下：(1) 在 CLAUDE.md 工作流段加入一条 computational rule：「主 session 工具调用轮次 ≥15 轮时，在下一轮回复前主动告知 Vincent：context 轮次较多，建议开新 session，我会提供状态摘要。」——预防侧。(2) 在 CLAUDE.md 或专用规范文件中加入一条约定：「所有多步 agent（>3步）在中间步骤写入 checkpoint 文件至 00_Dump/Tasks/，格式参照 digest-pipeline 失败恢复设计。」——恢复侧。

**Alternative Considered（Additive）：**
B2 A4——新建 session-handoff.md template。增加维护成本；CLAUDE.md 一条规则覆盖同样效果。

**Why This One：** 预防（轮次预警）+ 恢复（checkpoint 约定）组合，均为 redirective，复用已有机制。digest-pipeline 的失败恢复树是现成模板，推广成本极低。

**Priority：中**（有具体失败场景但日常 session 较短时影响有限；context rot 可能被 shell-runner 委派的有效执行自然缓解）
**Effort：** 1-2小时
**Blast Radius：低**（CLAUDE.md 文本变更 + 可选 00_Dump/Tasks/ 目录创建）
**Evidence Strength：** 观察信号（improvement-queue.md 第14行 staging 积压是长 session 副产品之一；无单次 context 耗尽的 incident 记录）

---

### SYN-006
**Title：** improvement-queue.md 错误分类升级为结构化 HITL 触发条件表
**Source：** Cross（B2 Gap6 部分 + B3 缺口E）

**Gap：** HITL 触发点分布不均：scheduler 和 dump-processor 有显式确认门（B2 audit 第17行），其余 agent 无系统性 HITL 约束。更关键的是，已知故障场景（routing 失败、连续写入失败）没有结构化上报路径——主 session 可能静默降级而非告知 Vincent（B3 缺口E，CLAUDE.md 第27-35行仅描述 happy path）。

**Recommended Solution + Family（Redirective）：**
在 CLAUDE.md 工作流段增加一小节「升级条件」（3条）：(1) routing 失配（无匹配 agent）→ 明确告知 Vincent 无法处理，不静默降级；(2) 连续 2 次文件写入失败 → 停止，报告状态；(3) 主 session 发现规则冲突无法自行解决 → 停止，列出冲突，请 Vincent 裁决。使用 improvement-queue.md 已有的失败分类语言，不创建新文件。

**Alternative Considered（Additive）：**
B3 E2——写入前 Dump/ 备份约定（最小回滚）。作为可选附加，但不是 HITL 问题的核心修复。

**Why This One：** 已知失败模式（routing 失配，improvement-queue.md 第73-87行已记录多次）显式编码为停止条件，比事后修复成本低。3行规则修改，无新文件。

**Priority：中**（routing 失配已发生多次，但静默降级的主要风险是用户体验而非数据损坏）
**Effort：** 1小时
**Blast Radius：低**
**Evidence Strength：** 文档化失败（improvement-queue.md 第73-87行 routing 失败多次记录）

---

### SYN-007
**Title：** rejection_signals + improvement-queue 错误条目格式化为朴素 eval fixtures
**Source：** Cross（B3 缺口A + B3 缺口G + B1 间接）

**Gap：** 无任何自动化输出质量评估；用户反馈是唯一信号（B3 audit 第54行）。但 MEMORY.md 的 feedback_rejection_signals.md 和 improvement-queue.md 的错误记录已经是隐性 eval 数据集，未被利用（B3 缺口A Candidate A2）。

**Recommended Solution + Family（Substitutive）：**
将 feedback_rejection_signals.md 和 improvement-queue.md 中"凌喵错误"类条目格式化为三元组结构：`[context_summary, wrong_output_type, expected_behavior]`。system-diagnostics 每次运行时遍历这些三元组，自然语言测试当前行为是否仍会复现。不建新文件，不引入 eval 基础设施，使用现有审批流。

**Alternative Considered（Additive）：**
B3 A3——建立 Langfuse/Braintrust pipeline。对个人 AI OS 过度工程化，B3 自己标注 ⚠️ ALL-ADDITIVE 禁用。

**Why This One：** Substitutive 而非 Additive：把已有的错误记录升格为 eval fixtures，零新基础设施。朴素但诚实——在行为调控仍是"未解问题"（Böckeler F2）的前提下，approved fixtures 是最有实证支持的 workaround。

**Priority：中**（有值可挖，但当前错误三元组数量可能不足以产生系统性信号；短期人工标注优先于基础设施建设）
**Effort：** 2-3小时（格式化已有条目 + system-diagnostics prompt 小幅扩展）
**Blast Radius：低**
**Evidence Strength：** 观察信号（rejection signals 文件存在但未结构化利用）

---

### SYN-008
**Title：** Dashboard 写入升级为 hookify computational 约束，解除 inferential-only 高风险操作
**Source：** B3 缺口D

**Gap：** CLAUDE.md 禁止行为（第56-59行）3条均为自然语言 inferential 约束，无 computational 执行层保障。「日程未经 Vincent 确认不写入 Dashboard」这条 blast radius 最大（Dashboard 错误写入影响 Vincent 的日程可见性），但也最容易升级为 computational 保障（B3 缺口D Candidate D1）。

**Recommended Solution + Family（Redirective）：**
通过 hookify hook，在任何 Edit/Write 针对 Dashboard.md 的操作时强制插入确认步骤（要求 Vincent 明确 approve 后才执行写入）。复用已有 hookify 基础设施（feedback_settings_path_format.md 有格式规范），不修改 CLAUDE.md。

**Alternative Considered（Substitutive）：**
B3 D2——settings.json permissions 替代 inferential 约束（将主 session 的写入权限限制到特定目录）。实施复杂，可能误伤合法操作，当前规模下过重。

**Why This One：** 只对 blast radius 最大的单一操作升级为 computational 约束，其余保持 inferential（D3 reframing：高信任单用户场景 inferential 约束误报率低）。最小有效防护，不过度工程化。

**Priority：中**（已有 HITL 机制存在但非 computational；失败代价高但发生频率低）
**Effort：** 1-2小时（hookify 规则配置）
**Blast Radius：低**（仅影响 Dashboard.md 的写入操作）
**Evidence Strength：** 理论风险（无 Dashboard 误写 incident 记录，但防护成本极低值得做）

---

### SYN-009
**Title：** agent prompt 格式标准化：以 fitness-coach 硬约束注入模式为模板推广到其他 agent
**Source：** B1 Gap8 + B2 执行层一致性

**Gap：** 各 agent prompt 格式不一致——fitness-coach.md 有触发词 + 硬约束段 + 更新日期（B1 audit 第192行：「是 computational guide 的好例子」），knowledge-agent.md 第1行只有名称，system-diagnostics.md 第3行有职责描述但无正式 Intent 声明。格式不统一导致渐进式披露和 agent 导航效率低。

**Recommended Solution + Family（Redirective）：**
以 fitness-coach.md 格式（触发词 + 更新日期 + 职责声明 + [硬约束] 段）为基准，在系统诊断 session 里作为"格式统一"任务，将其他 agent prompt 头部标准化。不建模板文件，直接修改现有文件。

**Alternative Considered（Additive）：**
B1 Candidate B——建立 `90_Agents/_template.md` 规定标准结构。作为中期目标，当前先统一格式，再固化模板。

**Why This One：** 最小标准化动作，复用现有最优格式，无新文件。格式统一是其他改进（如渐进式披露、agent 发现）的前置条件。

**Priority：低**（功能不受影响，是改善可维护性的预防性工作）
**Effort：** 2小时（检查并更新5-6个 agent prompt 头部）
**Blast Radius：极低**（纯格式变更）
**Evidence Strength：** 观察信号（格式不一致可直接验证）

---

### SYN-010
**Title：** 83_Observations/ 和 87_People/ 建立 _manifest.md 索引
**Source：** B1 Gap5

**Gap：** 81_Identity/、82_Projects/、86_AI_Systems/ 已有 manifest 文件，但 83_Observations/、87_People/ 无索引（B1 audit 第17行）。87_People/ 是 MEMORY.md 人际关系知识库的权威来源（reference_people.md），无索引时 agent 导航只能靠 prompt 硬编码路径。

**Recommended Solution + Family（Redirective）：**
复制现有 manifest 模板（type/cluster/last_updated 格式，参考 81_Identity/_manifest.md）为 83_Observations/ 和 87_People/ 建立索引文件，列出各目录的文件功能摘要。纯文件创建，无 agent 改动。84_Fitness/ 和 85_System/ 暂不处理（agent prompt 已有硬编码导航，B1 Candidate B reframing 成立）。

**Alternative Considered（Reframing）：**
B1 Candidate B——agent prompt 内的硬编码导航已够用，manifest 是多余的文档层。对 84_Fitness/ 和 85_System/ 成立，但 83_Observations/ 和 87_People/ 没有等价的硬编码导航，reframing 不适用。

**Why This One：** 局部应用，只对真正缺少导航的两个目录执行，不过度标准化。

**Priority：低**（不影响当前功能，是长期可维护性投资）
**Effort：** 1小时
**Blast Radius：极低**
**Evidence Strength：** 观察信号（目录存在无索引可直接验证）

---

### SYN-011
**Title：** _staging.md 加入最小操作摘要行，提供轻量 audit trail
**Source：** B3 缺口C

**Gap：** shell-runner 原则让主 session 保持干净，但代价是中间状态主动丢弃，zero replay 能力（B3 风险3）。当前 _staging.md 只存 Vincent 的观察数据，无任何操作记录。

**Recommended Solution + Family（Redirective）：**
在 _staging.md 追加写入机制中加入操作摘要行：每次 subagent 调用后追加 `[HH:MM] agent=X action=Y target=Z result=ok/fail`。不建新文件，不改变 _staging.md 主体功能（观察数据暂存），只在现有文件末尾增加一个操作日志区。

**Alternative Considered（Reframing）：**
B3 C3——接受低 observability 作为个人 OS 的合理 tradeoff；B3 的 trace 标准针对多用户生产系统。对完整 DAG trace 成立，但最小 audit trail（知道"哪个 agent 写了什么"）在多步 session 失败排查时有实际价值，成本极低。

**Why This One：** 不追求生产级 trace，只追求最小可调试性。_staging.md 已有追加写入机制，格式扩展成本接近零。

**Priority：低**（当前调试摩擦可接受；主要价值在 digest-pipeline 这类多步 session 失败时）
**Effort：** 30分钟（CLAUDE.md 或 shell-runner 约定添加一行操作摘要指令）
**Blast Radius：极低**
**Evidence Strength：** 理论风险（无具体因缺乏 trace 导致的 incident，但成本极低值得做）

---

> **注：** 以下两项为"观察中"状态，当前规模不需要立即行动。
>
> **SYN-WATCH-A：** agent 间 handoff payload schema 结构化（B2 Gap3 R4）——当前约定可工作，结构化成本 > 当前风险；规模扩大后优先。
>
> **SYN-WATCH-B：** 并行 agent 调度控制（B2 Gap7 RF3）——当前日均调用量小，串行够用，B2 audit 自身推荐 Reframing（RF3）。

---

## Section 4：MeowOS 已有的真实优势

从三份审计中收集，已对标行业标准或超出预期的实现。

1. **Filesystem memory 架构与行业收敛完全对齐。** 362个文件分层目录、无向量库（B1 audit 第208行）。Jerry Liu、Boris Cherny 独立得出同结论（master_synthesis 收敛A）；MeowOS 早于研究结论独立实现。

2. **shell-runner 委派覆盖率接近100%。** CLAUDE.md L34-35 + 01_Routing.md L51 + 所有主要 agent prompt 均有委派声明（B2 audit 第163行）。Jason Liu 实测数据：subagent 路径比 slash command 路径信噪比高8倍（B1 audit 第210行）。MeowOS 独立实现了同一设计。

3. **improvement-queue + 系统诊断审批流是有效的人工 GC 机制。** Lopopolo 主张4要求持续 GC（master_synthesis 第75行）；MeowOS 用人工审批版本实现，符合"人类注意力是瓶颈"的设计原则（B1 audit 第212行）。

4. **HITL 确认门在高风险写入场景覆盖良好。** scheduler.md L32-34、dump-processor.md Step 2-3、dashboard.md L46 均有显式确认门（B2 audit 第167行），与 B2 Section 5"不可逆动作前停止"原则匹配。

5. **MEMORY.md 的 feedback_*.md 系列是行业罕见的持续性错误记录层。** 50+子文件每个本质上是一个"人工标注失败案例"（B3 audit 第179行）。Hamel 的"从真实错误做 error analysis"建议在 MeowOS 已有朴素实现。

6. **MCP 暴露极度克制。** settings.json 仅 ms365 一个 MCP server（B2 audit 第183行），对比行业的"300+ tools → 62% accuracy"下降，MeowOS 工具选择精准。

7. **01_Routing.md 是有效的路由集中管理实现。** 20+触发词 + 冲突解决规则，与 B2 Section 2.7（每个 agent 应有清晰 handoff_description）对齐（B2 audit 第178行）。

8. **fitness-coach 的 [硬约束] 段头部注入是 computational guide 的最佳实践。** primacy 位置 + 明确触发条件 + 违反后果（B1 audit 第216行）。值得推广为所有 agent 的标准头部格式。

9. **digest-pipeline 失败恢复树是系统内的 recovery 最佳实践。** 4种独立故障状态 + 分支处理路径（B2 audit 第172行），是目前唯一实现了 B2 Section 5 retry/recovery 的组件，可作为其他 agent 的模板。

10. **rejection_signals 专项追踪是 behaviour harness 的朴素先进实现。** feedback_rejection_signals.md 的存在（B3 audit 第182行）——大多数 agent 系统没有这一层；Böckeler approved fixtures pattern 的逆向版本。

---

## Section 5：表面像缺口但实际不是问题（Explicit Non-Problems）

1. **Prompt Caching 无结构支撑。** B1 Gap3 提出此问题，但 B1 自己的推荐是 Reframing（Candidate B）：MeowOS 是单用户低频请求系统，每次 session 的 system prompt 重新计算成本相对较低。投入 4-6小时做 cache breakpoint 标注，收益在当前规模不足以证明。正确做法：接受现状，观察 session 规模是否增长。

2. **MEMORY.md 与 habits.md 内容重叠。** B1 Gap7 提出，但 B1 自己的推荐是 Reframing（Candidate A）：两个系统有不同读者和不同维护机制，重叠是有意冗余，一个失效时另一个兜底。无实际错误行为证据。

3. **并行 agent 调度缺乏明确控制。** B2 Gap7，B2 自己推荐 Reframing（RF3）：当前日均 agent 调用量小，串行够用。过度设计在当前规模没有收益。

4. **完整 DAG trace / replay 能力缺失。** B3 缺口C，B3 自己推荐 C3 Reframing：trace 标准针对多用户生产系统，单用户 OS 中 Vincent 本人即是调试者，全链路 trace 是 overkill。最小 audit trail（SYN-011）够用。

5. **全面 Computational 约束化。** B3 缺口D 提出用 settings.json 权限替代全部 inferential 约束（D2）——这在单用户高信任场景是过度工程化。Vincent 即是所有者、操作者、审批者，NeMo Colang 级别的 computational policy 针对外部不可信用户输入，不适用于 MeowOS 场景。保持 Dashboard 写入一处 computational（SYN-008），其余 inferential 足够。

---

## Section 6：Meta-Observations

### 三份审计的一致性程度

整体高度一致，核心问题（system-diagnostics 自评失真、Task State 断裂、Context Reset 缺失、GC 缺位）在 B1/B2/B3 各自独立发现。这是高置信度信号。

分歧集中在"值不值得做"：B1 在 Prompt Caching（Gap3）和 MEMORY.md 双写（Gap7）上更倾向于 Reframing（不做），这与 B2/B3 的立场一致，三者都是自我否定了这两个 gap。这是健康的审计态度。

### 审计偏差评估

**B1（信息层）**：整体克制，自我应用 Reframing 最多（3个 gap 推荐 Reframing 而非修复）。可能略微低估了 Prompt Caching 的长期价值，但在当前规模下判断是合理的。

**B2（执行层）**：覆盖最广，19个候选方案。在 Gap7（并行调度）上准确应用 Reframing（RF3），在 Gap4（工具后处理）上明确标注 A3 为孤立 Additive 并推荐 Redirective。整体偏保守，是正向的。

**B3（质量层）**：对 GC 缺口（缺口F）的 F2 方案（ALL-ADDITIVE）给出了最诚实的标注：「GC 本质上就是新基础设施，Lopopolo 原方案亦然；中期建立有合理性」。这种"这是 Additive 但 Additive 在此有合理性"的区分很有价值，避免了教条化。

**总体：** 三份审计没有"只有建议"的审计——B1/B2/B3 全部自我否定了若干 gap，推荐的都以 Redirective 为主。这是对审计哲学的正确执行。

### All-Additive 候选提醒

三份审计中明确标注 ⚠️ ALL-ADDITIVE 或明确不推荐的 Additive 方案：
- B3 A3（建 Langfuse/Braintrust pipeline）→ 禁用，对个人 OS 过度工程化
- B2 A1（新增 planning agent）→ 低优先级，R2 Redirective 方案已覆盖
- B2 A3（新建 context-compressor agent）→ 不推荐，R7 全局规则已覆盖
- B3 F2（golden-principles.md + gc-agent.md）→ 标注为中期目标，当前 F1 Redirective 足够

以上均未进入本候选清单。

---

*合成完成时间：2026-04-14*
*本文件为候选清单，待 Vincent 审批后方可写入 improvement-queue.md*
