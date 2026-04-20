# Challenge 5 Rethink: Design Principles (2026-04-17)

Vincent 从头重新思考 Challenge 5 的设计原则清单。

## 核心原则

1. **互不冲突** - 不应与现有解决方案（Qualtrics / Salesforce / Analytic Partners）在功能上产生冲突或过度重合
2. **错位竞争** - 不在准确性或专业性上与现有平台硬碰硬
3. **低门槛 + 高上限** - 避免一切需要 coding / IT / 专业工具才能实现的制度；让所有人都能通过**自然语言**完成需求
4. **双向兼容**：
   - 普通用户是底板（向下兼容）
   - 硬核用户可通过**更专业、更数学或更 coding** 的方式实现功能（向上兼容）
5. **吸收精华** - 借鉴现有平台在思想和功能点上的精华，但想到新功能时必须 check，确保与既有方案没有重叠

## 设计红线

- **集成 UI**：一个 UI 体系 / 一个网址，功能尽可能集成
- **反碎片化**：拒绝 Salesforce 式的多 Studio UI 分裂

## 不做

- Salesforce 的画布式流程图
- Salesforce 的邮件编辑器
- 任何会与 Qualtrics / Salesforce / AP 在其核心功能上重合的东西

## 可以借鉴的方向

- **Segment Builder 式的用户切片交互**（不是"过去 90 天买过吸尘器"这种具体业务逻辑，而是用条件组合切信号 / 切用户群的**能力形态**）

## 待想清楚

- **Agentforce 上下游关系** - Vincent 直觉觉得 Challenge 5 和 Agentforce 应该某种形式上构成上下游，但尚未具体化

---

2026-04-17 记录，Vincent 去 Amazon 做一手调研回来后继续。

---

## 2026-04-17 追加（Vincent Amazon 调研回料后）

### 观察 1 决策：选 B

早期缺陷信号捕捉**升为 marketing 预警的一部分**（不是 QC-only 的"顺带演示"）。
理由：它影响品牌感知 / 送礼满意度 / repeat purchase / creator PR 风险，这些都是 marketing 关心的。

### 观察 2 扩展：使用场景 / Usage Occasion 作为 whitespace

Vincent 一手例子：Shark 吹风机在"家用"场景输给 Dyson / 徕芬，但在"出差"场景赢，因为皮质包装箱 + 腾空的附件槽位 = 意外的旅行用容器。

→ review 里用户**自己讲的 usage context / occasion** 是现有工具不默认抓的信号。
→ 这是 Challenge 5 可能的一条 whitespace 轴：**usage occasion segmentation map**。

### "ROI-attributable product decision" 作为设计思考点

Vincent 的核心洞察：Challenge 5 把 "marketing insight" 转译成 **product team 能 attribute ROI 的 decision**。
例：descriptive (3.9 分) → predictive (修这 2 个 issue 预计 4.1 分) → narrative ("Expected monthly sales impact $X, priority high")。

这对 Mark Barrocas / Joyce 办公室审批预算的场景特别有说服力。

---

## 2026-04-17 追加：Monitor & Optimize 作为设计红线

Vincent 看到其他 AI solution 厂商使用的 3 阶段 process 框架：

1. **Discover & Diagnose** (Understand first, automate second)
   - 学习业务怎么运作：目标 / 约束 / 交接 / "win" 定义
   - 映射 tech stack + 数据住在哪
   - 审计流程找真实 bottleneck + 决定什么该 / 不该自动化

2. **Design, Build & Validate** (Custom solutions, tested before launch)
   - 优先高影响机会 + 决定 AI 在哪帮 / 不帮
   - 设计 custom workflow + 真数据测不同方法 + 白话解释选择
   - real-world 环境 eval before full rollout

3. **Launch, Monitor & Optimize** (Continuous improvement, not a one-off project)
   - 明确 success metrics + safeguards
   - 持续监测 performance + 收集 team 和 customer feedback + 快速修问题
   - 持续 refine prompts / logic / models

### 对 Challenge 5 的含义

