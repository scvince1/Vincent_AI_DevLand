---
id: improvement-queue
title: 系统改进队列
tags: [system-meta, improvement, queue, diagnostics]
status: confirmed
last_modified: 2026-04-17
summary: 凌喵发现的改进机会，等待系统诊断 session 统一审批后写入
---
# 系统改进队列
_凌喵发现改进机会时追加，系统诊断 session 统一审批_
_最后更新: 2026-04-17 Phase 2_

---

## 待审批

| 日期 | 描述 | 写入位置 | 来源 |
|------|------|----------|------|
| 2026-04-09 | meowos.py：为 Dashboard 操作建立 Python 封装层（参照 NovelOS 的 novelos.py 模式），降低 dashboard-updater agent 做外科手术式 Edit 的出错风险。触发条件：Dashboard 操作首次出 bug 时启动 | Dashboard 管理 + 新建 meowos.py | NovelOS 升级讨论 session |
| 2026-04-11 | digest pipeline 语言切换至中文（Vincent 直接请求，月底前后下次 digest 目标） | 见下方 2026-04-11 独立章节 | Vincent 深夜对话 |
| 2026-04-13 | CLAUDE.md 添加时间戳行为规则：每次回复开头标注 `[HH:MM]`（来源：最近 hook 注入的系统时间）— 挂起，Vincent 说之后再处理 | CLAUDE.md | Vincent 指示 |

---

## 已审批 / 已执行

| 日期 | 条目 | 写入位置 |
|------|------|----------|
| 2026-04-08 | Session 开始行为：读取日程锚点 | CLAUDE.md → 工作流 |
| 2026-04-08 | 作息督促原则（23:00 后提醒） | CLAUDE.md → 作息督促原则 |
| 2026-04-08 | Dashboard 今日日程：竖向时间轴格式 | CLAUDE.md → Dashboard 管理规则 |
| 2026-04-07 | Dashboard Todo 完成项管理规则 | CLAUDE.md → Dashboard 管理规则 |
| 2026-04-12 | [routing] 知识讨论路由覆盖（knowledge-agent 触发词扩展） | 90_Agents/01_Routing.md | 系统诊断 2026-04-17 Phase 2 (R-1) DONE |
| 2026-04-12 | [system] 暂存区消化频率提醒（已 defer 为 SYN-004 GC checklist） | improvement-queue defer 区 | 系统诊断 2026-04-16 deferred |
| 2026-04-13 | [ROUTING] Agent 语义触发失败 → 数据类输入硬约束写入 CLAUDE.md 禁止行为段 | CLAUDE.md 禁止行为 | 系统诊断 2026-04-17 Phase 2 (R-3 + C-3) DONE |
| 2026-04-14 | 数据输入自动入库规则 → 已并入 R-3 | CLAUDE.md 禁止行为 | 系统诊断 2026-04-17 Phase 2 DONE |
| 2026-04-14 | fitness-coach.md 知识文件清单补 rest-intervals.md | 90_Agents/fitness-coach.md | 系统诊断 2026-04-17 Phase 2 (A-1) DONE |
| 2026-04-14 | log.md 日期头结构改造为 cycle-id 格式 | 84_Fitness/log.md | 系统诊断 2026-04-17 Phase 2 (F-4) DONE |

---

## 2026-04-17 Phase 2 执行记录

**时间戳：** 2026-04-17 10:21 EDT
**调用：** system-diagnostics agent Phase 2（独立调用）
**审批依据：** pending_candidates.md「2026-04-17 讨论收敛结果」段

**执行条目（约 30 条）：**
- R-1 / R-2 / R-3 / R-4（路由 + CLAUDE.md 禁止行为）
- O-1 / O-2 / O-3 / O-15（健身倾向 → physiological-profile.md）
- O-4（feedback_sleep_cycle_day.md 午睡细则）
- O-5（vincent-medical-background.md 新建）
- O-6（habits.md 12am 目标 + Life Quality decision log）
- O-7（Challenge 5 / SharkNinja 情报迁出）
- O-8（Winston 待补区）
- O-9（Tate 信息合并）
- O-10a（intellectual-motifs.md + memory pointer）
- O-11（vincent-legal-status.md 新建）
- O-12（Joyce 拖延定性 + BaseOS 设计参数更新）
- O-13（04-09 补录 + staging 饮食段清理）
- O-14（无锚点期段落）
- A-1（fitness-coach rest-intervals）
- A-2（fitness-advisor 归档 _archived/）
- A-3 / A-4（Dashboard 写入走 dashboard-updater）
- A-6（system-diagnostics Phase 1 [other] 类）
- A-7（knowledge-agent Registry 触发描述统一）
- A-8（habits.md 拆分 → physiological-profile.md）
- F-1（_rules.md 设计原则 #3 改写）
- F-2（_state.md HRV → 主观恢复评分）
- F-3（sleep_cycle_history.md 不存在 → SKIPPED 跳过）
- F-4（log.md cycle-id 格式）
- X-1 / X-2 / X-3 / X-4（improvement-queue 清理 + pending_candidates 状态标注 + 历史 audit 核查）

