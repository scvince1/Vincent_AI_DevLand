---
id: 00_master_synthesis
title: Harness Engineering — 统一视角综合
tags: [harness, knowledge, synthesis, agent-design, impact]
status: confirmed
last_modified: 2026-04-15
summary: F1/F2/F3+G1/P1 五份一手研究合成，作为 B1/B2/B3 深挖的 master context
---
# Harness Engineering — 统一视角综合

**版本：** 2026-04-14（基于 F1/F2/F3 + G1/P1 五份一手研究合成）
**用途：** 作为 B1/B2/B3 深挖的 master context，以及 MeowOS Step B 审计的标尺。

---

## 0. 一句话地基

**Agent = Model + Harness**

Harness = LLM 之外的所有东西：context、tools、orchestration、memory、evaluation、constraints、recovery 及组织它们的胶水。

2026 年出现了一个真正的概念反转：**harness（不是模型）才是 agent 的主要所有权与资产承载体**。Manus $2B 收购案买的是 harness，不是模型。这句话是整个学科的商业与工程焦点所在。

---

## 1. 五个框架的横向地图

同一个东西，五种切法。理解它们的关系比记住任何一个都重要。

| 来源 | 术语 | 切法维度 | 主要贡献 | 局限 |
|------|------|---------|---------|------|
| **Weng 2023** | Planning / Memory / Tools | 3 组件（能力维度） | 开山分类学，所有人引用的词汇底座 | 没有 Authority、Control flow、Intent |
| **swyx IMPACT (2025-26)** | **I**ntent / **M**emory / **P**lanning / **A**uthority / **C**ontrol flow / **T**ools | 6 组件（工程完整性 checklist） | 补 Weng 的 Authority / Control flow / Intent 三个盲区 | 偏静态清单，不讲生命周期 |
| **B 站视频 6 层** | Context / Tools / Orchestration / Memory / Eval / Constraints-Recovery | 6 层（运行时阶段） | 面向实操的分层视角 | 二手解读，部分定义来自 Lopopolo 的术语引用 |
| **Böckeler Guides+Sensors** | Guides × Sensors 的 2×2（computational / inferential） | 控制论维度（前馈 + 反馈 × 确定 + AI） | 唯一引入 feedforward/feedback 控制论分类 + computational vs inferential 二分 | 3 调控类别（maintainability / architecture fitness / behaviour）中 behaviour 被明确标记为"未解" |
| **Lopopolo 5 主张** | 非结构化 5 条核心论断 | 哲学与设计原则层 | 给出学科的"第一性原理" | 不是框架，是宣言 |

### 框架映射表（不精确但有用）

| Weng 2023 | IMPACT | B站 6 层 | Böckeler | Lopopolo |
|-----------|--------|---------|---------|---------|
| — | **I**ntent | Context 管理（角色部分） | Guides（计算型） | 主张 1 |
| Memory | **M**emory | Memory & State | Guides（推理型）+ 长期 Sensors | 主张 4（garbage collection） |
| Planning | **P**lanning | 执行编排 | — | — |
| — | **A**uthority | 约束与恢复（部分） | Guides（硬约束） | — |
| — | **C**ontrol flow | 执行编排 + 工具系统 | Sensors 触发的控制 | — |
| Tools | **T**ools | 工具系统 | Guides（工具文档）+ Sensors（工具结果验证） | 主张 3（agent legibility） |
| — | — | 评估与观测 | Sensors（全部） | — |
| — | — | 约束 / 恢复 | Sensors + garbage collection | 主张 2、4 |

**读法：**
- 空格（—）= 该框架没有明确覆盖此维度
- Weng 2023 的三个盲区（Intent / Authority / Control flow）被 IMPACT 填补
- Böckeler 独家贡献：computational vs inferential 二分、feedforward vs feedback 控制论视角
- Lopopolo 独家贡献："garbage collection" 作为 codebase 级别的持续清理工作 + 5 条哲学主张

---

## 2. 真正的概念跃迁（不是词汇替换）

字面换词很多，真正的结构性变化只有少数几个。这些才是凌喵建议 Vincent 重点吸收的。

### 跃迁 1：所有权反转
Weng/IMPACT：模型是 agent，harness 是辅助。
Harness Engineering：**harness 是 agent，模型是被它编排的组件**。

**为什么重要：** 决定了投资方向 -- 应该往 harness 投工程资源，不是往选模型投资源。Manus $2B 是市场对这个反转的定价。

### 跃迁 2：失败归因重写
普通工程：模型不给力 → 换模型 / 调 prompt。
Harness Engineering（Lopopolo 主张 2）：**每一次模型失败都是 harness 的缺陷**。

