---
id: B1_information_layer
title: B1 — Information Layer Deep Dive
tags: [harness, knowledge, information-layer, memory, context]
status: confirmed
last_modified: 2026-04-15
summary: IMPACT 的 I+M 层深挖：context window 机制、MemGPT、prompt caching
---
# B1 — Information Layer Deep Dive
## Intent · Memory · Context Plumbing

**版本:** 2026-04-14
**基于:** jxnl.co context engineering series (DIRECT), MemGPT/arxiv (DIRECT), mem0 README (DIRECT), Letta README (DIRECT), Anthropic prompt-caching docs (DIRECT), Eugene Yan LLM patterns (DIRECT), "Lost in the Middle" / arXiv:2307.03172 (DIRECT), master_synthesis (local)
**前置:** 读过 `00_master_synthesis.md`
**范围:** IMPACT 的 I + M，加上 context window 的全部机制；工具/编排/评估不在此层

---

## Section 1 — 概念基础：为什么 Context 是 Agent 的真正瓶颈

### 1.1 "模型看到的"是什么

从机制层说起。Transformer 处理的是一个 token 序列。每个 token 在注意力计算时能"看到"序列里所有其他 token，但这种"看"不是等权重的。

**三个硬约束：**

1. **长度上限（Context Window）。** 超出窗口的内容物理上不存在。模型对它一无所知，没有截断警告，没有降级，就是不存在。这不是软限制。

2. **位置敏感性（Primacy & Recency Bias）。** "Lost in the Middle"（Liu et al., 2023 / arXiv:2307.03172）做了定量实验：把相关信息放在长上下文的中间位置，模型性能显著下降；放在开头或结尾则表现最好。这不是 RAG 的问题，是 Transformer 注意力分布的问题。

3. **注意力稀释（Attention Dilution）。** 上下文越长，每个 token 的注意力"预算"被摊薄。长文档里一条关键指令被 10 万个 token 淹没，模型遵循它的概率下降，不是因为指令模糊，是因为它的相对权重太低。

**实践含义：** 上下文不是一个"越多越好"的资源，它是一个有容量、有位置敏感性、会稀释注意力的受限信道。**管理上下文 = 管理信道质量，不只是管理信道容量。**

### 1.2 Context Pollution vs Context Rot

Jason Liu 在他的 Context Engineering 系列（jxnl.co）里区分了两个现象：

- **Context Pollution**（上下文污染）：有价值的推理上下文被计算上廉价、信息上低密度的内容淹没。典型例子：把 15 万个 token 的测试日志直接倒进主线程。刘的实测数据：slash command 路径 169,000 tokens 91% 是噪音；subagent 路径 21,000 tokens 76% 是有效信息，信噪比提升 8 倍。（来源：jxnl.co/writing/2025/08/29/context-engineering-slash-commands-subagents/）

- **Context Rot**（上下文腐化）：随着对话轮数增加，输入长度增大，模型处理上下文的可靠性持续下降。不是一次性污染，是渐进式性能衰退。

两者都是真实现象，都有不同的应对策略（分别是：隔离/subagent 架构，和：压缩/compaction）。

---

## Section 2 — Context Window 管理

### 2.1 Prompt Caching 的机制（以 Anthropic 为具体例子）

Anthropic 的 prompt caching 提供两种模式（来源：docs.anthropic.com/en/docs/build-with-claude/prompt-caching）：

- **Automatic caching**：在请求 top level 加 `cache_control` 字段，系统自动把缓存断点放在最后一个可缓存块，随着对话增长自动向前移。适合多轮对话场景。

- **Explicit cache breakpoints**：在具体 content block 上手动放 `cache_control`，精细控制哪些内容被缓存。

缓存有效期：5分钟（默认）或 1 小时（扩展 TTL）。

**为什么重要：** 对于有稳定系统 prompt + 稳定知识库的 agent（比如 MeowOS），把 system prompt 和 KB 放在缓存 breakpoint 前面，后续请求只需要计算新 token 的 attention，成本显著下降。但关键的工程前提：**缓存失效的内容必须稳定**。频繁变化的内容放在缓存前面会导致高 cache miss 率，反而比不缓存更贵。

### 2.2 Layered System Prompt（分层系统提示）

工程实践已经形成三层共识：

