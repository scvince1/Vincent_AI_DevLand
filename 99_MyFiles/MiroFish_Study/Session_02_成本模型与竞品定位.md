# Session 02 — 成本模型与竞品定位

**日期**: 2026-04-16 (Thu)
**对象**: MiroFish 成本架构 + LLM 代理模拟空间竞品定位
**文件范围**:
- MiroFish: `config.py` / `.env.example` / `simulation_config_generator.py` (992行) / `oasis_profile_generator.py` (1205行) / `llm_client.py` / `retry.py` / `run_parallel_simulation.py`
- OASIS 框架: `github.com/camel-ai/oasis` v0.2.5 (`SocialAgent` / `UserInfo.to_system_message` / `chat_agent.py` / `env.py`)

---

## 1. 今天看了什么

### 1.1 Session 1 未核对项 fresh verify 结果 (2026-04)

| 目标 | 核对结果 |
|---|---|
| Aaru | Dec 2025 Series A, $50M+ @ $1B headline (分层估值, Redpoint 领投). 已 pivot 成 "Lumen" B2B 消费预测. 客户: Accenture/EY/IPG. 单 sim $0.08, GM 75%, ARR <$10M. 2024 大选 MI/NV/PA/WI 全错. Nate Silver 2026-04-11 宣布 AI 民调 "fake polls", 不入 Silver Bulletin 聚合 |
| AgentSociety | 清华 FIB 实验室 (非复旦), PI 李勇, Jinghua Piao 第一作者. v2.1.5 发布 2026-04-15. 10K agents × 5M interactions 公开 scale 记录. 成本零披露, 无量化 validation. GitHub 937★ |
| 新入场重磅 | **Simile** — Stanford spinout (Joon Park + Percy Liang), 2026-02-12 $100M Series A (Index 领投, Bain + Fei-Fei Li + Karpathy 天使), CVS Health 客户, 用"1000人 qual 深访 + 行为科学文献"训练. **Qualtrics Edge Audiences** credit 计价, 25年 response 数据 fine-tune (最强 incumbent). Lakmoos €10K, Artificial Societies $40/月 (价格底部) |
| BigCo 动态 | YouGov 公开唱衰, Ipsos 谨慎, Kantar 积极. McKinsey/BCG 无公开产品. Anthropic/OpenAI/Block 推 Agentic AI Foundation (Linux Foundation, 基础设施非 sim 产品) |
| MURM | 全网无匹配. Vincent 后确认: 语音输入错误, 无效 |

### 1.2 MiroFish 代码扒掘

**Repo**: `github.com/666ghj/MiroFish`, 55.6K★, 作者郭航江 (盛大集团), 陈天桥 24h $4.1M 投资, 基于 CAMEL-AI OASIS 框架

**默认参数**:

| 参数 | 值 | 谁决定 |
|---|---|---|
| agent 数 | = entity 数 (1:1) | Zep 图谱上游 |
| total_simulation_hours | 72 (可 24-168) | LLM 动态 |
| minutes_per_round | 60 (dataclass default) / 30 (run_parallel fallback, 冲突) | 两处不一致 |
| Monte Carlo | **无此机制** | N/A |
| 模型 | gpt-4o-mini (config.py hardcode) / Qwen-plus (.env 推荐) | .env 注入 |
| prompt caching | **未调用** | N/A |
| 并发控制 | ThreadPoolExecutor(2) + Semaphore(30) + asyncio.gather | 有 |

**关键冲突 (未解)**: `config.py` 有 `OASIS_DEFAULT_MAX_ROUNDS=10`, 与 `total_hours=72` 可能存在 override 关系. Session 3 开头第一件事验证。

### 1.3 OASIS 框架底层机制

**Agent 生命周期**:
1. `generate_twitter_agent_graph(profile_path, model, actions)` 读 profile JSON → 构造 `UserInfo` → 实例化 `SocialAgent` → 入 `AgentGraph`
2. `oasis.make(agent_graph, platform, semaphore=30)` → `OasisEnv`
3. `env.reset()` 启动 platform + 注册 agents
4. 每轮 `env.step()` → `async with llm_semaphore: await agent.perform_action_by_llm()` → asyncio.gather 并发

