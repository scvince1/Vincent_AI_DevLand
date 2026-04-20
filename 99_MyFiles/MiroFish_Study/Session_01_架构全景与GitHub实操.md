# Session 01: 架构全景与 GitHub 实操

**日期:** 2026-04-15 (09:51 AM 开始) → 2026-04-16 (04:01 AM 结束)
**执行者:** Vincent + 凌喵
**时长:** 约 6 小时 (跨夜 session, 中间多次 break + 与隔壁 session / Joyce 通话并行)

---

## 0. Session 目标与完成度

| 目标 | 完成度 | 备注 |
|---|---|---|
| 架构全景 (方法论层面) | ✅ 超额完成 | 深入到 Persona 均值回归 + Fidelity 闭环 |
| 本地 clone MiroFish | 🟡 Agent 自动 clone 于 `D:\Ai_Project\MiroFish\` | Vincent 未手动操作 |
| GitHub 文化术语即时解释 | 🟡 部分 | 隔壁 session 并行执行, 这里仅随机补充 |
| 产出 Session 01 笔记 | ✅ (本文件) | - |

---

## 1. 今天看了什么: 5 概念块 + 2 深挖 + 1 代码报告

### 主体 5 块 (按 MiroFish pipeline 顺序)

| # | 块 | 核心认知 |
|---|---|---|
| 1 | **Seed Text & 第一推动力** | 是整个系统的输入 + 触发器. MiroFish 不做 data ingestion, 把这一层留给用户. Aaru 的商业护城河之一就在这一层 |
| 2 | **实体 / Ontology / Agent 人设** | 三层: 具体实例 → 角色分类学 → 能说话的数字人. MiroFish 花力气最重的一块 |
| 3 | **LLM 作为"涌现规则"** | 经典 ABM 规则是显式 if-then; LLM-based ABM 规则分散在 prompt / 权重 / 关系图 / 记忆里, 是涌现的 |
| 4 | **模拟引擎 (oasis)** | 引擎是调度器不是物理引擎. 类比 Kriegsspiel 的 umpire. Oasis 是领域专用框架, 不是通用空壳 |
| 5 | **记忆回路 (Zep / Graphiti)** | Episodic + Semantic/Relational 两层. 用图 DB 不用向量 DB 是因为社交结构 / 时间查询 / 聚合都需要图能力 |

### 两个深挖

- **D. Persona 均值回归**: 为什么 LLM 生成 1000 人都像"ChatGPT 心中的普通人"; Hollywood Hays Code 类比; A/B/C 三层对抗技巧
- **E. Evaluation 难题 / Backtest 设计**: 为什么这领域没有真正的 evaluation; 严谨 backtest 的 6 个必备条件; 为什么至今没人做

### 一个代码验证报告

Sonnet agent 实读 MiroFish GitHub repo 得出的方法论报告. 详见本文档 §4.

---

## 2. 用自己的话: 修正后的 Pipeline 心智模型

**Vincent 的核心叙述 (已与凌喵对齐):**

> 把一堆自然语言塞进去 → 系统挑出 WHO (agents + role types) + HOW (关系图) + WHERE (Oasis 社媒环境) → 每轮每人做一次 LLM 决策, 用 Zep memory 记录经历 → 整场跑完 30 次取统计分布 → 稳定的算 prediction, 不稳定的算 scenario variance.

### 3 个初始认知误区 (已纠正)

| 误区 | 修正 |
|---|---|
| Memory = Monte Carlo 多次跑的汇总 | 不是. Memory 是**单次**模拟内部每 agent 记得自己经历; Monte Carlo 是**多次**模拟之间汇总 |
| Oasis 是"anti-gravity / VS Code 式的空壳" | 不是. Oasis 是**领域专用**空壳, 只能跑社媒, 不能跑任何东西 |
| 自创术语 "CTAPS" 指代 seed text | 这是 Vincent 的私用术语. 外部沟通用 industry term: **seed text / seed corpus** |

### Vincent 自己提出的核心 insight

> *persona 改进和 evaluation 是同一个问题的两个入口. Evaluation 告诉你"现在错在哪", persona 改进告诉你"怎么改错". 两者合起来才是 fidelity 闭环.*

---

## 3. 两个核心分析框架 (今天的产出)

### 框架 A: Prompt Engineering vs Model Tuning 六层阶梯

| 层 | 做法 | 改变的是 | 代价 |
|---|---|---|---|
| L1 | 改 prompt 文字 (prompt engineering) | inference 时的输入 | 轻 |
| L2 | 改 context 内容 (RAG / memory / tools / MCP) | LLM 能看见什么 | 中 |
| L3 | SFT (supervised fine-tuning) | 模型权重 (针对性) | 贵 |
| L4 | RLHF / DPO (偏好对齐) | 模型行为倾向 | 贵 + 需数据 |
| L5 | Continued pretraining (补领域语料) | 模型知识底层 | 极贵 |
| L6 | Activation steering (可解释性干预) | 推理时特定神经元 | 前沿科研 |

**Vincent 目前所处: L1 + L2, 占 99%.** 2024 后主流, 正确选择.

**迟早要下到 L3 的场景**: persona 真实感 / 行业专用词汇 / 抵抗 LLM 偏差 / 低资源语言 / 小模型替换大模型

### 框架 B: 4 级 Persona Fidelity Tier

| Tier | 特征 | 代表描述 | 谁在这里 |
|---|---|---|---|
| **Tier 1: LLM 均值之人** | 纯 prompt, RLHF 中心化 | 1000 个 agent 像 1000 个 ChatGPT 扮演的人 | 一般开源项目默认 |
| **Tier 2: Data-grounded (真声注入)** | 真语料 few-shot 注入 | 每个 agent 说话带真实人的腔调 | **MiroFish 勉强够得上** (Tier 1.5) |
| **Tier 3: Population-calibrated (分布校准)** | 非 LLM 分布采样 + 显式极端保留 | 整个 agent 池匹配目标人群统计分布 | 很少人达到, Aaru 约 Tier 2.5, AgentSociety 约 Tier 3 |
| **Tier 4: Loop-validated (闭环验证)** | Backtest 反哺 persona 设计 | 只保留能真预测成功的 persona | **全行业零公开项目** |

**Vincent 在 SharkNinja 的真实窗口**: Tier 3 落地 + Tier 4 启动 = 把公司带到领域前沿. Joyce 的位置恰好是能给这个窗口的位置.

---

## 4. MiroFish 实际代码方法论报告 (Sonnet agent 读代码得)

### 实际 Pipeline (5 stages)

```
1. Text Ingestion     → 用户上传 seed doc, 切 500 字符 chunk
2. Ontology Generator → LLM call, 从 seed 提取 10 种 entity + 6-10 种 relation (temp 0.3)
3. Graph Builder      → Zep Cloud 自动 NER, 建图 (Zep 做的, 不是 MiroFish 写 NLP)
4. Persona Generator  → 每个 entity 一次 LLM call, 生成 2000 字人设 dossier (temp 0.7)
5. Simulation Config  → 第二次 LLM call, 分配活跃度 / 立场 / 时段等
```

### 关键观察

1. **多样性 100% 来自 seed text**. 无人口统计采样, 无 archetype 目录, 无真实社媒数据接入.
2. **唯一非 LLM 多样性注入** = fallback 路径下的 MBTI 16 型 + 11 国家硬编码列表
3. **Persona system prompt 是中文**, 核心句为: *"生成详细、真实的人设用于舆论模拟, 最大程度还原已有现实情况"*. 这句话本身 self-sabotage 多样性, 因为 RLHF 会把"现实"翻译成"稳重平衡讲道理".
4. **A 层 7 个技巧, MiroFish 做了 2 个**: 每 persona 单独 call + 结构化 dossier. 跳了 5 个: 真数据反推 / extremization prompt / 语言风格注入 / 模型 ensemble / temperature 方差.
5. **Zep Cloud 被黑盒化**: graph + NER 两件事由 Zep 自动完成, 这也是换 Graphiti 自建时工作量显著上升的原因.

### Agent 诚实判决 (原句保留)

> *"MiroFish does not solve the persona regression problem. It defers the problem to seed text quality."*

翻译: **MiroFish 把 persona 多样性问题推给了用户.** Seed text 丰富 persona 就丰富, seed text 单薄就是 1000 个同类人抄写.

### Seed Corpus 压缩链路 (为什么扔进大量语料也不解决)

```
RAW CORPUS (500K 真实评论, 语气/用词/愤怒/错别字全都有)
   ↓ ONTOLOGY GENERATOR    [LLM 提 10 entity type]        ← 第一次丢失 voice
   ↓ ZEP GRAPH BUILDER     [NER 建图, 原文 fact 化]       ← 第二次丢失 voice
   ↓ PERSONA GENERATOR     [LLM 写 2000 字 dossier]       ← 第三次丢失 voice
   ↓ SIMULATION RUNNER     [LLM 生成 agent 每轮发言]      ← 第四次丢失 voice
