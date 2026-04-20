# Signal Ops — Challenge 5 Product Spec v0.4

**Product Codename:** Signal Ops
**Positioning:** Linear for consumer insight / PagerDuty for brand health
**Data boundary:** Amazon + Reddit public scraping only
**Target delivery:** 2-day live hackathon demo, agent team joint dev handoff-ready
**Generated:** 2026-04-17

---

## Part 1. 产品定位与市场

### 1.1 一句话定位

**Signal Ops** = Amazon + Reddit consumer signal → AI auto-generated ticket queue → team workflow → closed-loop prescriptive action. 给 CPG 品牌 E-commerce / Brand / CI 团队的 daily ops 产品.

### 1.2 三句话 pitch

SharkNinja 每天有 10,000+ 条 Amazon review + Reddit thread 流过, Bailey 式 Senior Manager 靠截图 + Slack 传 signal. Signal Ops 把每条可行动的 signal 转成 AI-drafted ticket (带 evidence + 预期 impact + prescriptive action), Team Lead 分派, Owner 执行, 系统 track 到 Amazon rating 恢复 auto-close. 季末产出 "我们 catch 了 N 个 signal → resolve 了 M 个 → ROI \$X" 的量化交付. Revuze 只出 dashboard + alerts 没有 closed loop; Jira / Linear 纯手工 entry 不 data-driven; PagerDuty 只管 crisis 不管 opportunity. 白空间属于我们.

### 1.3 市场 positioning 九宫格

| 产品 | Data-driven auto ticket | Closed-loop tracking | Opportunity+Threat+Strategic 全型 | Consumer insight domain | Reddit 覆盖 | AI prose narrative |
|---|---|---|---|---|---|---|
| Revuze | ✗ | ✗ | ✗ (只 alerts) | ✓ | ✗ | ✗ (Capterra 吐槽) |
| Jira / Linear | ✗ (人工) | ✓ | ✓ | ✗ | ✗ | ✗ |
| PagerDuty | ✓ (incident) | ✓ | ✗ (只 threat) | ✗ | ✗ | ✗ |
| Zendesk | ✓ (customer-initiated) | ✓ | ✗ | 部分 | ✗ | ✗ |
| Vibe Kanban | ✓ (AI agent) | ✓ | 部分 | ✗ (dev 域) | ✗ | 部分 |
| **Signal Ops (我们)** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### 1.4 vs Revuze 深度差异

- **Reddit**: Revuze 硬缺席; Signal Ops 核心数据源
- **Ticket workflow**: Revuze 无; Signal Ops 核心
- **AI prose narrative**: Capterra 验证 Revuze 5 年缺失; Signal Ops 填补
- **Halo effect 时滞**: Revuze 需跨平台 API; Signal Ops 仅 scrape 即可
- **Say-do gap 叙事**: Revuze 盲区; Signal Ops 核心叙事
- **UI 透明度**: Revuze 锁 demo 后; Signal Ops live demo
- **Amazon ↔ Reddit stitching**: Revuze 三 Hub 割裂; Signal Ops 双源融合
- **Predictive What-If**: Revuze 弱 (外推); Signal Ops 模拟改动后预期 trajectory
- **Scheduled report + smart alert with prescriptive**: Revuze 无; Signal Ops 有

### 1.5 vs SharkNinja 现工具栈 (不替换, 补位层)

- **Qualtrics XM Discover**: 他们 post-purchase CSAT/NPS/CC 对话. 我们 pre-purchase + public 3rd-party (Amazon + Reddit). 互补不冲突.
- **Salesforce + Agentforce**: 他们 1st-party CRM 中枢. 我们 3rd-party 公开信号. 完全不 overlap.
- **Analytic Partners GPS Enterprise**: 他们 \$7 亿广告 MMM 优化. 我们不做投放 ROI 归因, 做产品/品牌 signal. 互补.
- **Internal Brandwatch / Sprinklr (若有)**: 他们多平台 + Boolean 门槛. 我们 Amazon + Reddit 深 + baby-friendly NL query. 互补.

### 1.6 白空间一句话

**Consumer-signal-driven auto-generated tickets with prescriptive action + team workflow + closed-loop tracking** = 市场唯一.

---

## Part 2. 服务人群 & 权限

### 2.1 3-layer user structure

**Layer A: Team Lead (Director+ 级)**
- Role: Director of E-commerce / VP of Brand / Senior Director CI
- Daily actions: triage new tickets queue / assign to members / review metrics / approve Mark weekly narrative
- Session rhythm: 早上看 Team Queue 15-30 mins / 周一 standup / 周五 narrative review
- Pain point solved: 之前靠 Slack 催人, 现在 assignment + SLA 可 track

**Layer B: Team Members (Bailey pattern + peers + 下属)**
- Role: Senior Manager E-commerce / Brand Manager / CI Analyst / E-comm Associate
- Daily actions: work my inbox / 打开 ticket evidence 看 review/thread / 写 prescriptive action / @mention 协作 / 标记 close
- Session rhythm: 早上 inbox 30 mins / 下午 2 小时 drill-down + action writing / 周五 narrative contribution
- Pain point solved: 之前每条 signal 从 discovery 到 action 自己全 stack, 现在 AI drafted 一半, 她只需 validate + refine

**Layer C: Sponsor (CMO / Mark Barrocas 办公室)**
- Role: CMO / CEO / VP Marketing
- NOT daily user
- Weekly: 收 team weekly narrative email (Bailey + Team Lead 综合)
- Monthly: 看 quarterly KPI dashboard (opened / resolved / impact \$)
- Quarterly: 看 ROI-attributable 叙事报告

### 2.2 Persona 卡

**Bailey Marquis-Wu (anchor Persona)**
- Senior Manager E-commerce, CPG 品类 3 年经验
- 每日工作: Amazon review 扫 + 竞品监测 + Reddit 搜自家/竞品讨论 + 给 Director 周报
- Tech literacy: baby-friendly LLM 用户 (不是 prompt engineer), Excel 熟练, 看过 Looker/Tableau 但不会建
- 权限现状: 没有 Qualtrics API 权限 / 没有 Salesforce admin / Reddit 是 personal account
- Signal Ops 期望: 替她做"扫"这步, 让她做"决策 + action"

