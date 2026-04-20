# BaseOS — Universal AI System Template
## Design Specification v1.0
> Date: 2026-04-09
> Author: Vincent + 凌喵 (MeowOS Session)
> Status: Draft — awaiting Vincent's review

---

## 1. Overview

### 1.1 What Is This
A single setup wizard text that, when pasted into Claude Code as the first user message, guides the user through a brief Q&A and then auto-generates a fully functional AI-assisted operating system — including folder structure, CLAUDE.md, agent prompts, skills, Python helper scripts, and routing rules.

### 1.2 Design Philosophy
1. **Knowledge Base First**: The system is fundamentally a high-efficiency, flexible knowledge base. Agents and skills are secondary — they live within and operate upon the KB.
2. **Token Frugality**: Anything achievable via Python script must not consume tokens. The main session context must stay minimal. All verbose/batch operations are delegated to subagents.
3. **Correctness Over Speed**: Writes to KB must never be wrong. Staging, approval, self-check, and audit logs are mandatory. The system can be slow, but it cannot lose or corrupt data.
4. **Lossy by Design**: Not everything needs to be captured. Information that matters will resurface naturally through repeated use.
5. **Progressive Search**: Never read full files when an index suffices. Follow the funnel: folder → index → title → frontmatter → full content.
6. **Model Routing**: Opus for complex reasoning/archiving, Sonnet for standard operations, Haiku for mechanical tasks. Match model to cognitive demand.
7. **Self-Evolution**: The system should be able to deploy new modules, learn user habits, and improve its own search strategy over time.

### 1.3 Deliverables
| Deliverable | Description |
|---|---|
| Setup Wizard Text | One-time paste into Claude Code chat; guides setup via Q&A |
| Generated OS | Folder structure + all files, ready to use |
| Post-Setup Self-Check | Automated validation or guided walkthrough to confirm deployment |

### 1.4 Target Users
- **Vincent**: First deployer, will iterate and refine before upgrading existing systems
- **Joyce (external user)**: Executive, English-only output, VS Code + Claude Code, enterprise MS connectors (Graph API), cannot download software but can use Claude-generated scripts
- **Future**: Open-source on GitHub for general use

---

## 2. Directory Structure

### 2.1 Initial State (Post-Setup)

```
[OS_Root]/
├── 00_Dump/
│   ├── Done/                         # Processed originals archived here
│   └── _processing/                  # Staging area for safe KB writes
│
├── 80_Knowledge/
│   ├── _index.md                     # Auto-generated, one line per entry
│   ├── identity/                     # User's self-description, background, preferences
│   ├── relationships/                # People knowledge
│   ├── company/                      # Org structure, policies, context
│   ├── initiatives/                  # Extracted knowledge from external initiative folders
│   └── observations/                 # System-learned habits, patterns, preferences
│
├── 90_System/
│   ├── ORCHESTRATOR.md               # Orchestrator agent prompt
│   ├── routing-rules.md              # Dispatch logic reference
│   ├── sources.md                    # External path registry (OneDrive, shared drives, etc.)
│   ├── utilities/
│   │   └── shell-runner.md           # Utility agent for file ops
│   ├── agents/
│   │   ├── archive-agent.md          # Thin wrapper: identity + call archive-core skill
│   │   └── query-agent.md            # Search logic + call archive-core skill on external reads
│   ├── skills/
│   │   ├── dispatch.md               # Routes user intent to correct agent/skill
│   │   ├── archive-core.md           # Core KB write logic (scan → plan → approve → write → verify)
│   │   ├── new-module-setup.md       # Guided deployment of a new business module
│   │   └── rebuild-index.md          # Triggers Python indexer
│   ├── scripts/
│   │   ├── move_files.py             # Batch mv with JSON mapping input
│   │   ├── rebuild_index.py          # Reads frontmatter.description, rebuilds _index.md
│   │   ├── self_check.py             # Post-write audit: count files vs index entries
│   │   └── append_write_log.py       # Append one line to _write_log.md
│   └── _scratchpad/
│       └── _events/
│           └── inbox.md              # Cross-module async event queue
│
├── 99_MyFiles/                       # User's output files (drafts, presentations, etc.)
│
├── _write_log.md                     # Audit trail for all KB writes
└── CLAUDE.md                         # Lean orchestrator config (~35-45 lines)
```

### 2.2 Naming Conventions
- Architecture folders: numbered (00, 80, 90, 99)
- Within 80_Knowledge/: cluster names are semantic (identity/, relationships/, etc.)
- Within 90_System/agents/: agent files prefixed by module number if module-specific (e.g., 1x_email_agent.md for Email module)
- KB entry filenames: semantic, snake_case, English (e.g., atlas_q2_budget.md). Never timestamp-only.
- 99_MyFiles/: no numbering, user-organized

