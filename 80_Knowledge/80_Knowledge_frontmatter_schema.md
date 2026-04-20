---
id: frontmatter-schema
title: 80_Knowledge Frontmatter Schema Reference
tags: [schema, reference, meta]
status: confirmed
last_modified: 2026-04-15
---

# 80_Knowledge Frontmatter Schema Reference

_Enforced by knowledge-agent on every write. Do not bypass._

## Core Fields (all entries)

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | kebab-case, unique within folder |
| `title` | string | yes | Human-readable name |
| `tags` | list | yes | At least one tag |
| `status` | string | yes | `draft` / `confirmed` / `deprecated` |
| `last_modified` | date | yes | `YYYY-MM-DD` |

## Optional Fields (all entries)

| Field | Type | Notes |
|---|---|---|
| `summary` | string | One-sentence description |
| `source` | string | URL or citation |
| `related` | list | Relative paths or IDs of related files |

## Type-Specific Fields

### learned (88_Learned/)
```yaml
concept: [概念或发现名称]
author: [原作者]
source_title: [书/文章/报告标题]
source_date: [原始发表年份]
logged: [YYYY-MM-DD]
```

### people (87_People/)
```yaml
name: [全名]
relation: [与 Vincent 的关系]
context: [认识场景/相关背景]
logged: [YYYY-MM-DD]
```

### project (82_Projects/)
```yaml
status: active | paused | completed | archived
```

### observation / staging (83_Observations/)
```yaml
logged: [YYYY-MM-DD]
session: [session 标识，可选]
```