| 层级 | 内容类型 | 更新频率 | 示例 |
|------|---------|---------|------|
| **Permanent** | 角色定义、核心原则、禁止行为 | 极少 | CLAUDE.md 中的角色部分 |
| **Sticky** | 当前会话的任务上下文、用户 profile | 按 session | Dashboard 摘要、当前项目状态 |
| **Ephemeral** | 工具结果、当前步骤输出 | 每轮 | 文件读取内容、搜索结果 |

混在一起的危险：如果把 ephemeral 内容（工具输出）放在 permanent 内容（角色定义）前面，缓存 breakpoint 的位置就错了，永久层每次都得重新计算。

**OpenAI 的教训（来自 master_synthesis 的 Convergence D）：** 早期把所有指令放在单个 agent.md 里，一次性加载。上线后发现性能下降并且成本高。解决方案：改为目录页 + 子文档，启动时只加载 metadata，按需加载细节。这就是分层的工程价值。

### 2.3 上下文压缩策略

**策略光谱（从轻到重）：**

1. **截断（Truncation）**：最简单，丢弃最旧内容。问题：可能丢掉关键历史状态，没有语义保留。

2. **滚动摘要（Rolling Summary）**：每隔 N 轮，把旧对话压缩成摘要，替换原始内容。保留语义，丢失细节。

3. **结构化 Compaction**：Jason Liu 的核心主张（jxnl.co/writing/2025/08/30/context-engineering-compaction/）。不是无差别压缩，是用不同的专项 prompt 压缩不同类型的信息：
   - 失败模式检测 compaction：压缩关注 loops、linter 冲突、最近删掉的代码被重新写回
   - 用户反馈聚类 compaction：压缩关注纠正请求、偏好声明、工作流中断信号
   - 语言切换分析 compaction：关注 framework switches、跨语言调试

**Liu 的理论基础：** "If in-context learning is gradient descent, then compaction is momentum." 压缩不只是存储事实，是保留学习轨迹的方向（optimization path）。丢掉"我试了 X 失败了，然后 Y 成功了因为 Z"这条轨迹，相当于丢掉了 momentum，下一轮可能重蹈覆辙。

4. **Context Reset（Lopopolo 模式）**：不是压缩，是主动清空并重建。当 context 已经严重污染，或者任务边界非常清晰时（完成了一个独立子任务），用一个新 session 承载下一步，只把关键状态（不是完整历史）传入。

   **什么时候用 reset vs compaction：**
   - 任务完全独立，旧历史不影响新任务 → Reset
   - 任务连续，历史有因果关系但 context 过长 → Compaction
   - 中间出现了不可恢复的错误状态 → Reset

### 2.4 Attention Poisoning 和 Mid-Context Forgetting：真实证据

**"Lost in the Middle"（Liu et al., 2023）的核心发现（直接从 arxiv:2307.03172 获取）：**

- 在多文档问答和键值检索任务上，当相关信息在中间位置时，所有测试的语言模型性能都显著下降
- 即使是专门针对长上下文优化的模型也有这个问题
- 性能在开头和结尾最高，中间最低（U 形曲线）

**工程含义：**
- 关键约束应该放在系统提示的开头（或明确的末尾），不要被大量工具文档埋在中间
- 如果必须有长列表，把最重要的条目放在头部
- 这也是为什么"把所有工具说明都堆在系统提示里"是反模式：重要的约束被淹没在工具文档中间

---

## Section 3 — Memory 架构

### 3.1 为什么 Filesystem > Vector DB（刘 + Cherny 的收敛论证）

这是 2025-2026 年从业者圈子里最重要的反直觉收敛之一。

**为什么直觉上人们选向量库：**
- 语义搜索听起来更"智能"
- 向量相似度 = 语义相关性，理论上更精准的检索

**为什么实践中 filesystem 赢了（Jerry Liu + Boris Cherny 独立得出同结论）：**

1. **透明性。** 文件系统里的内容是 human-readable 的。可以 `cat`，可以 grep，可以 diff。向量库的内容是 embedding，不能直接检查。调试一个"为什么模型不知道 X"的问题，文件系统 5 分钟，向量库可能要半天。

2. **可靠性。** 文件系统检索（基于路径/名称/grep）是确定性的。向量检索是概率性的：相关文档可能被语义上相似但内容不相关的文档挤出 top-k。这种偶发失败很难复现和修复。

