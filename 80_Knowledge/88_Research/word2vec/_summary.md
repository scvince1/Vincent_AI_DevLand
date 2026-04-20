---
concept: word2vec
generated_by: 凌喵
generated_on: 2026-04-16
based_on: primary sources listed in _sources.md (NOT YET SCRAPED as of generation)
disclaimer: |
  This summary is 凌喵's narrative synthesis from training memory + dialogue with Vincent on 2026-04-16.
  Most listed primary sources have not yet been independently scraped and verified against.
  Sources will be scraped via kb-builder skill and cross-checked.
  In case of conflict between this summary and primary sources, primary sources win.
  For article or interview use, verify against primary sources listed in _sources.md before citing.
---

# word2vec 的故事: 语义怎么被数学捕捉

> 一段 2013 年 NLP 范式革命的来龙去脉。从 1957 年 Firth 一句格言, 到 56 年后它被工程化为可执行代码, 中间走过哪些弯路、埋了哪些伏笔。顺便抖出了 AI 伦理第一案。

## 引子: 一个看起来很难的问题

假设手上有几百万段文本 (比如整部维基百科), 要做到:

- 给一段新文字 (词、短语或完整句子), **毫秒级**找到"意思最近的"几段
- **"意思近" 不等于 "字面近"**:
  - 车 (car) 和 汽车 (automobile) 应该很近
  - 猫 和 狗 应该比较近 (都是宠物)
  - "打死蚊子" 和 "打车去机场" 里的两个"打"字, 应该**不近** (同字异义)
- 不允许挨个逐字对比几百万段文本 (太慢)

这个问题从 1957 年被正式提出, 到 2013 年才真正被解决。56 年。

## 1954-1957: 两位老派语言学家埋下种子

**1954 年**, 哥伦比亚大学的语言学家 **Zellig Harris** (后来是 Noam Chomsky 的博士导师) 发表了一篇叫 *Distributional Structure* 的论文。他提出一个接近数学的命题:

> 如果两个语言单位 (词、短语) 在"完全相同的语境"里能互相替换, 那它们的意义就相同。语境的重叠程度, 可以用来**测量**意义的相似度。

**三年后, 1957 年**, 英国语言学家 **J.R. Firth** (LSE + SOAS 那一派) 留下了一句今天 NLP 圈几乎每个人都引用的话:

> **"You shall know a word by the company it keeps."**
> 你只能通过一个词的伴随者来认识它。

Harris 给出了数学化的命题, Firth 给出了传播力十足的格言。两者合在一起, 构成了 **distributional hypothesis** (分布假设) 的双源头。哲学含义就一句:

> 一个词的"意思"不在它的拼写、词性、句法树位置里, 而在它**周围出现的那些词**里。

举例: 听到 "The _____ barked at the mailman", 你知道空格里大概是 "dog"。不是因为拼写, 不是因为它是名词, 是因为在你读过的所有英文里, "barked" 和 "mailman" 附近**经常出现 "dog"**。

50 多年里, 这只是哲学, 没人知道怎么把它变成算法。

## 同一年, 对面山头的革命: Chomsky 1957

历史的讽刺性在这里发作。**1957 年, 就在 Firth 写下那句话的同一年**, MIT 的 **Noam Chomsky** 出版了 *Syntactic Structures*。

Chomsky 的主张和分布派**几乎完全相反**:

- 语言的本质是一套**内生的规则系统**, 不是靠观察使用数据能还原的
- 句子结构是通过**语法规则生成**, 不是**从使用习惯涌现**
- 小孩能学会复杂语言这件事, 证明人脑自带"普遍语法"(Universal Grammar)

这套 **生成语法 (generative grammar)** 在之后 30 年**几乎垄断了理论语言学**。结果:

- 计算语言学的重心在句法树、规则、推理
- 分布假设被视为"肤浅"(只看表面共现, 没抓住语言深层结构)
- 所有跟统计、神经网络、数据驱动有关的方法都被打入冷宫

**1966 年的 ALPAC 报告** (美国科学院受国防部委托对机器翻译的评估) 在 Chomsky 思潮影响下, 建议**削减机器翻译研究经费**。机器翻译研究因此**停摆了近 10 年**。NLP 第一次冬天的一部分, 就是这样来的。

## 1960s-1970s: 符号 AI 的黄金时代

这段时间 NLP 的代表作都走"人工定义意义 + 硬编码"路线:

- **ELIZA** (Weizenbaum, 1966): 模式匹配伪装成心理治疗师, 没有真正理解, 但用户以为它懂
- **SHRDLU** (Winograd, 1970): 积木世界里的自然语言指令系统, 所有知识手工编码
- **Conceptual Dependency** (Schank, 1972): 把句子解析成手工设计的语义 schema
- **Frame Semantics** (Fillmore, 1976): 意义 = 结构化场景模板 (如"餐厅 frame"里有"顾客、服务员、菜单、结账")

这些工作共同的特点: **意义靠人工定义, 用硬编码的方式塞给机器**。

最后撞上的墙叫 **knowledge bottleneck** (知识瓶颈):

> 要让机器懂任何话, 先得有人把对应的知识手写进去。规模上不去, 泛化能力差。

## 1975: 一条被忽略的平行线 — Salton 的向量空间

在主流 NLP 被 Chomsky 和符号主义占领的时候, **信息检索 (Information Retrieval) 领域**走了一条不同的路。

**1975 年, 康奈尔大学的 Gerard Salton** 提出了 **Vector Space Model** (向量空间模型) 用于文档检索:

- 每个文档表示为一个向量 (每个维度对应一个词)
- 查询也是向量
- 用余弦相似度找最相关的文档

这是分布思想的**第一次工程化**, 但它被视为"检索工具", 不是"语言理解方法"。IR 领域在符号主义 NLP 的旁边安静地发展, 两个领域几乎不互相引用。

## 1985-1995: WordNet, 符号主义最后的堡垒

1985 年, 普林斯顿的心理学家 **George Miller** 启动了 **WordNet** 项目: 一个**手工构建的英语词汇语义网络**。

- 词被组织成 **synsets** (同义词集合)
- synsets 之间有**上下位关系 (hypernymy)、部分整体关系 (meronymy)、反义关系 (antonymy)** 等
- 1995 年首次公开发布, 成为此后 20 年 NLP 的基础资源

WordNet 是**符号主义对意义的最后一次大规模正面尝试**。它有用、精致、至今仍被引用。但它也暴露了这条路的根本瓶颈:

- 一整个团队花 **10 年**, 只覆盖了英文
- 新词、专业术语、方言永远落后
- 语义关系的颗粒度只能靠人拍脑袋决定
- 其他语言要**从头再来一遍**

**到 WordNet 发布那年 (1995), Harris 和 Firth 的分布假设仍然没有被工程化, 已经过去了 38 年。**

## 1988-1990: Latent Semantic Analysis — 第一道光

真正把"意思从数据里涌现出来"这个理念**首次工程化**的, 是 1988-1990 年 Bellcore 实验室的一个团队: **Deerwester, Dumais, Landauer, Furnas, Harshman**, 他们提出了 **Latent Semantic Analysis (LSA)**。

做法:

1. 构造一个大矩阵: 行是文档, 列是词, 每个格子是"这个词在这个文档里出现的次数"
2. 用线性代数的 **SVD (Singular Value Decomposition, 奇异值分解)** 把这个巨大的稀疏矩阵压缩成一个低维稠密矩阵
3. 压缩后每个词对应一个**向量** (通常 200-500 维)
4. 向量相似度 ≈ 语义相似度

这已经**非常接近 word2vec 的骨架了**。区别在于:

- LSA 用统计矩阵分解 (纯数学, 不涉及神经网络)
- 要一次加载整个矩阵, 计算成本在当时非常高
- 得到的向量质量比后来的 word2vec 弱, 但比手工方法好得多

LSA 是 1990s 信息检索领域的主流方法, 1998 年 Google 诞生时, 这类"向量语义检索"已经是工业技术。

**但 LSA 没有引发 2013 年那样的整体范式翻转**, 因为:

- 它被视为"信息检索工具", 不是"理解语言的框架"
- 计算规模有限, 没法跑到互联网全量文本
- 它没有一个直白的传播性演示 (比如 king - man + woman = queen)
- 主流 NLP 和 IR 是分开的社群

## 1990s: 统计 NLP 的崛起

与 LSA 平行, 整个 NLP 领域在 1990 年代经历了**从规则到统计**的转向:

- **1993 年**, IBM 的 Brown 等人发表 *The Mathematics of Statistical Machine Translation*, 把机器翻译彻底变成概率问题。这让**已经冻结近 20 年的 MT 研究重新启动**, 统计 MT 从此主导直到 2015 年左右被神经 MT 取代
- **Hidden Markov Models (HMM)** 成为词性标注的标配
- **Penn Treebank** (1993) 给整个领域提供了标准数据集
- **n-gram 语言模型** 成为语音识别的基础

Chomsky 的纯符号派开始退潮。**"让数据说话"成为 NLP 主流**。

这期间, 神经网络在 AI 整体处于低谷 (1995-2006 俗称 "neural winter"), 被 SVM、随机森林、贝叶斯方法等统计工具挤下主流。

## 2000s: 分布式语义的慢燃

2000 年代, 分布式语义作为 NLP 的一个子领域**一直在慢慢积累**:

- **Peter Turney** 的一系列工作 (2000-2010), 用共现统计解决类比、情感、隐喻等问题
- **Latent Dirichlet Allocation (LDA)** (Blei, 2003), 主题模型, 用概率生成式方式处理文档
- **HAL** (Hyperspace Analogue to Language, Lund & Burgess, 1996), 另一个共现向量空间

所有这些工作**规模都很小**, 数据量级停留在千万词级别, 没有今天的亿级、百亿级、万亿级规模。

## 2003: 早产的 word2vec — Bengio 的神经语言模型

**2003 年**, 蒙特利尔大学的 **Yoshua Bengio** (后来的图灵奖得主) 等人发了一篇叫 *A Neural Probabilistic Language Model* 的论文。这是**第一次用神经网络做语言建模**:

- 每个词对应一个**低维向量** (30-100 维)
- 用一个简单神经网络预测下一个词
- 向量作为网络参数的一部分, 和网络一起训练

**这篇论文几乎包含了 word2vec 的所有核心思想**, 比 Mikolov 早了整整 10 年。

**那为什么 word2vec 才是那个"改变领域"的工作?**

Bengio 2003 的工作在当时算得**非常慢**, 训练一次要几天, 只能跑小数据集 (AP News 语料, 约 1400 万词)。当时没有 GPU、CPU 也不够强、神经网络工具链不成熟。它停在了"这在理论上行得通"的阶段, 没进入"工程上可用"的阶段。

Mikolov 2013 的贡献, 与其说是**发明了 embeddings 的想法**, 不如说是**把这个想法简化 + 加速到能在亿级语料上跑**。他用极简的 CBOW / Skip-gram 架构 (比 Bengio 2003 的网络还简单), 配合 2012 年后 GPU 加速的普及, 让训练时间从"几天"降到"几小时", 从"千万词"升到"千亿词"。

## 2006-2012: 深度学习的再起

长期处于 AI 阴影下的神经网络, 在 2006 年迎来转折点。

**2006 年**, 多伦多大学的 **Geoffrey Hinton** (也是图灵奖得主之一) 发表 *A Fast Learning Algorithm for Deep Belief Nets*。这篇论文让"深层神经网络其实可以被训练"这件事重新有了希望, 引发了 **deep learning** 这个词的重新流行。

**2012 年**, Hinton 实验室的 **AlexNet** 在 ImageNet 图像识别大赛上碾压所有传统方法, 误差率直接砍掉 10 个百分点。这是**深度学习正式回归 AI 主流**的标志事件。GPU 训练神经网络从此变成标配。

一夜之间, 整个 AI 学界的共识改变:

> 先前被判死刑的神经网络其实只是在等硬件和数据。现在都齐了。

这个氛围下, Mikolov 在 Brno 大学做博士时的递归神经语言模型工作 (2010-2012), 移植到 Google 的大规模语料 + GPU 基础设施, 在 2013 年初变成了 word2vec。

## 2013: word2vec 终于把哲学变成了算法

**Tomas Mikolov 在 Google**, 2013 年发了一篇叫 *Efficient Estimation of Word Representations in Vector Space* 的论文。做的事简单到令人发指:

1. 搭一个**很小的**神经网络, 输入一个词, 输出一串数字 (典型是 300 个)
2. 训练任务**只有一个**, 二选一:
   - **CBOW** (Continuous Bag-of-Words): 给上下文几个词, 猜中间缺的那个词
   - **Skip-gram**: 给中间的词, 猜它上下文可能是哪些词