**Marcus Chen (Team Lead Persona)**
- Director E-commerce, 负责 10-15 人 team
- 每日工作: review team progress / align with VP / cross-functional meeting / prioritize backlog
- Signal Ops 期望: Team Queue 一眼知 workload + 热点 / AI 帮 severity 排序 / assignment 不需纠结

**Nora Patel (Sponsor Persona)**
- CMO's Chief of Staff
- 只在周报 / 季报场景接触 Signal Ops 输出
- 期望: coherent narrative + specific action taken + measurable impact

### 2.3 权限 matrix

| Action | Team Lead | Team Member | Sponsor |
|---|---|---|---|
| View Team Queue | ✓ | ✓ | ✗ (只看 narrative) |
| View My Inbox | ✓ (所有人的) | ✓ (自己的) | ✗ |
| Create ticket manually | ✓ | ✓ | ✗ |
| AI auto-create ticket | ✓ (system) | ✓ (system) | ✗ |
| Assign ticket | ✓ | ✗ (只能自 claim) | ✗ |
| Edit ticket content | ✓ | ✓ (自己的 + watched) | ✗ |
| Change severity | ✓ | Request only | ✗ |
| Close ticket | ✓ | ✓ (owner 或 watcher) | ✗ |
| Export narrative | ✓ | ✓ | ✓ (只读 email) |
| Configure integrations | ✓ | ✗ | ✗ |
| Modify signal rules | ✓ | Request only | ✗ |

注: **团队协作 = demo-only**. 实际 2 天构建:
- Permission matrix 以 UI 状态展示 (按钮 enabled/disabled)
- Assignment drag-drop 是 visual 演示, persist 到 local state
- Team members 列表是 mock 数据
- 后端 stub API endpoints `/api/team/*` 预留, 不实接 SSO

---

## Part 3. Core Primitives

### 3.1 Contextual Review Parsing (CRP)

每条 Amazon review / Reddit comment 进入 pipeline 后拆成 5 维度 context tensor:

1. **时间维**: 发表时间 / 提及的使用时长 ("2 个月后") / 季节性 / 事件关联
2. **关系维**: 发表者是 buyer / gifter / gifted / unrelated / influencer 角色 / 受访者 relation
3. **场景维**: usage occasion (daily / occasion / gifting / emergency) / 物理场景 (kitchen / office / travel) / 人群 (couple / family / single)
4. **评分维** (Amazon 才有): star rating / helpful votes / verified status / incentivized flag
5. **决策维**: pre-purchase (考虑中) / 刚购买 / 使用中 / 推荐中 / 放弃中 / switcher

每条 review/comment = 5-tuple context + 原文 + extracted aspects.

存储: structured JSON with nested context tags.

### 3.2 Amazon ↔ Reddit Stitching

- **Product-level 绑定**: Amazon ASIN ↔ Reddit mention (SKU / 型号 / 系列名模糊匹配 + 用户确认)
- **Topic-level 关联**: Amazon review 聊的 aspect ↔ Reddit thread 聊的同 aspect
- **Temporal alignment**: Reddit thread 发表时间 vs Amazon review wave 时间 → Halo effect 检测
- **Share of discussion**: 某 Aspect 在 Amazon vs Reddit 的提及比例

### 3.3 Signal Detection Engine

规则 + LLM hybrid:

**规则层 (fast, 确定性)**
- Star rating change > 0.2 in 7 days
- Review volume spike > 2σ
- Negative sentiment ratio > 30% in 7 days
- Specific keyword cluster appearance (e.g., "broke", "dangerous", "recall")
- New competitor product launch (Amazon BSR new entry)
- Reddit thread volume spike > 3σ
- Cross-platform correlation (Reddit buzz + Amazon wave 时滞 > 2 weeks)

**LLM 层 (slow, 语义)**
- Emerging aspect detection (人没提过的新话题)
- Narrative coherence check (多条 review 共同 pattern)
- Prescriptive action 建议生成
- Severity 评估 + 可读 title 生成

### 3.4 AI Prose Narrative Generator

- Input: ticket cluster / period range
- Output: coherent 1-3 段英文 prose (Bailey / Mark 可读)
- Tone control: internal briefing / CMO-facing / external comms
- 保持 evidence 可追溯 (每段话附 supporting ticket / review ID)

### 3.5 Ticket Lifecycle (7 状态 + Review gate)

```
[Raw Signal] → [Dedup Check] → [AI Draft] → [New] → [Triaged] → [In Progress] → [Review] → [Resolved] → [Archived]
                                                                                       ↓
                                                                                  [Reopened]
```

- **New**: AI just drafted, 未 Lead triage
- **Triaged**: severity + due date confirmed, 未 assign 或刚 assign
- **In Progress**: Owner 正在工作
- **Review**: Owner 标记"my part done", 等 signal recovery 或 Lead verify (Vibe Kanban Review gate 模式)
- **Resolved**: AI 检测 signal 恢复 + owner 确认 OR Lead 批准 close
- **Archived**: 30 天后自动 archive
- **Reopened**: Resolved 后 signal 再次劣化 → 自动 reopen

---

## Part 4. Information Architecture