3. **结构可控。** 文件系统的层次结构（`80_Knowledge/83_Observations/habits.md`）本身就编码了知识的组织方式，和 agent 的导航方式一致。向量库的 namespace 概念没有文件系统的目录直观。

4. **工具支持。** 代码 agent 的工具链（Bash, Read, Grep, Glob）天然操作文件系统。向量库需要额外的客户端 SDK，增加了工具数量和失败面。

5. **源代码验证。** G1（github ecosystem scan）扫描了 Claude Code、Cursor、Aider，全部用 filesystem 作为 memory，没有一个用向量库。这不是偶然。

**什么时候向量库确实有价值：**
- 知识库超大（>100 万 token），无法放进 context，需要语义召回
- 多语言、多模态的内容需要跨形式检索
- 专门的 RAG pipeline 而非 agent memory

**对 MeowOS 的直接含义：** 继续用 `80_Knowledge/` 分目录文件。不要被"升级到向量库"的诱惑带偏。

### 3.2 三种状态必须分离：Session / Task / Long-term

**为什么分离是核心原则，不是风格偏好：**

**Session State（会话状态）：**
- 生命周期：一个 claude session
- 内容：当前对话的临时推理、工具调用的中间结果、当前轮次的待办
- 存储：只在 context window，不持久化
- 不该跨越的边界：session 结束后不应该残留在 long-term memory 里

**Task State（任务状态）：**
- 生命周期：一个任务的完整执行过程（可能跨多个 session）
- 内容：任务目标、当前进度、中间产物、失败历史
- 存储：文件系统里的任务专属文件
- 典型例子：MeowOS 的 `00_Dump/` 里的某个任务文件

**Long-term State（长期状态）：**
- 生命周期：跨时间、跨项目的持久知识
- 内容：用户偏好、已验证的事实、学到的模式、关系图谱
- 存储：`80_Knowledge/` 的结构化知识库
- 典型例子：MeowOS 的 `habits.md`、`87_People/`

**混淆的后果（concrete failure modes）：**
- Session state 写入 long-term → 临时的错误推断或特例污染长期知识
- Task state 和 long-term 混合 → 任务结束后遗留了"脏状态"，影响未来对话
- Long-term 全部塞进每个 session → context 被无关历史污染，注意力稀释

**master_synthesis 的诊断：** MeowOS 当前三类状态未明确分离，这是 B1 层最重要的改进方向。

### 3.3 MemGPT 的层级记忆模型

MemGPT（Packer et al., 2023 / arXiv:2310.08560，现在的 Letta 项目）的核心思想：把操作系统的虚拟内存管理搬到 LLM 的记忆管理里。

**OS 比拟：**
- CPU 寄存器 → Context Window（最快，最贵，容量最小）
- RAM → External Storage（可快速调入 context 的文件/数据库）
- 磁盘 → Long-term Archive（需要更多步骤才能访问）

**关键机制：Virtual Context Management**
- 当 context 接近上限，主动把不活跃内容"换出"到外部存储
- 当需要某段历史，通过工具调用"换入"
- 用"中断"机制管理自己和用户之间的控制流切换

**Letta API 里的 memory_blocks：** （来自 Letta README）
```python
memory_blocks=[
    {"label": "human", "value": "..."},   # 关于用户的持久知识
    {"label": "persona", "value": "..."}  # agent 的角色定义
]
```
这直接实现了 long-term state（human/persona blocks）和 session state（conversation）的分离。

### 3.4 mem0 的选择性检索 Pipeline

mem0（arXiv:2504.19413）的架构和 MemGPT 不同，目标也不同：

**设计目标：** 不是管理 context window，是在对话之间持久化个性化记忆，做 per-user 的长期学习。

**核心 Pipeline：**
1. 对话结束后，用 LLM 从对话中提取"记忆候选"
2. 检索现有记忆中相关条目
3. 对比：新信息是否和现有记忆冲突？是更新/合并/新增？
4. 写入向量存储（语义索引）+ 图存储（关系索引）

**benchmark 数据（mem0 README）：** vs OpenAI Memory，+26% 准确率，91% 更快响应，90% 更少 token 使用。

