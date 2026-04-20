# Signal Ops — UI Text Sketch v0.5

Reference: Challenge 5 产品 Spec v0.5 Part 4-5 + Part 14 at `spec_v0.5.md`
Target: 2-day hackathon agent team UI build handoff
v0.5 delta: Compare Builder (§12 新增) + Products Browse / Compare sub-tabs (§5 更新)

---

## 0. 整体框架

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Signal Ops          🔍 Search...          🔔 3   👤 Bailey ▼       │
├──────┬───────────────────────────────────────────────────────────────────┤
│      │                                                                   │
│ NAV  │                          MAIN CONTENT                             │
│      │                                                                   │
│      │                                                                   │
│      │                                                                   │
└──────┴───────────────────────────────────────────────────────────────────┘

左导航 200px / 顶栏 56px / 主内容 fluid max 1400px
```

### 左导航 tab 列表

| Icon | Name | Badge | Purpose |
|---|---|---|---|
| 📊 | Dashboard | — | 首页 (landing default) |
| 📥 | My Inbox | 8 | 个人 ticket queue |
| 🏢 | Team Queue | 32 | 全队 ticket 视图 |
| 📦 | Products | — | Category/SKU browser + Compare sub-view (v0.5) |
| 🔍 | Evidence | — | Raw review/thread search |
| 📝 | Narratives | — | Weekly/monthly narrative |
| 🌱 | Steward | — | Digest/Event/CEP/Query |
| ⚙️ | Admin | — | Settings (mostly stub) |

---

## 1. Dashboard (Page 1 — 首页)

```
┌──────┬────────────────────────────────────────────────────────────────────┐
│ NAV  │ ▲ 早安 Bailey。今日 Reddit 3 条新信号 / Amazon 2 个 rating 波动       │
│      │                                            [Today ▼] [Export ⤓]    │
│ 📊●  │ ┌──────────┬──────────┬──────────┬──────────┐                       │
│ 📥8  │ │ OPEN     │ OVERDUE  │ RESOLVED │ IMPACT   │                       │
│ 🏢32 │ │   8      │   1      │  12/wk   │ $24K     │                       │
│ 📦   │ └──────────┴──────────┴──────────┴──────────┘                       │
│ 🔍   │                                                                    │
│ 📝   │ ▼ 优先队列 (priority queue, AI triage)                               │
│ 🌱   │ ┌────────────────────────────────────────────────────────────────┐ │
│ ⚙️    │ │ 🔴 HIGH Ninja Creami 4-star drift → prescriptive ready │5d    │ │
│      │ │ 🟡 MED Shark NV360 shipping sentiment -18% this week │7d      │ │
│      │ │ 🟢 INSIGHT r/vacuums buzz +400% (Halo 预警)           │14d    │ │
│      │ │ 📘 STRATEGIC Mother's Day 3 周前 gift thread research  │21d    │ │
│      │ └────────────────────────────────────────────────────────────────┘ │
│      │                                                                    │
│      │ ┌──── Upcoming Event ────┬──── CEP Coverage Gap ────┐              │
│      │ │ Mother's Day: 3 weeks  │ "iced coffee" scene: 12% │              │
│      │ │ Gift thread research → │ Competitor avg: 34% ⚠️    │              │
│      │ │ [Generate Strategic ➜] │ [Dig into Reddit ➜]      │              │
│      │ └────────────────────────┴──────────────────────────┘              │
│      │                                                                    │
│      │ ▼ Team Pulse (demo-only, mocked)                                   │
│      │ Marcus: 5 assigned / Alex: 3 / Sam: 4 / You: 8                    │
│      │                                                                    │
│      │ ▼ 最近活动                                                          │
│      │ · Alex 关闭 "Ninja Blender 8-cup noise" (2 hr ago)                   │
│      │ · AI 新建 "Shark FLEX AZ1002 Reddit negative spike" (4 hr ago)      │
│      │ · Marcus 分派 "Creami 4-star" 给 Bailey (6 hr ago)                  │
│      │                                                                    │
└──────┴────────────────────────────────────────────────────────────────────┘
```

---

## 2. My Inbox (Page 2)

```
┌──────┬────────────────────────────────────────────────────────────────────┐
│ NAV  │ 📥 My Inbox (8 open)                 [List|Compact|Board] [+ New]  │
│      │                                                                    │
│ 📊   │ [All] [Opportunity 3] [Threat 2] [Insight 2] [Strategic 1]         │
│ 📥●  │ [🔴High 2] [🟡Med 4] [🟢Low 2]  [Amazon] [Reddit] [Both 5]         │
│ 🏢32 │                                                                    │
│ 📦   │ ┌───────────────────────────────────────────────────────────────┐ │
│ 🔍   │ │ 🔴 HIGH OPPORTUNITY · Due 5d · Amazon+Reddit                  │ │
│ 📝   │ │ Ninja Creami 4-star drift — 隔层难开 + 马达噪音                 │ │
│ 🌱   │ │ 👤 Bailey  🔗 12 reviews · 3 r/ice_cream threads              │ │
│ ⚙️    │ │ Prescriptive: 改隔层设计 + 减噪 → 预期 4.1★ / $24K monthly     │ │
│      │ │ ⏱ 2 hr ago by AI · 💬 1 comment                               │ │
│      │ └───────────────────────────────────────────────────────────────┘ │
│      │                                                                    │
│      │ ┌───────────────────────────────────────────────────────────────┐ │
│      │ │ 🟡 MED THREAT · Due 7d · Amazon                                │ │
│      │ │ Shark NV360 shipping sentiment -18% this week                 │ │
│      │ │ 👤 Bailey  🔗 28 reviews cluster                               │ │
│      │ │ Prescriptive: 检查 Fulfilled-by-Amazon warehouse / escalate    │ │
│      │ │ ⏱ Yesterday by AI                                             │ │
│      │ └───────────────────────────────────────────────────────────────┘ │
│      │                                                                    │
│      │ ┌───────────────────────────────────────────────────────────────┐ │
│      │ │ 🟢 LOW INSIGHT · Due 14d · Reddit                             │ │
│      │ │ r/vacuums +400% buzz — Halo 预警 Amazon review wave 2-3 wk later│ │
│      │ │ 👤 Bailey  🔗 14 threads, 3 subreddit spread                   │ │
│      │ │ Prescriptive: 深度 analyze thread content + 对比历史 Halo 样本 │ │
│      │ │ ⏱ 3 hr ago by AI                                              │ │
│      │ └───────────────────────────────────────────────────────────────┘ │
│      │                                                                    │
│      │ (...scrollable)                                                    │
└──────┴────────────────────────────────────────────────────────────────────┘
```

---

## 3. Team Queue (Page 3, demo-only)

```
┌──────┬────────────────────────────────────────────────────────────────────┐
│ NAV  │ 🏢 Team Queue (32 open)    Group:[Status ▼] [+ Bulk Assign]        │
│      │                                                                    │
│ 📊   │ ┌─── NEW (5) ────┬── TRIAGED (8) ──┬─ IN PROGRESS (14) ─┬ REVIEW(3)┐│
│ 📥   │ │ 🔴 Dyson launch│ 🟡 Bailey: Creami│ 🟢 Alex: NV360    │ 🟡 Sam:… ││
│ 🏢●  │ │ 🟡 r/shark 新帖│ 🟡 Bailey: NV360 │ 🔴 Alex: Creami   │ 🟢 Marcus││
│ 📦   │ │ 🟢 Stem cleaner│ 🟢 Sam: FLEX…   │ 🟡 Sam: blender   │           ││
│ 🔍   │ │ 🟢 Creami Gelato│ ...             │ ...              │           ││
│ 📝   │ │ 🟢 CEP gap    │                 │                   │           ││
│ 🌱   │ └────────────────┴──────────────────┴───────────────────┴──────────┘│
│ ⚙️    │                                                                    │
│      │ ▼ Workload (demo mock)                                              │
│      │ ┌──────────┬──────┬───────────────────┐                             │
│      │ │ Member   │ Open │ Avg Resolution    │                             │
│      │ │ Bailey   │  8   │ 4.2 days          │                             │
│      │ │ Alex     │  3   │ 3.8 days          │                             │
│      │ │ Sam      │  4   │ 5.1 days          │                             │
│      │ │ Marcus L │  1   │ 2.5 days          │                             │
│      │ └──────────┴──────┴───────────────────┘                             │
│      │                                                                    │
│      │ Drag ticket to a member avatar to assign. (demo only: local state) │
└──────┴────────────────────────────────────────────────────────────────────┘
```

---

## 4. Ticket Detail (Modal / Pinned Right Panel)

```
┌─── Ticket #T-1024 ──────────────────────────────────────[×]────┐
│                                                                │
│ 🔴 HIGH · OPPORTUNITY · Due 2026-04-22 · Amazon+Reddit         │
│ Ninja Creami 4-star drift — 隔层难开 + 马达噪音                 │
│ 👤 Owner: Bailey  Status: [In Progress ▼]  [Mark Review]       │
│                                                                │
│ [Overview] [Evidence 15] [Activity 3] [Related 2]              │
│ ──────────────────────────────────────────────────────────────│
│                                                                │
│ ▼ AI Summary (editable)                                        │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Creami 4★ 占比从 32% 升至 41% 过去 14 天。集中抱怨: (1) 隔层难 │ │
│ │ 开 (占 68% of 4★ 负评); (2) 马达声音大 (占 52%)。Reddit r/Ice- │ │
│ │ Cream 同期 3 thread 提同样问题。说明已非偶发。                  │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                │
│ ▼ Prescriptive Action (editable)                               │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ 1. 工程评估隔层开启力 (目标 ≤ 2.3 N)                         │ │
│ │ 2. 材料组评估噪音降低可行性                                    │ │
│ │ 3. PDP 前置回答 "如何打开隔层" + video demo                   │ │
│ │ 4. 客服话术 update                                          │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                │
│ ▼ Expected Impact                                              │
│ Rating 4.0 → 4.1 (14 days) · Monthly sales +$24K · Confidence 高│
│                                                                │
│ 🏷 Tags: creami | kitchen | 4-star-mitigation | Q2-2026         │
│                                                                │
│ [Save Changes] [Mark Review] [Close with Notes]                │
└────────────────────────────────────────────────────────────────┘
```

---

## 5. Products (Page 4, v0.5 分为 Browse + Compare 两 sub-tab)

顶部 sub-tab: `[Browse ●] [Compare]`

Browse = 以下 v0.4 原 Products 内容 (category tree + product detail).
Compare = v0.5 新增 Cross-entity Comparison Builder, 详见 §12.

### 5.1 Browse sub-tab

```
┌──────┬────────────────────────────────────────────────────────────────────┐
│ NAV  │ 📦 Products  [Browse ●] [Compare]  > Shark > Vacuum  [Search…]     │
│      │                                                                    │
│ 📊   │ ┌── Categories ─────┬─── Ninja Creami NC501 ─────────────────────┐ │
│ 📥   │ │ ▸ Ninja            │ Health Score: 74 / 100 (-3 this week)      │ │
│ 🏢   │ │   ▸ Blender        │ Star: 4.0 (14d ago: 4.2)                   │ │
│ 📦●  │ │   ▸ Creami         │ Review vol: 842 (30d) · Reddit mention: 38 │ │
│ 🔍   │ │     · NC501 ●     │                                            │ │
│ 📝   │ │     · NC299       │ ▼ Aspect Sentiment (Volume × Sentiment)     │ │
│ 🌱   │ │     · NC301       │    ┌────────────────────────────┐          │ │
│ ⚙️    │ │   ▸ Coffee        │    │  Flavor ●                  │          │ │
│      │ │ ▸ Shark           │    │ Noise ●                    │          │ │
│      │ │                    │    │  Lid  ○                    │          │ │
│      │ │                    │    │ Price      ●               │          │ │
│      │ │                    │    │ Cleaning  ○                │          │ │
│      │ │                    │    └────────────────────────────┘          │ │
│      │ │                    │    ●=positive  ○=negative                 │ │
│      │ │                    │                                            │ │
│      │ │                    │ ▼ Related Tickets (3 open)                 │ │
│      │ │                    │ · 🔴 4-star drift (T-1024)                 │ │
│      │ │                    │ · 🟡 Reddit r/ice_cream buzz (T-1031)      │ │
│      │ │                    │ · 🟢 Q&A gap: "how to clean pint" (T-1018) │ │
│      │ └────────────────────┴────────────────────────────────────────────┘ │
└──────┴────────────────────────────────────────────────────────────────────┘
```

---

## 6. Evidence Browser (Page 5)

```
┌──────┬────────────────────────────────────────────────────────────────────┐
│ NAV  │ 🔍 Evidence   [Amazon] [Reddit] [Both ●]  Product: Creami NC501    │
│      │                                                                    │
│ 📊   │ Date: [Last 30d ▼]  Sort: [Impact ▼]                [+ Create Tkt] │
│ 📥   │                                                                    │
│ 🏢   │ ┌───────────────────────────────────────────────────────────────┐ │
│ 📦   │ │ ⭐️3 Amazon · 2026-04-15 · verified · 👍24                      │ │
│ 🔍●  │ │ "The lid is impossible to open after freezing. My partner…"   │ │
│ 📝   │ │ CRP: 时:新购7d · 关:couple · 场:daily-kitchen · 决:使用中          │ │
│ 🌱   │ │ 标签: lid-opening, post-freeze, ergonomic                       │ │
│ ⚙️    │ │ [→ Create Ticket] [Add to T-1024]                             │ │
│      │ └───────────────────────────────────────────────────────────────┘ │
│      │                                                                    │
│      │ ┌───────────────────────────────────────────────────────────────┐ │
│      │ │ 🔶 Reddit r/icecream · 2026-04-12 · 👆47 ⬇3                   │ │
│      │ │ "Thinking of buying Creami vs Cuisinart ICE-30. Pros and…"   │ │
│      │ │ CRP: 时:purchase-consideration · 关:self · 场:home-occasional   │ │
│      │ │      · 决:pre-purchase (switcher: Cuisinart owner)             │ │
│      │ │ 28 comments: 68% recommend Creami · aspects discussed:         │ │
│      │ │   flavor, texture, cleaning, noise                            │ │
│      │ │ [→ View thread] [+ Create Ticket]                              │ │
│      │ └───────────────────────────────────────────────────────────────┘ │
└──────┴────────────────────────────────────────────────────────────────────┘
```

---

## 7. Narratives (Page 6)

```
┌──────┬────────────────────────────────────────────────────────────────────┐
│ NAV  │ 📝 Narratives     [Weekly] [Monthly] [Quarterly] [Event]           │
│      │                                                                    │
│ 📊   │ ▼ Drafts                                                           │
│ 📥   │ · [EDIT] 2026-04-12 week — "SharkNinja Consumer Consciousness"    │
│ 🏢   │ · [GENERATE] 2026-04-05 week (auto draft available)               │
│ 📦   │ · [GENERATE] Mother's Day prep (3 weeks out)                      │
│ 🔍   │ · [SCHEDULED] 2026-Q1 quarterly (due week of 2026-04-26)          │
│ 📝●  │                                                                    │
│ 🌱   │ ▼ Active Editor: "Week of 2026-04-12"                              │
│ ⚙️    │ ┌───────────────────────────────────────────────────────────────┐ │
│      │ │ [AI] Last week SharkNinja 的 consumer pulse 呈现 3 大 pattern:  │ │
│      │ │ 首先, Creami 4★ drift (T-1024) 源于隔层设计 + 噪音, 为 Q2 优先.  │ │
│      │ │ Prescriptive action 已启动 (PDP 改 + 工程评估). [edit]          │ │
│      │ │                                                                │ │
│      │ │ 第二, r/vacuums 出现 Shark NV360 的 Halo 预警 (T-1031). 根据历 │ │
│      │ │ 史 pattern, 我们预计 Amazon review wave 将于 2-3 周后到达. [edit]│ │
│      │ │                                                                │ │
│      │ │ 第三, Mother's Day 3 周前, CEP coverage 在 "iced coffee" 场景仍 │ │
│      │ │ 低于竞品均值 (12% vs 34%). 建议 Q2 content calendar 加强此场景.│ │
│      │ └───────────────────────────────────────────────────────────────┘ │
│      │                                                                    │
│      │ [Regenerate Section] [Export PPT] [Export Email] [Share to Slack] │
└──────┴────────────────────────────────────────────────────────────────────┘
```

---

## 8. Steward — Daily Digest (Page 7, default sub-tab)

```
┌──────┬────────────────────────────────────────────────────────────────────┐
│ NAV  │ 🌱 Steward    [Daily Digest ●] [Event Lens] [CEP Map] [Curiosity]  │
│      │                                                                    │
│ 📊   │ ▼ Today's Digest (2026-04-17, 昨夜 + 周末)                          │
│ 📥   │                                                                    │
│ 🏢   │ 1. Amazon top 3 notable reviews                                    │
│ 📦   │    · Creami new 1★ "broke after 3 uses" (likely Q1 defect batch)  │
│ 🔍   │    · Shark FLEX positive 5★ streak +23% this week                 │
│ 📝   │    · Ninja blender recipe 新提及 "smoothie bowl" uptick           │
│ 🌱●  │                                                                    │
│ ⚙️    │ 2. Reddit 周末 buzz                                                │
│      │    · r/vacuums 22 new threads (Shark mentioned 12x, 8 positive)   │
│      │    · r/ice_cream Creami thread 3 new, sentiment neutral           │
│      │    · r/BuyItForLife cross-sub migration Ninja blender +15%        │
│      │                                                                    │
│      │ 3. Competitor launch 预告                                           │
│      │    · Cuisinart ICE-70 launching 2026-05-01 (Amazon 已预告)         │
│      │                                                                    │
│      │ 4. Emerging CEP signal                                              │
│      │    · "road trip" + blender 场景在 r/roadtrip 讨论上升 (弱信号)     │
│      │                                                                    │
│      │ [Convert All to Tickets] [Dismiss Individual] [Save for Later]    │
└──────┴────────────────────────────────────────────────────────────────────┘
```

### 8a. Event Lens sub-tab

```
▼ Event Lens — Mother's Day 2026-05-11 (3 weeks out)
Historical performance:
  2024: 4.1★ avg across gift-positioned SKUs
  2025: 4.0★ — dip from noise aspect