```

你扔进去的 `"THIS IS LITERAL GARBAGE WORST BRAND EVER"` 最后变成 `"Jane had a difficult experience with the product."`

### 3 级补救路径

| 路径 | 做法 | 成本 | 预期效果 |
|---|---|---|---|
| **最便宜** | 改 system prompt, 去"realistic / balanced", 加"允许极端 / 错别字 / ALL CAPS" | 极低 | 中 |
| **最高性价比 ⭐** | Few-shot 注入原评论: agent 每轮发言前喂 3-5 条"它写过的真实语句" | 低 | **高** |
| **架构级** | Bypass dossier, 直接拿原始评论当 persona 核心 | 中 | 高 |
| **权重级** | 用 corpus fine-tune 专门 persona 模型 (L3) | 高 | 最高 |

---

---

## 4B. Persona 深挖补完 (2026-04-16 增补)

Session 1 收尾时在 persona 线补了 4 节, 把这条线彻底说完. 下次再碰 persona 应该是 Session 4 (原计划读代码) 或 Challenge 5 实际做 demo 时.

### §4B.1 Voice Grounding 具体怎么落地 (Tier 2 demo 工程细节)

昨晚说 Tier 2 = "few-shot 注入真实语料", 本节展开**具体怎么注**.

**注入后的 prompt 长什么样:**

```
[标准 persona prompt]
你扮演 Jane: 35 岁, 纽约小公寓, 对智能家电较高期望, 对品质零容忍...