**产品层面**：Challenge 5 产品本身必须**可被 monitor + optimize**。
- 不是 one-off delivery
- UX 要暴露 feedback loop（用户能告诉系统哪里做错了）
- 内部要有：数据 lineage / model versioning / A/B 测试机制 / success metric tracking
- 系统 must evolve as SharkNinja 业务演化（新品类 / 新 SKU / 新平台加入）

**Service 层面**（可选）：这个 3 阶段框架也可以作为 Vincent 对 SharkNinja 的 service delivery framework（面试时能讲的 methodical 落地流程）。

### 设计锚点

- **Feedback loop** 是一级 UX 要素，不是附加功能
- **Success metrics + safeguards** 在 launch 前必须明确
- **Continuous improvement** 写进产品 roadmap，不是"有空再做"

---

## 2026-04-17 追加：Mark Barrocas 公开战略观点（Vincent 从 podcast + 演讲一手听到）

### Mark 原话（Vincent 转述）

1. 把产品**品类铺广**，让消费者在各种场景都能**想到和选择 SharkNinja**
2. **不要让用户多年后需要更换时忘了 SharkNinja**，从而随机选其他厂商
3. 希望 customers **恨不得每年都换或买一些 SharkNinja 新产品**

### 映射到 Ehrenberg-Bass (Byron Sharp) 框架

| Mark 的话 | 框架对应 |
|---|---|
| 品类铺广 + 让 customer 做各种事情时想到 | Mental Availability 广度 + 多 CEP 占领 |
| 不要被用户忘了 | Mental Availability 持久性；品牌选择大多是 habit / available first |
| 每年换或买新产品 | Category Expansion per Household（一户多品类） |

### 对 Challenge 5 的战略含义

**Mark 的 mental model = Ehrenberg-Bass 式**（虽可能没显式引用 Sharp）。

Challenge 5 应追踪的信号：
- **CEP 覆盖度**：SharkNinja 在哪些购买情境里出现 / 被忘
- **跨品类心智份额**：同一消费者是否在 vacuum → FlexStyle → Creami → CryoGlow 之间自然联想
- **"被忘了随机选其他" 的预警信号**：在 review / 社交讨论里识别 "I used to have a Shark but went with Dyson this time" 类 switching narrative

→ **Challenge 5 可以作为 Mark 战略诉求（8 大品类扩张）的测量工具**，而不仅是 VoC 分析平台。

### 面试 pitch 含义

跟 Joyce / Mark 办公室讲 Challenge 5 时，**用 Ehrenberg-Bass 的语言框架不水土不服**，反而是对齐 Mark 内部思维。

---

## 2026-04-17 追加：Data Graveyard 的正确理解（Vincent reframe）

### Vincent 的 distinction

- **存档 / 记录本身合法** — 有些东西存在的意义就是"为了存在"
- **真正问题不是没人读**，是**为"以防万一"手动维护大量不被读的东西** → 浪费人力和认知
- 反面错误也不对：完全不做 archive → 以防万一时什么都没有

### 正确的解法（Vincent 明确表达）

1. **适当自动化** — 轻量化 + 简便 + 快速产出
2. **On-demand 可取** — 你需要时系统马上给
3. **不是自动化报告本身** — 不是做一个 auto-generated dashboard factory

### 映射到 AI / LLM 时代的 UX 范式转移

| 旧范式（BI / 传统 CI） | 新范式（Challenge 5 方向） |
|---|---|
| Pre-compute everything → store dashboard → user queries | Store raw signals → LLM on-demand synthesize → user gets what when they ask |
| 维护 taxonomy / rule / dashboard 需要专职人力 | Raw signal auto-ingest，分析 on-demand 生成 |
| "你需要先想清楚要看什么" | "你说一声，系统马上组织给你" |
| Dashboard 是产品 | Dashboard 是问出来的答案 |

### 设计含义

- **Raw signal 层要全**（不删东西，archive 合理）
- **Synthesis 层按需触发**（不 pre-compute 大 dashboard）
- **UX 入口是自然语言 + LLM generate**，不是 "配好的 dashboard 供 browse"
- 对应 2024-2026 BI 的 **Agentic BI + Natural Language Query** 趋势