**为什么它用向量库而文件系统方案不用？**
因为 mem0 的场景是大规模多用户（SaaS），需要跨用户的语义检索，容量远超任何 agent 的 context window。单个 agent 的个人 KB 完全不是同一个规模。

**对 MeowOS 的含义：** mem0 的"提取-对比-合并"流程是好的设计模式，但底层存储用文件系统而非向量库更适合 MeowOS 的规模。MeowOS 的 `_staging.md` + `habits.md` 架构已经在做类似的事，但"合并/去重"步骤没有显式化。

### 3.5 Memory 误处理的具体失败模式

**失败 1：Session 污染 Long-term**
症状：agent 在一次对话中形成了错误判断（比如错误地推断用户的偏好），直接写入了 habits.md，后续所有 session 都被这个错误影响。
根因：写入长期记忆的触发条件太宽松，没有区分"这次对话的临时推断"和"已验证的稳定事实"。

**失败 2：Task State 遗留**
症状：任务 A 的中间文件（比如某个调试状态）被后来的任务 B 误读为稳定 knowledge，导致行为异常。
根因：任务结束时没有清理机制，或者任务文件和 knowledge 文件没有物理隔离。

**失败 3：Cross-session 记忆断裂**
症状：用户在 session 1 建立了某个重要上下文（"我在开发功能 X，需要特别注意 Y"），session 2 完全不知道，重新从零开始，反复确认已知信息。
根因：没有 task state 的跨 session 持久化机制。

**失败 4：Context Reset 时机错误**
症状：在一个有长历史的复杂任务中过早 reset，新 session 缺失关键的失败历史，重蹈之前的错误路径。
根因：把 context reset 当成"清理 context"而不是"跨越任务边界"的操作。

---

## Section 4 — Intent / Persona / Role 设计

### 4.1 System Prompt 作为 Computational Guide

Böckeler 的分类中，**computational guide** = 确定性、精确、可测试的指令集合，对应于传统软件工程里的"代码"，而不是"注释"。

**区别在于：**
- 装饰性 persona（"You are a helpful assistant"）= 注释。可以被覆盖，可以被模型的训练倾向稀释。
- Computational guide = 代码。包含精确的行为规则，有可验证的输出预期，违反时可以被检测。

**什么构成 computational guide 的内容：**
- 明确的决策规则（"当 X 发生时，做 Y，不做 Z"）
- 边界条件（"永远不做 A"）
- 输出格式约束（可以被自动验证）
- 优先级排序（"当 B 和 C 冲突时，B 优先"）

**什么不构成 computational guide 的内容：**
- 风格描述（"friendly and professional"）
- 模糊期望（"be thorough"）
- 无约束的角色描述（"you are an expert at X"）

### 4.2 好的 Persona 定义 vs 装饰性 Persona

**装饰性 Persona（反例）：**
```
You are a helpful AI assistant with expertise in data analysis. 
You communicate clearly and professionally. You are thorough and accurate.
```

这段话：
- 没有任何可测试的行为预期
- 所有形容词（helpful, clear, professional, thorough, accurate）都是训练数据里频繁出现的，模型本来就倾向于这样，这些"指令"基本没有新信息
- 遇到边界情况时，这段话完全无法帮助模型做决策

**有效 Persona（正例，来自 MeowOS CLAUDE.md 的逻辑）：**
- 明确的自称和称呼规则（可验证）
- 明确的语言跟随规则（可验证）
- 明确的禁止行为列表（可测试）
- 明确的文件读写委派原则（有操作后果）
- 明确的意图模糊处理规则（有决策路径）

**关键洞察：** 好的 persona 定义通过**约束搜索空间**来工作，而不是通过**描述期望行为**来工作。你不需要告诉模型"要专业"，你需要告诉模型"当你不确定用户意图时，先问清楚，不要猜"。后者才是约束。

### 4.3 IMPACT 的 Intent 和 Böckeler 的 Guides 的关系

两个框架说的是同一个层面，但侧重不同：

- **IMPACT Intent（swyx）**：偏功能性定义，"这个 agent 是为了什么目的而存在的"，是战略层。
- **Böckeler Computational Guide**：偏操作性定义，"这个 agent 在具体场景下应该怎么行动"，是战术层。

