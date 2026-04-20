---
type: knowledge
domain: ai-strategy
created: 2026-04-07
tags: [ai-deployment, organizational, cognitive-infrastructure, multi-agent, enterprise]
---

# 组织认知基础设施 (Organizational Cognitive Infrastructure)

Strategic framework for deploying multi-agent AI at organizational scale. Source: COO Office strategic sessions, 2026.

## Core Problem: The Organizational Epistemic Problem

Three alignment failures that consume ~30% of senior leadership time:

| Alignment Type | English | Description |
|---|---|---|
| 信息对齐 | Aligning Information | Who knows what; where information lives |
| 进度对齐 | Aligning Progress | How many initiatives in flight; who's accountable; current status |
| 粒度对齐 | Aligning Ignorance | Who doesn't know what; identifying invisible cognitive gaps between decision-makers |

Root cause: organizations lack a **Shared Epistemic Ground** — the foundational layer where decision-makers can at least see where disagreements exist and who holds what information.

The problem isn't meeting frequency. It's that every alignment session rebuilds context from zero, so effort is non-cumulative.

## OCI Definition

> A continuously running system that enables every decision-maker in an organization to make decisions with as complete a context as possible at the moment of decision. It does not make decisions for people; it does not send messages for people. Its output is information quality, not specific documents or workflows.

## Five-Layer Architecture

| Layer | Role | Trigger |
|---|---|---|
| L0 Personal Sovereignty | Each person's private Personal Vault + Personal Shell. Absolutely isolated. Never enters any organizational database. | User-initiated |
| L1 Perception | Continuous listening/structured extraction from email, reports, files, meetings | Real-time + event |
| L2 Memory & Understanding | Initiative Registry, Organizational Knowledge Graph, Decision Log maintenance | On information inflow |
| L3 Cross-functional | Meeting prep, report drafting, finance, cross-region bridge reports, cross-initiative synthesis | Event-triggered |
| L4 Governance & Healing | Permissions matrix, trigger routing, audit trails, escalation protocols | Always-on backend |

**Key design principle:** All agents only prepare and surface findings. Never make decisions for humans. Never send messages. Any output remains a draft until human confirmation.

## Seven Interaction Modes

| # | Mode | Description |
|---|---|---|
| ① | Ambient | Agents run in background; results appear automatically in work surfaces. AI presence is invisible. |
| ② | Review & Approve | Agent prepares everything, presents to human, waits for confirmation, then executes. Nothing happens without confirmation. |
| ③ | Exception Surfacing | Silent during normal operations; surfaces anomalies proactively (budget overrun, overdue reports, unread emails from direct reports). |
| ④ | Document Co-presence | Opens a project document; Agent's context includes full document plus all related historical information. |
| ⑤ | Structured Intake | Agent proactively asks a structured set of questions; human answers; Agent processes. Eliminates blank-document problem. |
| ⑥ | Delegation | Human gives task description; Agent completes multi-step workflow in background; presents result. |
| ⑦ | Watch / Subscription | Continuous thematic filter: whenever a topic, person, or project code appears in any new incoming information, results are pushed as summary. |

## Judgment Standard Sources

Three sources for AI judgment calibration:

1. **Model training knowledge** — pattern recognition, wide coverage, no preset rules needed. Weakness: may not be accurate for your specific organizational context.
2. **Explicitly defined hard rules** — numeric thresholds, clear escalation conditions. Precisely executable. Must be articulated clearly by humans.
3. **Organization's own historical data** — as system runs longer, accumulated history becomes primary calibration source. More accurate than generic model knowledge.

**Polanyi's Warning applied here:** Humans know more than they can articulate. You cannot ask users to pre-define all judgment criteria. Better approach: let system surface candidate judgments → user responds to specific cases ("correct / incorrect / because X") → system calibrates. This is why Review & Approve Mode is the most important interaction pattern.

## Knowledge Base Growth Mechanism

The model is stateless. But the context fed to the model can continuously compound.

```
User interaction
  → Interaction data enters raw log
  → Extraction trigger (real-time or batch)
  → Structured info enters knowledge base
  → Next call: retrieve relevant history
  → Inject into prompt context
  → Model generates with richer context
  → Loop
```

No design = no growth. The learning cycle must be deliberately engineered.

## Deployment Phases

### Phase 0 (Weeks 1–12): Build Data Capture Foundation

Goal: not insights. Goal is stable, structured data flowing into the system.

**Initiative Registry Cold Start:**
- Weeks 1–2: Agent scans 3 months of email; extracts project names, people groups, meeting patterns. No manual forms.
- Weeks 3–4: Sends minimal confirmation requests to inferred owners ("confirm or correct this one-line summary")
- Weeks 5–8: Registry goes live; status color system (green/yellow/red by recency)

Key byproduct: reveals "zombie projects" — budget still running, activity has stopped.

**Success Metrics:**
- Registry contains ≥30 confirmed active projects
- Meeting perception processes ≥80% of calendar events daily
- Finance file workflow running weekly without manual intervention
- Can answer "how many red-status projects right now?" in 10 seconds

### Phase 1 (Months 3–9): Deepen Personal Layer, Build Champion Network

Goal: not coverage. Goal is depth — core users (20 Power Users + C-Suite) genuinely using daily.

**Champion Network Building:** Never through training courses. Through authentic personal experiences that naturally spread.
Correct sequence: COO Office deep use (2–4 weeks) → natural discussion in direct reports → when 3+ people proactively ask "how do I get this?" → network has formed.

**Key output:** Not specific agents — an internal standard for "what good AI-assisted work looks like," built from real use and transmitted as culture.

### Phase 2 (Months 9–18): Organizational Layer Begins Working

Prerequisites: 6+ months of structured data; 50+ confirmed initiatives in registry; mature senior Personal Shells; 30–50 complete Decision Log entries.

**Milestone signals:**
1. Someone says "If the system hadn't told me, I would never have known about this"
2. Someone cites Decision Log: "We decided it this way last time because..."

## KPI Framework (Passive Measurement)

All metrics derived from data the system already processes. No additional reporting burden.

| KPI | Definition | Target |
|---|---|---|
| Information Latency | Time from event to all relevant people knowing | Track relative trend downward |
| Epistemic Alignment Failure Rate | Meeting/decision interruptions due to missing context | Background briefing time ↓ 20% within 12 months |
| Decision Capture Rate | % of identified decision signals confirmed into Decision Log | 60% at 6 months → 80% at 12 months |
| Registry Freshness | % of registry items updated within 2 weeks | Green ≥70%, Red ≤10% |

Do NOT track: agent count, user logins, per-task efficiency numbers. These are tool-layer metrics, not cognitive-layer metrics.

## Personal Information Sovereignty

Most common deployment failure mode: **trust failure**, not technical failure. Employees perceive the system as surveillance.

Design principle:
- Personal Vault lives on personal device only. Never enters organizational database. Never accessible by organizational Agents. Never in governance audit logs.
- Information flows from Personal Vault to organizational layer only through explicit, deliberate user choice.
- **Default: private. Active: public.**

This is not a feature. It is the foundational trust condition that makes the entire system viable.

## Tool-Layer vs. Cognitive Infrastructure

**Tool-layer AI** (visible, countable): Email drafting, data analysis, slide generation. Value directly measurable. Easy to replace.

**Cognitive infrastructure** (invisible, foundational): Changes the quality of every decision made. Value manifests as better meetings, fewer wrong assumptions, faster context alignment. Cannot be directly measured — but its absence is the company's most expensive problem.

When everyone's attention is on tool-layer, the missing cognitive layer is overlooked. That is where the actual value lives.