**为什么重要：** 直接否决了"这个模型不行换一个"的逃避路径。失败 = 缺了一个结构性能力。这是 debug 思维的根本转变。

### 跃迁 3：Agent 可读性作为一等设计约束
过去：代码给人看。
现在（Lopopolo 主张 3）：**代码同时为 agent 可读性和人类可读性设计**。

**为什么重要：** "Harnessability"（Böckeler 的术语）成为代码本身的属性。注释、命名、模块化不再只是软工原则，是 harness 性能的基础设施。

### 跃迁 4：熵是必然的，需要持续 GC
过去：偶尔重构。
现在（Lopopolo + Böckeler）：**Agent 生成的代码库会产生熵，需要持续的 garbage collection 后台任务**。不是 session 内 context pruning，是 codebase 级别、周级时间尺度、自动执行"黄金原则"。

**为什么重要：** 解释了为什么 agent 开发的项目长期会"坏掉"。必须有清理机制，不能靠人工冲刺。

### 跃迁 5：Behaviour Harness 是公开未解难题
Böckeler 明确标记：**maintainability 和 architecture fitness 有解（tests + linters + fitness functions），behaviour 没解**。

**为什么重要：** 警示工程师别假装已解决。这是研究前沿，不是工程问题。2026-2027 的 harness 工具创新大概率发生在这个方向。

---

## 3. 跨源头的收敛（多人独立说同一件事）

这些是高置信度的 takeaway。

### 收敛 A：Filesystem > Vector DB 作 memory
**证据链：**
- Jerry Liu（LlamaIndex 创始人）公开承认（人物雷达 P1）
- Boris Cherny（Claude Code 负责人）独立得出同结论
- G1 扒源码验证：Claude Code / Cursor / Aider 都用 filesystem

**结论：** 对 MeowOS 的启示 -- 继续用 `80_Knowledge/` 分目录文件作为 memory，不要上向量库。

### 收敛 B：Planner / Executor 拆分
**证据链：**
- Anthropic（Planner → Generator → Evaluator）
- Aider architect mode（两 agent 分离）
- OpenHands Planning Mode beta
- DeerFlow lead-agent + subagent 架构

**结论：** MeowOS 的系统诊断 agent 应该拆成"诊断 + 改进执行"两个 session。

### 收敛 C：模型质量平台化 → harness 成为差异化
**证据链：** Lopopolo、Chase、Cherny、Karpathy 全都独立表达此观点。Chase 金句：「better models alone won't get your AI agent to production」。

**结论：** 凌喵本身的 model 选择重要性下降，harness（CLAUDE.md 结构 + agent prompts + shell-runner 模式）的优化重要性上升。

### 收敛 D：渐进式披露 / 按需加载
**证据链：** OpenAI 的 agent.md 教训（一次性塞全部 → 改目录页+子文档）、Anthropic Skills 设计、MCP 的工具注册模式。出现在 5+ 源头。

**结论：** MeowOS 已经在做（CLAUDE.md 精简 + 子 agent prompt 按需读取）。可以更系统化 -- 每个 Skill/Agent 都应有标准化 metadata（name + description），启动时只加载这一层。

### 收敛 E：生产与验收必须分离
**证据链：** Anthropic Planner/Generator/Evaluator、Böckeler Sensors 分层、Lopopolo 主张 1（人类注意力是瓶颈 → 必须有自动验收）。

**结论：** MeowOS 的 ACE 自评机制存在"自评失真"风险，诊断和执行改进要分 session。

---

## 4. 活跃争论（field 内尚未解决的分歧）

理解争论比记忆共识更重要 -- 争论暴露了前沿。

### 争论 1：Willison vs swyx -- "agent" 到底该怎么定义
- **Willison**（极简派）："An LLM agent runs tools in a loop to achieve a goal"（2025-09-18 原文直引）
- **swyx**（工程派）：这个定义漏掉 Memory、Planning、Authority -- 刚好是"能 demo 的 agent"和"能上线的 agent"的分水岭
- **凌喵的判断：** 两者不矛盾 -- Willison 优化「诊断」（这是不是 agent？），swyx 优化「施工」（要建啥？）。MeowOS 场景下 swyx 更有用。

### 争论 2：LangGraph 重 vs 轻
- 支持者：graph + checkpoint 是生产级 workflow 的正确抽象
- 批评者：单轮 RAG 这种简单任务上 graph model 增加不必要复杂度
- LangChain 官方现在的立场："use LangGraph for agents, not all LLM apps"（官方承认了这个问题）