正确的做法：Intent 回答"为什么"，Guide 回答"怎么做"。两者都需要。只有 Intent 没有 Guide，agent 会泛化地接近 Intent 但在具体行为上漂移；只有 Guide 没有 Intent，agent 在 Guide 没覆盖到的情况下没有基础做推断。

### 4.4 系统提示的常见反模式

**反模式 1：厨房水槽（Kitchen Sink）**
把所有可能有用的信息都塞进系统提示：工具文档、背景知识、行为规则、角色描述、格式要求、示例……结果是：
- 注意力稀释（重要约束被淹没）
- 缓存效率低（内容太长且经常变化）
- 规则之间的冲突变多
- 没有渐进式披露，所有内容一次性加载

**反模式 2：矛盾规则**
常见于系统提示随着时间累积，新规则加进去但旧规则没有清理：
"你是一个高效专业的助手"（rule A）vs "你在懈怠时温柔提醒"（rule B）在特定情况下可以矛盾。
更危险的矛盾："不要读写文件"（安全规则）vs "帮我整理 KB"（任务期望），如果系统提示里这两条都有且没有优先级，模型会产生不确定行为。

**反模式 3：无优先级的规则列表**
10 条行为规则，条件之间有重叠，但没有显式的优先级顺序。模型在规则冲突时会依赖训练偏差来打破平衡，而不是按照你的意图。

**反模式 4：Role Description 替代 Behavior Specification**
"你是一个资深数据科学家" → 这告诉模型什么都行，因为"资深数据科学家"在训练数据里有无数种行为模式。
"当用户提供数据集时，先描述数据的形状和缺失值情况，然后再提出分析建议" → 这是行为规范。

---

## Section 5 — 模式与反模式汇总表

| Pattern 名称 | 解决的问题 | 适用场景 | 不适用场景 | 来源 |
|-------------|-----------|---------|-----------|------|
| **Subagent 隔离** | Context Pollution | 需要产生大量噪音输出的任务（测试、日志分析） | 任务需要和主线程持续双向交互 | Jason Liu, jxnl.co/2025/08/29 |
| **Prompt Caching** | 重复计算开销 | 有稳定 system prompt + KB 的多轮对话 | 内容变化频繁、cache miss 率高 | Anthropic docs |
| **Layered System Prompt** | 注意力稀释 + 缓存效率 | 所有 agent harness 设计 | 极简单的单轮任务 | 行业共识，5+ 来源 |
| **Structured Compaction** | Context Rot | 长时间运行的任务 | 任务完全独立、短 context 任务 | Jason Liu, jxnl.co/2025/08/30 |
| **Context Reset** | 严重污染 / 任务边界 | 子任务完成、错误恢复、长期项目的阶段切换 | 连续推理任务、历史必须传递 | Lopopolo, Symphony |
| **Filesystem Memory** | 透明性 + 可调试性 | 单 agent 或小规模 KB | 大规模多用户 SaaS 记忆系统 | Jerry Liu + Boris Cherny（收敛） |
| **三类状态分离** | Session 污染 / Task 遗留 | 所有跨 session agent | 短暂的无状态任务 | Weng 2023, IMPACT, MemGPT |
| **Computational Guide** | Persona 漂移 | 有明确行为约束需求的 agent | 开放性创意任务（约束反而有害） | Böckeler |
| **渐进式披露（Progressive Disclosure）** | 上下文膨胀 | 知识库大、工具多 | 所有信息都是每次必需的 | OpenAI agent.md 教训, Anthropic Skills |

---

## Section 6 — 四个具体失败场景

### 失败场景 A：Agent 指令飘移（Instruction Drift）

**症状：** Agent 在长对话中逐渐忽略系统提示里的关键约束，行为越来越接近"通用助手"而非预期角色。用户发现 agent 开始做被明确禁止的事，或者在不该自主决策的地方自主决策。

**信息层根因：** 系统提示的约束指令被 context 里的大量对话内容稀释，注意力权重降低。加上"Lost in the Middle"效应，长对话中系统提示在相对位置上已经是"中间"了。

**Canonical Fix：**
1. 关键约束放在系统提示的最前面（primacy）
2. 对话压缩时把关键约束重新注入（compaction 时加"约束提醒"块）
3. 或者周期性 context reset，确保新 session 从干净的系统提示开始

**谁讨论过：** Liu et al. 2023（Lost in the Middle 实验），Jason Liu（context pollution 分析）