### 4.1 整体布局

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
```

- **左导航 (固定 200px 宽, 不 collapse default)**: tab list + count badges + active highlight
- **顶栏 (固定 56px 高)**: logo + 全局 search + 通知 bell + 用户 avatar + team switcher (stub)
- **主内容 (fluid)**: 每 tab 自己的布局

### 4.2 Tab 列表 (左导航 order)

| Icon | Tab Name | Badge | Landing state |
|---|---|---|---|
| 📊 | Dashboard | — | 首页 default |
| 📥 | My Inbox | 8 | 个人 ticket list |
| 🏢 | Team Queue | 32 | 全队 ticket list |
| 📦 | Products | — | Category / SKU browser |
| 🔍 | Evidence | — | Raw review/thread search |
| 📝 | Narratives | — | Week/month narrative builder |
| 🌱 | Steward | — | Daily Digest / Event Lens / CEP Map |
| ⚙️ | Admin | — | Settings / integrations (mostly stub) |

### 4.3 Tab 之间跳转规则

- Ticket 里点 evidence link → 跳 Evidence tab, 保留 ticket 上下文浮标
- Evidence 里点"Create Ticket" → 回 Inbox with new ticket 预填
- Narratives 引用的 ticket → 点击 jump to ticket detail modal
- Dashboard 所有 card 可点 → 跳对应 tab

---

## Part 5. Page-by-Page UX Spec (with UI Text Sketches)

完整 UI text sketch 见伴生文件 `ui_sketch_v0.4.md`. 本 Part 按页面列出 purpose / content / 交互要点.

### 5.1 Page 1: Dashboard (首页)

**目的:** 30 秒概览 "今天值得 Bailey 关注什么".

**内容 layout (from top to bottom):**
- Top row: greeting + period selector
- KPI row (4 mini cards): Open / Overdue / Resolved this week / Impact this week
- Priority queue preview: top 4 AI-triaged tickets
- Upcoming event + CEP micromap: 2 sided card
- Team pulse strip (demo-only): member open count
- Recent activity feed: last 5 actions

**关键交互:**
- KPI card click → filter Inbox to that subset
- Priority queue item click → open ticket detail modal
- Event card → Steward Event Lens tab
- CEP gap card → Steward CEP Map tab

### 5.2 Page 2: My Inbox

**目的:** Bailey 工作主战场, 看 "我今天要处理什么".

**内容:**
- Top: 3 view mode toggle [List|Compact|Board]
- Filter chips row 1: Ticket Type (Opportunity/Threat/Insight/Strategic/Question) with count
- Filter chips row 2: Severity + Data source
- Ticket list: card 形式, 滚动
- Each card: severity icon + type tag + due + title + owner + evidence summary + prescriptive preview + timestamp

**关键交互:**
- Card click → open ticket detail (modal 或 right panel)
- [+ New] → blank ticket template
- Board view → 5-column kanban by status
- Compact view → 1-line-per-ticket dense list
- Bulk select for batch actions (close / assign / archive)

### 5.3 Page 3: Team Queue (demo-only UI)

**目的:** Team Lead 看全队 backlog + workload, assign 新 ticket.

**内容:**
- Top: group selector (by Status / Owner / Type / Severity / Product)
- Default group = Status → 5-column Kanban (New / Triaged / In Progress / Review / Resolved)
- Bottom: Workload mini-table (each team member open count + avg resolution)

**关键交互 (demo-only):**
- Drag ticket card between columns (status change)
- Drag ticket card onto a member avatar (assignment; state persists locally only)
- Filter by owner → personal view of another member
- [+ Bulk Assign] opens mass assignment dialog (demo)

### 5.4 Ticket Detail (Modal / Full Page)

**目的:** Bailey drill into 某 ticket 写 prescriptive action, 看 evidence, close.

**内容:**
- Header: severity + type + due + title + owner + status dropdown + [Mark Review] button
- 4 tabs: Overview / Evidence / Activity / Related
- **Overview tab**: AI summary (editable textarea) / Prescriptive action (editable list) / Expected impact (rating delta + $ + confidence) / Tags
- **Evidence tab**: embedded review cards + Reddit thread previews + 情感 mini-chart + source filter
- **Activity tab**: comment thread + status change log + assignment history
- **Related tab**: linked tickets (cluster / dupes / follow-ups / parent-child)
- Footer: [Save] [Mark Review] [Close with Notes]

**关键交互:**
- Edit summary/prescriptive → autosave on blur
- Mark Review → status 变 Review
- Close with Notes → prompt for close reason then status Resolved
- Evidence item click → open Evidence browser with this item focused

### 5.5 Page 4: Products (Category / SKU Browser)

**目的:** Bailey 主动 drill into 某产品看健康度, 不依赖 ticket.

**内容:**
- Left: category tree (collapsible, 3-level deep max)
- Right main: selected product detail
- Product detail sections: Health Score + Star trajectory + Review volume + Reddit mentions + Aspect Sentiment chart (Volume × Sentiment 2D) + Related Tickets list

**关键交互:**
- Category tree 展开 / 收起
- Product click → load detail
- Aspect dot click → filter Evidence to that aspect
- Related ticket click → open ticket detail

### 5.6 Page 5: Evidence Browser

**目的:** 查单条 review / Reddit thread 深度 + 上下文 + CRP 5-dim.

**内容:**
- Top filter: Source (Amazon / Reddit / Both) + Product + Date range + Sort
- List of evidence cards
- Each card: source icon + rating/upvote + date + excerpt + CRP 5-dim tags + aspect tags + [Create Ticket] / [Add to existing]
- Sidebar (optional): aspect cluster filter

**关键交互:**
- Source toggle
- Evidence card click → expand to full text
- [+ Create Ticket] → inbox with prefilled ticket
- [Add to T-XXXX] → append as supporting evidence
- Highlighted terms → click to filter by term

### 5.7 Page 6: Narratives

**目的:** 生成 / 编辑 / 导出 周报 / 月报 / 季报 / 事件 叙事.

**内容:**
- Top: period type tabs (Weekly / Monthly / Quarterly / Event)
- Drafts list: past + upcoming
- Active editor: section-by-section markdown editable + inline ticket ID references
- Export options: PPT / PDF / Email / Slack

**关键交互:**
- Generate button → AI draft
- Section [edit] → inline text editor
- [Regenerate Section] → AI redoes that section
- Export click → download file or send to service
- Ticket ID mention → hoverable preview

### 5.8 Page 7: Steward

**目的:** Bailey 非 alarm 时 stewardship 工具; 产 Strategic / Insight ticket.

**内容:**
- 4 子 tabs: Daily Digest / Event Lens / CEP Map / Curiosity Browser
- NL Query bar always visible at top

**Daily Digest 子 tab:**
- 4 section: Amazon top reviews / Reddit buzz / Competitor launches / Emerging CEP signal
- Actions: Convert All to Tickets / Dismiss / Save for Later

**Event Lens 子 tab:**
- Upcoming events list
- Selected event → historical performance + Reddit patterns + recommended SKUs + content angle ideas
- [Generate Strategic Ticket] [Export Brief]

**CEP Map 子 tab:**
- Category selector
- Table: CEP 场景 × brands (我们 + 主要 2-3 竞品)
- Gap indicators
- [Create Strategic Ticket] for big gaps

**Curiosity Browser 子 tab:**
- Top 10 today's interesting but not alarming items
- Each item → [Save] [Create Ticket] [Dismiss]

### 5.9 Page 8: Admin (Mostly Stub)

**目的:** 配置层.

**内容:**
- Sub-tabs: Team / Signal Rules / Data Sources / Integrations
- **Team**: member list + role (demo mock)
- **Signal Rules**: rule list + enable/disable (demo mock edit)
- **Data Sources**: ASIN list + subreddit list with add/remove
- **Integrations**: Jira / Asana / Slack / Salesforce / Qualtrics all show "Coming soon"

---

## Part 6. Ticket System Detail

### 6.1 五型 Ticket 定义

**Opportunity Ticket (机会型)**
- 语义: signal 提示了一个主动改善机会
- Example subtypes:
  - Chill Pill 4-star prescriptive
  - PDP gap (Reddit 问题 + Amazon Q&A 未答)
  - New purchase motivator 发现
  - CEP coverage gap
  - Pricing optimization opportunity
  - Listing content 补全 (keyword / How to)
- Color: 🟢 Green / Blue
- Default severity: Low to Medium
- Default due: 7-14 days

**Threat Ticket (威胁型)**
- 语义: signal 提示 brand / product 健康下滑
- Example subtypes:
  - Rating drop
  - Review volume negative spike
  - Crisis detection (Amazon spike + Reddit 负面联合)
  - Competitor launch with share-shift risk
  - Touchpoint sentiment drop (shipping / returns / packaging)
  - Compliance / safety 风险关键词出现
- Color: 🔴 Red
- Default severity: Medium to High
- Default due: 1-7 days (severity-dependent)

**Insight Ticket (洞察型)**
- 语义: 发现值得研究的 pattern, 非 crisis 非 opportunity 但需跟进
- Example subtypes:
  - Halo effect signal (Reddit → Amazon 时滞领先)
  - Emerging trend
  - Product switcher narrative
  - Cross-subreddit migration
  - Long-term cohort shift
  - Unusual usage scenario
- Color: 🟡 Yellow / Orange
- Default severity: Low
- Default due: 14-21 days

**Strategic Ticket (战略型)**
- 语义: 不是 signal-driven, 是 rhythm-driven (周报 / 月报 / 事件)
- Example subtypes:
  - Weekly narrative draft
  - Event Lens prep (holiday / product launch)
  - Monthly CEP coverage review
  - Quarterly Mark material
  - Annual competitive landscape
- Color: 📘 Blue
- Default severity: Medium
- Default due: rhythm-aligned (Friday for weekly, 3 weeks before event)

**Question Ticket (待决型)**
- 语义: 产品 PDP / content 层有缺口, 需要人工回答或补全
- Example subtypes:
  - Unanswered Amazon Q&A 超过 N 天
  - Reddit 高频问题 cluster 但 PDP 未覆盖
  - Missing How-to content
  - Ambiguous product spec
- Color: ❓ Gray
- Default severity: Low
- Default due: 10-14 days

### 6.2 Ticket Card Data Schema

```json
{
  "id": "T-1024",
  "type": "Opportunity",
  "subtype": "4-star-drift",
  "severity": "High",
  "status": "In Progress",
  "title": "Ninja Creami 4-star drift — 隔层难开 + 马达噪音",
  "summary": "AI-generated human-readable insight paragraph",
  "prescriptive_action": "AI-drafted action list (editable by owner)",
  "prompt_for_automation": "Optional: AI-executable prompt for future agent exec (Vibe Kanban inspired)",
  "expected_impact": {
    "rating_delta": "+0.1",
    "monthly_sales_usd": 24000,
    "confidence": "high",
    "time_to_realize_days": 14
  },
  "product": {
    "brand": "Ninja",
    "line": "Creami",
    "sku": "NC501",
    "asin": "B0D9NQX3YV"
  },
  "data_source": ["amazon", "reddit"],
  "evidence": [
    {
      "type": "amazon_review",
      "id": "R1A2B3",
      "excerpt": "The lid is impossible…",
      "rating": 3,
      "date": "2026-04-15"
    },
    {
      "type": "reddit_thread",
      "id": "t3_abc123",
      "subreddit": "icecream",
      "upvotes": 47,
      "date": "2026-04-12"
    }
  ],
  "signal_metadata": {
    "detection_rule": "star_drift_7d + aspect_cluster",
    "confidence": 0.87,
    "first_detected": "2026-04-15T10:23Z",
    "last_updated": "2026-04-17T08:15Z"
  },
  "ownership": {
    "owner_id": "bailey",
    "watchers": ["marcus", "alex"],
    "created_by": "ai_signal_engine"
  },
  "timing": {
    "created": "2026-04-17T08:15Z",
    "triaged": "2026-04-17T09:30Z",
    "assigned": "2026-04-17T09:30Z",
    "due": "2026-04-22T23:59Z",
    "sla_suggested_by": "ai"
  },
  "tags": ["creami", "kitchen", "4-star-mitigation", "Q2-2026"],
  "related_ticket_ids": ["T-1031"],
  "duplicate_of": null,
  "activity_log": [
    {"ts": "...", "actor": "ai", "action": "created"},
    {"ts": "...", "actor": "marcus", "action": "assigned_to_bailey"},
    {"ts": "...", "actor": "bailey", "action": "edited_prescriptive"}
  ]
}
```

### 6.3 Signal → Ticket Pipeline (9 步详细)

1. **Data Ingestion**: Scrape Amazon (ASINs) / Reddit (subreddits) 按 schedule (e.g., 每 15 分钟)
2. **Contextual Review Parsing**: 每条原文抽 5 维 context tensor + aspects
3. **Signal Detection**: 规则层 + LLM 层 hybrid check
4. **Dedup Check**: 与 open tickets 对比 (同 product + 同 aspect cluster + 7 天内 → merge 到 existing)
5. **AI Draft**: LLM 生成 title / summary / prescriptive / expected impact / severity / due date
6. **New Ticket 入队**: 进 Team Queue (status=New)
7. **Lead Triage**: Team Lead review, 调 severity / due / assign owner → status=Triaged
8. **Owner Execution**: Owner 打开 ticket, 读 evidence, 编辑 prescriptive, 写 action taken → status=In Progress → Mark Review
9. **Close**: AI 持续监测 signal; 若恢复 (rating 反弹 / sentiment 翻正 / volume 回正常) → suggest close → owner 或 Lead confirm → status=Resolved; 30 天后 Archived

### 6.4 Dedup & Cluster Logic

- **Exact match**: 同 product + 同 subtype + 7 天内 → drop as dup
- **Fuzzy cluster**: 同 product + 相近 aspect cluster (embedding similarity > 0.85) → 建议 merge
- **Cross-product cluster**: 同 aspect 跨多 SKU → 创建 higher-level Strategic ticket ("品类级 pattern")
- **User override**: "这不该是 ticket" 按钮 → fed back to signal rule confidence calibration

### 6.5 Severity 校准

- **High**: \$50K+ monthly impact 或 rating drop > 0.3 或 safety keyword
- **Medium**: \$10-50K impact 或 rating drop 0.1-0.3 或 emerging trend 值得 deep-dive
- **Low**: < \$10K impact 或 nice-to-have opportunity 或 weak signal

Impact 估算基于: product 历史 conversion rate × rating-to-sales elasticity × review volume affected.

### 6.6 Review Gate (Vibe Kanban inspired)

**关键原则: AI-generated prescriptive action 或 AI-suggested close 必须经人工 Review 才进 Resolved.**

流程:
- Owner 工作 ticket 完成 → 点 [Mark Review]
- Status → Review
- 系统监测 signal recovery 情况
- 若 signal 恢复 → AI suggest close with recovery evidence
- Owner 或 Team Lead 最终 [Confirm Close]

这一步防止 AI 幻觉类错误直接进入 resolved, 保持审计 trail.

---

## Part 7. Steward 层 (非 alarm 时的主动 stewardship)

### 7.1 Daily Digest

- **触发:** 每天早 7am 自动生成 (用户时区)
- **产出:** Digest card on Dashboard + Option to create Insight tickets
- **内容:** 昨夜 top 3 Amazon notable reviews + 昨夜 Reddit buzz + 竞品 launch 预告 + emerging CEP weak signal
- **用户操作:** 一键 "Convert interesting to Insight ticket"

### 7.2 Event Lens

- **触发:** 营销日历绑定的 event 提前 N 周 (Mother's Day 3 周前 / Prime Day 4 周前 / 自家新品 2 周前)
- **产出:** Event brief card + auto-generated Strategic ticket
- **内容:** 历史同期 performance + Reddit gift/event thread patterns + 推荐 focus SKUs + content angle 建议
- **用户操作:** Edit brief → Assign to team → Follow progress

### 7.3 CEP Coverage Map

- **触发:** 每月 1 号自动刷新 + 用户可随时查询
- **产出:** Category CEP 覆盖度 dashboard + auto-generated Strategic ticket for gaps > 10 pts
- **内容:** 各 CEP 场景我们 vs 竞品占比, gap 排序
- **用户操作:** Click gap → view supporting Reddit threads → create campaign Strategic ticket

### 7.4 Weekly Narrative Builder

- **触发:** 每周五 2pm 自动生成 draft
- **产出:** 叙事 draft (三段式: last week patterns / key tickets resolved / outlook next week)
- **内容:** 组装本周 closed tickets + open high-severity + Steward layer 发现
- **用户操作:** Edit → Export to email / PPT / Slack

### 7.5 Natural Language Curiosity Query

- **触发:** 用户在任意 page 顶栏输入
- **示例:** "Why are customers recently praising Shark FLEX?" / "Which Reddit subreddits discuss our blender for road trips?" / "过去 6 个月 Reddit 有多少人从 Dyson 换到 Shark?"
- **产出:** Inline answer + supporting evidence + option to "Save as Insight ticket"
- **实现:** RAG over signal store + LLM synthesis

### 7.6 Curiosity Browser (bonus)

- 每天 top 10 "interesting but not alarming" review / thread
- Serendipity feed
- Click to see context / Save to Evidence / Create ticket

---

## Part 8. Data Pipeline & Backend

### 8.1 Amazon Scrape Specification

**Sources:**
- Product page (title, description, bullets, price history, BSR, availability)
- Reviews (all, paginated, includes "updated" reviews)
- Q&A section
- Customer images (metadata only — caption text if any)

**Fields per review:**

```json
{
  "review_id": "R1A2B3",
  "asin": "B0D9NQX3YV",
  "rating": 3,
  "title": "Okay but with issues",
  "body": "...",
  "date": "2026-04-15",
  "verified_purchase": true,
  "helpful_votes": 24,
  "vine_program": false,
  "incentivized_flag": false,
  "updated_date": null,
  "media": {"image_count": 2, "video": false},
  "reviewer_id": "A1B2C3",
  "reviewer_name": "Jane D.",
  "variant": {"size": "16oz", "color": "silver"}
}
```

**Q&A fields:**

```json
{
  "question_id": "...",
  "question_text": "...",
  "question_date": "...",
  "answers": [{"text": "...", "voter_count": 12, "is_seller": false}],
  "vote_count": 24,
  "asked_by_reviewer": null
}
```

**Rate limit strategy:**
- 遵循 robots.txt
- 代理池 rotation
- Respect crawl-delay
- Exponential backoff on 429
- Demo 期间 cache 足量数据到 local SQLite

### 8.2 Reddit Scrape Specification

**Sources:**
- Subreddits (tracked list, admin-configurable)
- Threads (title, body, metadata)
- Comments (threaded, all levels)
- Author metadata (public only: account age, total karma range)

**Fields per thread:**

```json
{
  "thread_id": "t3_abc123",
  "subreddit": "icecream",
  "title": "...",
  "body": "...",
  "author": "username",
  "author_account_age_days": 1200,
  "upvotes": 47,
  "downvotes_est": 3,
  "comment_count": 28,
  "created_utc": "...",
  "flair": "discussion",
  "is_stickied": false,
  "url_matched_products": ["B0D9NQX3YV"]
}
```

**Comment fields:**

```json
{
  "comment_id": "t1_def456",
  "parent_id": "...",
  "body": "...",
  "author": "...",
  "upvotes": 12,
  "created_utc": "...",
  "depth": 2
}
```

**API approach:**
- 如能用 Reddit Public API (PRAW) 优先 (即使 Vincent 说 no API, Reddit 本身就是 public API, 这是 fair use)
- Fallback: web scraping old.reddit.com
- Demo cache 10 subreddits × 90 天 threads

### 8.3 Storage Schema

**SQLite / Postgres tables:**

- `amazon_reviews` (see schema above)
- `amazon_qa`
- `amazon_products` (ASIN metadata + BSR history)
- `reddit_threads`
- `reddit_comments`
- `subreddits` (tracked list)
- `signal_events` (detection output pre-ticket)
- `tickets` (see schema in 6.2)
- `activity_log`
- `narratives` (drafts + finals)
- `team_members` (demo mock)
- `signal_rules` (admin editable)
- `users` (demo mock with permissions)

### 8.4 LLM Integration Points

**Models:**
- Primary: Claude Sonnet 4.6 (cost-effective, fast)
- Fallback / complex: Claude Opus 4.7 (narrative generation, complex reasoning)

**Prompt patterns:**

1. **Review aspect extraction** (每 review 调用)
2. **CRP 5-dim tagging** (每 review/thread 调用)
3. **Signal severity + title draft** (每 new signal event 调用)
4. **Prescriptive action generation** (每 ticket 调用)
5. **Narrative prose generation** (周报生成时调用)
6. **NL query → structured query** (用户 curiosity query 时)
7. **Cluster similarity check** (dedup 时调用)

**Cost control:**
- Cache common prompts
- Batch review processing
- Use small model for simple classification, large for narrative

### 8.5 Stub API 预留接口 (Team collab + 未来 integrations)

```
POST /api/team/assign          # assign ticket to member
GET  /api/team/members         # team member list
POST /api/team/watch           # add watcher to ticket
POST /api/integrations/jira/sync       # export to Jira
POST /api/integrations/salesforce/case # push to Salesforce Service Cloud case
POST /api/integrations/slack/post      # post narrative to Slack
POST /api/integrations/qualtrics/link  # link existing Qualtrics survey
GET  /api/mcp/ticket           # MCP endpoint for external AI agents to create tickets
POST /api/narrative/export     # PPT / PDF / Email export
```

2-day 实现: 所有 endpoint 返回 mock success response + log 请求; 无真实外部集成.

---

## Part 9. UX Patterns / Design Language

### 9.1 Density & Layout
- 信息密度向 Linear 看齐 (不是 Notion 的 airy, 不是 Jira 的 cluttered)
- 主内容最大 1400px, 居中
- 左导航固定 200px
- 顶栏 56px

### 9.2 Color Semantic
- Severity: 🔴 High (#DC2626) / 🟡 Medium (#EAB308) / 🟢 Low (#22C55E)
- Ticket type: Opportunity (Green/Blue) / Threat (Red) / Insight (Amber) / Strategic (Blue) / Question (Gray)
- Sentiment dots: Green (positive) / Red (negative) / Gray (neutral)
- Action primary: #0F172A (near-black)
- Action secondary: #64748B (slate-500)

### 9.3 Typography
- Heading: Inter / SF Pro 半粗 16-24px
- Body: 13-14px
- Mono (数据 / IDs): JetBrains Mono 12-13px

### 9.4 Card design
- Border-radius 8px
- Subtle shadow on hover
- Left 4px color strip = severity
- Right-side small icons = data source (Amazon / Reddit)

### 9.5 Filter Chips
- Horizontal pill-shaped chips, Active state = 填充 primary color
- 点击 toggle on/off
- 多 chip = AND 逻辑

### 9.6 Search
- 顶栏全局 search
- 默认 search tickets
- Prefix modifier: `product:` `reviewer:` `date:` `severity:`
- 或 NL 直接问 (Steward tab NL Query)

### 9.7 Modal vs Inline
- Ticket detail = modal (overlay) 或 pinned right-panel (可选)
- Settings / admin = full page
- Quick preview (hover 0.5s) = small popover

### 9.8 Empty states
- "No tickets yet" → friendly illustration + "Signals detected overnight will appear here"
- "No evidence match" → "Try broader date range or different product"
- Onboarding empty state with 3 demo ticket templates 可一键加载

### 9.9 Loading states
- Skeleton cards (not spinner)
- Shimmer effect on initial load
- Inline spinner for actions

### 9.10 Error states
- Inline error toast top-right
- "Retry" button always available
- Error boundary fallback page

---

## Part 10. MVP Scope & Demo Narrative

### 10.1 Must-have for 2-day demo

**Functional:**
- Dashboard 首页 render with mock + some real data
- Inbox with 10-15 real AI-drafted tickets (scraped Amazon + Reddit)
- Ticket detail modal with editable prescriptive + evidence embed
- Team Queue view (visual, drag-drop stub)
- Products page with 2-3 SKU drill-down
- Evidence Browser with search + filter
- Narratives tab with 1 pre-generated weekly narrative + edit
- Steward: Daily Digest functional + Event Lens static + CEP Map static
- Admin: stub screens

**Real data:**
- 2-3 SKUs scraped real Amazon (300+ reviews each)
- 5-8 subreddits scraped real Reddit (90 days)
- Real AI-drafted tickets for above products
- Real weekly narrative generation

**Stub / mock:**
- Team member list (4 mock users)
- Assignment drag-drop local-state only
- All integrations "Coming soon"
- NL Query answers pre-canned for 3-5 demo questions
- Halo effect chart with 1 pre-computed example

### 10.2 Demo Flow (10 min pitch)

1. **开场 30s**: 问题陈述 — SharkNinja Bailey 每天 10K+ signal, 当前 workflow Slack 截图传, 我们要 tech this
2. **Dashboard 1 min**: show 首页, 点 priority queue item
3. **Ticket detail 2 min**: 打开 Ninja Creami 4-star ticket, 展示 AI summary / evidence / prescriptive / expected impact. 强调每部分都可 Bailey edit
4. **Team Queue 1 min**: 切到 Team view, drag-drop assign 演示
5. **Evidence 1 min**: 点 ticket 进 Evidence browser, 展示 Amazon review + Reddit thread stitching
6. **Halo Effect 演示 1.5 min**: Reddit r/vacuums buzz → Amazon review wave 时滞 chart (有 2 周前 Reddit + 今日 Amazon) → 创建 Insight ticket
7. **Steward 1.5 min**: Daily Digest + CEP Coverage Map gap + Event Lens Mother's Day brief
8. **Narrative 1 min**: Show weekly narrative auto-generated → 一键 export (click 动作)
9. **收尾 30s**: vs Revuze + Jira 九宫格, 强调 consumer-signal-driven ticket + closed loop moat

### 10.3 Non-functional 指标

- **Performance**: Dashboard < 2s load / Ticket detail < 500ms open
- **Mobile**: viewable but not fully functional (demo 笔记本屏)
- **Offline**: SQLite 本地 cache, demo 若断网可 continue

---

## Part 11. Demo Data

### 11.1 Selected SKUs

1. **Ninja Creami NC501** (ASIN: B0D9NQX3YV)
   - Reason: 已有 anchor Chill Pill 例子 (4-star drift)
   - Real reviews: 500+ (scraped)
   - Reddit presence: r/icecream, r/ninja, r/BuyItForLife

2. **Shark NV360 Navigator Lift-Away** (ASIN: B00SMLJPGE)
   - Reason: Reddit presence 强, 经典 vacuum
   - Real reviews: 1000+
   - Reddit presence: r/vacuums, r/CleaningTips

3. **Ninja CM401 Specialty Coffee Maker** (ASIN: B07VPQWY2J)
   - Reason: Event Lens 演示 (Mother's Day gift angle)
   - Real reviews: 800+
   - Reddit presence: r/coffee, r/gifts, r/AskMen

### 11.2 Tracked Subreddits (demo)

- r/icecream / r/vacuums / r/coffee / r/BuyItForLife
- r/gifts / r/AskMen / r/AskWomen
- r/ninja / r/CleaningTips / r/roadtrip

### 11.3 Pre-generated AI Tickets (demo 必备)

至少 10-15 张跨 5 型:
- 3 Opportunity (包括 Chill Pill)
- 3 Threat (包括 shipping sentiment drop)
- 3 Insight (包括 Halo, switcher narrative, CEP gap)
- 3 Strategic (Weekly narrative / Mother's Day prep / Monthly CEP review)
- 3 Question (Amazon Q&A gaps)

### 11.4 Pre-canned NL Query answers

- "What's hot on Reddit about our blender?" → canned response
- "Which 4-star review clusters should we prioritize?" → canned
- "How's Cuisinart new launch going?" → canned

---

## Part 12. Tech Stack & Agent Dev 分工

### 12.1 Recommended Tech Stack

**Frontend:**
- Next.js 14+ (React + SSR)
- TypeScript
- Tailwind CSS + shadcn/ui components
- Recharts or Chart.js 数据可视化
- Zustand / React Context 状态管理

**Backend:**
- Python FastAPI (fast, async, auto OpenAPI docs)
- SQLite for demo (migrate to Postgres post-hackathon)
- SQLAlchemy ORM
- Pydantic schema

**Data Pipeline:**
- Playwright (Amazon scraping) or BeautifulSoup for simpler
- PRAW (Reddit API)
- Celery / APScheduler for periodic scraping (demo 可简化为 manual trigger)

**LLM:**
- Anthropic SDK (Claude Sonnet 4.6 default, Opus 4.7 for narrative)
- Prompt templates in dedicated module
- Embedding for dedup clustering (Voyage or OpenAI ada)

**Deployment:**
- Vercel (frontend)
- Railway / Render (backend + DB)
- LocalStack for demo if internet uncertain

### 12.2 Agent Dev 分工 (suggested 4 subteams)

**Stream 1: Frontend (2 agents)**
- Agent A: Layout + Nav + Dashboard + Settings pages
- Agent B: Ticket components (card, detail modal, list filters) + Evidence browser + Narrative editor
- Dependencies: Stream 3 API contract defined

**Stream 2: Backend + Data Pipeline (2 agents)**
- Agent C: Amazon + Reddit scraper + SQLite persistence
- Agent D: FastAPI endpoints (ticket CRUD + query + stub integrations) + WebSocket for live updates
- Dependencies: 无, 可先启动

**Stream 3: LLM + Signal Engine (2 agents)**
- Agent E: CRP 5-dim parser + aspect extraction + signal detection rules
- Agent F: Ticket AI draft (title + summary + prescriptive + severity) + Narrative generator + NL query RAG
- Dependencies: Stream 2 storage schema ready

**Stream 4: Integration + Demo Polish (1 agent + Vincent)**
- Agent G: Glue code / demo data seed / demo script
- Vincent: final pitch narrative + slide deck

**依赖 DAG:**

```
Stream 2 (schema) ───┬───► Stream 3 (LLM) ──┐
                     │                       ├─► Stream 4 (glue)