**Persona 注入**: **一次性写入 system_message, 跨轮持久**. MiroFish 传的 profile JSON 只在 `SocialAgent.__init__` 解析一次. (Session 1 "每轮重注入" 假设错误已修正)

**每轮 LLM call prompt 构造**:
- System: 固定模板 "You're a Twitter user..." + description (~500 tok)
- User: `await env.to_text_prompt()` 含 "I have X followers" + "see posts: {posts}" (~1500 tok, 随 post 数线性涨)
- Tools schema: **30 个 function 每次全量带** (~900 tok, 无 filter)
- Memory: 跨轮累积全部 system+user+assistant 消息 (**无 window 无 summarization**, 仅 token_limit 硬截断)
- Output: 1 tool call (~200 tok)

**隐藏二次爆炸点**: OASIS memory 累积机制. 长 sim 后期每 agent memory 累到 20-50K tok, 远超学术快 experiment 的 4.8K tok/trial 均值。

---

## 2. 用自己的话解释

### 2.1 成本三段占比 (单平台 1000 agents × 72 rounds, 考虑 memory 累积)

| 段 | token/sim | 占比 | 是什么 |
|---|---|---|---|
| Persona 生成 | ~19M (15M in + 4M out, 一次性) | ~2% | 每 entity 一次 LLM call 生成 profile JSON |
| **Simulation round** | **~1B** (1000 × 72 × 14K avg per turn) | **~97.5%** | 每 agent 每轮 1 次 call, memory 累积是主推 input |
| Report | ~0.4M (章节 × (1+5 tool + 2 reflection)) | ~0.1% | max_tokens=4096 |

### 2.2 $100K 估算校准

Vincent 估: 15B token × Sonnet ≈ $100K per sim.

修正 (代码证据):
| 模型路线 | 单 sim 成本 | 备注 |
|---|---|---|
| Qwen-plus / GPT-4o-mini | **$100-$1K** | MiroFish 默认路径 |
| Sonnet 4.5 全路 | **$2K-$6K** | 升档但不到 $100K |
| Opus 4.6 全路 | **$10K-$25K** | memory 满载 + Opus 接近原估 |

**两个假设错误**:
1. Monte Carlo 30 次 — MiroFish 不做 MC, 删 30x
2. 默认 Sonnet 全价 — 实际默认 Qwen-plus, 差 20-50x

**直觉方向对** ("超过 $1M 说明架构有问题"), 但 $100K 是 Opus 全路 + memory 最大累积的上界, 非 default 场景。

**真实商业档位**:
- $100-200 (Qwen): 日常 / demo
- $2K (Sonnet): 关键决策
- $10K (Opus + 1M context): 年度战略

与 Vincent 商业直觉 "单次几百刀" 吻合。

### 2.3 95% 成本集中在 simulation round

任何不碰 simulation 的砍法 = 无效. 砍法四家族:

| 家族 | 动作 | 省率 | 精度代价 |
|---|---|---|---|
| 砍量 | agent / turn / MC 减少 | 10-30x | 统计显著性崩 |
| 换路由 | 便宜模型跑决策 / 贵模型跑 persona+report | 5-15x | 中低 |
| 改范式 | embedding+rule 替代多数 turn, LLM 只关键节点 | 20-100x | 高, 要重写内核 |
| 换存储 | persona 向量化 + behavior model (distilled) 代替 LLM | 50-200x | 最高, 等于 re-architect |

前两个是"调参", 后两个是"重写". Vincent "每个部件都砍" 的直觉对, 但优先级偏 — simulation > persona > report。

### 2.4 Memory 累积是之前 miss 的变量

学术均值 4,800 tok/trial 是快 experiment 值. OASIS 实情是 memory 无限涨, 72 轮后期每 agent input 累到 20-50K tok. 推升成本估算 3 倍。

**推论**: MiroFish 商业化跑 72 轮 sim 必须加 summarization hook (OASIS 不原生支持, 要 fork)。

