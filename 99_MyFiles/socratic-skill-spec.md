# Socratic Learning System — Design Spec

**Status**: Draft v0.1
**Date**: 2026-04-16
**Author**: Vincent + 凌喵 (collaborative design)
**Source context**: 脱胎于 MiroFish Session 1 (2026-04-15/16); 在 5 轮成功的问答循环后正式化

---

## 概述 (Overview)

一个双 skill 组成的学习系统, 帮助 Vincent 用**苏格拉底式问答**深入学习技术与非技术话题, 同时保证所有**事实性内容基于可验证的知识库 (KB), 而非 LLM 的训练记忆**。

### 核心动机

- LLM 训练数据有 **bias / 陈旧 / hallucination 风险**, 不适合做"事实教学"
- Vincent 要用学到的内容**写文章 / 准备面试**, 必须掌握事实主权
- 苏格拉底式问答**逼 Vincent 推理**, 即使不知道答案也有启发价值
- Vincent 的"人的 sloppiness"是 design constraint, skill 要主动帮他摊开"不知道自己不知道"的东西

### 要规避 vs 要保留

| 要规避 | 要保留 |
|---|---|
| LLM 的 hallucination | LLM 的语言处理能力 |
| 训练数据陈旧 | LLM 的逻辑推理能力 |
| 模型的事实生成 | 模型的教学组织能力 |

**不是去 LLM, 是去 LLM 的事实生成化**。

### 架构: 双 skill

```
┌─────────────────────────────────────────────────┐
│ 前置: KB Builder skill                         │
│ 输入: 话题 (e.g. "word2vec") / 用户给的材料    │
│ 输出: {KB_ROOT}/<concept>/ 结构化知识目录      │
│       含原文 + metadata + (可选) summary       │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ 主: Socratic Learning skill                    │
│ 输入: 话题 / 大方向, 从 KB 拉素材              │
│ 输出: 问答式教学, 标准答案必 cite KB           │
└─────────────────────────────────────────────────┘
```

---

## 基础设施 (Shared Infrastructure)

### KB_ROOT 变量

Skill 所有路径引用均通过**变量**, 不硬编码。

```
KB_ROOT = D:\Ai_Project\MeowOS\80_Knowledge\88_Research
```

Skill 运行时把 `{KB_ROOT}` 替换为实际路径。未来迁移 / 复用 / 通用化**只需改一行**。

### 目录结构 (1a 概念级扁平)

```
{KB_ROOT}/
├── word2vec/
│   ├── mikolov-2013-efficient-estimation.md    # 原文
│   ├── mikolov-2013-distributed-representations.md
│   ├── bolukbasi-2016-man-programmer.md
│   ├── _meta.md                                 # concept metadata
│   ├── _sources.md                              # source registry
│   └── _summary.md                              # 可选 semantic summary (凌喵生成)
├── attention/
│   ├── vaswani-2017-attention-is-all.md
│   ├── bahdanau-2014-neural-mt-attention.md
│   └── _meta.md
├── bi-temporal/
│   └── ...
├── _inbox/                                      # PDF drop zone (Workflow A)
├── _todo-paywall.md                             # sources 待 Vincent UChicago 手动下载
└── _registry.md                                 # master index of all concepts
```

**原则**: 每个概念一个扁平目录, 概念生长时自然分裂。不提前预设 domain 分层, 成熟后再考虑升级到 1b 领域级。

### Metadata 模式 (`_meta.md`)

每个概念目录的 `_meta.md`:

```yaml
concept: word2vec
status: populated
created: 2026-04-16
last_updated: 2026-04-16
freshness_tier: slow          # or "fast" for fields needing re-scrape every 2mo
domain_tags: [ml-ai, nlp, embeddings]  # 软标签, 不决定目录位置
source_count: 3
summary_available: true
```

### Source registry 模式 (`_sources.md`)

```markdown
| File | Title | Author | Year | URL/DOI | Access | Notes |
|---|---|---|---|---|---|---|
| mikolov-2013-efficient-estimation.md | Efficient Estimation... | Mikolov et al. | 2013 | arXiv:1301.3781 | OA | 原论文 |
| bolukbasi-2016-man-programmer.md | Man is to... | Bolukbasi et al. | 2016 | NIPS 2016 | Vincent-fetched UChicago | bias paper |
```

---

## Skill 1: Socratic Learning (主)

### Trigger (两种并存)

1. **显式命令**: Vincent 说 `苏格拉底` / `/socratic` / `问答式学习` / `开始 Q&A 模式`
2. **凌喵提议**: 当 Vincent 说"学习 X" / "深入理解 Y" 等学习意图时, 凌喵**在开题前主动提议**切换模式, Vincent 确认才启动