Stream 1 (frontend) ─┘                       │
                                              ▼
                                          Demo Ready
```

### 12.3 Parallel vs Serial

**Day 1:**
- Morning: All 4 streams 启动 (Stream 1 mock API contract, Stream 2 schema + scrape start, Stream 3 prompt design, Stream 4 demo data plan)
- Afternoon: Stream 1 & 2 converge on API, Stream 3 接入 Stream 2
- Evening: Stream 4 begin glue

**Day 2:**
- Morning: Integration testing + polish
- Afternoon: Demo rehearsal + edge case fix
- Evening: Final demo-ready

---

## Part 13. Post-Hackathon Roadmap + Appendix

### 13.1 Post-Hackathon 2-week sprint

- Real Jira / Asana integration (Stream 4 API stub → real sync)
- Real Salesforce Service Cloud case push
- Real Slack narrative posting
- Auth + Multi-tenant (SSO Okta / Azure AD)
- Real team assignment persistence (Postgres, not local state)
- Admin panel full functionality

### 13.2 Post-Hackathon 3-month

- Add more data sources (Walmart, Target marketplace reviews) (仍 public scrape)
- Qualtrics integration (solicited data 作补充但不替代 unsolicited 叙事)
- Multi-language (欧洲市场)
- Custom signal rule builder UI
- SharkNinja internal tool integration
- Competitive monitoring 至品类头部 10 品牌

### 13.3 Scale-up roadmap

- SKU count 20+ → 500+
- Reviews 100K → 50M
- Real-time (15 min latency → 5 min)
- Multi-brand 支持 (给 SharkNinja 其他品牌家族 / 或 Revuze-style 卖给其他 CPG)

### 13.4 Appendix A: Full Ticket Examples (3 real)

**Example 1: Opportunity Ticket - Chill Pill**

```
ID: T-1024
Type: Opportunity / 4-star-drift
Severity: High
Title: Ninja Creami 4-star drift — 隔层难开 + 马达噪音
Summary:
  Creami 4★ 占比从 32% (2026-04-01) 升至 41% (2026-04-15)。12 条 Amazon
  review + 3 r/icecream threads 集中抱怨: (1) 隔层打开力 68% 负评提及;
  (2) 马达噪音 52%。Reddit 讨论从 r/icecream 扩至 r/smallkitchenappliance,
  说明 pattern 跨受众。
