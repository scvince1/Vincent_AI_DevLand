---
id: index-pipeline-readme
title: Index Pipeline — Auto-Parse + Validation
tags: [meta, index, pipeline, automation]
status: active
last_modified: 2026-04-21
---

# Index Pipeline

Python 脚本 pipeline 扫描 `80_Knowledge/` 全库，产出三张 Index 的 diff 报告。**不直接写入 Index**——只产 report，由 Vincent 或 knowledge-agent 审批后应用。

## 脚本

- `scan_kb.py` — 扫描全库，提取所有 frontmatter，按路由规则分类
- `diff_indexes.py` — 对比现有 Index vs 扫描结果，输出 diff（missing/stale/schema-violation）

## 使用

```bash
cd D:\Ai_Project\MeowOS\80_Knowledge\85_System\index_pipeline
python scan_kb.py > scan_report.json
python diff_indexes.py scan_report.json > diff_report.md
```

## 检测能力

`diff_indexes.py` 产出的报告包含:

1. **Missing / Stale / No-ID / Incomplete** 条目（三张 Index 对比）
2. **Files with no frontmatter** (应补 frontmatter 的文件)
3. **Unrouted files** (不在路由表的文件)
4. **88_Research Own Registry** diff（concept 目录 vs _registry.md 声明）
5. **ID Uniqueness Check**（跨文件 id 碰撞检测）
6. **Ghost Reference Detection**（frontmatter `related:` 字段指向不存在的目标）

所有检测**只读不改**，输出 markdown diff report 供审阅。

## 路由规则（与 knowledge-agent.md 保持一致）

| 路径前缀 | Index |
|---|---|
| 81_Identity/ · 82_Projects/ · 87_People/ · 88_Plants/knowledge/ | Entity_Index |
| 82_Health/ · 84_AI_Tech/ · 84_Fitness/ · 85_System/harness_engineering/ · 88_Learned/ · 88_Research/ · 89_Business/ | Knowledge_Index |
| 83_Observations/ · 85_System/（非 harness）· 85_System/dreamwalk/ · 86_AI_Systems/ · 90_Deprecated/ | Meta_Index |

## 运行时机

- 手动: Vincent 怀疑 Index 有漂移时跑一次
- 系统诊断 session 固定跑一次
- 未来可加 Cron（每周一次）

## 输出

- `scan_report.json`: 所有文件的 frontmatter 数据 + 目标 Index
- `diff_report.md`: 人类可读的 missing/stale/violation 清单
