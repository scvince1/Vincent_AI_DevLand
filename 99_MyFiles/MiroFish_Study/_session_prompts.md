# Session启动Prompt备忘

每次开始新session时，复制对应的prompt使用。

---

## Session 1: 架构全景 + GitHub实操

```
启动 MiroFish Reading Project - Session 1

读取以下文件作为上下文：
- D:\Ai_Project\MeowOS\99_MyFiles\MiroFish_Study\2026-04-10-mirofish-reading-project-design.md (项目设计spec)
- D:\Ai_Project\MeowOS\99_MyFiles\MiroFish_Study\00_Landscape_Research.md (竞品与行业调研)

今天执行 Session 1: 架构全景 + GitHub实操

目标：
1. 给我一张能自己讲清楚的 MiroFish 整体架构图（数据流、核心模块、关键依赖）
2. 手把手带我把 MiroFish repo (https://github.com/666ghj/MiroFish) clone 到本地 D:\Ai_Project\MiroFish\
3. 遇到任何 GitHub/Git/开发者文化的术语要即时解释

重要背景：
- 这是我第一次深度使用一个完整 GitHub 项目，开发者文化对我来说是黑话
- 我不部署不跑代码，只读
- 贯穿案例是"品牌舆情预测"场景
- 每个 session 产出一份阅读笔记存到 MiroFish_Study/ 文件夹，命名格式 Session_01_xxx.md
- 时间预算：1-2 小时

按 spec 第 5 节的 session 操作方式执行：前5分钟定位 → 主体对话式阅读 → 最后10分钟整理笔记。
```

---

## Session 2: 成本模型 + 竞品定位

```
启动 MiroFish Reading Project - Session 2

读取以下文件作为上下文：
- D:\Ai_Project\MeowOS\99_MyFiles\MiroFish_Study\2026-04-10-mirofish-reading-project-design.md (项目设计spec)
- D:\Ai_Project\MeowOS\99_MyFiles\MiroFish_Study\Session_01_架构全景与GitHub实操.md (上次笔记)
- D:\Ai_Project\MeowOS\99_MyFiles\MiroFish_Study\References\ (三篇论文, 如需调用)

今天执行 Session 2: 成本模型 + 竞品定位

目标：
1. 拆清 MiroFish 一次完整 simulation 的 token 成本 (persona generation / simulation round / report 三段)
2. 分析 model routing 设计 (有无分层用便宜/贵模型)
3. 核对竞品最新动态 (Aaru, AgentSociety, MURM, 新入场者) — 这次 session 开场必须先跑 fresh verification
4. 讨论 Opus 4.6 / Claude 1M context 对 MiroFish 架构的影响

重要背景：
- Session 1 已把方法论架构过完, 本次聚焦成本和竞品
- Vincent 的 Challenge 5 = SharkNinja 家电品牌舆情预测 (Session 1 定下的贯穿案例)
- Session 1 留了"未核对项清单", 本 session 开场必须先跑 sonnet parallel subagents 核对
- 笔记命名: Session_02_成本模型与竞品定位.md
- 时间预算: 1-2 小时

按 spec 第 5 节的 session 操作方式执行：前5分钟定位(含 fresh verify) → 主体对话式阅读 → 最后10分钟整理笔记。

开场引导问题: "你预估一次 1000 人 × 72 小时模拟的合理成本是多少? 如果实际贵了 10 倍, 你会怎么砍? 从哪一环砍?"
```

---

*后续session的prompt会在每个session结束时追加到这里。*