Prescriptive Action:
  1. 工程评估隔层开启力 (目标 ≤ 2.3 N)
  2. 材料组评估隔音改造可行性
  3. PDP 前置回答 "如何打开隔层" + 30s video demo
  4. 客服话术更新加入此 case
  5. Amazon Q&A 主动答 3 个高频相关问题
Expected Impact: +0.1★ in 14d → $24K monthly sales lift, confidence high
Evidence: 12 Amazon reviews + 3 Reddit threads (links)
Due: 2026-04-22
Owner: Bailey
```

**Example 2: Insight Ticket - Halo Effect**

```
ID: T-1031
Type: Insight / halo-effect-signal
Severity: Low→Medium (随时间升级)
Title: r/vacuums buzz +400% on Shark FLEX — Amazon review wave 预警 2-3 wk 后
Summary:
  Reddit r/vacuums 过去 3 周 Shark FLEX mentions +400%, sentiment 70% 正。
  历史 Halo pattern 显示此类 Reddit buzz 约 14-21 天后触发 Amazon review
  wave 增长 30-50%。建议 2-3 周内监测 + 准备 positive-momentum marketing
  leverage。
Prescriptive Action:
  1. 每天 monitor Amazon FLEX review volume
  2. 准备 positive marketing angle 可在 wave 启动时 capitalize
  3. 若 2 周后仍无 wave → 降级为 Insight weak signal
  4. 若 wave 来 → 升级为 Strategic (leverage 时机)