3. 训练数据: **互联网抓来的原始文本**。**没有词典监督、没有人工标签、没有谁告诉它 "车和汽车是同义词"**
4. 训练完成后, 网络中间某一层的那 300 个数字, 就是**这个词的 embedding 向量**

这不是思想上的创新, 是**思想的工程化封顶**。Firth 1957 + Harris 1954 + Bengio 2003 的组合, 终于达到了"工程可用"的门槛。

## 3 个违反直觉的设计

### (1) 不用任何人工标注的训练集

word2vec 是 **self-supervised** (自监督): 模型自己给自己出题 ("猜缺失的词"), 自己打分。这是关键突破, 因为人工标注规模上不去, 而互联网文本**万亿级免费供应**。

### (2) 拼写和词性完全不进模型

每个词开始只是一个随机 ID, 对应一个随机初始化的 300 维向量 (都是噪声)。模型从头看训练语料, 通过预测任务**反推**每个词该长什么样。最后 "car" 和 "automobile" 的向量极接近, 不是因为谁告诉模型它们是同义词, 而是因为它们在语料里**出现的上下文极其相似** (周围都经常是 "drive", "road", "engine")。

### (3) 维度没有人类可读的含义

word2vec 的 300 个维度**没有一个是人类能单独解读的**。它们是训练自己涌现出来的一组坐标轴, 要综合起来才捕捉意思。这件事让很多人不舒服: 它**能用但你无法完全解释它**。这也是 ML 可解释性 (interpretability) 研究领域的起点。

## 最震惊当年的一个演示

word2vec 论文里给出了一个让所有人下巴掉的结果:

> **vec(king) - vec(man) + vec(woman) ≈ vec(queen)**
>
> **vec(Paris) - vec(France) + vec(Germany) ≈ vec(Berlin)**

在这些看起来毫无含义的向量上做**线性代数运算**, 居然能得出语义类比。

为什么? 因为"性别切换"或"首都-国家"这种关系在训练语料里是**系统性规律**, 于是在向量空间里自然形成了一个方向 (direction)。向量加减就是沿着这些方向走。

这个结果发表后, NLP 圈震动。**前几十年堆砌的词典、同义词库、语法树, 突然都被一个 300 维向量的加减法超越了**。

## 副作用: 2016 年被抖出来的偏见丑闻

2013-2015 大家都在庆祝 word2vec 的魔法。**2016 年**, **Bolukbasi 等人** (Boston University 和 Microsoft Research 的合作组) 发了一篇叫 *Man is to Computer Programmer as Woman is to Homemaker? Debiasing Word Embeddings* 的论文。

他们做了同样的向量运算, 结果是:

> **vec(man) - vec(computer programmer) + vec(woman) ≈ vec(homemaker)**
>
> **vec(doctor)** 更接近 **vec(he)** 而不是 **vec(she)**

embedding **忠实地学会了训练语料里的社会偏见** (性别、种族、职业刻板印象), 然后把它们编码进了数学空间。

**没人故意把偏见设计进模型**, 但训练数据 (书、新闻、网络文本) 本身就是偏见的载体, 神经网络做了它该做的事: **忠实地吸收了统计规律**。

**这是 AI 伦理第一次正式进入 ML 主流学术讨论**。之后十年, debias embedding / fair representation learning 成了一整个研究方向。

从印刷术、电报到社交媒体, 技术忠实映射社会现实然后引发社会论战, 是每一次都重演的模式。word2vec 只是这个模式在 AI 时代的第一个主角。

## 2013 之后的演进线

| 年 | 工作 | 进步点 |
|---|---|---|
| 2013 | **word2vec** (Google, Mikolov) | 词级 embedding, self-supervised |
| 2014 | **GloVe** (Stanford, Pennington) | 词级, 不同数学路径 (矩阵分解路线) |
| 2016-2017 | **fastText** (Facebook, Mikolov 跳槽后) | 加入 subword, 处理未登录词 |
| 2018 | **ELMo** (AllenNLP) | 同一个词在不同上下文可以有不同向量 |
| 2018 | **BERT** (Google, Devlin) | transformer-based, 全上下文感知 |
| 2019+ | **Sentence-BERT** | 从词级升到句子级 |
| 2024+ | OpenAI / Cohere / Anthropic embedding API | 1536-3072 维, 段落级 |

今天所有 **RAG (Retrieval-Augmented Generation) 系统、向量数据库 (Pinecone / Qdrant / Zep)、语义搜索、AI agent 的长时记忆**, 底层都是这条线的延伸。