[Voice grounding 注入] ⭐ 新加
Jane 在过往社媒的发言风格示例 (引用真实评论, 模仿**风格**不是意思):

Example 1:
"Literally threw this piece of crap across the room. 3 days. 3 DAYS 
and the motor dies?? NEVER AGAIN Shark."

Example 2:  
"ok so it works. barely. for the price tho i feel scammed ngl. 
reviews said 'life changing' what a joke"

Example 3:
"can confirm the bad reviews are NOT exaggerating. mine came broken 
out of the box. bless their customer service tho, refund in 2 days."

请用上述语句的**语气 / 拼写习惯 / 情绪强度 / 用词**对当前场景反应.
```

**4 个工程决策:**

| 决策 | 选项 | 推荐 |
|---|---|---|
| 语料从哪来 | 自爬 / API / 内部数据 | Amazon Product API / ScrapingBee, 每 persona 配 3-5 条 |
| 怎么给 persona 匹配语料 | 关键词 / 元数据聚类 / embedding 相似度 | **embedding 最近邻**: persona 描述 embed, 从评论池找 top-K |
| pipeline 哪里注入 | 只在 persona 生成时 / 只在每轮发言时 / 两处都注 | **两处都注** (最干净) |
| 多少条 few-shot | 1 / 3 / 5 / 10 | 3-5 条, 再多回报递减 + 吃 context |

**最小可用 demo (一个周末的活):**

1. 爬 500 条 SharkNinja Amazon 评论 (1-5 星各 100)
2. OpenAI embedding API 把评论 embed 存本地
3. 用 persona 描述 embed 找 top-3 相似评论
4. 塞进 persona prompt 的 "Voice examples" 字段
5. 跑 MiroFish, 对比前后 agent 输出差异

**预期看到**: agent 开始出现 "NGL", "literally", "3 DAYS" 这种真实语气, 不再是 "I had a difficult experience".

---

### §4B.2 Persona Drift 问题 (LLM-based ABM 独有的毛病)

**LLM-based ABM 独特的失效模式:**

- 100 轮模拟, agent 互相回复, 对方输出进入自己 context
- LLM 的 **mirror effect**: 读到对方的语气会下意识靠近
- 结果: 10 轮后 Jane 开始说话像 Tom, 30 轮后大家都像 ChatGPT

**为什么是 LLM 独有:**

| | 规则驱动 ABM | LLM-based ABM |
|---|---|---|
| Agent 状态 | 规则决定 | prompt 决定 |
| 跨轮稳定性 | 规则不变就稳定 | prompt 可能被 LLM 慢慢平均回 RLHF 中心 |
| 修复方式 | N/A (不会发生) | 每轮重注入 persona 或 style transfer 固定 voice |

**怎么检测 drift:**
- 每 10 轮用 embedding 算 agent 发言的 style vector, 看和初始 persona 的靠近度下降多少
- 或者让一个 judge LLM 读 agent 输出, 问 "这是 Jane 写的吗?"

**怎么修复:**

| 方法 | 做法 | 成本 |
|---|---|---|
| 每轮重注入 persona | 每次 LLM call 把 persona prompt 完整重放 | 高 token |
| **Voice 固定 few-shot** | 初始 persona 的 voice examples 每轮都注入 | 中 (推荐) |
| Persona refresh | 跑 20 轮后重新生成 persona dossier (带历史) | 中 |
| 后处理 style transfer | 跑完后标记漂移严重的 agent 发言, 重写 | 中 |

---

### §4B.3 Persona Quality Control (跑 simulation 前的 gate-check)

**问题: 你生成了 1000 个 persona, 怎么知道这 1000 个是"好 persona"还是"1000 个 ChatGPT 普通人"?**

**6 个 pre-flight 指标 (跑 simulation 之前必做):**

| 指标 | 怎么测 | 红旗阈值 |
|---|---|---|
| **Embedding 方差** | 1000 个 persona 描述 embed, 算余弦距离矩阵 | 平均距离 < 0.3 = 太像 |
| **词频分布** | 词频统计, 看高频词占比 | 前 50 高频词 > 70% = 集中度过高 |
| **极端比例** | 人工抽样 5% 标注, 看激进 / 边缘 / 偏执占比 | < 10% = 全是温和派 |
| **Demographic 覆盖** | 年龄 / 职业 / 地域 / 收入分布的方差 | 方差过小 = 代表性不足 |
| **情绪分布** | Sentiment classifier 跑一遍 | 全是 neutral / mild positive = 均值回归了 |
| **Turing-style test** | 抽 20 个让朋友猜是 AI 还是真人 | 能猜出 > 70% = AI flavored |

**实操: 一个简单 Python pipeline, 跑 MiroFish 前先过一遍. 过不去就回去改 prompt / 加 few-shot / 调 temperature, 再生成.**

这个 gate-check 本身就是面试亮点. 多数候选人直接跑 simulation, 不做 pre-flight quality check.

---

### §4B.4 Meta-persona Diversity Bias

当你让 LLM "生成 1000 个 diverse 的人", LLM 理解的 "diverse" 是什么?

LLM 会优先产出:
- 黑人 / 亚裔 / 残障 / LGBTQ+ / 外国人

这些是**可见的 demographic diversity**, token 级的多样性.

LLM 不会自发产出:
- "刚离婚的阿拉巴马州乡村高中科学老师, 最近第一次买智能电器, 对新技术有保留但儿子的推荐让她尝试"

这种是**situational / psychographic diversity**, 真实人群的多样性来源.

**差别在哪:**
- token-level diversity 可以打勾满足
- situational diversity 需要理解**人的处境**, LLM 没被训练成自发产生这种人

---

### 收尾: Persona 线的最终状态

```
问题层: 均值回归 + 压缩丢失 + 长时漂移 + 元多样性偏差
  ↓