Reddit gift thread patterns:
  r/gifts: Ninja blender mentioned 12x in last year (rank #7)
  r/AskMen: coffee maker gifts 34% mention of brand
Recommended focus SKUs:
  - Ninja CM401 (gift-heavy)
  - Creami NC501
Content angle ideas:
  - "Gift that lasts: 2-year follow-up reviews"
  - "For the coffee dad" angle (r/AskMen signal)
[Generate Strategic Ticket] [Export Brief to Brand Team]
```

### 8b. CEP Coverage Map sub-tab

```
▼ CEP Coverage — Ninja Blender Category
Competitor baseline:
  "smoothie morning"  SharkNinja: 42%  Cuisinart: 38%  Vitamix: 51%  ✓
  "baby food prep"    SharkNinja: 15%  Cuisinart: 22%  Vitamix: 28%  ⚠️
  "iced coffee"       SharkNinja: 12%  Cuisinart: 34%  Vitamix: 19%  ⚠️
  "cocktail party"    SharkNinja: 28%  Cuisinart: 32%  Vitamix: 18%  ✓
  "protein shake"     SharkNinja: 48%  Cuisinart: 22%  Vitamix: 41%  🏆
Gaps:
  - "baby food": 落后 7-13 pts
  - "iced coffee": 落后 22 pts (最大 gap)
[Create Strategic Ticket: Iced coffee CEP campaign]
```

---

## 9. Admin (Page 8, mostly stub)

```
┌──────┬────────────────────────────────────────────────────────────────────┐
│ NAV  │ ⚙️ Admin   [Team] [Signal Rules] [Data Sources] [Integrations]     │
│      │                                                                    │
│ ...  │ ▼ Integrations (all stub)                                          │
│ ⚙️●   │ ┌──────────┬────────────────┬────────────┐                        │
│      │ │ Jira     │ Disabled       │ [Connect]  │ (Coming soon)          │
│      │ │ Salesforce│ Disabled       │ [Connect]  │ (Coming soon)          │
│      │ │ Slack    │ Disabled       │ [Connect]  │ (Coming soon)          │
│      │ │ Qualtrics│ Disabled       │ [Connect]  │ (Coming soon)          │
│      │ │ Asana    │ Disabled       │ [Connect]  │ (Coming soon)          │
│      │ └──────────┴────────────────┴────────────┘                        │
│      │                                                                    │
│      │ ▼ Data Sources                                                     │
│      │ Amazon ASINs tracked: 23 (Creami, Shark Vac, Ninja Blender…)      │
│      │ Reddit subreddits: r/vacuums, r/ice_cream, r/BuyItForLife…        │
│      │ [+ Add ASIN] [+ Add Subreddit]                                    │
│      │                                                                    │
│      │ ▼ Signal Rules (simplified UI)                                     │
│      │ · Star drift > 0.2 / 7d → Threat ticket                           │
│      │ · Review volume +2σ → Insight ticket                              │
│      │ · Reddit thread +3σ → Insight ticket                              │
│      │ · Halo correlation > 0.6 → Insight ticket                         │
│      │ [+ Add Rule] [Edit existing]                                      │
└──────┴────────────────────────────────────────────────────────────────────┘
```

---

## 10. Color & Component Key

**Severity / Ticket Type:**
- 🔴 High severity (#DC2626) — also Threat ticket
- 🟡 Medium severity (#EAB308) — also Insight ticket
- 🟢 Low severity (#22C55E) — also Opportunity ticket
- 📘 Strategic ticket (Blue)
- ❓ Question ticket (Gray)

**Data source:**
- 🟧 Amazon evidence
- 🔶 Reddit evidence
- ⭐️ star rating (Amazon)
- 👆 upvotes (Reddit)

**Sentiment dots:**
- ● positive
- ○ negative
- ◐ neutral/mixed

**Status arrows/indicators:**
- ● active nav tab
- ▼ expandable section
- ▸ tree-node collapsed
- ➜ call-to-action

---

## 11. Development Handoff 要点

**Frontend agents 用此 sketch 作为 layout 参考:**
- 左导航 固定 200px, 不 collapse (MVP)
- 顶栏固定 56px
- 主内容 max-width 1400px, 居中
- Card 设计: border-radius 8px, 左侧 4px color strip = severity
- Typography: Inter/SF Pro 半粗 heading / 13-14px body
- Density 参考 Linear (info-dense 但不 cluttered)

**Interactions to implement (MVP):**
- Left nav 切换页面
- Ticket card click → open detail modal
- Ticket detail "Save" / "Mark Review" / "Close"
- Filter chips toggle
- Product tree 展开/收起
- Evidence list 分页 / scroll
- Narrative editor inline edit
- Steward tab 切换

**Stub (demo-only):**
- Team Queue drag-drop → local state, no persistence
- Admin Integrations → all "Coming soon"
- NL Query → pre-canned responses for 3-5 demo queries

---

---

## 12. Compare Builder (v0.5 新增)

Location: Products tab 的 `[Compare]` sub-tab.

### 12.1 主视图 (同品类, 3 列 SKU/Line 比较)

```
┌──────┬────────────────────────────────────────────────────────────────────┐
│ NAV  │ 📦 Products  [Browse] [Compare ●]        [+ New Group] [Save ▼]    │
│      │                                                                    │
│ 📊   │ Watched Group: [Navigator vs Dyson V family ▼] [Rename] [Delete]  │
│ 📥   │                                                                    │
│ 🏢   │ ┌── Col 1 ──────┬── Col 2 ──────┬── Col 3 ──────┬── [+ Add col] ┐ │
│ 📦●  │ │ [SKU ▼]       │ [SKU ▼]       │ [Line ▼]      │               │ │
│ 🔍   │ │ Shark NV360   │ Dyson V8      │ Dyson V line  │               │ │
│ 📝   │ │ Mid-tier      │ High-tier     │ High-tier     │               │ │
│ 🌱   │ │ Category:     │ Category:     │ Category:     │               │ │
│ ⚙️    │ │  Vacuum       │  Vacuum       │  Vacuum       │               │ │
│      │ └───────────────┴───────────────┴───────────────┴───────────────┘ │
│      │                                                                    │
│      │ ▼ Category Aspect Radar (Vacuum, 8 轴 AI mining + admin approved)  │
│      │ ┌──────────────────────────────────────────────────────────────┐ │
│      │ │              Suction                                         │ │
│      │ │        ⬤       ◆      ◇                                       │ │
│      │ │   Battery          Dust-Bin                                  │ │
│      │ │      ⬤       ◆  ◇                                             │ │
│      │ │  Weight                    Attachments                      │ │
│      │ │                                                              │ │
│      │ │   Noise                        Maneuverability              │ │
│      │ │             Durability                                       │ │
│      │ │                                                              │ │
│      │ │ ⬤ NV360   ◆ V8   ◇ V line (review-weighted aggregate)        │ │
│      │ └──────────────────────────────────────────────────────────────┘ │
│      │                                                                    │
│      │ ▼ Brand Aspect Radar (全品类通用, 8 轴, 仅 Brand-level 列 render)  │
│      │ (当前 3 列均 SKU / Line 级, 无 Brand-level, 此 radar 隐藏)          │
│      │                                                                    │
│      │ ▼ Spec Table                                                       │
│      │ ┌──────────────┬──────────┬──────────┬────────────┐                │
│      │ │ Field        │ NV360    │ V8       │ V line     │                │
│      │ ├──────────────┼──────────┼──────────┼────────────┤                │
│      │ │ Price        │ $229     │ $349     │ $299-749   │                │
│      │ │ Rating       │ 4.4      │ 4.3      │ 4.4 (agg)  │                │
│      │ │ Review vol   │ 1,200    │ 3,400    │ 12,800     │                │
│      │ │ Reddit (30d) │ 84       │ 210      │ 520        │                │
│      │ │ Top 3 +      │ 力强/轻量/│ 电池/做工/│ 整体/做工/  │                │
│      │ │              │ 耐用      │ 吸力     │ 耐用       │                │
│      │ │ Top 3 -      │ 电池/噪音/│ 价贵/重/  │ 价贵/配件难/ │                │
│      │ │              │ 配件少    │ 发热     │ 噪音       │                │
│      │ └──────────────┴──────────┴──────────┴────────────┘                │
│      │                                                                    │
│      │ ▼ AI Gap Analysis (Hybrid: 系统 flag, user 审批产 ticket)            │
│      │ 发现 2 个值得 investigate 的 gap:                                     │
│      │ · NV360 Battery 低于 V8 (−32%)               [Create Insight Tkt]  │
│      │ · NV360 Attachments 低于 V line agg (−18%)   [Create Insight Tkt]  │
│      │                                                                    │
└──────┴────────────────────────────────────────────────────────────────────┘
```

### 12.2 混粒度自动拆两 radar 同屏

User 同时选 Brand-level 列 (e.g., "Shark 整体") + SKU-level 列 (e.g., "Dyson V8"):

```
▼ Brand Aspect Radar (全品类通用, 8 轴, 接收 brand-level 列)
 ⬤ Shark 品牌整体 contour

▼ Category Aspect Radar (Vacuum, 8 轴, 接收 SKU / Line / Brand-in-Category / Category agg)
 ◆ Dyson V8 contour

[inline notice, dismissible]
 "列粒度不一致, 已自动拆两 radar 分别 render. (符合 Rule X)"
 [Dismiss]
```

### 12.3 跨品类同列 warn (Category Radar 退化)

User 在同一 Compare 混入跨品类 (Creami blender + Navigator vacuum):

```
▼ Brand Aspect Radar (可 render, 轴全品类通用)
 ⬤ Ninja 整体 overlay ◆ Shark 整体

▼ Category Aspect Radar:
 [inline notice, dismissible]
 "列跨品类, Category Radar 已退化为仅 Brand Radar.
  可按品类分组重比."
 [Dismiss]
```

### 12.4 列 picker 微观

每列顶部 picker:

```
┌── Col X ─────────────┐
│ 粒度: [SKU ▼]         │ ← 粒度 chip 切: Brand / Category / Line / SKU
│ 搜索: [ Shark N...▼ ] │ ← typeahead search
│                       │
│ Tier filter:          │
│ [All ▼] / [Mid-tier]  │
│                       │
│ ─── 选中 ───          │
│ Shark NV360           │
│ (Mid-tier, Vacuum)    │
│ [×] 移除               │
└───────────────────────┘
```

### 12.5 Ticket 双向 tie-in

Ticket detail 增 `[View in Compare]` 按钮, Related tab 加 Related Comparisons, Evidence tab 加 Linked Comparison Snapshot:

```
┌─── Ticket #T-1024 ──────────────────────────────────────[×]────┐
│ 🔴 HIGH · OPPORTUNITY · Due 2026-04-22 · Amazon+Reddit         │
│ Ninja Creami 4-star drift — 隔层难开 + 马达噪音                 │
│ 👤 Owner: Bailey  Status: [In Progress ▼]                      │
│ [Mark Review] [View in Compare] [Close with Notes]             │
│                                                                │
│ [Overview] [Evidence 15] [Activity 3] [Related 2]              │
│                                                                │
│ (Related tab 新增一栏:)                                         │
│ ▼ Related Comparisons (1)                                      │
│ · 📊 Creami vs competitors (2026-04-16 snapshot) [View] [↗]    │
│                                                                │
│ (Evidence tab 新增一类:)                                        │
│ ▼ Linked Comparison Snapshot                                   │
│   (embedded small radar + table 静态图, click → View in Compare)│
└────────────────────────────────────────────────────────────────┘
```

`[View in Compare]` 点击 → 跳 Products → Compare sub-view, 预填当前 ticket 相关 product 为 Col 1, 补 user 之前 Watched Group 或 default competitor 为 Col 2+.

### 12.6 Gap → Insight Ticket 预填 (Hybrid flow)

Compare 里某 gap 点 `[Create Insight Ticket]`:

```
┌─── New Insight Ticket (from Compare) ──────────────────[×]────┐
│ AI 已预填, 请审核 + Save.                                       │
│                                                                │
│ Type: 🟡 Insight  Severity: [Low ▼]  Due: [14 days ▼]          │
│ Title: Shark NV360 Battery 低于 Dyson V8 (−32%) [edit]         │
│                                                                │
│ Summary:                                                       │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Cross-entity Comparison 显示 Shark NV360 在 Battery 维度    │ │
│ │ review-weighted aspect score 显著落后 Dyson V8 (对标列).    │ │
│ │ 用户抱怨集中 charging 时长 + 持续力. 建议 deeper dive.       │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                │
│ Evidence:                                                      │
│ · Comparison Snapshot (2026-04-18, NV360 vs V8 vs V line)     │
│ · [+ Add Evidence] (pull Amazon review cluster)                │
│                                                                │
│ Prescriptive Action (AI 初稿, editable):                       │
│ 1. Pull recent NV360 Battery 负评 cluster                      │
│ 2. 跟工程组询 battery supplier roadmap                          │
│ 3. Amazon Q&A 主动答 battery 相关 3 问题                        │
│                                                                │
│ [Save as New] [Cancel]                                         │
└────────────────────────────────────────────────────────────────┘
```

### 12.7 Watched Competitor Group 管理

顶部 Group selector + action buttons:

```
┌─────────────────────────────────────────────────┐
│ Watched Group: [Navigator vs Dyson V family ▼] │
│                                                 │
│ Group list (dropdown):                          │
│ · Navigator vs Dyson V family (current ●)      │
│ · Creami vs Cuisinart vs Breville              │
│ · Blender heavy-duty comparison                │
│ · [+ New Empty Group]                          │
│                                                 │
│ Group actions:                                  │
│ [Rename] [Delete] [Duplicate] [Save as New]    │
└─────────────────────────────────────────────────┘
```

Equivalence 纯 user 手选 (v0.5 不做 AI auto-suggest / Reddit "I switched" 提取).
权限: 所有用户同权限 (v0.5 UI stub).

---

## 13. v0.5 Color & Component 补充

**Compare view 特有:**
- Radar contour 样式: Col 1 实心圆 ⬤ / Col 2 实心菱 ◆ / Col 3 空心菱 ◇ / Col 4+ 色阶差
- Radar 底色 grid: #E5E7EB (slate-200)
- Gap 提示 chip: 🟠 Amber background (注意, 非 alarm)
- Inline notice: 柔和 info 色 (#DBEAFE bg + #1E40AF text), dismissible

---

# End of UI Sketch v0.5
