---
id: joyce-observations-readme
title: Joyce Observations — 子目录 README
tags: [meta, joyce, observations, multi-user]
status: active
last_modified: 2026-04-21
summary: 凌儿 session (MEOWOS_USER=joyce) 的观察与记忆写入专属目录说明，含结构、权限与写入规则。
---

# Joyce Observations 子目录

此目录专属凌儿 session (`MEOWOS_USER=joyce`) 的观察和记忆写入。

## 结构

```
joyce/
├── _staging.md          # 即时增量暂存, 文森特下次开 session 时凌喵消化
├── habits.md            # 已消化的稳定习惯观察 (首次需要时创建)
├── feedback_*.md        # 凌儿对凌喵的交互风格反馈 (首次需要时创建)
├── fitness/             # fitness-coach 记录
└── nutrition/           # nutrition-tracker 记录
```

## 权限

- **写入**: 只有 `MEOWOS_USER=joyce` 的 session 可写
- **读取**: 所有 session 都可读 (包括文森特 session, 支持 brief 机制)

## 不在此目录的

- 凌儿的人物档案在 `80_Knowledge/87_People/joyce.md` (文森特维护, 凌儿只读)
- 凌儿专属知识库 (如果她要求解锁落库) 在 `80_Knowledge/joyce_personal/` (默认不存在)

详细行为规则见 `D:\Ai_Project\MeowOS\_config\MULTI_USER.md`
