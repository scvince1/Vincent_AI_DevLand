---
id: skill-opt-darwin-skill
title: Darwin-Skill 深度调研
tags: [synthesis, research, skill-optimization, darwin-skill, claude-skills, autoresearch]
status: active
last_modified: 2026-04-21
concept: skill-optimization
type: synthesis
generated_by: subagent-research
scope: darwin-skill 项目逆向 + 逐字引用分析：8 维 rubric、hill-climbing 循环、git revert 棘轮、评分独立性设计；Karpathy autoresearch 对应关系
source_date: 2026-04-16
---

# Darwin-Skill 深度调研

**来源 URLs:**
- Main repo: https://github.com/alchaincyf/darwin-skill
- SKILL.md raw: https://raw.githubusercontent.com/alchaincyf/darwin-skill/master/SKILL.md
- 掘金: https://juejin.cn/post/7628813128284143631
- Blog: https://jimo.studio/blog/darwin-skill-released-a-revolutionary-self-evolving-skill-system/
- SkillsReview: https://skills-review.com/skills/darwin-skill
- 作者主页: https://github.com/alchaincyf

**Fetch 日期:** 2026-04-16

---

## 元数据

| 项 | 值 |
|---|---|
| 仓库名 | alchaincyf/darwin-skill |
| Star | 949 |
| Fork | 110 |
| License | MIT |
| 最新 commit | 2026-04-14 |
| 主语言 | HTML 98.5%, JavaScript 1.5% |
| 安装量 | 43,439（skills-review.com 数据）|
| 安装命令 | npx skills add alchaincyf/darwin-skill |

---

## 作者身份

**GitHub handle:** alchaincyf
**自称:** 花叔（公众号「花叔」）

**个人描述（原话）:**
> 我不会写代码。一行都不会。但我用 AI 做出了 AppStore 付费榜 Top 1 的产品（小猫补光灯），写了 9 本技术书，造了一个能「蒸馏任何人思维方式」的开源框架。

**平台:** B 站、YouTube (@Alchain)、小红书、微博、X、WeChat 公众号「花叔」、huasheng.ai / bookai.top

**主要开源项目（按 star 排序）:**

| 仓库 | Stars | 描述 |
|------|-------|------|
| nuwa-skill | 11.7k | 蒸馏任何人的思维方式（心智模型 + 决策启发式 + 表达 DNA）|
| zhangxuefeng-skill | 6k | 张雪峰认知操作系统 |
| hermes-agent-orange-book | 2.6k | AI agent 框架指南 |
| darwin-skill | 949 | 本项目，自主 skill 优化 |
| steve-jobs-skill | 736 | 乔布斯认知操作系统，由 nuwa-skill 生成 |
| karpathy-skill | -- | Karpathy 认知操作系统 |
| munger-skill | -- | 芒格认知操作系统 |

**关键背景:** nuwa-skill 是生成器（任何公众人物 -> SKILL.md 格式认知操作系统），darwin-skill 是优化器（现有 SKILL.md -> 质量更高的 SKILL.md）。两者互补，构成「生成 -> 优化」完整闭环。

---

## 仓库文件结构




## Commit 历史（完整13条）

    2026-04-14  9f4dced  add: dark achievement + white gold result card templates  [alchaincyf + claude]
    2026-04-14  aaf3664  add: visual result card + HD screenshot script  [alchaincyf + claude]
    2026-04-14  7db5122  broaden: Claude Code Skill to Agent Skill, support Codex/OpenClaw/Trae/CodeBuddy
    2026-04-13  d11316b  rename: better.skill -> 达尔文.skill
    2026-04-13  44c2dc9  rename: Auto Skill Optimizer -> better.skill
    2026-04-13  d376fd9  upgrade: replace Mermaid with VI-consistent HTML chart screenshots
    2026-04-13  065ec0c  add: SVG banner + GitHub Pages showcase
    2026-04-13  33bbc3f  upgrade: add Mermaid flow diagrams
    2026-04    10ce74f  init: Auto Skill Optimizer  [alchaincyf + claude]

命名演化: Auto Skill Optimizer -> better.skill -> 达尔文.skill。从 init 到正式开源约 2 天。

---

## SKILL.md 全文（curl 直取，逐字引用）

以下内容从 raw.githubusercontent.com 直接 curl 获取，未做任何改动。

