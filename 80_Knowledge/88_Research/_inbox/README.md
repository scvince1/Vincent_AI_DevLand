---
id: 88-research-inbox-readme
title: 88_Research/_inbox/ — Subagent Research Staging Area
tags: [meta, research, inbox, staging]
status: active
last_modified: 2026-04-21
---

# 88_Research/_inbox/

Subagent research 的**临时归档区**。Research subagent 做完 synthesis 统一写到这里，之后由 knowledge-agent 的 `inbox_archive` 模式归档到正式位置 + 登 Index。

## 写入要求

Research subagent 写入时必须:

1. **路径**: `88_Research/_inbox/<concept>/<filename>.md`（concept 用 kebab-case）
2. **Frontmatter**（必备字段）:

```yaml
---
id: <kebab-case-id>
title: <原标题>
tags: [synthesis, research, <其他 topic 标签>]
status: active
last_modified: <YYYY-MM-DD>
concept: <concept 名>
type: synthesis
generated_by: <subagent 名字 / main-session>
scope: <一句话说这文档干嘛的>
---
```

3. **正文**: markdown

## 归档流程

1. Subagent 写入 `_inbox/<concept>/<file>.md`
2. 主 session 派 knowledge-agent 做 `inbox_archive` 模式
3. knowledge-agent 迁移文件到 `88_Research/<concept>/<file>.md`
4. 登记 Knowledge_Index + 更新 `88_Research/_registry.md`

## 架构位置

- shell-runner scope guard 对 `88_Research/_inbox/**` 放行（见 `C:\Users\scvin\.claude\agents\shell-runner.md`）
- 路由说明见 `90_Agents/knowledge-agent.md` 的 "Research Subagent 入库通道" 特殊规则段
- 总规则见 `CLAUDE.md` 的 "Subagent Research 归档通道" 段
