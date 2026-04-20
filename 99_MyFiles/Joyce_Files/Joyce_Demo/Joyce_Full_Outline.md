# KB Workshop · Full Outline (for rehearsal)

**North star:** the draft is not the point. The rhythm is.

## Timeline

| Time | Block |
|---|---|
| 00:00-05:00 | 0. Tech setup |
| 05:00-15:00 | 1. Email Agent check-in |
| 15:00-28:00 | 2. KB + three things + flowchart |
| 28:00-48:00 | 3. Bootstrap + first ingest |
| 48:00-58:00 | 4. Bridge |
| 58:00-60:00 | 6. Close |

---

## Block 0 · Tech Setup (5 min)

**What to do:** open tool, hand-raise check, assistant catches stragglers.

**Key line:** "Cannot start teaching until everyone is open."

**Why this matters:** audience settles. You establish you'll hold hard timings.

**Common mistake:** over-reassuring stragglers. Don't. Stay on timeline.

---

## Block 1 · Email Agent Check-in (10 min)

**Two seed questions:**

- Q1 (hands): "Who actually drafted with Email Agent since last time?"
- Q2: "One surprise, good or bad?"

**Pivot line:** "The gap exists because Email Agent doesn't know who you are or who the other person is. Today we build the memory layer that fixes that."

**Closing framing:** "Today is not another agent. It's the foundation every future agent plugs into. Email Agent today. Calendar Agent tomorrow."

**Why this matters:** continuity. The gap you name here is exactly what the rest of the hour fixes.

**Preempt a likely question:** "Is the new thing replacing Email Agent?" No. It is a layer beneath Email Agent. Email Agent now asks this layer for help. Every future agent asks the same layer.

**If no one speaks up:** tell one off-voice moment yourself (e.g., "my agent wrote to our CEO like I was writing a first-week intern"). Move on.

---

## Block 2 · KB Concept + Three Things + Flowchart (13 min)

### 2a · What a KB Is (3 min)

**Core:** "A Knowledge Base sounds scary. It is not. It is a folder with a handful of .md documents in it. .md is plain text. No different from the Word docs you write, the PPTs you build, the PDFs you read."

**Analogy:** "The client folder on your D drive is a KB. Each client is a folder, with notes, contracts, minutes inside. The only new thing today is we let the agent read it."

**Anecdote (verbatim):** "Nothing to be scary about. It is a technology. It is not rocket science. I have a high school friend who literally built a rocket in his backyard. He now runs a rocket science business. He was one of the stupid kids in high school. So I guess rocket science isn't that hard."

**Closer:** "Today's KB closes the gap. Who you are. Who you work with. The context."

**Why this matters:** demystify. Attendees often picture a database. Naming it "a folder of text" removes the fear.

### 2b · Three Things (5 min)

**On-screen diagram:** Write → Read → Use.

**The three explained:**

1. **Write.** Information really gets into the KB. You typing, or the agent ingesting. Fails when: info is in your head but never lands.

2. **Read.** When someone needs that info, they actually go read the right file. Fails when: info is there but the agent does not look. Or looks at the wrong card.

3. **Use.** Reading the right info actually changes the output. Fails when: agent read the card, but the draft looks the same as if it had not.

**Doctor analogy (use for clarifying):** "A doctor and a patient file. The file exists with history written down. The doctor opens it before the appointment. The doctor actually changes the treatment based on what was in the file. All three, or the file is theater."

**Compressed 30-sec version (use if the room goes blank):** "A KB works when three things all happen. You write it down. The agent reads the right file. Reading changes the output. If a draft feels wrong, ask which of the three broke."

**Diagnostic use:** this is a debugging tool, not a memorization exercise. When a draft disappoints, ask which of Write / Read / Use broke.

**Common confusion:** the audience may hear "three steps in order." They are not steps. They are three simultaneous conditions. All have to hold.

**Preview into next blocks:** "In the next 20 minutes you do Write. In the 10 minutes after, Read and Use."

### 2c · Brain Flowchart + KB Map (4 min)

**On-screen flowchart:**
```
Your instruction
 ├ person + project → read both → draft
 ├ person only → read person + linked projects → draft
 └ project only → read project + linked people → draft
```

