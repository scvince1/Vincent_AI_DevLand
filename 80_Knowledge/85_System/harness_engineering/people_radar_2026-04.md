---
id: people_radar_2026-04
title: People Radar — Harness Engineering Field
tags: [harness, knowledge, people, practitioners, radar]
status: confirmed
last_modified: 2026-04-15
summary: 15位 harness engineering 领域关键人物追踪（10验证+5新增）
---
# People Radar: Harness Engineering Field

**Source:** P1 scout agent
**Date:** 2026-04-14
**Scope:** 15 tracked voices (10 validated + 5 additions) shaping the harness engineering discipline.

---

## Verified Core List (10)

| Person | Outlet | Focus | Why Track |
|---|---|---|---|
| Simon Willison | simonwillison.net | LLM CLI tooling, agent security | Most prolific public practitioner voice; daily posts |
| Hamel Husain | hamel.dev | Eval methodology, eval-driven dev | Field's leading evals practitioner |
| Eugene Yan | eugeneyan.com | LLM patterns, evals, RecSys × agents | Anthropic MTS; "LLM patterns" canonical |
| Jason Liu | jxnl.co | Context engineering for agentic RAG | Instructor (3M+ monthly DL); context-as-harness-layer leader |
| Omar Khattab | omarkhattab.com | DSPy, declarative LM programming | MIT CSAIL; dominant framework for programming-not-prompting agents |
| Harrison Chase | blog.langchain.com | Context engineering, long-horizon agents | LangChain CEO; coined "context engineering is the new AI moat" |
| Jerry Liu | llamaindex.ai/blog | Agentic document workflows, filesystem-first | LlamaIndex CEO |
| Andrej Karpathy | karpathy.ai | "Agentic engineering", Software 3.0 framing | Highest-reach public educator; shapes field vocabulary |
| Chip Huyen | huyenchip.com | Foundation model applications, tool selection, planning | "AI Engineering" = O'Reilly's #1 read book |
| Boris Cherny | Anthropic webinars / Pragmatic Engineer | Claude Code architecture | Built the most-used agentic coding harness in 2026 |

---

## Additions (5) -- Essential

### Ryan Lopopolo (OpenAI Frontier / Symphony)
- **The name-giver.** His Feb 2026 essay coined "harness engineering" and triggered field-wide conversation.
- Primary: https://openai.com/index/harness-engineering/ + https://www.latent.space/p/harness-eng (April 7 2026)
- Core claim: The discipline of building everything-except-the-model layer is now a first-class engineering specialty.
- Symphony case: 1M+ LOC, 0 human-written code, 0 human review pre-merge.

### swyx (Shawn Wang) -- Latent Space / AI Engineer
- **Co-host of the field's most influential podcast. Created the IMPACT framework** (Intent, Memory, Planning, Authority, Control Flow, Tools).
- Primary: https://www.latent.space/ + https://www.swyx.io/
- Core claim: "LLM + tools + loop" is too minimal; agents that ship need all 6 IMPACT components.
- Breakdown: https://www.morphllm.com/agent-engineering

### Shreya Shankar -- UC Berkeley / Parlance Labs
- **Co-creator (with Hamel) of the leading evals curriculum.** O'Reilly publishing "Evals for AI Engineers" Spring 2026.
- Primary: https://www.sh-reya.com/
- Research focus: LLM-as-judge alignment with human preferences; agent error analysis methodology.
- Co-authored FAQ: https://hamel.dev/blog/posts/evals-faq/ (Jan 15 2026)

### Birgitta Böckeler -- Thoughtworks / martinfowler.com
- **Most rigorous practitioner guide to harness engineering** (April 2 2026). Introduced guides-and-sensors taxonomy.
- Primary: https://martinfowler.com/articles/harness-engineering.html
- Earlier memo: https://martinfowler.com/articles/exploring-gen-ai/harness-engineering-memo.html (Feb 17 2026)
- Core claim: Harness = everything except the model; three layers: context (guides), constraints, garbage collection (sensors).

### Lilian Weng -- Thinking Machines Lab (ex-OpenAI VP Research)
- **Her 2023 "LLM Powered Autonomous Agents" post remains the most-cited practitioner reference for agent architecture.**
- Primary: https://lilianweng.github.io/ + Thinking Machines Lab
- Canonical post: https://lilianweng.github.io/posts/2023-06-23-agent/
- Current: Co-founded Thinking Machines Lab (with Mira Murati team). Research on test-time diffusion reasoning.

---

## Deprioritization Notes (no removals)

- **Eugene Yan** -- blog cadence slower in early 2026 (last confirmed post late 2025). Still canonical; just set lower alert frequency.
- **Boris Cherny** -- no personal blog/RSS. Follow via Anthropic webinars, Lenny's Newsletter, Pragmatic Engineer.

---

## Cross-Person Themes (this is gold)