---

### 失败场景 B：跨 Session 记忆丢失

**症状：** 用户建立的重要上下文（"我在 A 项目里，需要特别注意 Y 约束"）在 session 结束后消失。下一个 session 的 agent 完全不知道，要求用户重新解释，产生重复的确认问答。

**信息层根因：** Task state 没有从 session state 里分离出来持久化。Session 结束即状态消失。

**Canonical Fix：**
1. 在 session 结束时（或任务达到里程碑时）主动写入 task state 文件
2. 新 session 开始时的 startup 行为里加入"读取当前任务状态"
3. 区分 task state（任务特定，有限期）和 long-term state（跨任务，持久）

**谁讨论过：** MemGPT/Letta（virtual context management），MeowOS master_synthesis（三类状态未分离的缺口）

---

### 失败场景 C：重复犯错（Amnesia Loop）

**症状：** Agent 在同一个任务里，把已经试过且失败的方案再次尝试。用户意识到 agent 在兜圈子，每次失败后的重置让 agent 忘掉了之前的失败历史。

**信息层根因：** Compaction 丢失了失败轨迹。用"summaries of results"替换了"failed attempts + reasons"，新的 context 里看不到"我已经试过 X 了，它在 Y 情况下失败"。Liu 称之为 compaction 丢失了 momentum（学习方向）。

**Canonical Fix：**
1. Compaction prompt 里明确要求保留失败路径："compact focusing on: what was tried, why it failed, what the key constraint is"
2. 专设"死角列表"（dead-end log）作为任务状态的一部分，不参与 compaction，持久保留
3. Agent 在计划新行动前先查 dead-end log

**谁讨论过：** Jason Liu（jxnl.co/2025/08/30，compaction momentum 概念），Liu 的 Claude plays Pokemon 案例

---

### 失败场景 D：系统提示规则冲突导致的不可预测行为

**症状：** Agent 在特定边界情况下的行为完全不可预测，有时执行 A，有时执行 B，没有明显规律。调试时发现 A 和 B 都能在系统提示里找到支持。

**信息层根因：** 系统提示有矛盾规则，没有优先级定义。模型在规则冲突时依赖训练偏差打破平衡，结果取决于该边界情况在训练数据里更接近哪个规则的原型。这是随机的，不是确定的。

**Canonical Fix：**
1. 显式声明规则优先级（"当 A 和 B 冲突时，A 优先"）
2. 对系统提示做规则一致性审计：枚举可能的边界场景，检查规则是否给出唯一确定的行为
3. 矛盾规则通常来自"历史积累"，需要定期 GC（Lopopolo 的 garbage collection 原则在系统提示层面同样适用）

**谁讨论过：** Böckeler（computational guide 概念，隐含了规则精确性要求），Lopopolo（garbage collection，提示层面的熵积累）

---

## Section 7 — 学习者应该内化的心智模型

**1. Context 是信道，不是仓库。**
信道有容量上限、有位置敏感性、会被噪音稀释。管理 context 的思维模式不是"放多少信息"而是"保持信道质量"。把 context 当仓库的人会被 context pollution 和 attention dilution 反复打脸。

**2. 记忆的生命周期必须和它的用途匹配。**
三类状态（session/task/long-term）不是任意的分类，是根据"这个信息需要活多久才有用"来划分的。把短命信息放进长期存储 = 污染；把长命信息只存 session = 遗失。每条信息写入时应该有明确的生命周期预期。

**3. Persona 通过约束搜索空间工作，不通过描述期望工作。**
"你是个专业助手"描述期望，不约束行为。"当意图不明时，先问清楚再行动"约束行为。能被测试的才是真正的 guide；不能被测试的是注释。

**4. Compaction 不是"把长的变短"，是"保留因果链，丢弃执行细节"。**
把一段对话从 50k tokens 压到 2k tokens，如果只保留了最终结果而丢了导致结果的关键决策路径，那 agent 在后续遇到类似岔路时会重新出错。Compaction 的质量 = 保留了多少"为什么"，而不是保留了多少"是什么"。

**5. 系统提示是会积累熵的代码，需要定期 GC。**
每次"加一条规则"都没问题。500 条规则积累后，矛盾、冗余、过时的规则形成"提示债"。就像代码债。需要有人定期审计：这条规则还有效吗？和其他规则冲突吗？这也是为什么 MeowOS 设计了 improvement-queue + system-diagnostics session——这就是提示层面的 GC 机制。