Evidence: 14 Reddit threads cross 3 subreddits
Due: 2026-05-01 (2 周 check-in)
Owner: Bailey
```

**Example 3: Strategic Ticket - Mother's Day prep**

```
ID: T-1050
Type: Strategic / event-prep
Severity: Medium
Title: Mother's Day 2026-05-11 prep — 3 周 out
Summary:
  历史同期 gift-positioned SKU 平均 4.1★ (2024) → 4.0★ (2025, noise dip)。
  Reddit r/gifts, r/AskMen Mother's Day + coffee / blender 讨论 peak
  开始于 Apr 20-25。推荐 focus: Ninja CM401 (coffee), Creami NC501
  (dessert gift angle)。Content angle 建议从 r/AskMen 分析得:
  "coffee for dads (unexpected mother's day twist)"、"gift that lasts"
  (2-year follow-up review 叙事)。
Prescriptive Action:
  1. Brand team 接到 brief, 产 3 content angles
  2. Ecommerce 准备 Amazon A+ content 更新
  3. CM401 + NC501 库存 check
  4. Pre-Mother's-Day Reddit 预热 post 可行性 evaluate
Evidence: historical performance data + 45 r/gifts threads + 28 r/AskMen threads
Due: 2026-05-04 (1 week before event)
Owner: Bailey + Brand lead
```

### 13.5 Appendix B: Prompt Templates (关键 LLM prompt)

**Prompt 1: CRP 5-dim extraction**

```
Given this review/thread, extract 5-dimension context tensor:
1. Time: when written / usage duration mentioned / seasonal / event
2. Relation: role of writer (self/gifter/gifted/etc)
3. Scene: usage occasion, physical setting, social context
4. Rating: star + votes + verified status (Amazon only)
5. Decision: stage (pre-purchase, post-purchase, using, abandoning, switching)