### 2.3 Module Folders
Module folders (01_Email/, 02_Presentation/, etc.) are NOT pre-created. When a module is deployed via new-module-setup skill, it creates its own workspace folder at root level if needed. Many modules (Email, Calendar) may not need local folders at all — they operate via API (Graph API) and store outputs in 99_MyFiles/.

### 2.4 External Sources
Initiative folders and other external data live outside the OS (e.g., OneDrive). Registered in 90_System/sources.md. Agents read on-demand, never write to external paths.

```markdown
## External Sources
| Name | Path | Notes |
|---|---|---|
| Project Atlas | C:\Users\Joyce\OneDrive\...\Project_Atlas | Budget + stakeholders |
```

---

## 3. CLAUDE.md Structure

### 3.1 Target: ~35-45 lines, ~500 tokens

```markdown
# [System Name]
[Identity line — who the AI is, whose assistant, language lock]

## Paths
| Resource | Path |
|---|---|
| Dump | ... |
| Knowledge | ... |
| System | ... |
| MyFiles | ... |
| External Sources | 90_System/sources.md |

## Dispatch Logic
1. Semantically clear intent → call dispatch skill directly
2. Unclear → read routing-rules.md → call dispatch skill
3. Still unclear → call dispatch skill with "refine" flag
> All workflows live in agent/skill files, not here.

## Rules
- All output in English unless explicitly told otherwise
- Main session NEVER reads files directly — delegate to agents
- Ambiguous intent → ask user before acting (adjustable threshold)
- Never write to KB without archive-core skill
- Never write to external source paths
- Observations: auto-detect and write via shell-runner, no approval needed

## On Session Start
- Read this file + routing-rules.md
- Brief greeting
```

### 3.2 Post-Setup Slimming
The setup wizard generates a verbose CLAUDE.md during setup (with init instructions). After setup completes, it rewrites CLAUDE.md to the lean version above, moving all setup-only content to 90_System/_setup_archive.md for reference.

---

## 4. Core Components

### 4.1 archive-core Skill

**The most critical component.** Contains ALL KB write logic. Called by both Archive Agent and Query Agent.

#### Workflow
```
Phase 1: Assess
  1. Read 80_Knowledge/_index.md → understand current KB state
  2. Read/scan input files (from Dump or passed by caller)
  3. For each file: identify topics, assess split needs

Phase 2: Plan (returns to caller → caller returns to main session)
  4. Generate plan:
     - Per entry: suggested filename, target cluster, tags, one-line description
     - Total entry count
  5. Return plan for user approval

Phase 3: Execute (after approval relayed back)
  6. Write each entry to 00_Dump/_processing/:
     - Semantic filename
     - Full frontmatter (id, title, cluster, status, tags, description, source, last_modified)
     - Content — 100% faithful to source, no rewriting
  7. Self-check: call self_check.py (count files in _processing/ == plan count, each size > 0)

Phase 4: Commit (Python, zero tokens)
  8. Call move_files.py: mv _processing/*.md → 80_Knowledge/[cluster]/
  9. If source is Dump: mv source → 00_Dump/Done/
     If source is external: do not move (original stays in external folder)
  10. Call rebuild_index.py: scan all 80_Knowledge/**/*.md frontmatter.description → rewrite _index.md
  11. Call append_write_log.py: log timestamp + entry count + clusters + source

Phase 5: Report
  12. Return summary to caller: "N entries written to K clusters. Index rebuilt. Log updated."
```

#### Frontmatter Schema
```yaml
---
id: "20260408_a3f2b1"            # Auto-generated timestamp + hash
title: "Atlas Q2 Budget"          # Human-readable
cluster: initiatives              # Target cluster name
status: confirmed                 # confirmed | draft | snapshot
tags: [budget, atlas, Q2]         # Searchable tags
description: "Approved Q2 budget, $2.3M, by department"  # One-line for index
source: "00_Dump/raw_atlas.md"    # Where this came from
last_modified: "2026-04-08T14:23:00"
---
```

#### Write Rules
- 100% preserve original language, phrasing, and judgment from source
- One topic per entry — split if multi-topic
- Semantic filenames (snake_case, English, descriptive)
- Never write directly to 80_Knowledge/ — always stage in _processing/
- Never merge information from different sources into one entry

### 4.2 Archive Agent