### Inputs

- 话题 / 方向 (来自 Vincent)
- KB 对应目录内容 (已建则优先用; 未建则触发 KB Builder)
- Vincent 的背景状态 (凌喵根据 memory 调整难度)

### Outputs

- 每一轮的 Q&A 交互: 场景 → 问题 → Vincent 答 → 凌喵评估 → 教学 → 下一题
- 可选落盘: 追问多或 Vincent 明确要求时, 整轮讨论 → `.md` 落到 `99_MyFiles/`

### 教学协议 (每轮 7 步)

**Step 1. 话题粒度协商 (suggest-first)**

若 Vincent 给**大领域** (e.g. "ML"), 凌喵**不开题**, 先 list 几条轴:

> "ML 这个领域挺大, 我列几条轴你挑: 架构类 / 硬件类 / 数学原理类 / 历史演进类 / 应用类 / ... 先走哪条?"

若给**具体话题** (e.g. "word2vec"), 直接进 Step 2。

**Step 2. KB 新鲜度检查**

凌喵读目标 concept 的 `_meta.md`:
- `freshness_tier: fast` + `last_updated > 2mo`: 提醒 Vincent, 问要不要重抓
- `freshness_tier: slow`: 默认不重抓, 但也问一句"要不要更新"
- **KB 不存在**: 触发 KB Builder 先建, 建完回来

**Step 3. 场景锚定 + 问题构造**

- 开场给**具体场景** (优先引用 Vincent 正在做的 project 如 MiroFish, 让问题接地)
- 问题用**方法论式**, 不用 recall 式:
  - ✅ "如果让你从零设计 X, 你会怎么搞?"
  - ❌ "X 是什么意思? / X 这个协议叫什么?"
- 题目藏一个**反直觉钩子** (业内答案 vs 自然直觉的差距)
- 默认不给提示, Vincent 说"卡住"或"提示"才给

**Step 4. 容错**

- 允许 Vincent 直说"不知道 / 卡住 / 超纲"
- 不羞辱, 不降智, 不强行要 Vincent 挤答案
- 记录 Vincent 的"不知道"点, 供后续追问

**Step 5. 评估 + 教学**

Vincent 答完后:
- 先评估: 用**"对的部分 + 漏的部分"表格**
- 再教学标准答案, 必须:
  - **带人物 + 年份 + 论文** (历史锚点)
  - **所有事实性陈述 cite `{KB_ROOT}/<concept>/<source_file>`**
  - **关键 context 论断也 cite**
  - 一般 contextual 说法可不强制 cite
- KB 里没有的部分: 明确标注 `[凌喵训练记忆, 未经 KB 验证]`

**Step 6. 邀请追问 + 主动侦测**

教学完后:
- **邀请 Vincent 追问**: "有什么要继续挖的?"
- **邀请词汇深挖**: "哪个词 / 概念要单独展开?"
- **凌喵主动侦测**: 若 Vincent 答题中某术语看起来没完全理解 (反直觉使用 / 避开不用), 凌喵主动问: "你对 X 的理解是 Y 这样吗? 要不要我单独解释 X?"

**Step 7. Next 决策**

所有追问完了, 凌喵问:

> "下一题, 还是收官?"

若 Vincent 选收官且本轮有落盘价值 (追问多 / 内容深), 凌喵提议:

> "这轮讨论要不要落成 .md 存到 `99_MyFiles/`, 以后复习或分享?"

### Stretch 难度校准

**默认**: **边界外一点点**。含义:

- Vincent 现有知识 + 一步推理可达
- 不追求当场完全消化, 接受他"晚些回来看"
- "太简单"或"超纲了": 下一题动态调节
- 凌喵记录"哪些概念 Vincent 说过晚点回来", 未来路过时提醒

**哲学基础 (Vincent 原话)**:
> "只要一直在学, 总有看得懂的时候; 只要一直在学, 总会不停地遇到同一个领域内的概念和知识点。"

### 引用严格度

| 类型 | 是否必 cite |
|---|---|
| 事实性陈述 (年份 / 人名 / 论文标题 / 具体数值) | **必** |
| 关键 context 论断 (e.g. "Chomsky 主导让分布派被边缘化 30 年") | **必** |
| 一般 contextual 说法 (e.g. "这件事值得停下来想 10 秒") | 不强制 |
| 凌喵的评论 / 类比 / 教学框架 | 不需 (明显是凌喵的) |

格式: `[{KB_ROOT}/word2vec/mikolov-2013.md L42-50]` (文件 + 行号范围)

---

