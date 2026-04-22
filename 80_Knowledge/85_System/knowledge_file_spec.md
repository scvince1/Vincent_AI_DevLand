---
id: knowledge-file-spec
title: MeowOS 知识文件 Frontmatter 规范
tags: [spec, system, meta]
status: confirmed
last_modified: 2026-04-21
scope: 80_Knowledge 下所有 .md 的 frontmatter 约定
summary: MeowOS 知识文件的 frontmatter 字段定义、status 枚举、Worldbook 注入字段
maintenance: Vincent + 凌喵 共同维护
version: 1.0
---

# MeowOS 知识文件 Frontmatter 规范

## 1. 适用范围

**覆盖**：`D:\Ai_Project\MeowOS\80_Knowledge\**\*.md`

**不覆盖**：
- `C:\Users\scvin\.claude\projects\d--Ai-Project-MeowOS\memory\**`（Claude Code auto-memory，自动管理）
- `_staging.md` / `_inbox/` / `00_Dump/`（暂存档）
- 机器生成 dump（subtitle / wa-sync 等）

**原则**：memory 层的事实若对 Discord bot 有用，凌喵归档时 promote 到 `80_Knowledge/`，不让 bot 直接读 memory。

## 2. 必需 frontmatter 字段

```yaml
---
id: <kebab-case 唯一标识>
title: <人类可读标题>
tags: [<tag1>, <tag2>, ...]
status: draft | confirmed | evolving | deprecated | stale
last_modified: YYYY-MM-DD
---
```

### status 枚举语义

| 值 | 含义 |
|---|---|
| draft | 正在写，事实未 confirm |
| confirmed | 事实 confirmed |
| evolving | 信息还在演化，需定期更新（如 current role） |
| deprecated | 主动废弃，不再维护 |
| stale | 事实过期但未主动废弃，引用前要验证 |

## 3. 常用 optional 字段

- `summary`：一句话档案摘要（50 字内）
- `relationship` / `role` / `scope`：档案类型特定
- `maintenance`：谁维护 / 谁只读

## 4. Worldbook 字段（opt-in）

Worldbook = Discord bot 的 keyword-triggered 注入层。**声明以下字段即入索引**，缺省不索引。

```yaml
worldbook_keys: [<key1>, <key2>, ...]    # 触发关键词数组；缺省 = 不索引
worldbook_summary: |                      # optional；注入 bot 的轻量版
  <200 字以内的核心事实>
worldbook_order: 100                      # optional；默认 100，数字大 = 优先级高
```

`worldbook_summary` 缺省时：Worldbook 注入整档案 content，按 token budget 截断。

### order 约定

| 优先级 | 用例 |
|---|---|
| 200 | 核心人物（Joyce / 凌喵 / Vincent） |
| 100 | 常规档案（朋友 / 项目 / 高频概念） |
| 50 | 低频背景（学术引用 / 历史材料） |

## 5. 完整示例（Joyce 档案）

```yaml
---
id: joyce
title: Joyce / Joyce Ling
tags: [person, partner, triad, owner]
status: confirmed
last_modified: 2026-04-21
relationship: Vincent 伴侣；凌喵的喵喵大人
summary: SharkNinja CoS；凌喵的 owner；triad 顶位
maintenance: Vincent 维护，Joyce 只读
worldbook_keys: [Joyce, Joyce Ling, 喵喵大人, 凌儿]
worldbook_summary: |
  Joyce = Vincent 伴侣 + 凌喵的喵喵大人。
  SharkNinja Chief of Staff（Mark Barrocas），2026-03 入职 ~1.5 月，角色仍演化。
  称谓：Vincent 叫她凌儿；她叫 Vincent 爸爸；凌喵叫她喵喵大人（第二人称）或 Joyce。
  Register = sub + brat-leaning。Triad Hierarchy 顶位（Joyce > Vincent > 凌喵）。
  授权：主动通信 + 深夜睡眠监督（00:30 切睡觉模式 / 02:00 硬按）。
worldbook_order: 200
---
```

## 6. 写档案流程

```
1. 确认档案类型 → 从 85_System/_templates/<type>_template.md 复制
2. 填必需 frontmatter
3. 决定是否声明 worldbook_keys
4. 若声明 keys，默认也写 worldbook_summary
5. 通过 shell-runner Write 到对应目录
```

## 7. 迁移策略

- 已有 `80_Knowledge/**` 档案**按需补 frontmatter**，不强制一次性迁移
- 凌喵下次修改该档案时顺手补齐
- Vincent 明确说"先不补"的档案跳过

## 8. Templates

`85_System/_templates/` 提供三个 template：
- `person_template.md` — 人物档案
- `project_template.md` — 项目档案
- `observation_template.md` — 观察记录

写档案前 copy template，不从零起草。

## 9. 版本历史

- **1.0**（2026-04-21）：首版。定义 5 档 status + Worldbook opt-in 字段。