## 回头看: 56 年的"慢动作革命"

| 年 | 事件 | 距 word2vec |
|---|---|---|
| 1954 | Zellig Harris *Distributional Structure* | -59 |
| 1957 | Firth "company it keeps" | -56 |
| 1957 | Chomsky *Syntactic Structures* (压制分布派) | -56 |
| 1966 | ALPAC 报告, MT 研究停摆 | -47 |
| 1970s | 符号 AI 高峰 (ELIZA, SHRDLU, Schank) | ~-40 |
| 1975 | Salton 向量空间模型 (IR 领域) | -38 |
| 1985-95 | WordNet 建设 (符号主义最后一次大尝试) | -28 至 -18 |
| 1988-90 | **LSA 用 SVD 做向量语义** | -25 至 -23 |
| 1993 | 统计 MT 革命 | -20 |
| 1996 | HAL 共现向量空间 | -17 |
| 2003 | **Bengio 神经语言模型 (早产的 word2vec)** | -10 |
| 2006 | Hinton deep belief nets, 深度学习复苏开始 | -7 |
| 2012 | AlexNet, 深度学习回归主流 | -1 |
| 2013 | **word2vec** | 0 |

Firth 那句话变成可执行代码, 需要的不只是思想。它需要:

1. **Chomsky 范式的退潮** (统计方法被接受)
2. **符号主义碰墙** (WordNet 规模瓶颈暴露)
3. **统计基础设施成熟** (向量语义 LSA, 统计 MT)
4. **神经网络从低谷复活** (2006-2012 深度学习再起)
5. **硬件到位** (GPU 普及)
6. **大规模语料可得** (互联网文本爆炸)
7. **一个人愿意把所有这些拼起来** (Mikolov)

**思想先行半世纪, 工程跟上只需要几年。** 但在这"跟上"之前, 思想就躺在那里, 被几代学者引用, 没有变成任何产品, 也没有影响任何市场。

## 为什么这个故事值得讲

1. **范式转移的干净案例**: 从"人工定义意义"到"从数据涌现意义", NLP 整个领域在 2-3 年内完成了转向。这种事在科学史上不多见。
2. **哲学变算法的瞬间**: Firth 1957 年的一句话, 56 年后才被一个神经网络变成可执行代码。思想和工程之间的时差足以容下一整个学术流派的兴衰。
3. **AI 伦理的起点**: "技术忠实映射偏见"这件事, 从 2016 起成了 ML 所有研究团队的必答题。
4. **现代 LLM 的根**: ChatGPT、Claude、Gemini 所有这些产品的底层, 都有 word2vec 的直系血脉, 再往上追是 Bengio 2003, 再往上是 LSA 1990, 再往上是 Harris 1954。
5. **两个并行学派的对话**: Chomsky 的生成语法和 Firth 的分布语义, 吵了半个世纪, 最后是分布派赢了工程界。但 Chomsky 的语言学洞察是否在下一代模型 (如涉及语法结构的可解释 AI) 里以某种形式归来, 是个悬而未决的问题。

## 一个反思留在这里

word2vec 成功的那一刻, 整个 NLP 学界发现: **当数据足够多、训练目标足够简单、模型结构足够正确, 人为设计的那一层反而变成障碍**。

这个教训在之后十年被反复印证:

- 图像识别: 手工特征败给 CNN 端到端训练 (2012 AlexNet)
- 围棋: 人类棋谱败给自对弈 (2017 AlphaGo Zero)
- 语言: 句法分析器败给 transformer 大模型 (2019+)
- 蛋白质折叠: 物理化学规则败给 AlphaFold (2020)

每一次, 被淘汰的不是"知识", 而是"我们如何把知识塞给机器"。**知识仍然重要, 只是塞的方式变了**: 从显式规则变成了"准备数据, 给模型一个简单任务, 然后退后"。

这背后其实是一个关于**归纳 vs 演绎**的老问题。

符号派走的是演绎: 先定义什么是"意思", 然后让机器按定义行事。
分布派走的是归纳: 让机器看足够多的例子, 自己总结出"意思"是什么。

20 世纪大部分时间里, 主流科学哲学是演绎派的(理论先行, 实验验证)。**21 世纪 AI 的一个贡献, 是让归纳派拿回了它应得的位置**。

Firth 那句话, 57 年后仍然在正确的位置上。