## Skill 2: KB Builder (前置)

### Purpose

把一个**话题 (或一批话题)** 的权威知识从互联网**系统性抓下来**, 保留**原文 + 元数据**, 存入 `{KB_ROOT}/<concept>/`。

**不是**: LLM 总结提炼后让 Vincent 看摘要
**是**: 原文入库, 摘要可选附加, Vincent 永远能回到原始表达独立验证

### Trigger

- Socratic skill 发现目标 concept KB 空或过旧
- Vincent 显式 "给我抓一下 X 的 KB"
- Vincent 给一批 PDF / 链接 + "把这些入库, 补齐"

### Inputs

- **话题名** (e.g. "word2vec")
- **(可选) Vincent 提供的材料**: PDF / URL / 参考清单

### Outputs

- `{KB_ROOT}/<concept>/` 目录, 内含:
  - 原文文件 (一源一文件, 命名 `<author>-<year>-<short-title>.md`)
  - `_meta.md`
  - `_sources.md`
  - `_summary.md` (可选)

### 执行流程

**Step 1. 源识别**

凌喵按权威 tier 生成候选清单:

| Tier | 例子 | 信任度 |
|---|---|---|
| T1 原始论文 / 官方文档 | arXiv 论文 / 官方 RFC / GitHub 官方 readme | 最高 |
| T2 大刊 / 综述 | Nature / Science / ACM / IEEE / HBR | 高 |
| T3 Wikipedia + 其引用的原始资料 | Wiki 页 + 页尾 references | 中 |
| T4 成熟博客 / 技术分享 | Jay Alammar / Karpathy / Distill | 中 |
| T5 一般博客 / 论坛 | Medium / 知乎 / StackOverflow | 低, 只做佐证 |

按 T1 → T5 递减, 每条源带: URL / DOI / 作者 / 年份 / tier。

**Step 2. 源审批**

凌喵把候选清单给 Vincent, **Vincent 批准或修改**才开始抓。

Vincent 也可**主动给底板材料** (PDF / 链接清单), 这时:
- 他的材料作**权威底板**入库 (高优先级)
- 凌喵分析底板空白 (时间线缺哪段? 观点缺哪派?), suggest 外部补充
- 外部补充源标 `tier: supplementary, suggested by 凌喵`, 等 Vincent 批准

**Step 3. 抓取 (Workflow A + B 组合)**

对每个批准的源:

**Workflow B (自动 OA retrieval, 优先)**:

1. 查 **arXiv** (若 AI/CS 论文)
2. 查 **Semantic Scholar**
3. 查 **Unpaywall API** (免费公共 API)
4. 查**作者个人 / 实验室主页**
5. OA 版本找到 → 直接抓, 标 `access: OA-via-<source>`

**Workflow A (Paywall 手动协作, fallback)**:

OA 都没找到 → 加入 `{KB_ROOT}/_todo-paywall.md`:

```markdown
| Title | Author | Year | DOI | Target Database | Added | Fetched |
|---|---|---|---|---|---|---|
| Man is to Programmer... | Bolukbasi et al | 2016 | 10.5555/XXX | NIPS via UChicago Lib | 2026-04-16 | - |
```

流程:
1. 凌喵提醒 Vincent: "这些要你用 UChicago SSO 手动下, 列在 `_todo-paywall.md`"
2. Vincent 登 UChicago 图书馆 portal 下 PDF
3. Vincent 把 PDF 丢 `{KB_ROOT}/_inbox/`
4. 凌喵 (定期或 Vincent 叫一声) 扫 `_inbox/`, 自动入正规目录 + 更新 `_sources.md` + 划掉 `_todo-paywall.md` 对应行

**组合策略**: 每个源先跑 Workflow B, 没 OA 才进 Workflow A。**这能省 60-80% 的手动下载**。

**Step 4. 入库格式化**