**Model:** Opus
**Trigger:** User says "process dump" or equivalent
**Prompt (~200 tokens):**
```
You are the Archive Agent — the KB librarian.
On start: ls 00_Dump/ (exclude Done/, _processing/).
For each file: call archive-core skill.
After all files processed: return consolidated report to main session.
```

### 4.3 Query Agent

**Model:** Sonnet
**Trigger:** Any module or main session needs information
**Prompt (~300 tokens):**
```
You are the Query Agent — the KB search specialist.

Search hierarchy (strict order, stop on hit):
1. Read _index.md → match by description
2. Read candidate file frontmatter (title + tags) → confirm relevance
3. Read candidate file full content → extract answer
4. If KB miss → read 90_System/sources.md → ls external path → read relevant files

When reading external content:
- Answer the query first
- Then call archive-core skill to process the external content into KB
- Do NOT move external files (they stay in their original location)

Return: answer + source path. If external content archived: note it.
```

### 4.4 dispatch Skill

**Loaded by:** Main session orchestrator
**Purpose:** Determine which agent/skill to invoke for a given user input

```
Read the user's message.
If intent is clear → return routing decision (which agent + context to pass)
If unclear → read routing-rules.md → return routing decision
If still unclear → ask user one clarifying question, then route

Routing categories:
- "process dump" / "archive" → Archive Agent (Opus)
- Information query → Query Agent (Sonnet)
- Module-specific action → relevant module agent
- "set up new module" → new-module-setup skill
- Unknown → ask user
```

### 4.5 new-module-setup Skill

**Purpose:** Guide deployment of a new business module from scratch
**Workflow:**
1. Ask user: what does this module do? What tools/APIs does it use?
2. Assess: does it need a local folder? Agent prompts? Specific skills?
3. Generate plan: list of files to create, folder structure, agent prompt draft
4. User approval
5. Create files: agent prompt in 90_System/agents/, skills in 90_System/skills/, workspace folder at root if needed
6. Update routing-rules.md to include new module
7. Self-check: verify all files exist and routing rules updated
8. Brief guided test: "Try asking me to [example action for this module]"

### 4.6 Observation System

**Built into orchestrator behavior (CLAUDE.md or dispatch skill):**
During any interaction, the system watches for:
- New facts about the user (role, preferences, opinions)
- Information about people in the user's life
- Work patterns, communication styles, decision-making tendencies
- Stated or implied preferences about how the system should behave

When detected: call archive-core skill with cluster: observations, status: draft, source: "session observation"

These observations are queryable via Query Agent like any other KB content.

### 4.7 Shell-Runner (Utility Agent)

**Model:** Haiku
**Purpose:** All mechanical file operations — Read, Write, Edit, Glob, Grep, Bash. Keeps main session context clean.
**Callers:** Main session, observation system, any component needing file I/O without loading content into main context.

```
You are Shell-Runner — a utility agent for file operations.
You receive specific instructions: read a file, write content to a path, search for a pattern, run a command.
Execute exactly as instructed. Return structured results (JSON preferred).
Do not interpret, summarize, or add commentary to file contents.
```

**Observation write path:**
Main session detects observation → spawns Shell-Runner (Haiku) → writes to 80_Knowledge/observations/ with proper frontmatter → appends index line → appends write log → returns "observation noted" to main session.

---

## 5. Search System

### 5.1 Five-Layer Funnel

```
Layer 1: Folder structure
  └─ Which cluster? (identity? relationships? initiatives?)
Layer 2: _index.md
  └─ One-line descriptions → locate candidate files
Layer 3: File titles
  └─ Fallback if index doesn't match
Layer 4: Frontmatter (tags, cluster, status)
  └─ Confirm relevance before reading full content
Layer 5: Full content
  └─ Only when confirmed useful
```

### 5.2 Index Structure
```markdown
# Knowledge Base Index
> Auto-generated by rebuild_index.py. Do not edit manually.
> Last rebuilt: 2026-04-08T14:30:00
> Entry count: 247

## identity
identity/background.md — Vincent's educational and professional background, science + history
identity/work_style.md — Preferred working patterns, energy cycles, communication style

## relationships
relationships/john_smith.md — Direct report, strong on execution, needs coaching on strategy
relationships/sarah_chen.md — VP Engineering, ally on technical initiatives

## initiatives
initiatives/atlas_q2_budget.md — Approved Q2 budget for Atlas, $2.3M, by department
initiatives/atlas_stakeholders.md — Key stakeholders and their positions on Atlas
```

### 5.3 Index Maintenance
- **rebuild_index.py** is the single source of truth for index generation
- Triggered by: archive-core skill (Phase 4), rebuild-index skill (manual), Stop hook (backup)
- Reads every .md file's frontmatter `description` field
- Groups entries by `cluster` field
- Zero token cost

