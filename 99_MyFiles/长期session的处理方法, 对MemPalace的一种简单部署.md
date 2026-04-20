# 长期 Session 的处理方法：对 MemPalace 的一种简单部署

> 来源：MeowOS session 2026-04-08
> 用途：供其他 session 读取，了解 digest pipeline 的设计背景、实验结论与最终实现

---

## 一、问题起点

Vincent 发现了 [MemPalace](https://github.com/milla-jovovich/mempalace)——一个开源的 AI 对话记忆系统，核心思路是把历史 session 全文存进向量数据库（ChromaDB），用语义检索按需取片段注入 context。

**MemPalace 的关键指标**：
- LongMemEval 96.6% R@5（号称最高）
- 本地优先，零云依赖
- Palace 架构：Wing（项目）→ Room（话题）→ Hall（记忆类型）→ Closet（摘要→原文）
- 原文存储（不用 LLM 提炼摘要）

**Vincent 的核心关注**：
1. MemPalace 的 token 使用规模在真实场景下到底多大？
2. 它的架构里哪些思路可以借用到 MeowOS？
3. 有没有比向量检索更轻量的方式达到类似效果？

---

## 二、关键发现：normalize 是最大的杠杆

### Claude Code 的 session 存储

Claude Code 把每个 session 存为 JSONL 文件，位于：
```
C:\Users\scvin\.claude\projects\<project-path-encoded>\*.jsonl
```

这些文件 **90%+ 的体积是元数据噪音**：timestamps、uuids、tool_use blocks、tool_result blocks、system reminders、git state 等。

### MemPalace 的 normalize.py 做了什么

它的 `_try_claude_code_jsonl()` 函数只做一件事：
- 逐行读 JSONL
- 只保留 `type == "human" / "user" / "assistant"` 的行
- 只取 `message.content` 里的 text 块
- 跳过 tool_use、tool_result、thinking、image 等一切非文本内容

**实测效果**（MeowOS 最大的 session 文件）：
- 原始 JSONL: 1,612,605 bytes
- normalize 后: 143,088 bytes
- **保留比: 8.9%**

### 我们的 v2 改进

在 MemPalace 的 normalize 基础上，我们额外做了一步：**剥离 fenced code blocks**。

理由：Vincent 不写代码，session 里的代码块全是 AI 生成的实现细节。保留代码周围的讨论（"为什么这么做""还需要怎么调"），但把代码体本身替换为 `<code block: N lines of LANG, 省略>`。

估计额外节省 20-30% token（在代码密集型 session 中）。

---

## 三、模型对比实验

### 实验设计

选取一个中等体量的 session（`2b525bc7`，~9K token），用三个模型做同一份 digest：

**Pass 1**（单 session digest）：Haiku 4.5 / Sonnet 4.6 / Opus 4.6
**Pass 2**（二阶分析，只读 Pass 1 digest）：每份 Pass 1 × Sonnet 和 Opus = 6 份
**Judge**（两个独立 Opus 裁判）：分别评估 Pass 1 和 Pass 2

### Pass 1 裁判结论（满分 70）

| 模型 | 得分 | 成本 | 核心特征 |
|---|---|---|---|
| Haiku | 44 | $0.02 | 能看懂 session 形状，但 Reading Between Lines 基本是换措辞复述 |
| Sonnet | 55 | $0.05 | 稳定在"读出表面之下"的及格线 |
| Opus | 65 | $0.20 | 唯一读懂 Vincent 作为"作者"的。独有发现最多 |

裁判原话：**"Sonnet 读文本准确；Opus 读的是作者本人。"**

### Pass 2 裁判结论（满分 60）

```
         | Sonnet P2 | Opus P2 |
---------|-----------|---------|
Haiku P1 |    44     |   55    | ← 最高分
Sonnet P1|    41     |   52    |
Opus P1  |    46     |   54    |
```

**核心发现：Pass 2 模型比 Pass 1 质量重要得多。**
- Haiku × Opus (55) 打败了 Opus × Sonnet (46)
- 最弱 P1 + 最强 P2 > 最强 P1 + 最弱 P2
- **Sonnet 做 Pass 2 永远不值得**

### 金句问题

实验中发现模型选取的"金句"有五种不同逻辑：Voice 类、Views 类、Sharp moments 类、Context anchors 类、Diagnostic 类。后两种经常被混入，导致"金句"没有金句味。

**解决方案**：拆成两节：
- **Distinctive Lines**（不可转述的句子，不设上限，没有就写"无"）
- **Key Statements**（结构性参考，锚定事实和立场）

---

## 四、最终 Pipeline 设计

### 哲学原则

- **Lossy by Design**：不追求完备。漏掉的东西会因为 Vincent 长期使用系统自然再次出现。
- **水位线机制**：每次批处理只处理 mtime > last_processed_at 的 session，永不回头。
- **主 session 是净土**：一切读写派给 subagent，主 session 只看最终简报。
- **Cold insight 不自动升温**：pipeline 产物只是素材，写进 warm/hot memory 必须由 Vincent 在系统诊断时审批。

### 数据流

```
C:\Users\scvin\.claude\projects\d--Ai-Project-MeowOS\*.jsonl
    │
    │  manifest_scan.py（Python, 零 token）
    │  normalize + 1500 字符截断 + 更新 manifest
    ▼
D:\...\99_MyFiles\Normalized_Session_History\<uuid>.txt
    │
    │  Opus subagent × N（串行，每个读一份 txt）
    ▼
D:\...\Session_Digests\MeowOS\pass1\<uuid>.md
    │
    │  Opus subagent × 1（读所有 Pass 1 digest）
    ▼
D:\...\Session_Digests\MeowOS\pass2\synthesis_<date>.md
    │
    │  Sonnet subagent × 1（读 synthesis，写简报）
    ▼
D:\...\Session_Digests\MeowOS\pass2\report_<date>.md
    │
    │  update_watermark.py（Python, 零 token）
    ▼
manifest.md 水位线更新，下次只看之后的新 session
```

### 为什么砍掉了 Pass 0（Haiku 分类器）

原始设计有一个 Haiku Pass 0 来分类 substantive / operational / fragment。但分析发现：
- Vincent 已经把机械性任务路由到 claude.ai 网页版，能进 Claude Code session 的已经被前置筛过
- normalize 后 85% 的 token 量来自真正有实质内容的大型对话
- 用 Haiku 读全部 67 万 token 只为剔除 15% 的碎片，得不偿失
- **1500 字符的 Python 截断**可以零 token 成本干掉明显的 fragment

### 触发方式

1. Vincent 说"跑 digest pipeline"
2. 系统诊断时作为流程的一步自动触发

凌喵读 `digest_pipeline/RUN.md`，按步骤派 subagent 执行。

### 文件结构

```
80_Knowledge/86_AI_Systems/
├── digest_pipeline/
│   ├── normalize_jsonl.py      # 清洗 jsonl → txt，剥代码块
│   ├── manifest_scan.py        # 扫新 session，1500 字符截断，追加 manifest
│   ├── update_watermark.py     # 批处理完成后更新水位线
│   ├── prompts/
│   │   ├── pass1.md            # 单 session digest (Opus)
│   │   ├── pass2.md            # 跨 session 综合 (Opus)
│   │   └── pass3_reporter.md   # 面向 Vincent 的简报 (Sonnet)
│   ├── RUN.md                  # 运行手册（给凌喵读）
│   └── README.md
└── Session_Digests/
    ├── MeowOS/
    │   ├── manifest.md
    │   ├── pass1/
    │   └── pass2/
    └── _experiment/             # 模型对比实验的 9 份分析 + 2 份裁判报告
```

---

## 五、记忆温度分层

| 层 | 位置 | 加载时机 | 影响 |
|---|---|---|---|
| **Cold archive** | `Normalized_Session_History/*.txt` | 从不自动加载 | 零影响，是历史 |
| **Cold insight** | `Session_Digests/pass1/`、`pass2/` | 同上 | 零影响，是分析 |
| **Warm memory** | `80_Knowledge/` 下的结构化文件 | shell-runner 按需读 | 被读到时影响当轮 |
| **Hot memory** | `MEMORY.md` + 指向的文件 | 每次 session 开场自动注入 | 影响每一次互动 |

Pipeline 产物**只进 Cold insight**。升温到 Warm/Hot 的决定权在 Vincent，发生在系统诊断 session 里。

---

## 六、与 Dream Mode 的关系

Digest Pipeline 对应 Dream Mode 四阶段中的 **Gather + 部分 Consolidate**。

| Dream Mode 阶段 | MeowOS 覆盖情况 |
|---|---|
| Orient（先看全貌防重复） | ❌ 缺失，待加入系统诊断 |
| Gather（从 transcript 采集） | ✅ digest pipeline |
| Consolidate（合并到持久记忆） | ⚠️ 系统诊断在做，但缺日期转换和矛盾检测 |
| Prune（修剪死链和过期条目） | ❌ 缺失，待加入 |

后续改进方向（已记录，待系统诊断审批）：
1. 系统诊断标准化为四阶段
2. 加 Prune 硬规则（MEMORY.md 150 行限、last_verified、死链清理）
3. 系统诊断加"窄 grep 近期 transcript"作为 _staging.md 的补充采集

---

## 七、成本与规模参考

### MeowOS 历史数据（截至 2026-04-08）

- 45 个 session，normalize 后总计 1,119,506 字符（~67 万 token）
- 其中 85% 集中在 ~37 个 substantive session
- 最大 5 个文件占总量 55%

### 单次批处理预估（Max Plan）

- Step 1（Python normalize + scan）: 零 token
- Pass 1（37 × Opus）: ~37 次 subagent 调用，串行，约 40 分钟–2 小时
- Pass 2（1 × Opus）: 1 次调用
- Pass 3（1 × Sonnet）: 1 次调用
- 总计: ~39 次模型调用，全算进 Max Plan 订阅

### 如果走 API（参考）

- Pass 1 输入 ~15 万 token × $15/M = ~$2.3
- Pass 1 输出 ~7 万 token × $75/M = ~$5.3
- Pass 2 + Pass 3: ~$1
- 总计: **~$8.5**（一次性）