### 争论 3：Prompt 自优化 vs 手写
- DSPy / GEPA / TextGrad 阵营：prompt 应该像代码一样被编译和优化
- 传统阵营：可解释性 > 可优化性，手写 prompt 更可控
- Pydantic-AI #3179 提议集成 DSPy 风格优化器 -- 是观察的前沿标志

### 争论 4：Multi-Agent 是不是必要
隐性争论：有些 framework（CrewAI、AutoGen）主打 multi-agent，有些（Aider、Claude Code）坚持单 agent + 清晰工具。源码深度分析（G1）显示**单 agent + 好工具**在代码场景更有优势。

---

## 5. MeowOS 现状 × IMPACT × Böckeler 三维审计表

给 Step B 提前做一张诊断底表。

| 维度 | IMPACT 位置 | Böckeler 类型 | MeowOS 当前实现 | 缺口 |
|------|-----------|-------------|---------------|------|
| 角色与意图 | **I**ntent | Guides / computational | `CLAUDE.md`（角色 + 原则 + 禁止行为） | 无明显缺口 |
| 任务记忆 | **M**emory | Guides+Sensors 混合 | `80_Knowledge/` + `Dashboard.md` + staging | 三类状态未明确分离（session / task / long-term） |
| 规划 | **P**lanning | — | 仅 session 内 TodoWrite | **持久化 planning 缺失**，session 间无连续性 |
| 权限 | **A**uthority | Guides / computational | `settings.json` + 禁止行为段 | 缺少按 agent 类型的精细权限 |
| 控制流 | **C**ontrol flow | — | shell-runner 委派 + agent 调度 | 缺少 failure recovery / context reset 协议 |
| 工具 | **T**ools | Guides（文档）+ Sensors（结果验证） | Bash/Read/Edit/Skills/MCP | 工具结果验证（Sensors 侧）几乎没有 |
| 评估 | 隐含在其他 | Sensors / inferential | ACE 系统诊断 + 用户反馈 | 自动化输出质量评估缺失；自评失真风险 |
| 约束 + 恢复 | A 的一部分 | Sensors + garbage collection | 禁止行为列表 | **无失败恢复机制；无 codebase-level GC** |
| Harnessability | — | 元设计属性 | 知识库分层、shell-runner、Skills | 待评估：MeowOS 本身对外部 agent 的"可驾驭性"如何 |
| Behaviour 调控 | — | Sensors（未解） | — | **与行业共识一致：这是未解问题** |

---

## 6. B1/B2/B3 的搜索锚点

Step A 深读到此结束。接下来 B1/B2/B3（信息层 / 执行层 / 质量层）有了具体锚点：

### B1 信息层（Intent + Memory + Context）
- **必读源头**：Jason Liu context-engineering 系列（jxnl.co）、Chase Sequoia 访谈、Karpathy Software 3.0 框架
- **必看源码**：Claude Code（filesystem memory）、Aider（git diff 做 context）、mem0（独立 memory service）
- **核心问题**：三类状态（session / task / long-term）如何在文件系统层面干净分离？
- **开放辩论**：Prompt 作为代码（DSPy）vs 作为语言（手写）？

### B2 执行层（Planning + Control flow + Tools）
- **必读源头**：Lopopolo Symphony 案例、DeerFlow 2.0 设计文档、OpenHands Planning Mode
- **必看源码**：DeerFlow `packages/harness/deerflow/`、LangGraph checkpointing、Aider architect mode
- **核心问题**：何时单 agent + 好工具，何时 multi-agent？Planner/Executor 拆分的最小实践？
- **开放辩论**：MCP 够不够？AG-UI 是否必需？

### B3 质量层（Evaluation + Constraints + Recovery）
- **必读源头**：Hamel + Shankar evals FAQ、Böckeler Sensors 部分、NeMo Guardrails 设计
- **必看源码**：Promptfoo（OpenAI 刚收购，现在该读）、Langfuse、NeMo Guardrails Colang
- **核心问题**：behaviour 调控（未解问题）-- 有什么朴素的 workaround？context reset 协议长啥样？
- **开放辩论**：LLM-as-judge 如何防止循环验证？human-in-the-loop 的最小触发点？

---

## 7. 给 Vincent 的一个诚实提醒

这份综合覆盖了 5 个框架，但**不能替代读原文**。凌喵在这里做了翻译和映射，翻译就会丢失微妙。

- 如果你要写文章（HBR / LinkedIn），**必须回原文**，这份综合只能作为导航。
- 如果你要审计 MeowOS（Step B），**这份综合够用**。
- 如果你要和别人辩论这个领域，**回原文**，尤其是 Willison vs swyx 那条线。

5 份一手资料都在 `source_texts/`，随时可以回查喵。
