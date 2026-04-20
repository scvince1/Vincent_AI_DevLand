---
id: baseos-plan
title: BaseOS — Universal AI OS Template
tags: [project, baseos, architecture, open-source]
status: confirmed
last_modified: 2026-04-17
goal: Test deploy v0.1 in empty folder; iterate toward open-source release
summary: Universal AI OS template (KB-first, token frugal, model routing); Joyce is first external user
---

# BaseOS — Universal AI OS Template

**Goal:** Test deploy v0.1 in empty folder; iterate toward open-source release.

## Why

MeowOS, Horsys, NovelOS are all hand-built variants of the same architecture. BaseOS extracts the reusable pattern into a deployable template. First external user is Joyce; target is open-source GitHub release. The build process is the product — learning through construction.

## Current State

Design Spec v4 + Setup Wizard v0.5 written. Ready for first test deploy in empty folder. Not yet deployed.

Reusable template that can spawn systems like MeowOS, Horsys, NovelOS. First external user: Joyce (executive, solid code background). Target: open source on GitHub.

## Design Principles

- Knowledge Base first, Agents/Skills second
- Token frugality: Python for mechanical ops, shell-runner for all I/O
- Correctness over speed: staging → approval → self-check → Python commit → audit log
- Model routing: Opus (complex reasoning) / Sonnet (standard) / Haiku (mechanical I/O)
- Single orchestrator + dispatch skill routing
- External data sources: on-demand read only, never write to external paths
- archive-core skill = single source of truth for all KB writes
- Memory temperature: Hot (CLAUDE.md) → Warm (KB via index) → Cold (archives)
- 5-layer search funnel: folder → index → title → frontmatter → full content

## Joyce as Design Constraint

Joyce's limitations are design requirements, not obstacles. Her gap is non-use, not incapacity (solid code background). BaseOS must work for an exec user without assuming prompt-engineering habit.

## Current Goal

Deploy v0.1 wizard in an empty folder and validate end-to-end. Iterate into mature spec. Gradually upgrade existing systems (MeowOS → Horsys → NovelOS).

## Active Threads

- [ ] Test deploy in empty folder (Design Spec v4 → 99_MyFiles/BaseOS_Design_Spec_v4.md; Setup Wizard v0.5 → 99_MyFiles/BaseOS_Setup_Wizard_v0.5.md)

## Pending / Open Questions

- Post-test iteration roadmap pending first test deploy results
- Joyce onboarding timing TBD

## Blockers

None confirmed.

## Deployment Roadmap

1. Vincent tests on new project
2. Iterate into mature spec
3. Upgrade existing systems
4. Open source on GitHub
5. Joyce onboards as first external user

## External Reference

| File | Path |
|---|---|
| Design Spec v4 | `D:\Ai_Project\MeowOS\99_MyFiles\BaseOS_Design_Spec_v4.md` |
| Setup Wizard v0.5 (active) | `D:\Ai_Project\MeowOS\99_MyFiles\BaseOS_Setup_Wizard_v0.5.md` |

## Next Check-in Cue

When Vincent mentions "BaseOS deploy", "wizard test", or "test the OS in a folder".

## 设计参数更新 (从 staging 归档 2026-04-17)

### 2026-04-11 ACE 机制的 load-bearing 地位（设计原则）
- 知识库的"镜面/mirror"功能是 MeowOS 和未来 BaseOS 的**核心价值之一**，不是生产力工具的副产品
- 自我增强机制在任何性能/token 优化权衡中都应被当作 **load-bearing 特性**，不可轻易裁剪
- **ACE 用户侧前置条件候选原则：** 用户的真诚/脆弱是系统镜面质量的前提条件（详见 [intellectual-motifs.md § 作为洞察的幸福](../81_Identity/intellectual-motifs.md)）

### 2026-04-12 吞药片体验 → BaseOS 设计点
- Vincent 觉得每天吞一大把药片是不开心体验，但能坚持
- Joyce 很难坚持吞药片
- **supplement compliance 摩擦降低** 是 BaseOS 或给 Joyce 的系统的设计点

### 2026-04-09 Joyce 系统需求（BaseOS 设计来源）
- 企业高管，使用公司 PC，不能下载软件，但可运行 Claude Code 生成的脚本
- 有 VS Code + Python，企业 Microsoft 计划（Graph API 可用于 Outlook/Teams/Calendar）
- 所有工作输出须为英语（半母语，11-13 岁来美）
- **根因：** 每天把所有工作放进一个 massive session，context 爆炸
- 习惯：忙时忘记拆 session，把一整天工作堆在一起
- 目标愿景：AI 处理 email、calendar、Teams、会议、演示文稿、项目管理
- 现有知识文件：一个 20k+ token 的单体 .md + 几个小 .md（个人信息、公司信息、关系笔记、工作偏好）

---

## Session Index

- 2026-04-09 — v0.1 wizard drafted, 3 audit rounds completed. Ready for test deploy.
- 2026-04-11 — ACE load-bearing 地位确认（设计原则不可裁剪）
- 2026-04-12 — supplement compliance 摩擦降低作为 Joyce 系统设计点
- 2026-04-17 — 设计参数从 staging 归档整合

## Pointers

- Memory: project_baseos, feedback_joyce_design_constraint, feedback_joyce_attribution_invisible, user_joyce_role_current
- Workspace: 99_MyFiles/ (BaseOS_Design_Spec_v4.md, BaseOS_Setup_Wizard_v0.5.md [active; v0.4 superseded])
- Related: 82_Projects/horsys-tracker.md, 82_Projects/novelos-tracker.md (downstream systems for eventual BaseOS upgrade)

## 从 memory 迁入（2026-04-17 — 定位与约束备注）

See `80_Knowledge/82_Projects/baseos-plan.md` for current state, active threads, session index, blockers.

**Why live elsewhere:** 82_Projects is the canonical per-project live README registry (established 2026-04-17). This memory entry exists as index pointer only; it will not be deep-maintained here going forward.

**Topic summary (for index relevance):** BaseOS high-centralization user-facing office system; NOT "AI OS template"; Joyce as design constraint; prior "Universal AI OS" framing superseded 2026-04-16; positioning: Personal Office Steward (proposed, not confirmed).

## 从 memory 迁入（2026-04-17 — Joyce PTA 交付方向）

- Current priority: build a Tech Demo featuring an Agentic AI workflow.
- Secondary: build Joyce's Personal AI System via BaseOS template (v0.1 wizard drafted 2026-04-09, ready for test deploy).
- Why: Demonstrating agentic solutions is the primary deliverable right now.
- How to apply: Any AI work for Joyce should default to agentic/workflow-oriented design.

## 从 memory 迁入（2026-04-17 — 关键文件路径与部署计划）

BaseOS is Vincent's in-progress product vision for a high-centralization, user-facing office system. Positioning corrected 2026-04-16; see project_baseos.md for positioning notes.

**Key files:**
- Design Spec: D:\Ai_Project\MeowOS\99_MyFiles\BaseOS_Design_Spec_v1.md
- Setup Wizard v0.1: D:\Ai_Project\MeowOS\99_MyFiles\BaseOS_Setup_Wizard_v0.1.md

**Status (2026-04-16):** positioning being reworked from "Universal AI OS Template" toward office-assistant framing. Architecture internals may still apply; product-level narrative needs revision. v0.1 wizard was 3-round audited under prior framing.

**Planned deployment path (from earlier):**
1. Vincent tests on a new project folder
2. Iterate into mature spec
3. Gradually upgrade existing systems (MeowOS, Horsys, NovelOS)
4. Open source on GitHub
5. Joyce = first external user