这解释了为什么 MiroFish 第三方实测 44 agents × 10 rounds ≈ $0.06 (memory 未爆), 但线性外推到 1000 × 72 会严重低估。

### 2.5 MiroFish 架构三个设计缺口 (= Vincent fork 的三刀)

| 缺口 | 后果 | Fork ROI |
|---|---|---|
| 无 Anthropic prompt caching | System(500)+Tools(900) prefix 每轮每 agent 白付全价, 100M token 白走 | **最高**. Cache read 便宜 10x, 单 sim 省 $270+ (Sonnet级) |
| 无 model routing (quality) | Opus 跑 simulation 烧钱, Qwen 跑 persona 质量差 | **次高**. 分层可降 5-10x |
| 无 budget guard prompt | LLM 决定时长时不知道钱, 随便开 168h | **低成本高 ROI**. 改一行 prompt 省 2-5x |

### 2.6 Agent 数 = entity 数, 规模卡在上游

`simulation_config_generator` 不决定 agent 数. Entity 数由 Zep 图谱从种子文本抽取. **Session 3 的主题正是这条链路**: `text_processor.py` → `ontology_generator.py` → `graph_builder.py`.

Challenge 5 落地: 一条 SharkNinja Amazon 差评作为种子 → Zep 抽出 N 个 entity → 一次 sim 跑 N 个 agent。

### 2.7 纯远程 API 架构 (对比学术论文 self-host)

| 路线 | MiroFish | OASIS 原论文 |
|---|---|---|
| 推理 | 远程 API (阿里云/OpenAI) | Llama3-8B 自托管 27×A100 |
| 前期投入 | $0 | GPU 硬件 $$$$ |
| 适合 | 商业化 / 初创 | 学术 / 大厂数据中心 |
| 证据 | 全 OpenAI SDK 格式, 无 CUDA/vllm/torch 依赖 | arxiv 2411.11581 |

**临界点**: 稳定月消耗 >10B token 时 self-host 划算. MiroFish 当前远低于该线, API 是对的。

**未来分叉**: 若做 SharkNinja domain fine-tune persona, 进 training 区, 需本地 GPU 或 vendor FT 服务 (4-10x inference 单价). Aaru 的 "20K H100-hr 训 1M digital citizens" 是 training, 非 inference. Session 6+ 课题。

### 2.8 Prompt Caching 本质 (今天新 get 的概念)

**起源**: LLM API 按 token 计费, prompt 里大段反复不变内容 (system / tools schema / few-shot examples) 每次都重付钱。

**机制** (Claude Opus 4.6 示例):

| 类型 | 价格 |
|---|---|
| 正常 input | $15/M |
| Cache write (首次建) | ~$18.75/M (+25% tax) |
| Cache read (后续命中) | **$1.5/M** (-90%) |
| TTL | 5 分钟 |

**规则**: 只缓存 prompt 的 prefix (前缀), 变的内容必须放后面. 原理: LLM attention 从左到右, 前缀相同则 KV cache 可复用。

**类比 (Vincent quant 背景最好理解)**:
- 活字印刷: 常用字刻一次, 后续反复复用
- PreparedStatement (SQL): 模板 compile 一次, 后续只传参数
- 预编译头 (C++): 大段 `#include` 一次编译, 后续复用

**MiroFish 场景**: System + tools prefix ~1400 tok 每 agent 每轮都发, 完美 cache 对象. 100M token × $0.3 saved per sim (Sonnet级). 但 MiroFish 要 fork CAMEL backend 接 Anthropic native SDK 才能吃到红利, 这是 fork ROI #1。

---

## 3. 问题和想法

### 3.1 未解 / Session 3 开头要验

- **`OASIS_DEFAULT_MAX_ROUNDS=10` 与 `total_simulation_hours=72`**: 独立计数器还是 override? 若 override, 实际只跑 10 轮, 成本再 ÷7x, 整体估算重做
- **实际 token 消耗 log**: 跑一次真实 sim, 拿 API usage 数据, 验证 14K tok/turn avg 对不对

### 3.2 思考中