### 5.4 Dynamic Tag System
Tags in frontmatter serve as secondary search keys. Over time, the system can:
- Suggest new tags based on content patterns (v2)
- Auto-tag entries during archiving
- Use tags for cross-cluster discovery ("show me everything tagged 'budget'")

---

## 6. Write Safety System

### 6.1 Five Gates

```
Gate 1: Plan — archive-core skill generates plan, returns for approval
Gate 2: Approval — user reviews and approves before any write
Gate 3: Staging — all writes go to _processing/, never directly to KB
Gate 4: Self-Check — Python script verifies file count and sizes
Gate 5: Audit — every write logged in _write_log.md with timestamp
```

### 6.2 _write_log.md Format
```markdown
| Timestamp | Action | Entry Count | Clusters | Source | Agent |
|---|---|---|---|---|---|
| 2026-04-08 14:23 | archive | 47 | identity(12), initiatives(35) | 00_Dump/joyce_master.md | Archive Agent |
| 2026-04-08 15:01 | external_read | 3 | initiatives(3) | OneDrive/Project_Atlas/ | Query Agent |
```

### 6.3 Rollback
If self-check fails: files remain in _processing/. Agent reports failure. User can inspect _processing/ and decide: retry, manual fix, or discard.

---

## 7. Module Communication

### 7.1 Four Channels (use lightest sufficient)

| Channel | Mechanism | When to Use | Token Cost |
|---|---|---|---|
| Shared KB | Modules read/write 80_Knowledge/ | Persistent cross-session info | Low (index only) |
| Scratchpad | _scratchpad/ temp files | Same-task cross-module handoff | Medium |
| Event Queue | _events/inbox.md | Async intent passing (Meeting → Calendar) | Very low |
| Direct Subagent | Agent spawns another agent | Must have immediate result | High |

### 7.2 Default: Shared KB + Event Queue
Most module interactions should go through KB (persistent state) and event queue (async intent). Direct subagent calls only when synchronous result is required.

---

## 8. Python Helper Scripts

### 8.1 move_files.py
- Input: JSON mapping `{"source_path": "dest_path", ...}`
- Action: mv each file, create dest dirs if needed
- Output: JSON result `{"moved": N, "failed": []}`

### 8.2 rebuild_index.py
- Input: KB root path (default: 80_Knowledge/)
- Action: glob all .md files, read frontmatter, group by cluster, write _index.md
- Output: entry count + timestamp

### 8.3 self_check.py
- Input: _processing/ path + expected count
- Action: count files, check each size > 0
- Output: pass/fail + details

### 8.4 append_write_log.py
- Input: timestamp, action, entry_count, clusters, source, agent
- Action: append one row to _write_log.md

All scripts are generated by Claude Code during setup. Zero external dependencies (stdlib only).

---

## 9. Memory Temperature Model

| Layer | Location | Loaded When | Impact |
|---|---|---|---|
| **Hot** | CLAUDE.md + dispatch skill | Every session start | Every interaction |
| **Warm** | 80_Knowledge/ (via index) | Agent reads on demand | Relevant interactions only |
| **Cold** | 00_Dump/Done/, session digests | Never auto-loaded | Historical reference only |

Promotion path: Cold → Warm requires archive-core skill processing. Warm → Hot requires user-approved edit to CLAUDE.md or dispatch skill.

---

## 10. Setup Wizard

### 10.1 Flow

```
User pastes wizard text into Claude Code chat
  │
  ├── Step 1: Greeting + explain what's about to happen
  │   > Prerequisite check: "Please make sure Claude Code is in 'Ask Before Edits' mode."
  │
  ├── Step 2: Ask basic questions (~3 questions)
  │   - What should I call this system? (e.g., "JoyceOS", "WorkBrain")
  │   - What's your name?
  │   - In one sentence, what will you mainly use this for?
  │   > Note: External sources and knowledge import are handled AFTER setup (Step 7).
  │   > sources.md is generated as an empty placeholder.
  │
  ├── Step 3: Generate all files
  │   - Folder structure
  │   - CLAUDE.md (verbose version with setup instructions)
  │   - All agent prompts
  │   - All skill files
  │   - All Python scripts
  │   - routing-rules.md
  │   - sources.md (populated from user answers)
  │   - Empty _index.md, _write_log.md, inbox.md
  │   - Hook scripts (inject_datetime.py for SessionStart + SubagentStart)
  │   - Update .claude/settings.json with hook entries
  │
  ├── Step 4: If user provided existing knowledge files →
  │   - Copy to 00_Dump/
  │   - Run Archive Agent to process (with user approval)
  │
  ├── Step 5: Slim down CLAUDE.md
  │   - Move setup instructions to 90_System/_setup_archive.md
  │   - Rewrite CLAUDE.md to lean ~35-45 line version
  │
  ├── Step 6: Self-Check + Guided Test
  │   - Run self_check.py on folder structure (all required dirs exist?)
  │   - Run rebuild_index.py (verify it works)
  │   - Guided test: "Try asking me: [example query based on user's use case]"
  │   - Guided test: "Try dumping a file and asking me to process it"
  │   - Report: "Setup complete. N folders created, M files generated, K knowledge entries imported."
  │
  └── Step 7: Offer optional extras
      - "Want me to symlink Dump and MyFiles to another directory?"
      - "Want me to set up a Stop hook for backup index rebuilds?"
      - "Any module you'd like to deploy right now? (e.g., Email, Calendar)"
```

