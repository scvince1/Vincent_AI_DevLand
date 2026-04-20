---
id: fitness-nutrition
title: Fitness + Nutrition Agent System
status: active
tags: [fitness, nutrition, health, agents, sodium, potassium]
created: 2026-04-09
last_modified: 2026-04-17
---

# Fitness + Nutrition Agent System

**Goal:** 健康管理 agent 系统 — fitness tracking, nutrition logging, and sodium/potassium monitoring via dedicated AI agents.

## Why

Vincent is actively reducing sodium intake and tracking potassium balance. Fitness and nutrition data enter the system via daily conversation; agents handle logging, KB maintenance, and anomaly flagging. Tracking burden cap reached: no independent log/journal outside daily dialogue.

## Current State

System deployed 2026-04-09 at v2.1 spec level. Two agents implemented and ready for use: fitness-coach and nutrition-tracker. 18 KB files covering movement patterns, muscle fiber types, rest intervals, nutrition references, targets, supplements, and logs. Daily log and weekly volume tracking in place.

## Active Threads

- fitness-coach agent (→ `90_Agents/fitness-coach.md`)
- nutrition-tracker agent (→ `90_Agents/nutrition-tracker.md`)
- KB maintenance: `80_Knowledge/84_Fitness/` (11 files) + `80_Knowledge/84_Fitness/nutrition/` (7 files)

## Pending / Open Questions

- Exercise reminder: flag to Vincent if 3+ consecutive days without working out
- Sodium/potassium live verification required before reporting branded food data (Subway, USDA, etc.)

## Blockers

## Next Check-in Cue

When Vincent mentions food, workout, sodium, body weight, or any nutrition/fitness event. Route to agent — do not process in main session.

## Session Index

- 2026-04-09 — Spec v2.1 finalized; 18 KB files written; 2 agents implemented

## Pointers

- Memory: project_fitness_system, feedback_nutrition_sodium, feedback_nutrition_verify_live, feedback_exercise_reminder, feedback_use_meowos_agents_directly
- Fitness agent: 90_Agents/fitness-coach.md
- Nutrition agent: 90_Agents/nutrition-tracker.md
- Fitness KB root: 80_Knowledge/84_Fitness/
- Fitness KB files: _rules.md, _state.md, constraints.md, log.md, movement-patterns.md, muscle-fiber-types.md, rest-intervals.md, weekly-volume.md
- Nutrition KB: 80_Knowledge/84_Fitness/nutrition/ (avocado_reference.md, caffeine_reference.md, daily-log.md, hydration_reference.md, subway_reference.md, supplements.md, supplements_reference.md, targets.md)
- Related: 82_Projects/life_quality.md (fitness/nutrition as future life quality threads)

## 从 memory 迁入（2026-04-17 — 实施状态快照）

See `80_Knowledge/82_Projects/fitness-nutrition.md` for current state, active threads, session index, blockers.

**Why live elsewhere:** 82_Projects is the canonical per-project live README registry (established 2026-04-17). This memory entry exists as index pointer only; it will not be deep-maintained here going forward.

**Topic summary (for index relevance):** Fitness + nutrition agent system; spec v2.1 + 18 knowledge files + 2 agents (fitness-coach, nutrition-tracker) implemented 2026-04-09; ready for use, calibration period needed.