### Theme 1: "Harness Engineering" as named discipline -- 2026 consensus
Lopopolo, Chase, Böckeler, Cherny, swyx all converged within weeks of each other. Lopopolo coined the term (Feb 2026); Böckeler gave it systematic taxonomy; Chase framed it as competitive moat; swyx gave it component framework (IMPACT).

### Theme 2: Context engineering as the harness's core discipline
Chase, Jason Liu, Karpathy all use "context engineering" as primary frame. Scope debate:
- Chase: orchestration-centric ("what info in right format reaches LLM at right time")
- Liu: tools-centric ("designing what agents see -- including tool responses, not just prompts")
- Karpathy: treats it as the new version of "programming" itself

### Theme 3: Eval is the missing discipline, not tools
Hamel, Shreya, Eugene Yan aligned: field is over-indexed on tools, under-indexed on measurement. Hamel's "Revenge of the Data Scientist" + Shankar's O'Reilly book are coordinated push to make eval first-class engineering practice.

### Theme 4: Active debate -- "keep it simple" vs "full IMPACT"
- **Simon Willison**: agent = "LLM that runs tools in a loop to achieve a goal" (minimalist)
- **swyx**: explicitly rejects this as "leaves out memory, planning, authority -- exactly what separates agents that ship from agents that demo"
- Ongoing as of March 2026.

### Theme 5: Filesystem as universal memory substrate
Jerry Liu + Boris Cherny independently converged: filesystem (not vector DB) is right primary memory abstraction for agents. Claude Code uses file-based conversation history; LlamaIndex analysis of coding agents points to same pattern.

### Theme 6: Model quality plateauing → harness quality becomes differentiator
Lopopolo, Chase, Cherny, Karpathy all echo same operational finding. Lopopolo: "models and harnesses become isomorphic to human capability for the job." Chase: "better models alone won't get your AI agent to production."

---

## Follow Strategy (Signal-to-Noise ratings)

| Person | Best Channel | S/N | Notes |
|---|---|---|---|
| Simon Willison | simonwillison.net RSS + Substack | ★★★★★ | Daily posts; highest-volume high-quality |
| Hamel Husain | hamel.dev RSS | ★★★★★ | Low volume, dense and actionable |
| Shreya Shankar | sh-reya.com + X @sh_reya | ★★★★☆ | Research cadence |
| Eugene Yan | eugeneyan.com RSS | ★★★★☆ | Slower in 2026 but canonical |
| Jason Liu | jxnl.co RSS + X @jxnlco | ★★★★☆ | Consistent RAG/context focus |
| Omar Khattab | X @lateinteraction + DSPy GitHub | ★★★☆☆ | Low social volume, high importance |
| Harrison Chase | LangChain blog + podcast appearances | ★★★★☆ | Sequoia/Latent Space appearances |
| Jerry Liu | LlamaIndex blog + X @jerryjliu0 | ★★★★☆ | X > blog for signal |
| Andrej Karpathy | X @karpathy + YouTube | ★★★★☆ | Low frequency, very high reach |
| Chip Huyen | huyenchip.com + X @chipro | ★★★★☆ | Book is primary asset |
| Boris Cherny | Anthropic webinars + Pragmatic Engineer | ★★★★☆ | No personal blog; journalist-curated |
| Ryan Lopopolo | OpenAI engineering + Latent Space | ★★★★★ | Single breakthrough so far; watch follow-ups |
| swyx | latent.space Substack + X @swyx | ★★★★★ | Community hub; must-subscribe |
| Birgitta Böckeler | martinfowler.com RSS | ★★★★☆ | Low volume, high rigor |
| Lilian Weng | Lil'Log RSS + Thinking Machines blog | ★★★★★ | Rare but field-defining |

---

## Key URLs (priority follows)

**Origin text of "harness engineering":**
- https://openai.com/index/harness-engineering/ (Lopopolo, Feb 2026)
- https://www.latent.space/p/harness-eng (Lopopolo podcast, Apr 7 2026)

**Most structured practitioner guide:**
- https://martinfowler.com/articles/harness-engineering.html (Böckeler, Apr 2 2026)

**Canonical component taxonomy:**
- https://lilianweng.github.io/posts/2023-06-23-agent/ (Weng, 2023 -- still referenced in 2026)

**IMPACT framework:**
- https://www.latent.space/p/agent (swyx)
- https://www.morphllm.com/agent-engineering (breakdown)

**Evals canonical FAQ:**
- https://hamel.dev/blog/posts/evals-faq/ (Husain + Shankar, Jan 15 2026)

**Context engineering thesis:**
- https://sequoiacap.com/podcast/context-engineering-our-way-to-long-horizon-agents-langchains-harrison-chase/ (Chase, early 2026)

**Simon Willison minimalist counter:**
- https://simonw.substack.com/p/i-think-agent-may-finally-have-a