---

## Section 8 — 延伸阅读与质量评级

| 来源 | 最适合的子主题 | 信噪比 | 备注 |
|------|-------------|--------|------|
| **jxnl.co Context Engineering Series** | Context Pollution, Compaction, Subagents | ★★★★★ | Jason Liu 本人从 LlamaIndex 咨询实践中提炼，有具体数字和架构决策 |
| **arXiv:2307.03172 (Lost in the Middle)** | Attention Dilution, 位置敏感性 | ★★★★★ | 同行评审，TACL 发表，有实验数据，是这个领域最常引用的证据 |
| **arXiv:2310.08560 (MemGPT)** | 层级记忆架构, Virtual Context Management | ★★★★☆ | 学术严谨，但现在项目已变成 Letta，部分接口已变化 |
| **mem0 README + arXiv:2504.19413** | 选择性记忆提取 Pipeline, 多用户记忆服务 | ★★★★☆ | 有 benchmark 数据，架构文档清楚，适合了解 per-user memory 服务设计 |
| **Anthropic Prompt Caching Docs** | Cache 机制细节, TTL, 断点设计 | ★★★★★ | 官方第一手，最权威 |
| **Eugene Yan LLM Patterns** | RAG, Evals, Guardrails 的系统视角 | ★★★★☆ | 覆盖面广，偏 survey，适合建立全局感，不够深 |
| **Letta README** | 层级记忆的当代实现，memory_blocks API | ★★★☆☆ | 接口文档清楚，但架构文档分散在多个子页，需要深挖 |
| **master_synthesis（本地）** | 框架映射 + MeowOS 审计底表 | ★★★★★（针对本场景） | 已经做了跨源映射，是 B1/B2/B3 的最好导航 |

**Harrison Chase (LangChain) 的相关内容：** 在 Sequoia 的 URL 和 blog.langchain.com/context-engineering/ 均无法直接获取文章内容（404/CSS-only）。已知立场（来自 master_synthesis）：Chase 的核心论点是"better models alone won't get your AI agent to production"，强调 harness 才是生产差距的来源。但 context engineering 的具体技术内容需要从其他渠道获取。

---

## Section 9 — 来源可靠性说明

| URL | 状态 | 说明 |
|-----|------|------|
| jxnl.co/writing/2025/08/28/context-engineering-index/ | **DIRECT** | HTML + text 成功提取 |
| jxnl.co/writing/2025/08/29/context-engineering-slash-commands-subagents/ | **DIRECT** | HTML + text 成功提取，有具体数字 |
| jxnl.co/writing/2025/08/30/context-engineering-compaction/ | **DIRECT** | HTML + text 成功提取 |
| jxnl.co/writing/2025/09/11/rethinking-rag-architecture-for-the-age-of-agents/ | **DIRECT** | HTML + text 成功提取（Beyang Liu/Sourcegraph 对话）|
| jxnl.co/writing/2025/08/27/facets-context-engineering/ | **DIRECT** | HTML + text 成功提取（独立一篇 facets 文章）|
| arxiv.org/abs/2310.08560 (MemGPT) | **DIRECT** | Abstract 成功提取 |
| arxiv.org/abs/2307.03172 (Lost in the Middle) | **DIRECT** | Abstract + key findings 成功提取 |
| github.com/mem0ai/mem0 README | **DIRECT** | README 成功提取，包含 benchmark 数据 |
| github.com/letta-ai/letta README | **DIRECT** | README 成功提取 |
| docs.anthropic.com/en/docs/build-with-claude/prompt-caching | **DIRECT** | 主要内容成功提取（Next.js 页面，非 HTML，通过文本提取）|
| eugeneyan.com/writing/llm-patterns/ | **DIRECT** | 完整文章成功提取 |
| blog.langchain.com/context-engineering/ | **FAILED** | 404 Page not found |
| sequoiacap.com/article/context-engineering-perspective/ | **INDIRECT** | 页面加载但主体内容未能提取（纯 CSS/JS，无文本内容） |

---

*生成时间：2026-04-14*
*B1 agent 作业完成。B2（执行层）和 B3（质量层）请见同目录其他文件。*