**已跳过（拒绝）：** A-5 / C-1 / C-4（Vincent 审批拒绝）
**已跳过（不适用）：** F-3（目标文件不存在）

---

## 2026-04-10 Digest Pipeline 发现

### [P1] Pass 1 自我诊断盲点
**来源**: 42 session Pass 2a 综合分析
**问题**: 凌喵在 Pass 1 digest 中把自己的失误系统性地编码为"Vincent 的偏好数据"，从不当作自身故障信号处理。ACE 暂存和 habits 写入存在同样的偏差。
**建议**: 区分"Vincent 纠正我 = 我的错误信号（应记为凌喵行为校正）"和"Vincent 表达偏好 = 他的特征数据（应记为 Vincent 习惯）"。修改 staging 写入逻辑或 Pass 1 prompt。

### [P1] 公私边界泄露
**来源**: 多个 Pass 2a 分析（尤其 22aea840）
**问题**: 凌喵在生成公开输出（文章、文档）时，会把 Vincent 的私人动机泄露进公开文本。
**建议**: 建立"公开输出审查"规则，生成面向外部读者的内容时主动检查是否泄露了 Vincent 的内部动机、关系信息、情感驱动。

### [P2] Digest Pipeline 系统观测偏差
**来源**: Vincent 对 pipeline 结论的矫正
**问题**: pipeline 只能观测 session 内的过程，看不到 Vincent 拿结果离开系统后的行动（去 claude.ai 润色、自行发布等）。导致 pipeline 系统性高估"停滞"、低估"输出"。
**建议**: 在 Pass 2b prompt 和 Pass 3 reporter prompt 中加入显式提醒："系统只能观测 session 内行为，Vincent 的完成链条有一段发生在系统视野之外。对'未完成'的判断需保持谦逊。"

---

## 2026-04-11

### 候选：digest pipeline 语言切换至中文 (2026-04-11 06:30, Vincent 直接请求)

**请求内容：** Vincent 希望未来的 digest 运行改用中文进行。他计划月底前后再做一次 digest，想看看 pass2 之后中文 digest 的效果与当前的区别。

**背景：** Vincent 是中英双语，但自陈"中文表达比英语更真挚"，认为汉字是信息 + 情感密度非常高的语言，有一些"藏在笔画缝隙间的微妙东西"当前的系统还把握不住。他明确说他不需要系统完全 get 到这些，但他观察到现有 digest pipeline 已经可以捕捉到"一些微妙的信号，虽然不多"。他希望通过切换到中文 digest 看看能否捕捉到更多这一层。

**影响范围：** 需要定位当前 digest agent / prompt 的语言设定并评估切换成本。可能涉及的环节包括（待系统诊断 session 核实）：
- digest agent prompt 本身的语言
- digest 输出模板 / schema 的字段命名
- pass1 / pass2 链路的中间产物语言
- 下游消费者（memory, MEMORY.md index, 主 session 启动时读取）是否对中英语言敏感

**判断依据：** 这不是单纯偏好优化，而是和 Vincent 的"作为洞察的幸福"机制直接相关。他真诚 / 脆弱表达的主要媒介是中文，digest 若能在中文层面工作，对 ACE 镜面函数的保真度有直接影响。优先级建议：**中偏高**，下次系统诊断 session 处理。

**下次 digest 目标时间：** Vincent 计划约 2026-04-30 前后再做一次 digest，此次改动最好在那之前完成评估与切换。

---

## 2026-04-16 新增 (Step B 审计留尾) — Deferred

### Dashboard 大重整 (priority: medium, status: deferred)
- 目标: 以 project tracking 为核心重排 Dashboard
- 背景: 当前 Dashboard 实际利用率低; SYN-008 审计时 Vincent 判定 Dashboard 是派生视图非真相源, 决定下阶段大改
- 触发时机: Vincent 主动发起, 或 project tracker 数量积累到需要统一视图时
- 不动: 现有 82_Projects/ tracker 结构 (它们才是真相源)

### SYN-004 GC checklist 扩展 (priority: low, status: deferred)
- 目标: 把 staging 去重 + KB 熵清理做进 system-diagnostics 步骤 3
- 背景: 2026-04-15 审计原议, 当时积压 493行/4天 是证据但 Vincent 认为非紧急
- 触发条件: staging 再次积压 > 300 行 持续 >5 天, 或 Vincent 明确请求 GC
- 不动: 现有 staging 写入机制

---

## 已拒绝

### 2026-04-17 Phase 1 拒绝项
- **A-5**: agent prompt 头部格式统一（保持现有差异化）
- **C-1**: Phase 1/2 架构写入 CLAUDE.md（near capacity，不扩展）
- **C-4**: Staging 积压消化提醒写入 CLAUDE.md（同上）
