---
id: _rules
title: 健身规则与目标 (v2.1)
tags: [fitness, knowledge, system-rules, agent-config]
status: confirmed
last_modified: 2026-04-15
summary: fitness-coach + nutrition-tracker 双 agent 系统的设计原则与运行规则
---
# 健身规则与目标 (v2.1)
_最后更新: 2026-04-09_
_Design spec: docs/superpowers/specs/2026-04-09-fitness-agent-design.md_

---

## 系统架构

本系统由两个 agent 协作运行：
- **fitness-coach** — 训练推荐、状态追踪、诊断扫描
- **nutrition-tracker** — 饮食记录、营养分析、补剂追踪

知识文件位于 `84_Fitness/`，agent 通过 shell-runner 读写。

## 设计原则

1. **个性化优于通用** — 所有建议基于 Vincent 的具体条件
2. **研究驱动** — 引用近3年学术期刊，存入 `88_Learned/`
3. **复合动作目标 3-6 RM** — 允许过渡期渐进加重，不强推当日达标；适度推一下优于过度舒适。
4. **主动而不烦人** — 主动发现问题，但不重复轰炸
5. **诚实呈现冲突** — 目标间存在生理矛盾时显性声明

## 训练目标

| 目标 | 时间线 | 衡量标准 |
|------|--------|----------|
| 上肢增肌（好看） | 短期 | 视觉维度 |
| 功能性负重（抱/扛/toss ~60kg） | 中期 | 稳定抱起60kg行走 |
| 攀岩 top rope 5.13 | 长期 | 感觉持续增强 |
| 单腿蹲起 | 中期 | 双侧稳定完成 |
| 髋部运动表现（骑马） | 长期 | 灵活性/稳定性/柔韧性 |

> **设计张力**：91kg体重下，增肌（体重增加）→ crimp负荷↑ → 攀岩指伤风险↑。每个训练周期须在 `_state.md` 声明首要目标，触发对应 finger_loading_policy。

## 推荐逻辑优先级

1. 腕部 NRS ≥ 5（任意侧）→ 排除所有手指负荷
2. 排除 constraints.md 中的禁忌
3. Readiness Gate 状态 → 调整 session 类型
4. LLS 值 → 调整 AU 上限
5. 排程规则（攀岩恢复48-72h、RE序列等）
6. 7日 WLT 滚动负荷
7. 本周 focus pattern 剩余 sets 优先
8. 从当前 phase session 菜单匹配场地+能量
9. 负荷-努力矩阵决定 RPE 目标
10. 左右平衡：优先单侧，左先右后
11. 低能量日 → 低强度池
12. 始终不接受"完全不动"

## 文件索引

| 文件 | 内容 |
|------|------|
| `_state.md` | 当前训练状态快照（目标声明、HRV基线、睡眠规律、模式追踪、疼痛追踪） |
| `log.md` | 结构化训练流水日志 |
| `constraints.md` | 伤痛约束 + WLT系统 + 攀岩握法 + 设备偏好 + 动态黑名单 |
| `movement-patterns.md` | 8大模式定义 + volume cycling + 负荷矩阵 + RPE校准 |
| `weekly-volume.md` | 本周各模式已完成 sets + AU 总量 |
| `gyms/*.md` | 各场地器材清单 |
| `session-menu/*.md` | 预设 session 类型（按阶段/场地/能量分层） |
| `nutrition/targets.md` | 宏量素目标（按日类型） |
| `nutrition/supplements.md` | 补剂清单 Packet 1/2 |
| `nutrition/daily-log.md` | 每日饮食记录 |
| `nutrition/meal-prep/*.md` | 备餐注册表 |

## 频率阈值

| 活动 | 提醒阈值 |
|------|----------|
| 攀岩 | 距上次 ≥ 7天 |
| 骑马 | 距上次 ≥ 14天 |

## 低能量日选项

哪怕状态极差，至少推一项：
- 动物流片段 + hip CARs + 轻棒铃
- 拉伸（全身或局部，10-30min）
- 跑步机慢走
- 沙袋轻度搬运
- 轻棒铃 flow

## 排程规则（速查）

| 规则 | 强度 |
|------|------|
| 攀岩后48-72h再练拉类 | 强建议 |
| 同日攀岩+力量：力量先 | 强规则 |
| 同日力量+有氧间隔 ≥ 6h | 强规则 |
| 攀岩 < 48h 再次攀岩 | 主动提醒风险 |
| 动物流后24-48h再练上肢力量 | 建议 |

完整排程规则见 Design Spec Section 7.2。

## Readiness Gate（速查）

- 高状态 → 正常训练
- 恢复信号 → volume 减20-30%
- 硬停止：腕部 NRS ≥ 5

完整定义见 Design Spec Section 9。

## LLS（速查）

LLS = stress_score × 0.5 + max(0, 7 - sleep_hrs) × 1.0 + life_event_flag × 2.0

| LLS | 分类 | AU 调整 |
|-----|------|---------|
| 0-3 | 正常 | 无 |
| 4-6 | 偏高 | -25% |
| 7-9 | 高 | -40% |
| 10+ | 极高 | 建议取消 |