### Frontmatter

    name: darwin-skill
    description: Darwin Skill (达尔文.skill): autonomous skill optimizer inspired by Karpathy autoresearch.
    Evaluates SKILL.md files using an 8-dimension rubric (structure + effectiveness),
    runs hill-climbing with git version control, validates improvements through test prompts,
    and generates visual result cards.
    Trigger keywords: 优化skill / skill评分 / 自动优化 / auto optimize / skill质量检查 /
    达尔文 / darwin / 帮我改改skill / skill怎么样 / 提升skill质量 / skill review / skill打分

### 核心理念（原文）

借鉴 Karpathy autoresearch 的自主实验循环，对 skills 进行持续优化。
核心理念：评估 -> 改进 -> 实测验证 -> 人类确认 -> 保留或回滚 -> 生成成果卡片

### 设计哲学（原文逐字）

autoresearch 的精髓：
1. 单一可编辑资产 — 每次只改一个 SKILL.md
2. 双重评估 — 结构评分（静态分析）+ 效果验证（跑测试看输出）
3. 棘轮机制 — 只保留改进，自动回滚退步
4. 独立评分 — 评分用子agent，避免「自己改自己评」的偏差
5. 人在回路 — 每个skill优化完后暂停，用户确认再继续

与纯结构审查的区别：不只看 SKILL.md 写得规不规范，更看改完后实际跑出来的效果是否更好。

---

## 评估 Rubric（8维度，总分100）

### 结构维度（60分）— 静态分析

| # | 维度 | 权重 | 评分标准 |
|---|------|------|----------|
| 1 | Frontmatter质量 | 8 | name规范、description包含做什么+何时用+触发词、≤1024字符 |
| 2 | 工作流清晰度 | 15 | 步骤明确可执行、有序号、每步有明确输入/输出 |
| 3 | 边界条件覆盖 | 10 | 处理异常情况、有fallback路径、错误恢复 |
| 4 | 检查点设计 | 7 | 关键决策前有用户确认、防止自主失控 |
| 5 | 指令具体性 | 15 | 不模糊、有具体参数/格式/示例、可直接执行 |
| 6 | 资源整合度 | 5 | references/scripts/assets引用正确、路径可达 |

### 效果维度（40分）— 需要实测

| # | 维度 | 权重 | 评分标准 |
|---|------|------|----------|
| 7 | 整体架构 | 15 | 结构层次清晰、不冗余不遗漏、与花叔生态一致 |
| 8 | 实测表现 | 25 | 用测试prompt跑一遍，输出质量是否符合skill宣称的能力 |

**评分公式:** 总分 = Σ(维度分 × 权重) / 10，满分100。改进后总分必须严格高于改进前才保留。

### 实测表现评分方式（原文逐字）

1. 为每个skill设计2-3个典型用户prompt（最常见的使用场景，不是边缘case）
2. 用子agent执行：with_skill（带SKILL.md跑）vs baseline（不带skill跑同一prompt）
3. 对比输出质量：输出是否完成用户意图？相比baseline质量提升明显吗？有没有负面影响？

如果无法跑子agent，退化为干跑验证：读完skill后模拟执行思路，在results.tsv中标注 dry_run。

---

## 自主优化循环

### Phase 0: 初始化

1. 确认优化范围（全部 skills / 指定 skills）
2. 创建 git 分支：auto-optimize/YYYYMMDD-HHMM
3. 初始化 results.tsv（如不存在）
4. 读取现有 results.tsv 了解历史优化记录

### Phase 0.5: 测试Prompt设计

为每个skill设计2-3个测试prompt，覆盖最典型使用场景和一个稍复杂/有歧义的场景。
存到 skill目录/test-prompts.json，格式:
    [{"id": 1, "prompt": "用户会说的话", "expected": "期望输出的简短描述"}, ...]

展示给用户确认后再进入评估。测试prompt的质量决定了优化方向是否正确。

### Phase 1: 基线评估（原文伪代码）

    for each skill in 优化范围:
      # 结构评分（主agent可以做）
      1. 读取 SKILL.md 全文，按维度1-7逐项打分（附简短理由）
      # 效果评分（用子agent做，独立于主agent）
      3. 对每个测试prompt，spawn子agent：with_skill vs baseline
      4. 对比两组输出，打维度8的分
      5. 计算加权总分，记录到 results.tsv

