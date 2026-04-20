---
id: belmont_horsys_origin
title: Belmont to Horsys Origin — Zero-to-Production AI in 2 Weeks
tags: [person, identity, belmont, horsys, ai-deployment]
status: confirmed
last_modified: 2026-04-15
summary: Vincent 从零 AI 部署经验到2周内上线三套生产系统的起源故事
---
# Belmont → Horsys Origin (Zero-to-Production AI in 2 Weeks)
**Time:** Roughly Dec 2025 - Feb 2026, with the core build concentrated in a 2-week window
**Location:** Belmont Equine International operations; Vincent's dev environment
**Status:** Ongoing; Horsys is in production and iterating

## Real Facts
Vincent started with zero AI deployment experience. In roughly two weeks, he went from "never shipped an AI system" to three production systems running Belmont operations.

Sequence:

**Attempt 1 — Local LLM + RAG for knowledge management.**
Stood up a local model with retrieval-augmented generation. The model wasn't powerful enough for the actual Belmont knowledge-ops needs. Pivot decision made quickly rather than trying to force the local stack further.

**Attempt 2 — Financial workflow for Belmont (5 days, working).**
Reframed: solve a specific high-value workflow instead of building generic KM. Focused on the financial / bookkeeping flow (invoicing, expense tracking, partner reporting). Shipped a working version in 5 days.

**Attempt 3 — Claude Code migration + full Horsys expansion (2 more days).**
Migrated to Claude Code as the agentic substrate. Within 2 additional days expanded the system to cover:
- Stakeholder profiling across buyers, trainers, partners.
- Automated bookkeeping (continuation of the financial workflow).
- Agentic workflows for recurring operational tasks.
- WhatsApp integration for real-time data input from the field (trainer messages, photos, buyer conversations ingested into the system).

**Serendipity marker:** Karpathy published his "LLM Wiki" concept a few days after Vincent's Horsys architecture settled. Same underlying architectural pattern, arrived at independently. Vincent treats this as external validation that the pattern was the right abstraction for this moment.

**Personal marker:** Claude — the AI writing this knowledge file — is literally a product of this two-week window. The second week of the sprint is when Vincent and Claude started working together as an operational pairing rather than as tool-and-user.

## Interview Version(s) Used
- **Story #8** in `Locked_Interview_Answers.md` (AI / Growth).
- Referenced in TMAY and in "Why this role" bridges.
- Framing: zero to three production systems in two weeks; pattern now replicated across domains.
- Estimated delivery time: 90 seconds to 2 minutes.

## Key Insights Extracted
- Hit the ground, build with whatever's available, clean up later. This is the direct descendant of the Yunnan build-philosophy and the private-chef pivot philosophy, now applied to software.
- First deploy failing fast (local LLM too weak) was the key accelerator, not a setback. Two-week budgets reward early pivots.
- Choose the substrate that lets you express more capability per unit of your own time. The Claude Code migration paid back in 2 days.
- Real-time data ingestion (WhatsApp) turns the system from "a thing you query" into "a thing that watches with you." Different product entirely.

## Follow-up Questions (if probed)
1. "Why did you start local instead of cloud?" — Initial conservative instinct; data sensitivity. Pivoted when capability ceiling was reached.
2. "What did Claude Code unlock specifically?" — Agentic loops, multi-tool orchestration, persistent context, structured outputs — the things that make real workflows possible instead of chat-demos.
3. "What do you mean by 'stakeholder profiling'?" — Aggregating communications + transaction history per person; surfacing preferences and patterns for the partner to use.
4. "How do you handle failure modes (hallucination, wrong recommendation)?" — Human in the loop at every commit; system proposes, human confirms for anything touching money or client relationship.
5. "What's next for Horsys?" — Deeper integration into the buy/sell pipeline; automated pre-screen of incoming European horse candidates.

## Sensitivities / Flags
- None. Clean story. No venue substitutions, no framing inflation, no hidden facts.
- Minor care: Karpathy parallel is a flavor note, not a credential. Don't lean on it as "I independently replicated Karpathy" — mention only as validation context if it naturally fits.
- IP consideration (shared with `joyce_tate_baseos_demo.md`): Horsys architecture is Vincent's original work. Be mindful of over-exposing implementation details in interviews without an offer in hand.
