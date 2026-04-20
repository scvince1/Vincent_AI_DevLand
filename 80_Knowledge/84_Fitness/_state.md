---
id: _state
title: 训练状态快照
tags: [fitness, knowledge, state, readiness, hrv]
status: confirmed
last_modified: 2026-04-19
summary: 当前训练状态：目标优先级、HRV 基线、睡眠规律性指标实时快照
---
# 训练状态快照
更新: 2026-04-19

## 目标优先级声明（每周期更新）
current_primary_goal: hypertrophy
bodyweight_target: 维持91kg（不主动增重）
finger_loading_policy: conservative
phase: Layer2-Volume-Week1
focus_patterns: [H-Push, Hinge, V-Pull]

## 主观恢复评分（1-10，7日滚动）
subjective_recovery_7d_mean: [待建立]
baseline_ready: false（校准中，Day 0/14）
note: Apple Watch 存在但极少用；改用主观评分（起床 30min 内自评 1-10，10=充满能量，1=极度疲惫）

## 睡眠规律性（7日滚动）
sleep_midpoint_sd_7d: [待建立 - 数据点 < 7]
sleep_regularity_multiplier: 0.90（Cycle_04-18 中断睡眠，09:30 觉醒一次；总时长偏低）
last_7d_sleep_times: [2026-04-19 04:00, 2026-04-17 01:30, 2026-04-14 03:30 (fragmented), 2026-04-13 14:30, 2026-04-12 14:30, 2026-04-11 12:00, 2026-04-10 12:00]
last_7d_wake_times: [2026-04-19 11:30, 2026-04-18 11:57, 2026-04-14 14:30, 2026-04-13 19:00, 2026-04-12 19:00, 2026-04-11 19:30, 2026-04-10 19:30]
last_sleep_total_hours: 7.50（估算：04:00入睡→09:30中断(5.5h)+09:30重睡→11:30醒(2h)，中途眼罩脱落被光晃醒）
last_sleep_quality: fragmented（一次觉醒@09:30眼罩脱落；重入睡2h；净睡有缺口）
last_sleep_note: Cycle_04-18 deload 周期睡眠，中断一次，总量 ~7.5h，低于前 cycle 10.45h 恢复性睡眠；sleep_regularity_multiplier 从 1.00 降回 0.90

## 各模式上次训练
| 模式 | 上次日期 | 场地 | RPE | WLT | 备注 |
|------|----------|------|-----|-----|------|
| H-Push | 2026-04-17 | UM | 5 | 1 | 卧推 95lbs×10×6, 22min, sRPE:5, AU:110, 腕NRS: 0/0. 末 2 组不稳→真 RPE ≥8 |
| H-Pull | 2026-04-14 | Commercial gym | 6 | 1 | 背日, 35min, sRPE(physical):6, AU:228, 腕NRS: 左0/右0(默认) |
| V-Push | 2026-04-17 | UM | 5 | 0 | 哑铃推肩 25lbs×10×3 (随 H-Push), 腕NRS: 0/0 |
| V-Pull | 2026-04-14 | Commercial gym | 6 | 1 | 高位下拉+器械下拉+直臂下压, 13组, 腕NRS: 左0/右0(默认) |
| Hinge | 2026-04-12 | 公寓健身房 | 6.5 | 1 | DL 165/190lb + RDL 165/115lb, 31min, sRPE:6.5(physical)/9.5(CNS), AU:201, 腕NRS:0. CNS-LIMITED. 首次conventional DL, 动作模式未建立 |
| Knee | — | — | — | — | 待记录 (04-12 skipped due to nausea/CNS) |
| Carry | 2026-04-12 | 公寓→健身房 | 5 | 0 | 沙袋熊抱行走 40kg, 4×~1min (来回各2) |
| Rot | 2026-04-11 | 公寓健身房 | 6-7 | 0 | 站姿绳索转体 6组 |

## 活动频率追踪
| 活动 | 上次日期 | 距今天数 | 阈值 | 状态 |
|------|----------|----------|------|------|
| 攀岩 | 2026-04-15 | 0 | 7天 | 🟢 |
| 骑马 | — | — | 14天 | 🔴 |

## 关节疼痛追踪（最近2次）
| 部位 | Session 1 NRS | Session 2 NRS | 趋势 | 协议状态 |
|------|--------------|--------------|------|---------|
| 左腕 | 0 (04-17 力量+羽毛球) | 0 (04-19 活动1) | 无痛 | 正常 ✅ |
| 右腕 | 0 (04-17 力量+羽毛球) | 0 (04-19 活动1) | 无痛 | 正常 ✅ |

## 本周覆盖
攀岩 1次 | 骑马 0次 | WLT本周合计: 8/5 ⚠️ 超支 +3（04-15 攀岩 +1, 04-17 H-Push +1）

## Flags
- 04-14 24h 内：攀岩 + pull-heavy + 羽毛球 3 重叠加，CNS 已显债
- 04-15 攀岩 90 min（超建议 45 min × 2），WLT 累积至 7/5 超支 +2；明日 Cycle_04-16 强制 deload
- 04-17 RPE 校准注: 95lbs×10×6 末 2 组不稳, 真 RPE ≥8, 下次 rest 跑满 3 min 或末组 backoff 80-85 lbs; WLT 累积 8/5 超支 +3, 明日 04-18 强制 deload
- 04-19 活动1（性爱 session）已完成（19:30 EDT 报告）；happy 4，腕部 NRS 0/0；时长 TBD；活动2（高强度有氧）待执行；WLT 待活动2完成后更新

## Cycle_04-15 实际记录
actual_activity_2026-04-15: "攀岩（Velocity Climbing），90 min，sRPE 5.5，AU 495，WLT 1"
readiness_gate_2026-04-15: "恢复信号（WLT 6/5 超支；睡眠 ×0.90；摄入偏低）"
outcome_note: "实际时长超建议 2×（90 min vs 45 min 建议）；detraining return 第 2 次"