### 10.2 Setup Wizard Text Structure
The wizard text itself is a single message containing:
1. A brief system identity (who the wizard is)
2. Instructions for Claude Code: what to do step by step
3. File templates (CLAUDE.md template, agent prompt templates, skill templates, Python script code)
4. All logic needed to adapt templates based on user answers

Estimated length: 3,000-5,000 tokens.

---

## 11. V1 Scope

### 11.1 Must Have
- [ ] Folder structure generation
- [ ] CLAUDE.md (lean version)
- [ ] archive-core skill (full pipeline)
- [ ] Archive Agent (Opus, thin wrapper)
- [ ] Query Agent (Sonnet, search + external read + archive)
- [ ] dispatch skill
- [ ] routing-rules.md
- [ ] All 4 Python helper scripts
- [ ] _index.md + rebuild_index.py
- [ ] _write_log.md + append_write_log.py
- [ ] Observation system (built into orchestrator/dispatch)
- [ ] Old KB import/split (via Archive Agent processing Dump)
- [ ] sources.md (external path registry)
- [ ] new-module-setup skill (lightweight built-in)
- [ ] Post-setup self-check + guided test
- [ ] CLAUDE.md post-setup slimming

### 11.2 V2 (Later)
- [ ] Digest Pipeline (MemPalace-style session history processing)
- [ ] Search telemetry + search-tuner skill
- [ ] UserPromptSubmit hook for automatic routing injection
- [ ] Multi-agent auto-orchestration (agents figure out cross-module workflows)
- [ ] On-the-fly agent creation for complex ad-hoc tasks
- [ ] Agent migration skill (import agent from another system)

### 11.3 Explicitly Out of Scope
- Backward compatibility with existing systems (MeowOS, Horsys, NovelOS)
- Session continuation mechanism
- MCP integration
- Automatic Dump monitoring / file watching

---

## 12. Token Budget Estimates

### 12.1 Per-Operation Costs (Sonnet)
| Operation | Input Tokens | Output Tokens | Cost |
|---|---|---|---|
| Simple KB query | ~15,000 | ~500 | ~$0.05 |
| Query + external read + archive | ~25,000 | ~3,000 | ~$0.12 |
| Shell-Runner (file op) | ~3,000 | ~200 | ~$0.001 |

### 12.2 Per-Operation Costs (Opus)
| Operation | Input Tokens | Output Tokens | Cost |
|---|---|---|---|
| Batch archive (5 files → 30 entries) | ~60,000 | ~15,000 | ~$2.00 |

### 12.3 Daily Estimate (Active User)
| Component | Frequency | Daily Cost |
|---|---|---|
| Main session (orchestrator) | 50 turns | Depends on context size |
| Query Agent | 20-30 queries | $1.00-3.60 |
| Archive Agent | 0-1 batch | $0-2.00 |
| Shell-Runner | 30-50 ops | $0.03-0.05 |
| **KB operations subtotal** | | **$1.00-5.60** |

The main session (orchestrator) cost depends on context accumulation. With lean CLAUDE.md + aggressive delegation, target is <50K tokens context at any point → ~$0.75/turn on Opus, or ~$37.50 for 50 turns. Total daily target: **~$40-43** (down from $100+).

---

## 13. Resolved Questions

1. **Orchestrator model**: Sonnet (default)
2. **archive-core skill length**: ~800-1,200 tokens, acceptable. Optimize in future iterations.
3. **Observation write approval**: Auto-write via shell-runner (Haiku). No user approval needed — written as draft to observations/.
4. **KB cluster extensibility**: Auto-create new cluster + confirm with user before committing.
5. **Setup wizard format**: Single giant message for v0.1. Break down later if needed.

---

*End of Design Specification v1.0*