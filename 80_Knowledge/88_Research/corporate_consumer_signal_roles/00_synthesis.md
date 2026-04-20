# 00 Synthesis: Corporate Literacy + Challenge 5 Target User Recommendation

**Date:** 2026-04-17 (original); **Updated 2026-04-17 later same day** with SharkNinja-specific intel from `04_sharkninja_titles.md` and `05_sharkninja_people.md`.

**Key corrections from update:**
- Economic buyer changed from **Chief Growth Officer (Crossan-Matos)** to **Global Head of Media (Dave Kersey)**. CGO joined April 2025 and owns CX + growth, not Commerce Media. Commerce Media sits under Kersey.
- User-level title corrected from "Digital Shelf Manager" (industry term, not a SharkNinja title) to **Senior Manager, Ecommerce (Bailey Marquis-Wu pattern, Wayfair-pipeline)**.
- VP Commerce Media is an open role as of Feb 2026, tool can be positioned as "what the incoming VP owns on day one."

**Source reports:**
- `01_org_map.md` — organizational structure + ladders + reporting
- `02_day_in_life.md` — Mon-Fri reality of 8 consumer-signal roles
- `03_gap_analysis.md` — where the "hunch-without-tool" moment lives
- `04_sharkninja_titles.md` — SharkNinja's 36 confirmed title taxonomy + insider naming conventions
- `05_sharkninja_people.md` — 9 named individuals with LinkedIn + trade press citations

**This synthesis serves two purposes:** (1) corporate literacy Vincent can reuse for any future B2B/B2C product; (2) a concrete recommendation for who the Challenge 5 target user should be, with reasoning.

---

## Part 1: The Map (Corporate Literacy)

### Org shape at SharkNinja-scale consumer products companies

A ~$5B revenue consumer appliances/home/beauty company like SharkNinja has **eight functional groups** that touch consumer signal:

Marketing / Brand / Product / Consumer Insights / Customer Service (CX) / Quality & Safety / Comms-PR / Data-Analytics