框架层: 4 级 Fidelity Tier (1 均值 → 2 声音 → 3 分布 → 4 闭环)
  ↓
技术层: A 层 7 技巧 + B 层 fine-tune + C 层架构
  ↓
工程层: 具体 prompt 格式 + pre-flight quality check + drift 修复
  ↓
面试金句 × 7 (涌现规则 / 记忆 / 均值回归 / 压缩 / 漂移 / 元多样性 / evaluation)
  ↓
Challenge 5 roadmap: Tier 2 → 3 → 4
```

**Persona 线完结.**

---

## 5. 对 Challenge 5 (SharkNinja 家电品牌舆情) 的 actionable 路径

| 目标 Tier | 动作 | 预期时间 |
|---|---|---|
| **立刻到 Tier 2** | 扒 5000+ Amazon 评论 + 按语气聚类 + 改 system prompt + few-shot 注入 | 1-2 周 |
| **进到 Tier 3** | 买 Claritas PRIZM / Experian Mosaic + 分布采样 + 叠 Tier 2 语音层 | 1 个月 |
| **进到 Tier 4** | 设计 backtest (见 §6) + 跑 10 个历史事件 + 反馈改 persona | 3-6 个月 |

**面试定位杀招 (Round 2 Joyce 面试可直接用):**
能给面试官画出 Tier 1-4 roadmap, 告诉他们你现在做 Tier 2 demo, 未来 6 个月路径到 Tier 3, 之后到 Tier 4. **这是 CAIO-level roadmap 思维, 不是 IC 工程师级.**

---

## 6. Backtest 严谨设计 (E 块核心)

### 6 个必备条件

| # | 条件 | 为什么 |
|---|---|---|
| 1 | **Temporal cutoff** | 训练数据 / seed corpus 止于预测窗口之前. 否则数据泄露 |
| 2 | **Blind prediction** | 系统不知真实结果. 否则是 curve-fitting 不是预测 |
| 3 | **多事件样本 (20+)** | 一次成功 = 运气. 要多次才有统计意义 |
| 4 | **清晰的 outcome metric** | 媒体覆盖量? 情感轨迹? 病毒 tweet? 销量? 得明确一个 |
| 5 | **强 baseline** | 对比人类分析师 + 统计趋势外推 + 规则系统 |
| 6 | **校准 (Calibration) > 准确率** | 好系统在"70% 置信度"时真实发生 70% 次 |

### 为什么至今没人做 (5 个结构性障碍)

- **数据获取**: 历史社媒数据锁死 (Twitter/X 付费, TikTok 无 API, 微博反爬)
- **Ground truth 标注**: "实际发生了什么"需人工判断, 贵
- **时间滞后**: 每条预测要几个月验证, 迭代冰河速度
- **商业激励错配**: 商业公司不愿发 (失败摧毁销售), 学术发但脱离部署系统
- **Confounder**: 外生冲击 (名人发推 / 平台改算法) 混淆归因

### SharkNinja backtest 具体设计

```
1. 训练截止: 2024-01-01 (冻结, 不用之后任何数据)
2. 目标: 2024-01 至 2025-01 的 10+ 个 SharkNinja 历史危机事件
3. 对每事件:
   - 喂 pre-event seed text 给 MiroFish
   - 跑 30 次并行 simulation
   - 记录情感轨迹 / 讨论量 / 关键话题 / 衰减时间