如果子agent不可用，维度8用干跑验证打分，标注 dry_run。
基线评估完成后展示评分卡，暂停等用户确认再进入优化循环。

### Phase 2: 优化循环（原文伪代码，完整引用）

    for each skill:
      round = 0
      while round < MAX_ROUNDS (默认3):
        round += 1
        # Step 1: 找出得分最低的维度
        # Step 2: 生成1个具体改进方案（改什么/为什么/预期提升多少）
        # Step 3: 编辑 SKILL.md，git add + commit
        # Step 4: 重新评估（结构=主agent，效果=独立子agent）
        if 新总分 > 旧总分:
          status = keep
        else:
          status = revert
          git revert HEAD  # 创建新commit回滚，不用reset --hard
          break  # 该skill到瓶颈
      # 每个skill完后：展示git diff + 分数变化 + 输出对比，等用户确认

### Phase 2.5: 探索性重写（可选）

触发条件：连续2个skill都在round 1就break（涨不动）

    1. git stash 保存当前最优版本
    2. 从头重写SKILL.md（不是微调，是重新组织结构）
    3. 重新评估
    4. if 重写版 > stash版: 采用；else: git stash pop 恢复

必须征得用户同意后才执行。这解决了 hill-climbing 的局部最优问题。

---

## results.tsv 格式（原文逐字引用）

    timestamp  commit  skill  old_score  new_score  status  dimension  note  eval_mode
    2026-03-31T10:00  baseline  huashu-proofreading  -  78  baseline  -  初始评估  full_test
    2026-03-31T10:05  a1b2c3d  huashu-proofreading  78  84  keep  边界条件  补充fallback  full_test
    2026-03-31T10:10  b2c3d4e  huashu-proofreading  84  82  revert  指令具体性  过度细化  dry_run

eval_mode: full_test（跑了子agent）或 dry_run（模拟推演）
文件位置: .claude/skills/darwin-skill/results.tsv

---

## 优化策略库（P0-P3 优先级，原文引用）

P0: 效果问题（实测发现）— 输出偏离/带skill比不带还差/格式不符预期
P1: 结构性问题 — Frontmatter缺触发词/缺Phase-Step结构/缺确认检查点
P2: 具体性问题 — 步骤模糊/缺输入输出规格/缺异常处理
P3: 可读性问题 — 段落过长/重复描述/缺速查

---

## 约束规则（原文逐字引用）

1. 不改变skill的核心功能和用途 — 只优化写法和执行方式，不改做什么
2. 不引入新依赖 — 不添加skill原本没有的scripts或references文件
3. 每轮只改一个维度 — 避免多个变更导致无法归因
4. 保持文件大小合理 — 优化后SKILL.md不应超过原始大小的150%
5. 尊重花叔风格 — 中文为主、简洁为上
6. 可回滚 — 所有改动在git分支上，用git revert而非reset --hard
7. 评分独立性 — 效果维度必须用子agent或至少干跑验证，不能在同一上下文里改完直接评

---

## 成果卡片系统

3种视觉风格（随机选一）:
- Warm Swiss (.theme-swiss): 暖白底+赤陶橙，Inter字体，干净网格
- Dark Terminal (.theme-terminal): 近黑底+荧光绿，等宽字体，扫描线
- Newspaper (.theme-newspaper): 暖白纸+深红，衬线字体，双栏编辑风

生成命令: npx playwright screenshot file:///path/card.html#[theme] output.png --viewport-size=960,1280

品牌 tagline（原文）: Train your Skills like you train your models

---

## 设计灵感 — Karpathy 对应关系（原文引用）

Karpathy 原话: You write the goals and constraints in program.md; let an agent generate and test code deltas indefinitely; keep only what measurably improves the objective.

SKILL.md 中的对应关系:
    program.md   ->  本文件（评估rubric和约束规则）
    train.py     ->  每个SKILL.md
    val_bpb      ->  8维加权总分（含实测表现）
    git ratchet  ->  只保留有改进的commit
    test set     ->  每个skill的test-prompts.json

区别：增加了人在回路（autoresearch是全自主的，skill优化需要人的判断力），以及双重评估机制（结构+效果），因为skill的好坏比loss数值更微妙。

---

## 实测案例

来自 jimo.studio 发布博文（2026-04-14）:
- huashu-slides: 5轮优化，从能用但风险大变为稳得可以去喝咖啡
- comedy skill: 单次优化，解决风格选择无结构问题
- 7个 perspective skills: 5轮批量优化，达到风格稳定不飘移