**Key line:** "Every time you call the agent, internally it walks this tree. It enters at the top, walks to the leaf, reads the relevant cards."

**Cross-reference mechanics:** "When the agent reads Mark's card and sees 'Alpha,' it goes and reads Alpha too. You do not tag anything. You just write clearly."

**KB Map:**

| Component | Serves |
|---|---|
| `_index.md` | Read (entry point) |
| People / Projects | Read (substance) |
| Action Items / Commitments | Read (obligations) |
| Things I've Learned | Use (your judgment) |
| My Writing Style | Use (your voice) |
| `Dump/` | Write (low-friction inbox) |
| `Deprecated/` | Write (safety net) |

**Closer:** "Know which part serves which thing. When you extend your KB later, you know where new stuff belongs."

### 2d · One-Sentence Closer (1 min)

"Now we build it. I will call out which of the three you are in at every step."

---

## Block 3 · Bootstrap + First Ingest (20 min)

### 3a · One-Step Bootstrap (10 min)

**Lead-in:** "Last time you built Email Agent by pasting a long prompt. Same idea today, different purpose. One paste, setup done."

**Live action:**

1. Open a fresh claude.ai Project (or Claude Code session).
2. Paste the full content of `Knowledge_Agent_Bootstrap.md`.
3. AI asks: "Where should your Knowledge Base live?"
4. You answer: `default` (or a specific folder path).
5. AI creates `MyKB/` with six card folders, `Dump/`, `Dump/Done/`, `Deprecated/`, an empty `_index.md`, and a `CLAUDE.md` with the full agent prompt.
6. AI confirms setup and tells you what to do next.

**Show audience:** File Explorer with the new folder structure. Point to each folder briefly.

**Then scroll through `CLAUDE.md`, point to 6 anchors (~3 min):**

**0. What you are** (agent-agnostic memory layer)
"This agent does not work only with Email Agent. Any future agent plugs into this same layer."

**1. How to serve read queries** (index first, then cards)
"When anyone asks for context, check the index first, then drill into cards. Over-read when in doubt."

**2. The KB shape** (index + six folders + Dump + Deprecated)
"Map of the whole place. Six card folders plus the special folders."

**3. Ingest channels** (Dump / connected sources / inline)
"Three ways stuff gets in. Drop it. Connect a source. Tell me directly."

**4. How to write** (plain prose, no metadata)
"One paragraph per card. Like briefing a new friend."

**5. Incremental updates** (deprecate before overwrite)
"Never destroy old state. Archive it. You can look back."

**Teaching line (core teach):**
"I wrote this by asking one question repeatedly: what do I want the agent to do when X? Each paragraph answers one layer. That is prompt engineering."

**Why this matters:** audience sees the agent's inner rules as readable English, not as opaque magic. Empowers them to change it later.

**Common question:** "Do I have to write this every time?" No. It is written. The Bootstrap prompt pastes it for you. You only open it if you want to change the agent's behavior later.

### 3b · First Ingest (10 min)

**Your one sentence:**

> "Take my last 30 days of emails and organize them into MyKB. If my old Email Agent .md is still around, unpack it into these folders too."

**Wait 30-60 sec.** This is the most nerve-wracking moment. Do not fill silence.

**Show:**

1. `_index.md` first. Audience sees the one-page map of your world. Names, projects, open commitments.
2. `People/`. Individual cards.
3. The summary report: "Ingest complete. 54 items. New people (8): [names]. New projects (3): Alpha, Beta, Gamma. Updated people (4). Commitments (5). Items I could not process (1): calendar.ics, unsupported format."
4. Invite inline: "Mark just moved to Miami." / "I don't know Sarah well; don't make me sound too close."
5. Show the file being appended in real time.

**Inline cue lines:**
- "30 seconds ago People was empty. That is Write."
- "Your inline corrections are Write too, just more targeted."

**Fallback if ingest fails:** "I ran a baseline yesterday. Let me put it on screen. Your own ingest will continue later." (Baseline = your pre-run with fake email.)

---

## Block 4 · Bridge (10 min): Teaching Core

