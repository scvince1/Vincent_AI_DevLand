---
id: movement-patterns
title: 动作模式系统 (v2.1)
tags: [fitness, knowledge, movement-patterns, programming]
status: confirmed
last_modified: 2026-04-15
summary: 8个核心动作模式 + Volume Cycling，各模式目标 sets 与场地可用性对照
---
# 动作模式系统 (v2.1)
_最后更新: 2026-04-09_

---

## 1. 核心模式 (8) + Volume Cycling

| Pattern | 代号 | 目标对齐 | Focus sets | Maintenance sets |
|---------|------|----------|------------|------------------|
| Horizontal Push | H-Push | 上肢增肌（胸） | 12-18 | 6-8 |
| Horizontal Pull | H-Pull | 上肢增肌 + 攀岩平衡 | 12-14 | 6-8 |
| Vertical Push | V-Push | 上肢增肌（肩） | 8-10 | 4-6 |
| Vertical Pull | V-Pull | 攀岩专项 | 10-14 | 5-7 |
| Hip Hinge | Hinge | 负重目标 + 骑马髋部 | 10-14 | 5-7 |
| Knee Dominant | Knee | 单腿蹲起 + 骑马 | 10-14 | 5-7 |
| Loaded Carry | Carry | 负重目标（最直接） | 6-8 | 3-4 |
| Rotation/Anti-rotation | Rot | 骑马躯干稳定 + 攀岩 | 4-6 | 2-3 |

**Volume Cycling：** 同一时间只有 2-3 个 focus patterns 拿满容量，其余 maintenance。`_state.md` 中声明 `focus_patterns`，每 mesocycle 更新。

**容错设计：**
- 每次 session = focus + maintenance 的自足单元
- 不存在"欠债"机制 -- 跳过的天数不补
- Session 时间上限 60-75 分钟（含热身）
- Focus patterns 优先分配组数

---

## 2. 动作对应表（按场地）

| Pattern | 阳台 | 攀岩馆 | Full Gym | University |
|---------|------|--------|----------|------------|
| H-Push | 哑铃俯卧撑(中立腕!)、沙袋地板卧推 | 杠铃片地板卧推、俯卧撑变体 | DB/杠铃卧推 | 器械推胸、绳索飞鸟、卧推 |
| H-Pull | 弹力带划船、沙袋弯划 | DB划船、弹力带 | 绳索划船、DB划船 | 坐姿划船器、胸支撑划船 |
| V-Push | 棒铃推举、DB站姿推举 | DB肩推 | 杠铃OHP | 肩推器械、地雷管推举 |
| V-Pull | 引体向上杆、弹力带下拉 | 引体向上区(加重) | 高位下拉、引体 | 所有下拉/引体变体 |
| Hinge | 沙袋RDL、沙袋good morning | 杠铃片RDL、弹力带 | 杠铃RDL/硬拉 | Hex bar DL、GHD |
| Knee | 沙袋goblet squat、pistol进阶 | Box pistol squat、plate goblet | 杠铃深蹲、BSS | 腿举、hack squat |
| Carry | 沙袋熊抱行走(45kg) | 杠铃片/DB farmer carry | DB/杠铃carry | Trap bar carry、sled push |
| Rot | 棒铃360/10-to-2、弹力带旋转 | 弹力带Pallof、plate chop | 绳索woodchop | 所有绳索/器械选项 |

---

## 3. 负荷-努力矩阵（RPE/RIR）

| 相对负荷 (% 1RM) | RIR 目标 | 增肌有效性 | Vincent 的例子 |
|-------------------|----------|------------|----------------|
| ≥60% | 2-3 (RPE 7-8) | 充分 | 沙袋、俯卧撑(91kg)、杠铃compound |
| 30-60% | 1-2 (RPE 8-9) | 充分 | 较轻DB做compound |
| <30% | 0-1 (RPE 9-10) | 仅力竭时有效 | 12lb DB(侧平举等适配动作) |

**隔离 vs 复合力竭：** 复合动作保持 RIR 2-3；隔离/机械动作最后1-2组允许技术力竭。肩膀隔离是主要力竭场景。

**家庭RPE容差：** 阳台/沙袋 RPE 估计不如器械精确。前4周 RPE 7-8 目标接受 6-9 范围。UM/Full Gym 器械训练可作 RPE 校准锚点。

---

## 4. RPE 校准协议（前2-4周）

- 使用 RPE 范围(7-8)，不用点目标
- RIR 上限 ≤ 3（>4时准确度崩溃）
- 偶尔安排"验证组"——预测RIR后继续到力竭
- 连续多次 RPE 报 6-7 → agent 提醒"是不是可以加重了?"

---

## 5. 渐进超负荷追踪

- RPE 是跨场地通用货币
- Log 格式：`pattern | exercise | load | reps × sets | RPE | location | side | wrist_load_tag`
- 同一模式、同一 RPE 目标，跨周增加 volume 或 load
- 沙袋(固定45kg)渐进方式：volume → density → tempo → distance → complexity → grip difficulty → unilateral