每个抓到的源:
- 转成 markdown (PDF 用 OCR / text extraction 工具; 具体工具选择见开放问题 #4)
- **保留原文** (段落级别, 不摘要, 不改写)
- 文件头加 frontmatter:

```yaml
---
title: Efficient Estimation of Word Representations in Vector Space
author: Mikolov, T., et al.
year: 2013
venue: arXiv
doi_or_url: arXiv:1301.3781
access: OA
retrieved: 2026-04-16
concept: word2vec
source_tier: T1
---
```

- 文末附原始 URL + retrieval 时间戳

**Step 5. 可选 summary**

如 Vincent 要, 凌喵生成 `_summary.md`:
- 一段 plain-language 概述
- 一段关键公式 / 概念
- 一段 historical context
- **明确标注**: "此 summary 由凌喵基于原文生成, 原文见 `_sources.md` 各文件; 争议请查原文"

**不替代原文, 不是标准引用源**。

### KB 维护

- `_registry.md`: 所有 concepts 的主索引 (字母序 / recency / tier 三视图)
- `freshness_tier` 字段驱动 Socratic skill 的新鲜度检查
- Vincent 可手动修正 `_meta.md` / `_sources.md`, 凌喵遵从

---

## 3 条 Cross-cutting 规则

### 规则 A: Suggest-first for big domains

**触发**: Vincent 给"大领域"意图 (ML / 历史 / 哲学 etc.)
**行为**: 凌喵 list 几条轴, Vincent 挑, 再进入话题
**原则**: 尊重 Vincent "不知道自己不知道" 这个 design constraint
**Vincent 原话**:
> "我不可能完美精准地表达我所有的需求, 因为我没有办法知道我不知道的东西。"

### 规则 B: Q&A 开头检查 KB 新鲜度

**触发**: Socratic skill 每次开启, 先扫目标 concept 的 `_meta.md`
**行为**:
- `fast tier` + `> 2 个月`: 提醒 + 问要不要重抓
- `slow tier`: 默认不重抓, 但也问一句
- 没 KB: 触发 KB Builder 先建

### 规则 C: 用户自带材料 = 底板

**触发**: Vincent 提供 PDF / 链接清单
**行为**:
- 他的材料作**权威底板**入库
- 凌喵分析空白, suggest 外部补充
- 外部源 `tier: supplementary`, 等 Vincent 批准才入正规

---

## 开放问题 / 未来工作

1. **通用化 (v2+)**: 当前立足 MeowOS 架构。通用化时:
   - `KB_ROOT` 变成 skill 启动参数
   - `_inbox/` 和 `_todo-paywall.md` 改参数
   - Paywall workflow 改成"通用大学访问"模式 (不只 UChicago)

2. **多人协作**: 目前单用户。若 Joyce 等也要用, 需设计:
   - 共享 KB vs 个人 KB
   - attribution 如何分叉 (谁抓的 / 谁审的)

3. **跨 concept 关联**: `bi-temporal` 既和 databases 相关又和 agent-memory 相关。目前 1a 扁平没地方放关联。未来加 `_links.md`。

4. **PDF → markdown 准确性**: OCR 有损, 公式和表格特别困难。工具候选: PyMuPDF / Marker / Nougat / MinerU。需要决定 default + fallback 链。

5. **Freshness tier 自动判断**: 目前 Vincent 或凌喵手标 tier。未来可基于 concept 类型自动判断 (历史话题默认 slow, 近代技术默认 fast)。

6. **"Suspect Vincent 没懂"的判断依据**: 经验判断, 暂难形式化。先看实践效果, 后续迭代。

7. **Domain 从 1a 升级到 1b 的时机**: 何时触发升级? (concept 数 > 阈值? Vincent 主动要求?) 升级流程?

---

## Implementation 位置候选

| 位置 | 性质 | 当前推荐 |
|---|---|---|
| `~/.claude/skills/socratic-learning/SKILL.md` | CC 全局 skill, 任何 CC session 可调 | ⭐⭐⭐ |
| `~/.claude/skills/kb-builder/SKILL.md` | CC 全局 skill | ⭐⭐⭐ |
| `D:\Ai_Project\MeowOS\90_Agents\socratic-learning.md` | MeowOS agent prompt | ⭐⭐ |
| `D:\Ai_Project\MeowOS\99_MyFiles\socratic-skill-spec.md` | 先写 spec, 后决定实现形态 | **当前档** |

当前文件 **就是** 这份 spec (option 4)。Implementation (1-2 或 3) 等 Vincent review 后再落。

---

## 下一步

1. **Vincent review 这份 spec**, 确认或调整
2. 无大改后, 凌喵:
   - 把 Socratic Learning 拆成 `~/.claude/skills/socratic-learning/SKILL.md`
   - 把 KB Builder 拆成 `~/.claude/skills/kb-builder/SKILL.md`
   - 建 `{KB_ROOT}` 初始目录结构 + 空 `_registry.md`
   - 把本次已产出的 `word2vec-story.md` 拆进 `{KB_ROOT}/word2vec/` 作为 concept 的第一份内容 (把散布在 md 里的原始论文链接提取成 `_sources.md`)
3. **第一次实战**: 在 MiroFish Session 2 开始前, 用 Socratic skill 挑一个话题跑一遍, 检验流程

---

## Changelog

- **v0.1 (2026-04-16)**: 初稿。设计参数全部锁定。待 Vincent review。