## Cycle_04-17 实际记录
actual_activity_2026-04-17: "力量 UM (卧推 95lbs×10×6 + 推肩 25lbs×10×3) 22min sRPE 5 AU 110 + 羽毛球 UM 60min sRPE 4 AU 240; 日总 AU 350"
readiness_gate_2026-04-17: "恢复信号 (WLT 7/5 超支 +2, 睡眠 fragmented ×0.90, 摄入偏低)"
outcome_note: "H-Push 首次开启 focus (0→6 sets); 末 2 组真 RPE ≥8 → 下次组间需跑满 3 min; 羽毛球低强度不占 AU cap; WLT 本周累至 8/5 超支 +3; 烤肉 qualitative 入 daily-log, 蛋白估达标 ~200g, Na/kcal/fat/carb 均爆"

## Cycle_04-19 实际记录（进行中）
actual_activity_2026-04-19_act1: "性爱 session (高强度有氧) | 状态: completed | happy 4 | 腕NRS 0/0 | 时长 TBD | AU TBD | WLT TBD | 主观: '做爱是让人快乐的运动'"
actual_activity_2026-04-19_act2: "独立高强度有氧 | 状态: planned (未执行) | 待补报全字段"
readiness_gate_2026-04-19: "恢复信号 (WLT 8/5 超支 +3, 睡眠 fragmented ×0.90, LLS ~1-2)"
wrist_nrs_latest: "左 0 / 右 0（04-19 活动1，确认无痛）; 腕部拉伤前置风险解除"

## Sleep Cycle (authoritative day boundary)
# 规则：任何"今天/昨天"聚合前必须读本节。日历日期仅 fallback。
current_sleep_day_start: 2026-04-19 11:30 EDT
current_sleep_day_label: 2026-04-19-cycle (started 11:30)
last_wake_time: 2026-04-19 11:30 EDT
last_sleep_time: 2026-04-19 04:00 EDT
last_7d_wake_times: [2026-04-19 11:30, 2026-04-18 11:57, 2026-04-14 14:30, 2026-04-13 19:00, 2026-04-12 19:00, 2026-04-11 19:30, 2026-04-10 19:30]
last_7d_sleep_times: [2026-04-19 04:00, 2026-04-17 01:30, 2026-04-14 03:30 (fragmented), 2026-04-13 14:30, 2026-04-12 14:30, 2026-04-11 12:00, 2026-04-10 12:00]

### sleep_cycle_history (backfilled 2026-04-14 from session records + Vincent confirmation)

| cycle_id | wake (Miami) | sleep (Miami) | duration awake | training | notes |
|---|---|---|---|---|---|
| 04-09 | 2026-04-09 19:30 | 2026-04-10 12:00 | ~16.5h | 背+肩? (时间未定) | Vincent earlier stayed up all-nighter ending 04-09 13:00 sleep |
| 04-10 | 2026-04-10 19:30 | 2026-04-11 12:00 | ~16.5h | 胸+肩+核心 @ 04-11 03:37 | 计划 02:00 睡，实际 06:30 + 12:00 再完成 |
| 04-11 | 2026-04-11 19:30 | 2026-04-12 10:00 | ~14.5h | DL 硬拉 @ 04-12 04:30 | 计划 06:xx 睡，与凌儿聊天延至 10:00 |
| 04-12 | 2026-04-12 19:00 | 2026-04-13 14:30 | **~19.5h** | **无 — OFF cycle** | Vincent 自称"大夜"，一直醒 19.5h，唯一的休息日 |
| 04-13 | 2026-04-13 19:00 | 2026-04-14 03:30 | ~8.5h | 攀岩 Velocity ~20:00 1h + 聚餐 | 短 cycle，午睡恢复后再战 |
| 04-14 (current) | 2026-04-14 14:30 (碎片: 03:30 主眠 → 07:xx 电话 → 10:xx 回睡 → 14:30 final) | TBD | TBD | 背日 19:55-20:30 + 羽毛球 20:30-23:00 | sleep_regularity 0.90 |
| 04-17 | 2026-04-17 ~morning (wake 未精确记录) | 2026-04-17 01:30 | ~18h awake | 力量 UM 22min + 羽毛球 60min | 入睡后 10h27m 无觉醒，未戴眼罩，质量极佳 |
| 04-18 | 2026-04-18 11:57 | 2026-04-19 04:00 | ~16h | 无（deload） | deload cycle (WLT 8/5 超支 +3 + CNS 恢复)；睡眠 7.5h fragmented，0930 觉醒 |
| 04-19 (current) | 2026-04-19 11:30 | TBD | TBD | 计划：性爱 session（高强度有氧）+ 独立高强度有氧 | 恢复信号日；WLT 8/5 超支未回落；入库延迟（报告15:40 → 记录19:27 EDT）|

**规则确认（2026-04-14 23:55 Vincent 澄清）**:
- 天 = 确定醒来 → 确定睡着
- 午睡（罕见）不切断一天
- 14:30-19:00 on 04-13 的 4.5h 睡眠算 **终止 Cycle_04-12 的正式睡眠**，不是 nap（Vincent 起床后吃饭去攀岩 = 新 cycle 开始）

**核心发现**: Vincent 的"take 了至少一天 off"指的是 Cycle_04-12（04-12 晚至 04-13 下午 14:30 这 19.5h 清醒窗口无训练）。攀岩 (Cycle_04-13) 和 背日 (Cycle_04-14) 是 back-to-back 连续 cycle，中间隔 11h 睡眠（03:30→14:30），实际训练间隔约 20h 不是 30h。
