# MiroFish Reading Project - Design Spec

*Created: 2026-04-10*
*Status: Approved by Vincent*

---

## 1. 项目概述

### 是什么
一个为期约4周(8个session)的阅读理解项目。目标是深入理解MiroFish(多Agent群体智能预测引擎)的架构、原理、方法论和成本模型。

### 不是什么
- 不是部署项目 - 当前阶段不跑起来
- 不是开发项目 - 不写代码，只读代码
- 不是紧急项目 - 兴趣驱动，每周2次，每次1-2小时

### 为什么做
1. **面试武器**: 学习多Agent系统，直接关联Consumer Intelligence岗位。MiroFish的商业对标是估值$10亿的Aaru
2. **小说写作**: MiroFish本质是"故事推演引擎"，与NovelOS理念相关
3. **学术研究**: 历史情境模拟、政策推演的可能性
4. **与Jailbreak Challenge的关系**: Challenge做监测层(消费者正在说什么)，MiroFish做预测层(消费者接下来会怎样)，合在一起是完整的Consumer Intelligence Pipeline

### 优先级
兴趣项目。低于面试准备和Jailbreak Challenge。不赶时间，按节奏推进。

---

## 2. 项目结构

### 文件位置
`D:\Ai_Project\MeowOS\99_MyFiles\MiroFish_Study\`

### 已有文件
- `00_Landscape_Research.md` - 竞品、行业方案、商业媒体视角的综合调研

### 产出物
每次session产出一份阅读笔记:
```
Session_01_架构全景与GitHub实操.md
Session_02_成本模型与竞品定位.md
Session_03_种子文本与实体提取.md
...
```

### 笔记格式
每份笔记包含:
- **今天看了什么**: 哪些文件，哪些概念
- **用自己的话解释**: Vincent的理解，凌喵帮整理但核心是Vincent自己的话
- **问题和想法**: 没弄懂的、可改进的、联想到的应用场景
- **下次预告**: 下回要看什么

---

## 3. 贯穿案例

**品牌舆情预测**: "某消费品牌出事后，社交媒体舆论怎么演化"

选择理由:
- 与MiroFish默认能力最对口(原生支持舆情推演)
- 种子材料容易获取(真实品牌事件)
- 直接关联Consumer Intelligence岗位面试
- 可以和Jailbreak Challenge的SharkNinja案例呼应
- 具体品牌事件待Challenge方向确定后选定

全程跟着这个案例走，每个session看的都是案例经过的下一个环节。

---

## 4. 阅读路线图

### Phase 1: 全景 + 落地 (Session 1-2)

**Session 1: 架构全景 + GitHub实操**
- 看: 整体pipeline图、文件结构、依赖关系
- 做: 教Vincent clone repo到本地
- 带走: 一张自己能讲清楚的架构图 + 本地有了代码可以翻

**Session 2: 成本模型 + 竞品定位**
- 看: config.py、.env配置、LLM调用链路
- 结合: 00_Landscape_Research.md里的竞品信息
- 带走: 能回答"跑一次要花多少钱、贵在哪、怎么省"

### Phase 2: 跟着案例走前半段 (Session 3-5)

**Session 3: 种子文本 -> 实体提取**
- 看: text_processor.py, ontology_generator.py, graph_builder.py
- 案例对应: "一条品牌危机新闻被输入后，怎么变成人物关系网络"
- 带走: 理解实体提取和图谱构建的流程

**Session 4: 实体 -> Agent人设**
- 看: zep_entity_reader.py, oasis_profile_generator.py
- 案例对应: "图谱里的消费者节点怎么变成有性格的Agent"
- 带走: 理解人设生成的逻辑

**Session 5: 模拟配置生成**
- 看: simulation_config_generator.py, simulation_manager.py
- 案例对应: "模拟世界的规则是怎么被LLM设计出来的"
- 带走: 理解配置生成的决策链

### Phase 3: 跟着案例走后半段 (Session 6-7)

**Session 6: 模拟运行 + 记忆回写**
- 看: simulation_runner.py, run_parallel_simulation.py, zep_graph_memory_updater.py
- 案例对应: "Agent们在模拟Twitter/Reddit上怎么互动，记忆怎么演化"
- 带走: 理解模拟执行和记忆更新机制

**Session 7: 报告生成 + 对话**
- 看: report_agent.py, zep_tools.py
- 案例对应: "怎么从一堆模拟数据里提炼出舆情洞察报告"
- 带走: 理解ReACT循环和工具调用模式

### Phase 4: 回看全局 (Session 8)

**Session 8: 我的版本要改什么**
- 做: 回顾全部笔记，识别改进点，规划prototype方向
- 带走: "Vincent's MiroFish Fork"改造清单
- 输出: 从阅读项目过渡到开发项目的转折点

---

## 5. 每次Session的操作方式

### 时间结构 (1-2小时)

**前5分钟: 定位**
- 凌喵给出当天要看的文件列表
- 一个引导问题(如"今天我们要搞懂: 一段新闻是怎么变成人物关系网络的")

**主体: 对话式阅读 (50-90分钟)**
- 凌喵把代码按逻辑块拆开讲解，不逐行读，而是"这一块在干嘛"
- 每块代码配类比解释
- Vincent随时提问
- 遇到GitHub/开发者文化的东西即时解释

**最后10分钟: 收尾**
- Vincent用自己的话总结今天学到了什么
- 凌喵整理成笔记存到MiroFish_Study/
- 记下没弄懂的和下次要看的

### 关键原则
- **不读每一行代码，读"关键决策"** - 为什么作者这么做、有什么替代方案
- **始终回到案例线索** - "在品牌舆情这个场景里，这一步对应什么"
- **遇到新概念当场解释** - RAG、IPC、GraphRAG等，不积压
- **面试视角穿插** - 适时指出"这个点在面试里可以怎么说"

---

## 6. 前置知识补充计划

Vincent是第一次深入使用GitHub完整项目。以下概念在出现时即时教学:

### GitHub/Git
- clone, fork, branch, commit, PR, issue, star
- Conventional Commits格式
- README、LICENSE、.gitignore的作用
- 开源社区的基本礼仪

### 开发者文化
- 依赖管理(requirements.txt, package.json)
- 环境变量(.env)和配置管理
- Docker的概念(不需要深入)
- API的概念(前后端如何通信)

### AI/ML概念
- RAG (Retrieval-Augmented Generation)
- GraphRAG
- Agent-based Modeling
- Prompt engineering在代码中的体现

不做专门的补课session。所有概念在路线图中自然出现时教学。

---

## 7. 与其他项目的接口

### Jailbreak Challenge
- Challenge做监测层，MiroFish做预测层
- 品牌舆情案例可以复用Challenge的数据源和品类选择
- 面试叙事: "我先做了sentiment dashboard，同时在研究predictive simulation"

### 面试准备
- 每个session都注意积累面试素材
- 高管语言对照: synthetic personas, digital twins, silicon sample, share of model
- Aaru作为商业验证参考($10亿估值)

### NovelOS
- Session 7(报告生成)和ScrollWeaver项目有关联
- 故事推演能力是长期探索方向，不在本阅读项目范围内

---

## 8. 成功标准

完成8个session后，Vincent能够:

1. **画出并讲清** MiroFish的完整架构和数据流
2. **解释每个环节的原理** - 不需要能写代码，但能说出"它在这里做了什么、为什么这么做"
3. **识别关键决策和trade-off** - 比如"用Zep而不是本地方案的利弊"
4. **估算成本** - 跑一次模拟大概花多少钱，钱花在哪里
5. **说出改进方向** - "如果我自己做一个版本，我会改这些地方"
6. **在面试中自然提及** - 用高管听得懂的语言描述这个技术方向的价值