### Open (1 min, all four verbatim)

"Ten minutes. Four things.

**One. Raise your hand. Ask.** Ask me. Ask the AI. Find the answer yourself. The cheapest skill in this room.

**Two. Debugging with an AI is not as hard as you think.**

**Three. This is not programming. This is not rocket science.** Rocket science my high school friend did. This is easier.

**Four. Prompt engineering is a real skill.** You reflect on what you actually want. Identify the gap. Form a hypothesis. Test it. Iterate. Every step is learnable."

### Round 1 (~3 min)

**Your typed line:** "Email Agent. I have a Knowledge Agent at MyKB. Before drafting this reply, ask it for context on the sender and the project. Then write."

**Expected suboptimal draft:** "Hi Mark, hope you're doing well! Thanks so much for your email about Alpha. I'll review the updated timeline and get back to you by end of week."

**Stop. Reflect to audience:** "Three things to notice. First, it read. You see 'Alpha' and 'timeline' in the right places. Read worked. Second, the draft is polite. Competent. Third, and this is where we stop: it does not sound like me with Mark. My Knowledge Agent has a note saying Mark prefers concise, no-small-talk. But this draft opens with 'Hi Mark, hope you're doing well.' Exactly what Mark does not want. Read worked. Use did not close. What do I do now? I ask: what did I actually want?"

Hold up one finger. "I wanted Mark's voice. I did not say that. The gap is in what I said. Not in the agent. I say it again, more precisely."

### Round 2 (~3 min)

**Your typed line:** "Try again. When you reply to Mark, pull his communication preferences from Knowledge Agent first. Match exactly. Mark does not open with greetings. No small talk. Start with substance. Sign off with just my name."

**Expected improved draft:** "Mark, Reviewed the Alpha timeline. Two comments: [numbered list]. Joyce"

**Reflect:** "Better. No 'hope you're doing well.' Starts with substance. Sign-off with just my name. That is Mark's voice, and Mark's voice is how I actually write to Mark. I did not open any code. I did not edit any file. I talked. In English. More precisely the second time. That is prompt engineering."

### Round 3 (~2 min, skip if clock under 47 min)

**Your typed line:** "One more thing. Mark asked three questions. You addressed two. Find the third and add a one-line answer."

**Expected final draft:** Three numbered items, all three questions answered.

**Reflect:** "Three for three. Still no code. The draft is not the point. The rhythm is. What did I want? What did I get? Where's the gap? Say it again, more precisely. If you take that rhythm home, you do not need me to teach you anything else."

### Closer (~1 min, always)

"I told Email Agent to talk to Knowledge Agent. The Knowledge Agent did not care that it was Email Agent asking. Tomorrow it could be Calendar Agent. Or Slack Agent. Or an agent you build that does not yet exist. Every future agent you plug in gets smarter for free. You built the foundation once. From here you only iterate on the top layer. That is why today was worth an hour of your time."

### Fails fallback

Play 10-sec backup clip of Round 2 working. "It didn't want to play today. The rhythm is the lesson, not whether today's live run worked. Take that home."

---

## Block 6 · Close (2 min)

**Three takeaways:**
1. You have a KB. Index + six folders + Dump + Deprecated. Don't throw it out.
2. Next time you draft anything: tell the agent "check MyKB first, then write."
3. Next workshop: calendar, meetings, plugging a second agent.

**Personal line:** "This is the third iteration I've built. The first two weren't usable. This one is."

**Three-things callback:** "You walked through all three today. Write: you set it up and ingested. Read: the agent went and read cards. Use: the draft actually got better. That is the baseline. That is what we build from next time."

**Exit:** no stage Q&A. Materials go out via assistant on the internal network.

---

## Pre-stage checklist

- [ ] Bootstrap prompt on clipboard
- [ ] Fresh claude.ai Project or Claude Code session open
- [ ] Opus selected in Project Settings
- [ ] Mailbox authorized
- [ ] Test email from Mark in inbox
- [ ] Backup 10-sec clip on second tab
- [ ] Pre-run baseline folder ready to switch
- [ ] Water

*One-line self-reminder: the draft is not the point. The rhythm is.*