来自掘金文章: skill-A 67->78，skill-B 68->82

---

## 凌喵阅读笔记 & A-ha 时刻

### 1. 进化系统，不是 prompt engineering 工具

核心不是如何写好的 SKILL.md，而是如何自动发现并修复不好的 SKILL.md。input 是一批现有的已在用的 skills；output 是同样一批 skills 但质量更高。用户只需确认好不好。

### 2. 自己改自己评的偏差被显式设计掉了

评分独立性（约束7）是整个系统最聪明的决定。改 SKILL.md 的是主 agent，评效果的是独立子 agent。同一 context 里做过改动的 agent 评估时会被记忆污染，倾向于给自己的改动打高分。独立子 agent 评分解决的是 confirmation bias 问题。

### 3. 棘轮用 git revert 不用 reset --hard，是有意为之

保留了失败尝试的历史（results.tsv 记录 status=revert），可以事后分析哪类改进方向总是失败。reset --hard 永久丢失这个信息。审计轨迹是设计目标，不是副作用。

### 4. dry_run 降级机制是工程实用主义

子 agent 跑不了时不报错退出，而是降级为模拟推演并标注 dry_run。不完美的评估 > 零评估。对 Challenge 5 这类复杂 pipeline 有参考价值：评估机制需要能优雅降级。

### 5. Phase 2.5 探索性重写解决局部最优问题

hill-climbing 固有缺陷是局部最优。连续 2 个 skill 在 round 1 break 时提议从头重写，是 simulated annealing 式的跳出局部，且有 git stash 保底。

### 6. 实测表现权重最高（25分）是核心价值主张

60+40 分配里，实测表现单独占 25 分，是 8 个维度里最高的单项。大量 skill 写得规整，但实际调用效果平庸甚至有害——这是作者对 SKILL.md 生态的诊断。

### 7. 触发词是 skill 的门面，也是最低门槛

frontmatter description 要求做什么+何时用+触发词且 ≤1024 字符，触发词中英文均要有。在 Claude Code skill 调度机制里，触发词 matching 是路由核心。再好的 skill 无法被触发等于没有。

### 8. darwin-skill 是花叔生态的 meta-infrastructure

nuwa-skill 生成人物认知操作系统 -> 生成的 skills 质量参差 -> darwin-skill 自动优化这些 skills。rubric 里维度7 与花叔生态一致（权重15分），说明这不是通用优化器，而是针对特定生态调校的。两者合在一起是完整的生产+维护闭环。

### 9. 项目从 init 到开源不超过 2 天，安装量超 4 万

Claude Code skills 生态正处于早期爆发期，分发摩擦极低。这个增长速度本身是信息——做出来就会有人用。

### 10. 对 Challenge 5 的启示

Challenge 5 需要评估 scraper、sentiment analyzer、failure-mode classifier、prediction UI 各个节点的质量。darwin-skill 的框架提示：
- 评估要有 baseline 对比（相对改进量，不是绝对打分）
- 评估要双轨：结构静态分析 + 实测效果
- 失败改动要保留记录（标 revert，不是删掉），事后分析失败模式
- 评分独立性很关键：改节点的 agent 不能自己评自己

---

## 开放问题

1. rubric 可定制吗？ 不同类型 skill 权重分配应不同，目前未见定制机制。

2. 多 skill 依赖问题？ 优化一个 skill 会不会破坏依赖它的下游 skill？没有处理依赖图。

3. 测试 prompt 质量谁来评？ 覆盖错误场景 = garbage-in garbage-out。

4. 迁移到 Challenge 5 的路径？ 如何把 rubric 思路迁移到评估多组件 pipeline 的某个节点是开放设计问题。

5. security rating 50/100 标注 dangerous 具体指什么？ 自动修改文件 + git commit 在某些环境有副作用，细节未说明。

---

## 外部讨论摘要

- 掘金文章（2026-04）: 像训练模型一样优化你的 Agent Skills，强调只保留改进，时间就站在你这边
- jimo.studio blog（2026-04-14）: 作者全名 Yang Fangxian（花叔），革命性自进化技能系统
- skills-review.com: 43,439 安装，社区评分 1.84/5（零评论，数字来源待核实）
- 知乎/小红书未搜索到外部讨论，花叔有小红书账号，讨论可能在闭环内