- **Simile vs MiroFish 的 persona 源对比**: Simile "1000 人 qual 深访 + 行为科学文献" vs MiroFish "Zep 图谱抓取种子文本". 两条路径的 fidelity 天花板差异 (Session 4-5 再深入)
- **MiroFish 55.6K★ 但全网无 cost disclosure**: 作者没被问过还是刻意不披露? 商业化前必须自己跑实测数据
- **Aaru 2024 大选全错估值仍涨**: 商业信号不是预测准, 是客户信任 + partner lock-in. 面试 point: "single-point accuracy 不是商业衡量指标, retention 才是"
- **Nate Silver 2026-04-11 拒 AI 民调入聚合**: 行业对 synthetic research 的合法性还在搏斗, MiroFish 做 consumer sim (非政治) 是对的定位
- **LLM prompt 无 budget guard**: LLM 决定 simulation 时长时不知道自己花 Vincent 多少钱. 这是最低成本改造的最低垂果实
- **中国项目默认小模型 (Qwen/GPT-4o-mini)**: 不是 Claude 滤镜. 作者把 model choice 当 cost control 第一刀

### 3.3 面试角度

- **不能吹 "独创 LLM 预测消费者"**: 2026 这句话说出来就输. 必须垂直锚 Challenge 5 = 家电舆情
- **Simile / Aaru 是 table stakes**: 自己的差异化在 (a) 数据源 moat (SharkNinja Amazon review 的垄断访问) (b) 中国家电市场 domain 理解 (c) Joyce CAIO 角度的 partner lock-in
- **三档定价 $200/$2K/$10K** 跟 B2B AB test 商业直觉对得上, 是设计产品时的定价锚

### 3.4 竞品空间洞察

- "LLM 预测消费者" 已是 table stakes, 无 novelty 卖点
- Aaru (Accenture/IPG 渠道) / Simile (Stanford 学术 + CVS 大客户) / Qualtrics Edge (25 年数据) 各占一个 moat 维度
- AgentSociety 是 "纯方法前沿 + 商业真空", 不构成商业竞品, 是方法论对标
- **空间已挤, novelty 不是卖点. 垂直 + 数据 + 客户关系才是**

---

## 4. 下次预告 (Session 3)

### 4.1 主题

种子文本 → 实体提取链路. `text_processor.py` / `ontology_generator.py` / `graph_builder.py` 三件套。

### 4.2 Challenge 5 衔接

一条 SharkNinja Amazon 差评 (种子文本) → Zep 图谱实体关系图. 观察被抽出什么实体, 决定 simulation 的 agent 规模。

### 4.3 要回答

- 一条评论能抽出几个 entity? 关系怎么建?
- Zep 图谱的"检索"机制: 为每个 entity 挑 20 facts + 10 关联节点, 怎么排序?
- text 进来后的清洗 / 去重 / 分块策略
- Session 2 未解的 `MAX_ROUNDS=10 vs total_hours=72` 矛盾 (开头第一件事)

### 4.4 带走目标

能回答: **"一条差评如何变成 1000 个人的群体行为模拟种子?"**

---

## 附录: Session 2 关键数字 cheat sheet

- **MiroFish 单次 sim 真实成本区间**: $100-$1K (Qwen) / $2-6K (Sonnet) / $10-25K (Opus)
- **成本三段**: persona 2% / simulation 97.5% / report 0.1%
- **Per-turn token avg**: ~14K (考虑 memory 累积, 非学术均值 4.8K)
- **Total token per sim (1000×72)**: ~1B
- **Cache prefix**: system(500) + tools(900) = 1.4K 固定, 每 agent 每轮都发 → fork ROI #1
- **Agent 数公式**: = entity 数 = f(Zep 图谱, 种子文本)
- **架构路线**: 远程 API only, 非 local GPU
- **OASIS memory**: 无 window 无 summary, 72 轮后期 per-agent 累到 20-50K tok
- **竞品头部**: Aaru $1B / Simile $100M / Qualtrics Edge (Incumbent) / AgentSociety (学术)
- **三档定价意向**: $200 / $2K / $10K (与 B2B AB test 商业直觉对得上)

---

**Session 2 完结**