At SharkNinja specifically, the C-suite is **federated** rather than consolidated:
- **Global CMO (Adam Petrick)** — brand and marketing
- **Shark Beauty CMO (Kleona Mack)** — beauty vertical, separate reporting
- **Chief Growth Officer (Michelle Crossan-Matos)** — owns CX + growth strategy (joined Apr 2025; does NOT own Commerce Media)
- **Global Head of Media (Dave Kersey)** — owns Commerce Media + global media CoE (joined 2025, ex-L'Oreal USA)
- **VP, Commerce Media** — retail media as standalone P&L ($250-350K exec-level); **OPEN as of Feb 2026**, reports to Dave Kersey

Implication: a consumer signal intelligence tool has **at least 3 distinct exec buyers**, not one CMO.

### The 8 signal-facing roles compressed

| Role | Signal They See | Power | Current Tool | Frustration |
|---|---|---|---|---|
| **Digital Shelf Manager** | Amazon reviews first | Low | Amazon Seller Central (no clustering) | Screenshots to Slack, no audit trail |
| **Brand Manager** | Retail share + social | Mid-high | Brandwatch, NielsenIQ (analyst-gated) | 24-48hr turnaround kills Thursday hunches |
| **Consumer Insights Analyst** | Qualtrics surveys, NPS | Low (advisor) | Qualtrics, SPSS | "Validate-the-bias" trap with leadership |
| **CX Manager** | 10K+ tickets/quarter | Mid (escalates) | Salesforce Agentforce | Routing tool, not clustering tool |
| **Social Media Manager** | TikTok/Reddit real-time | Low | Sprinklr, Brandwatch | No safety-escalation path |
| **Product Marketing Mgr** | Competitive reviews | Mid | Looker, Amazon Seller Central | Reactive, post-launch |
| **Marketing Data Analyst** | Attribution, ROAS | Low (service) | Tableau, SQL | Too technical for non-analysts |
| **Quality Engineer** | Return units + CPSC | Mid-high (stop-ship) | SAP, CPSC portal, bench + screwdriver | Delayed, formal-channels-only |

### The structural asymmetry (the single most important finding)

> **The role with the MOST signal has the LEAST power. The role with the MOST power has the LEAST signal.**

Digital Shelf Manager sees Amazon review spikes in Week 1 but can't decide to recall. Quality Engineer can decide to recall but sees signal filtered through 3-5 intermediate hands in Week 16+. Between them, CX Manager + Brand Manager + Community Manager each hold a slice of the same pattern with no shared view.

The signal doesn't die from malice or absence. It dies because the person who sees it has **no tool to make it legible** to the person with authority to act.

---

## Part 2: Challenge 5 Target User Recommendation

### Vincent's design constraints (from design session)

- **Low cost:** no license, no training
- **Low emotional cost:** no shame for being wrong, no report to own
- **Low operational cost:** no query writing, no schema reading
- **Not competing on feature**, competing on **timing in the cycle** (before formal questions form)
- Serves a **state** not a role: "I have a hunch but can't say it"

### Recommended user: Senior Manager, Ecommerce (Bailey Marquis-Wu pattern)

**Note on title:** "Digital Shelf Manager" is industry shorthand, not a SharkNinja title. The actual SharkNinja analog is **Senior Manager, Ecommerce** (Bailey Marquis-Wu) or **Manager, Retail Marketing and Ecommerce** (Emily Fagerstrom). Both came from Wayfair site merchandising. Your target user persona should match this pipeline: Wayfair site-merchandising alumna, ~$80-144K Manager band, hands-on digital shelf work.

**Why (ranked reasoning):**

1. **Highest frequency of the hunch state.** Every week she sees 5-15 new reviews that trigger "wait, is this a pattern?" Agent 3's ranking puts her at Rank 1 for this reason.

2. **Current workaround IS the unprofessional toy Vincent describes.** She screenshots Amazon reviews into Slack. Vincent's tool is the structured, audit-trailed, triangulated version of the move she already makes.

3. **Low-emotional-cost axis directly solves her dilemma.** Flagging false alarms wastes senior time; missing real patterns causes Foodi-level disasters. A tool that says "here's evidence, not opinion" lets her escalate without personal exposure.

4. **No competitor occupies this space.** Brandwatch/Qualtrics are analyst-gated (upstream). Amazon Seller Central is transactional (downstream). The "5-minute hunch check" space is structurally empty.

5. **Power dynamic amplifies value.** Low decision authority + high upstream visibility = tool makes her *more effective at her existing job*, not a redundant layer. She becomes the person who gives safety team a pre-packaged triangulated signal instead of a Slack screenshot.

### The specific moment (use-case vignette)

**Tuesday 2pm. Sarah, Senior Manager, Ecommerce (Ninja line), ex-Wayfair site merchandising.**

She's reviewing weekend review volume in Amazon Seller Central. Three new 1-star reviews mention "suction loss after 3 weeks." She's seen "suction loss" mentioned before, but she's also seen hundreds of one-off complaints that went nowhere. She doesn't want to send another Slack that ends with "let's keep monitoring."

She opens Vincent's tool. Types: **"Ninja cordless vacuum, suction"**. Tool returns in 8 seconds:
- 14 Amazon reviews mentioning suction in last 21 days (vs 2 in prior 21 days)
- 1 r/Cleaning thread, 87 upvotes, 24 comments, 6 confirmed similar experiences
- 3 CS tickets tagged "suction" this week (pulled from shared export)

She clicks "share cluster." Copies URL. Pastes into Slack with one line: "suction complaints jumped 7x in 3 weeks, cross-channel. Link has the evidence." Tags brand manager, CX manager, QE.

**The tool converts her hunch into a timestamped, shareable, triangulated signal without her writing a single query. That is the entire product.**

### Why not the alternatives

| Alternative user | Why it doesn't fit as well |
|---|---|
| **CX Manager** | Salesforce already does most of her reporting; new tool competes with existing workflow |
| **Brand Manager** | Too senior; hunches come from reports others bring her, not direct observation |
| **Social Media Manager** | Right signal, wrong mandate (reputation, not safety); problem is cultural, not tooling |
| **Product Safety Engineer** | Too downstream; by the time she has the hunch, signal already died upstream |
| **Consumer Insights Analyst** | She has professional tools and professional mandate; your toy is beneath her grade |

### Buyer vs user mapping (critical for pitch)

| Layer | Who (named) | What they care about |
|---|---|---|
| **User** | Senior Manager, Ecommerce (Bailey Marquis-Wu pattern; Wayfair-pipeline; $80-144K Manager band) | Time-to-verify hunch, low shame cost, shareable output |
| **Champion** | **Matt Dubow** (VP/GM eCommerce Amazon; ex-Reckitt digital shelf) | Reckitt-grade digital shelf maturity, brought in-house |
| **Economic buyer** | **Dave Kersey** (Global Head of Media; ex-L'Oreal USA) | Infrastructure that the incoming VP Commerce Media owns on day one |
| **Strategic endorser** | **Calvin Anderson** (SVP Global Digital Experience; publicly on-record about AI-era attention) | Early-warning layer for AI-era attention battle |
| **Stakeholder (not buyer)** | Michelle Crossan-Matos (CGO; ex-Ulta UB Media background) | Natural ally; CX-to-growth pipeline resonance |

**Pitch move:** frame the tool as "we accelerate the Week 1 to Week 16 gap that produces Foodi-scale recalls." That language lands at **Global Head of Media (Kersey) and the open VP Commerce Media slot**, with CGO as stakeholder endorser. The user-level value (Sarah's Tuesday 2pm) is the demo; the buyer-level value (5-week earlier safety investigation) is the business case.

---

## Part 3: Open decisions (back to Vincent)

Before writing the R4 redesign or touching code, four decisions to lock:

1. **Do you accept the Bailey Marquis-Wu pattern (Senior Manager, Ecommerce; Wayfair-pipeline background) as target user?** If yes, lock. If no, which alternative from the "why not" table, and why?
2. **Which SharkNinja product line anchors the demo?** Foodi (highest-stakes recall narrative) / Ninja vacuums (current-day relevant) / Shark outdoor (lower-stakes, exploration-friendly). Product choice shapes the data shape.
3. **MVP scope:** how many signal sources does the v1 cross? Amazon + Reddit only (2), or Amazon + Reddit + CS + TikTok (4)? More sources = more triangulation power but more engineering.
4. **Pitch register at Monday interview:** demo to the role (Sarah's Tuesday 2pm) or to the buyer (CGO-level recall-prevention story)? Or both, and in what order?

---

**This synthesis is a recommendation, not a decree.** The map exists independently of the recommendation. If you pick a different user, the map still works. If you redesign the product shape, the map still works. The corporate literacy is yours now regardless of what you build.

---

## Quick-reference back links

- [01_org_map.md](./01_org_map.md) — full org structure + ladders + C-suite map
- [02_day_in_life.md](./02_day_in_life.md) — all 8 roles' Monday-Friday texture
- [03_gap_analysis.md](./03_gap_analysis.md) — ranked roles + Foodi counterfactual + key finding
- [04_sharkninja_titles.md](./04_sharkninja_titles.md) — 36 confirmed SharkNinja titles + ladders + salary + insider naming conventions (Pure Players, Commerce Media)
- [05_sharkninja_people.md](./05_sharkninja_people.md) — 9 named individuals with LinkedIn + trade press citations + corrected pitch architecture
