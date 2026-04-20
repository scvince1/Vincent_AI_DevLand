# KB Workshop · Stage Card

## Timeline

| Time | Block |
|---|---|
| 00:00-05:00 | 0. Tech setup |
| 05:00-15:00 | 1. Email Agent check-in |
| 15:00-28:00 | 2. KB + three things + flowchart |
| 28:00-48:00 | 3. Bootstrap + first ingest |
| 48:00-58:00 | 4. Bridge |
| 58:00-60:00 | 6. Close |

## Block 0 · Tech Setup (5m)

Open tool. Hand-raise: "prompt box visible?" Assistant handles stuck.

## Block 1 · Email Agent Check-in (10m)

- Q1 (hands): "Who drafted with Email Agent since last time?"
- Q2: "One surprise, good or bad?"
- Pivot: "The gap: agent doesn't know who you are or who they are. Today we fix that."
- Frame: "Not another agent. The foundation any future agent plugs into."

## Block 2 · KB + Three Things + Flowchart (13m)

### 2a · What a KB Is (3m)

- Folder of .md. Same as Word, PPT, PDF.
- Analogy: D-drive client folder.
- Anecdote: high-school friend, rocket science, "not that hard."

### 2b · Three Things (5m)

A KB works when all three happen:

1. **Write**: info gets in.
2. **Read**: agent reads the right file.
3. **Use**: reading changes the output.

**Doctor analogy (verbatim):** "File exists with history. Doctor opens it before the appointment. Doctor actually changes treatment based on it. All three happen, or the file is theater."

**Diagnostic:** "If a draft feels off, ask which of the three broke."

### 2c · Flowchart + Map (4m)

```
Your instruction
 ├ person + project → read both → draft
 ├ person only → read person + linked projects → draft
 └ project only → read project + linked people → draft
```

| Component | Serves |
|---|---|
| `_index.md` | Read (entry point) |
| People / Projects | Read (substance) |
| Action Items / Commitments | Read (obligations) |
| Things I've Learned | Use (judgment) |
| My Writing Style | Use (voice) |
| `Dump/` | Write (inbox) |
| `Deprecated/` | Write (safety net) |

### 2d · Closer (1m)

"Now we build it. I'll call out which of the three you're in at every step."

## Block 3 · Bootstrap + First Ingest (20m)

### 3a · One-Step Setup (10m)

Paste `Knowledge_Agent_Bootstrap.md` into a fresh claude.ai Project or Claude Code session.

AI asks: "Where should your KB live?" → You answer → AI creates `MyKB/` with six card folders, Dump, Dump/Done, Deprecated, `_index.md`, and `CLAUDE.md` with the full agent prompt.

Show File Explorer with the new structure.

Then scroll through `CLAUDE.md` and point to 6 anchors:

0. What you are (agent-agnostic memory layer)
1. Serve read queries (index first, then cards)
2. KB shape (index + six folders)
3. Ingest channels (Dump / connected / inline)
4. How to write (plain prose, no metadata)
5. Incremental updates (deprecate before overwrite)

Teaching line: "I wrote this by asking 'what do I want the agent to do when X?' That IS prompt engineering."

### 3b · First Ingest (10m)

Your line: "Take my last 30 days of emails and organize them into MyKB."

Wait 30-60 sec.

Show:
1. `_index.md` first (one-page map of your world).
2. `People/` (individual cards).
3. The auto summary: "Ingest complete. N items. New people: ... New projects: ... Commitments: ... Items I could not process: ..."
4. Invite inline: "Mark just moved to Miami." / "I don't know Sarah well; don't make me sound close."

Cue: "30 sec ago People was empty. You just did Write."

Fallback: pre-run baseline, ready to project.

## Block 4 · Bridge (10m): Teaching Core

**Open (verbatim, all four):**
1. Raise your hand. Ask.
2. Debugging with AI is not hard.
3. Not programming. Not rocket science.
4. Prompt engineering is a real skill: reflect, identify gap, hypothesize, test, iterate.

**Round 1:** "Email Agent. I have a Knowledge Agent at MyKB. Ask it for context on sender and project. Then draft."

*Draft likely opens "Hi Mark, hope you're doing well." That IS the lesson. Do not save it.*

Reflection: "It read. Draft doesn't sound like me with Mark. What did I want? Mark's voice. I didn't say that."

**Round 2:** "Try again. Pull Mark's preferences. Match exactly. No greetings. Start with substance. Sign off with just my name."

*Draft improves.*

Reflection: "I didn't code. I talked. More precisely the second time. That's prompt engineering."

**Round 3 (skip if under 47m):** "Mark asked three questions. You addressed two. Find the third, add a one-line answer."

**Closer (always):** "Knowledge Agent didn't care who asked. Calendar Agent tomorrow, same way. Every agent you plug in gets smarter for free. Foundation built once."

**Fails fallback:** play 10-sec backup clip. "It didn't want to play today. Rhythm is the lesson, not whether today worked."

## Block 6 · Close (2m)

**Three takeaways:**
1. You have a KB. Don't throw it out.
2. Tell the agent: "check MyKB first, then write."
3. Next: calendar, meetings, a second agent.

**Personal:** "Third iteration. First two unusable. This one is."

**Callback:** "You just did Write. Read. Use. That's the baseline."

*No Q&A. Materials via assistant.*

## Pre-Stage Checklist

- [ ] Bootstrap prompt on clipboard, fresh session open
- [ ] Opus selected in Project Settings
- [ ] Mailbox authorized
- [ ] Mark's test email in inbox
- [ ] Backup 10-sec clip on second tab
- [ ] Pre-run baseline ready
- [ ] Water on podium

*The draft is not the point. The rhythm is.*