Also extract aspects mentioned (feature/attribute + sentiment).

Output JSON.
Review: {review_text}
```

**Prompt 2: Ticket auto-draft**

```
You are a CPG brand analyst assistant. Given this signal cluster, draft a
ticket for the E-commerce team to action.

Signal: {signal_summary}
Evidence: {review_and_thread_excerpts}
Product: {product_info}
Historical context: {product_stats}

Generate:
- Ticket type (Opportunity/Threat/Insight/Strategic/Question)
- Severity (High/Medium/Low) with reasoning
- Title (<60 chars, specific, 中英 OK)
- Summary (1-2 paragraphs, human-readable, evidence-grounded)
- Prescriptive Action (3-5 specific steps the team can take)
- Expected Impact ($ monthly, rating delta, confidence)
- Due date (days from now)

Be specific, avoid vague statements. No hallucination — only use provided
evidence. Output JSON.
```

**Prompt 3: Weekly Narrative**

```
Generate a Chief-of-Staff-ready weekly narrative for SharkNinja brand
stewardship this week.

Closed tickets this week: {list}
Open high-severity: {list}
Steward discoveries: {list}

3-paragraph prose:
Para 1: Top pattern / achievement this week
Para 2: Concern or watch area
Para 3: Outlook next week + strategic alignment with Mark's priorities
(Mental Availability, category breadth, never forgotten)

