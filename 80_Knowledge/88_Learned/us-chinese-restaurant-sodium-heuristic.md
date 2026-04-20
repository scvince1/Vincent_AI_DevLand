---
id: us-chinese-restaurant-sodium-heuristic
title: "Us Chinese Restaurant Sodium Heuristic"
topic: 美国中餐馆 Na/MSG 估算启发式
source: Vincent 实测校准 2026-04-13 + KB 既有 +20% 规则局限
scope: 营养估算修正
status: confirmed
last_modified: 2026-04-15
---

# 美国中餐馆 Na/MSG 估算规则

## 核心校准

**原 KB 规则（[targets.md](D:\Ai_Project\MeowOS\80_Knowledge\84_Fitness\nutrition\targets.md)）：** 外卖/中餐 estimate 后 +20%。

**修正：** 该规则对**美国中餐馆**的 Na 严重低估。应使用如下分层：

| 场景 | Na 乘数 vs 家烹 | 典型单餐 Na |
|---|---|---|
| 家烹中餐（控盐） | 1× | 300-500 mg |
| 家烹中餐（重口） | 2× | 600-1000 mg |
| 中国本土普通餐馆 | 3-4× | 1200-1800 mg |
| **美国中餐馆 MSG-heavy** | **5-7×** | **2000-2500 mg / 顿** |
| 快餐连锁（Panda Express 等） | 6-8× | 2200-2800 mg |

## 为什么 US 中餐馆 Na 特别高

1. **MSG 标准用量**：1-2 tsp/菜，每 tsp MSG ≈ 5g → 含 Na ~600 mg
2. **酱料 heavy**：酱油+蚝油+豆瓣酱叠加，单菜 800-1200 mg Na 常见
3. **口味适应**：为适应美国消费者口感，盐和鲜味剂普遍过量
4. **连锁化效应**：中央厨房酱包预制，盐浓度难以调控

## 实用启发式（估算时）

**单菜 Na 底盘：**
- 素菜炒（如青椒土豆丝）：400-600 mg
- 荤素搭配（如青椒肉丝）：900-1300 mg
- 铁板/干烧/红烧海鲜：1000-1500 mg
- 深炸菜品调味：300-500 mg

**每多一道菜 → 单菜 Na 再叠加**（不要用均摊，盐是累积的）

**一整桌 4 人分享 4-5 道菜：总 Na 约 5000-7000 mg，单人 1200-1800 mg**

## 与 Vincent 健康目标的交互

- Na 日 UL：2300 mg（US Dietary Guidelines）
- Vincent 主动控 Na 中（[MEMORY feedback_nutrition_sodium.md]）
- **一顿美国中餐 = 日 UL 封顶**（甚至单餐超标）
- 跟进 48h 须主动低 Na 以均衡

## 规则触发

agent 识别到 Vincent 报告"美国中餐/Chinese restaurant/中餐馆 + 地点在美国"时：
1. 放弃 +20% 校正公式
2. 直接假设 Na = 日 UL × （0.8 ~ 1.2）
3. 标记 Na:K 临近或突破 1.0 风险
4. 自动触发后续 24-48h 低 Na 提示

## 数据来源

- Vincent 实测反馈 2026-04-13（4 道菜聚餐，单人 Na ~2300 mg 体感）
- CSPI（Center for Science in the Public Interest）历史报告：中餐馆单餐 Na 普遍 1500-3500 mg
- FDA MSG 科学摘要：MSG ~12% Na w/w
- KB 既有 [nutrition-for-hypertrophy-climber-recomp.md](D:\Ai_Project\MeowOS\80_Knowledge\88_Learned\nutrition-for-hypertrophy-climber-recomp.md) takeout heuristic