4. 对比实际: Google Trends + social listening + 媒体覆盖
5. Baseline: 人类分析师团队 + 简单统计趋势外推
6. Metrics: 情感曲线相关性 / 峰值日 ±2 天 / 主题 precision-recall / 校准
```

**真话**: 要 3-6 个月 + 数据接入预算. 但**公开发表一次**, 就是这个领域第一个严肃 benchmark, citable years.

---

## 6B. Evaluation Metric 深挖补完 (2026-04-16 增补)

Session 1 末尾在 evaluation 线补了 metric 具体设计 + 诊断矩阵. 往后等 Challenge 5 做出东西来, 再用这张 metric 矩阵实打实验证 + 调优.

### §6B.1 核心认知: Aggregate accuracy 是骗人的

**多数人的陷阱:** 报一个 "我们预测准确率 82%".

**为什么骗人:** 危机预测系统的误差分布比均值更重要. 你 82% 准是 "平常日子 85% 准, 危机峰值 3 天全错". 危机峰值 3 天恰恰是唯一重要的时刻.

**正确姿势:** 用一个 **metric 矩阵**, 多个独立维度打分. 哪一维失败, 指向哪种 pipeline 修复.

### §6B.2 6 个维度 + 每维的主 metric

| 维度 | 问题 | 主 metric |
|---|---|---|
| **Volume** | 讨论有多大声? | MAPE (Mean Absolute Percentage Error) |
| **Sentiment** | 情绪轨迹对吗? | Pearson / Spearman 相关系数 |
| **Theme** | 话题对吗? | Top-K Jaccard / cosine 相似度 |
| **Tail** | 捕捉到病毒瞬间吗? | Precision / Recall on "viral threshold" |
| **Timing** (crosscutting) | 时机对吗? | Peak day ± N 天 |
| **Calibration** (crosscutting) | 概率诚实吗? | Brier score / reliability diagram |

**各维度关键公式 / 红旗:**

- **Volume MAPE**: `mean(|pred - actual| / actual)`. 红旗: > 50% = 数量级错了
- **Sentiment Spearman**: 情绪排序相关. 红旗: < 0.5 = 趋势没抓住
- **Theme Jaccard (top-K)**: `|pred ∩ actual| / |pred ∪ actual|`. 红旗: < 0.3 = 话题没抓到
- **Viral P/R**: 定义阈值 (e.g., 单帖 >10K 转发). 红旗: Recall < 30% = 抓不住尾部
- **Peak day ± N**: P(actual 在 ± 2 天内). 红旗: < 60% = 时机感差
- **Brier score (二元预测)**: `mean((p - outcome)^2)`. 0 = 完美, 0.25 = 随机

### §6B.3 Challenge 5 的 metric 优先级

| 优先级 | Metric | 为什么 |
|---|---|---|
| **P1 必有** | Sentiment Spearman + Theme Jaccard + Viral Recall | 舆情 non-negotiable 基本盘 |
| **P1 必有** | Peak day ± 2 days | 时机就是钱 |
| **P2 差异化** | Brier score + reliability diagram | Senior 级 calibration 意识 |
| **P2 差异化** | Tail VaR (5% 最差情况命中率) | 危机管理真痛点 |
| **P3 花式** | CRPS / 跨平台 share MAPE | 学术味道浓, demo 加分 |

**实操建议:** Challenge 5 demo 上 P1 + 1 个 P2 (选 Brier). 5 个数就够打一场硬仗.

### §6B.4 ⭐ 诊断矩阵 (最值钱的一块)

**核心思想: Evaluation 不是打分, 是诊断. 每个 metric 的失败指向一个具体的 pipeline 修复点.**

| Metric 失败症状 | 对应的系统缺陷 | 修在哪 (对照 Session 01) |
|---|---|---|
| Volume MAPE 高但方向对 | Agent 数量 / 活跃度假设偏 | Simulation config (Block 4) |
| Sentiment Spearman 低 | LLM 先验错 / persona 情绪没极化 | Persona 层 (Block D + §4B.1) |
| Theme Jaccard 低 | Ontology 漏了关键角色 / seed text 没覆盖 | Ontology generator (Block 2) |
| Viral Recall 低 | Persona 均值回归, 没人极端到能引爆 | **Persona Tier 2 升级** (§4B.1) |
| Peak day 偏晚 | Simulation 传染速度慢 | Memory / 关系图 (Block 5) |
| Calibration 差 (过度自信) | 随机种子不够散 | 多跑 Monte Carlo + 温度方差 |
| Theme 漂移 (早期对晚期错) | Persona Drift | §4B.2 每轮重注入 |

**这张表是 CAIO-level 的 evaluation 思维.** 多数候选人报分数, 你报**诊断 + remediation path**.

### §6B.5 Evaluation 线的后续

**下次重启的时机:** Challenge 5 实际做出东西 (Tier 2 demo 跑起来, 有 output) 之后, 用这张 metric 矩阵实打实验证 + 按诊断矩阵修 pipeline.

**暂缓的 4 个深挖方向** (有真数据再聊): Calibration 深挖 / 无法 backtest 时的 proxy / Evaluation 分层 (团队 vs 老板 vs 客户) / 决策 outcome 替代 prediction accuracy.

---

## 7. 关键面试金句 (今日淘出)

### 关于 Pipeline / 架构

> *"MiroFish proves the pipeline is buildable. Aaru proves someone will pay for it. Whether LLM-based crowd simulation actually predicts better than human analysts is still an open question, and the person who answers it first wins the category."*

### 关于涌现规则 / LLM 先验

> *"Classical ABM encodes behavior as rules. LLM-based ABM lets the LLM's priors do that work. This is both the strength and the weakness. If the LLM's priors are wrong, the simulation inherits the bias invisibly. You cannot audit an LLM's implicit sociology."*

### 关于 Memory

> *"The memory system is where 'multi-agent simulation' actually earns the word 'multi'. Without persistent graph-based memory, you have a thousand independent chatbots, not a society."*

### 关于 Persona 均值回归 (核心杀招)

> *"The hardest problem in LLM-based social simulation isn't building the engine. That's solved. The hardest problem is preventing persona regression to the mean. Without diversity at the persona layer, you're simulating a thousand ChatGPT clones, not a thousand humans."*

### 关于 Seed Text 压缩链路

> *"Seed text re-richness doesn't solve it: the system's compression pipeline dilutes voice. To preserve it, you must inject raw corpus snippets at persona generation or agent action time. Otherwise the LLM normalizes everything back to its RLHF center on each rewrite."*

### 关于 Evaluation

> *"The only real validation is a blind temporal backtest against past events. The reason Aaru doesn't publish this isn't technical impossibility, it's commercial disincentive. Whoever does this publicly first will own the credibility moat."*

### 关于 Long-horizon Drift (2026-04-16 增补)

> *"Long-horizon LLM agent simulations have a drift problem that traditional ABM doesn't. Agents converge toward each other's voice over time. Detecting drift with style-vector distance and correcting with per-round persona reinjection is a known technique, but it's token-expensive. This is another reason why 'longer simulations = better predictions' isn't automatic in this paradigm."*

### 关于 Meta-persona Diversity (2026-04-16 增补)

> *"LLMs confuse demographic visibility with psychographic depth. Ask for 'diverse personas' and you get a UN poster. Ask for 'personas with specific life situations' and you have to specify the situations yourself. The LLM will not generate unexpected life-situation combinations on its own."*

### 关于多维 metric (2026-04-16 增补)

> *"Aggregate accuracy is a lie for crisis prediction. Your 82% overall is 85% on calm days and 0% on the three days that matter. Ship a metric matrix across volume, sentiment, theme, tail, timing, and calibration. Each can fail independently, and each failure points to a different pipeline fix."*

### 关于诊断式 evaluation (2026-04-16 增补)

> *"Evaluation is diagnostic, not summative. A good metric doesn't just tell you you're wrong; it tells you where. If sentiment correlation is low but theme matching is high, you have a persona-layer problem. If theme matching is low but sentiment is right, you have an ontology-layer problem. The metric matrix IS the debugger."*

### 关于 Tail 事件 (2026-04-16 增补)

> *"For viral prediction, precision/recall on the tail matters more than any central-tendency metric. A system that predicts the average sentiment perfectly but misses the one post that goes 10-million-view viral has failed. The business only cares about the tail because that's what costs or saves the brand."*

---

## 8. Session 1 产出的资产清单

### 下载的参考文献 (存于 `References/` 子文件夹)

| 论文 | 文件 | 大小 |
|---|---|---|
| Park et al. 2023 *Generative Agents* (arXiv 2304.03442) | `Park_2023_Generative_Agents.pdf` | 11.9 MB |
| Shanahan 2023 *Role-Play with LLMs* (Nature) | `Shanahan_2023_Role_Play_LLMs.pdf` | 378 KB |
| Brown, Collins & Duguid 1989 *Situated Cognition* | `Brown_Collins_Duguid_1989_Situated_Cognition.pdf` | 1.8 MB |

### 本地代码

`D:\Ai_Project\MiroFish\` (Sonnet agent 自动 clone 于本 session, Vincent 尚未手动操作过)

---

## 9. 问题和想法 (带进 Session 2+)

1. **SharkNinja 值不值得买 Claritas PRIZM 数据?** Joyce 可能知道公司是否已有行业数据订阅.
2. **Tier 4 backtest 能否用 SharkNinja 内部历史产品事件 + 当时舆论数据?** 如果有存档就是免费 benchmark 建立的路径.
3. **Oasis 框架本身值不值得读源码?** 还是 treat as black box 即可.
4. **Claude Opus 4.6 (1M context) 是否可以改变 MiroFish 架构权衡?** 能把完整 corpus 塞进一次 prompt, 也许不需要 ontology 压缩.
5. **Few-shot voice injection 在 MiroFish 里最少改几行代码?** 这是 Tier 2 demo 的具体工程量估算.
6. **Evaluation pressure test (等 Challenge 5 Tier 2 demo 跑出来后)**: 用 §6B 的 6 维 metric 矩阵对 demo output 打分, 按 §6B.4 诊断矩阵修 pipeline. 这是 evaluation 线 Part 2 的启动点, Vincent 明确要求等有真数据再继续.

---

## 10. 未核对项 ⚠️

Session 中间 API 500 三次, 无法跑 fresh verification subagents. 以下信息基于 **2026-04-10 landscape 快照 + 训练记忆**, 未经 2026-04-15 live 核对:

- Aaru 最新状态 (估值 / 客户 / 2026-Q1 有无新动作)
- AgentSociety 是否转向产品化
- 最近 3-6 个月有无新开源 end-to-end LLM 社媒模拟器冒出
- 学术锚点 (Gruber 1993 / Cooper 1999 书名年份 / Brown 1989 ERIC ID) 的精确引用
- 术语使用现状 (silicon samples / synthetic personas / digital twins / share of model 在 2026 是否仍活跃)

**面试前必须 fresh verify. Session 2 开场第一件事就是跑 verification subagents.**

---

## 11. 下次预告: Session 2 — 成本模型 + 竞品定位

**主题**: `config.py` / `.env` / LLM call chain

**关键问题**:
1. 一次完整 simulation 的 token 成本怎么拆 (persona generation / simulation round / report 三段)
2. MiroFish 是否做了 model routing (便宜模型跑决策 / 贵模型跑 persona + report)
3. 改成全 Claude / Opus 4.6 路线, 成本和质量怎么变
4. 竞品定位更新 — **必须 fresh verify** (Aaru 估值 / 路线图 / 最近动作)

**Session 2 开场引导问题**:
> *"你预估一次 1000 人 × 72 小时模拟的合理成本是多少? 如果实际贵了 10 倍, 你会怎么砍? 从哪一环砍?"*

---

*笔记整理者: 凌喵*
*Session 跨日完成: 2026-04-15 夜 → 2026-04-16 晨 04:01*