Tone: concise, evidence-grounded, leadership-level but not jargon-y.
Each claim should have traceable ticket-ID reference.
```

### 13.6 Appendix C: Academic Anchors (设计依据)

- Mudambi & Schuff 2010 MIS Q: 4-star 对 experience goods informative
- Hu/Pavlou/Zhang 2009, 2017: J 形分布, acquisition + underreporting bias
- Chevalier & Mayzlin 2006 JMR: 负面 review asymmetric impact
- Luca HBS 2011: 1-star = 5-9% 营收影响 (Yelp RDD)
- Say-do gap NIQ 2023: 65% say / 26% do
- Gartner CES 2013: 94% low-effort 复购
- Ehrenberg-Bass (Byron Sharp): Mental Availability + Physical Availability + CEPs
- Kahneman: System 1 vs System 2 advertising
- Binet & Field IPA 60/40: brand vs activation

### 13.7 Appendix D: References (research 文件)

- `Challenge_5_v3/product_hub.md` 至 `reporting_hub.md`: Revuze 9 hub 深度 reference
- `Challenge_5_v3/vibe_kanban_reference.md`: UX inspiration for ticket + Review gate
- `Challenge_5_v3/ui_sketch_v0.4.md`: 完整 UI text sketch (本 spec Part 5 的 sketch 合集)

---

# 完 / End of Spec v0.4
