# Challenge 5 Session Context Pack — for v0.5 Design Session

**Purpose:** 携带到新 session 的所有 spec_v0.4.md + ui_sketch_v0.4.md 里没带的 context. Read before starting v0.5 design.

**Generated:** 2026-04-18

---

## 0. 会话演进历史

- **R1-R4**: Vincent "把思考外包给凌喵" 阶段, solution-first 失败. 2026-04-17 推翻
- **Product redesign**: problem-definition-first, 并发 agent 研究 Revuze + marketing 平台 + SharkNinja 工具栈
- **v0.1 4-part spec**: 服务人群 / 功能 / 差异性 / 场景 (Bailey-anchor)
- **v0.2 non-alarming 增补**: Vincent 指出只有 alarm 不够, 加 Proactive Stewardship 层
- **v0.3 ticket-based reframe**: Vincent 提议用 ticket system 作为 product backbone
- **v0.4 detailed spec**: + Vibe Kanban 借鉴 + UI sketch + agent team dev-ready
- **v0.5 planned (new session goal)**: Cross-entity Comparison Builder + Aspect Radar + Tier/Equivalence taxonomy

---

## 1. Vincent 的 5 条设计原则

1. **互不冲突** — 新 feature 与已有 ticket / product / evidence 系统 coherent, 不撕裂现有架构
2. **错位 (实际升维)** — 不做 Revuze 版本替代, 做 Revuze architecturally 做不到的事. Cross-comparison 这块, Revuze 做 Feature-level SWOT; 我们要做 Product-level decision-path
3. **低门槛高上限** — baby-friendly 起步但支持 Bailey 成长成专家
4. **双向兼容** — 与现有 ticket / evidence / narrative 层互通, 发现 → 产 ticket, ticket → 触发 compare
5. **吸收精华** — Revuze / Jira / Vibe Kanban 做对的借鉴, 做错的升维

**第 0 条 meta:** 集成 UI / 反碎片化. 一个网址一个体系, 不要四处跳. Products page 加 Compare sub-view 比新建顶层 tab 更符合这条.

---

## 2. 红线 (Red Lines, 不可越过)

- 不做 Revuze Lite (Revuze 做 comparison 做了 5 年, 你要在同 feature 做得更好必须 architecturally 不同)
- 不做 nav 复杂化 (现有 8 tab 已满)
- 不做 vanity viz (radar 要有明确 action output, 不能只是好看)
- 不做 AI-only automation (tier 判定 / equivalence 映射需要 human-in-the-loop)
- 不做视频平台数据 (TikTok / YouTube / Instagram 不在数据域)
- 不替换 SharkNinja 现工具栈 (Qualtrics / Salesforce / Analytic Partners 不动)
- 不做 1st-party CRM 数据
- 不做跨零售商数据 (只 Amazon + Reddit)
- 不做 Boolean query UI (baby-friendly 原则)

---

## 3. 被 reject 的 paths (前车之鉴)

- **R1-R4 solution-first**: 不先定义 problem 就开始 design solution. Vincent 明确说 "我把思考外包给了你"
- **v0.1 pure dashboard + alerts**: 偏 reactive, 非 alarm 时无价值
- **"Revuze + Reddit" simple framing**: Vincent 明确说要 "升维 not Lite"
- **团队协作后端**: 2 天不够, UI stub only
- **CINT panel 自有样本**: 与 say-do gap 哲学冲突
- **跨品牌 Brand Tracker 深覆盖**: 2 天做不到, 聚焦 3 SKU 示范
- **"Attempt 模型" (Vibe Kanban 式 多 agent 并行尝试)**: 数据驱动确定性推荐不需要

---

## 4. Bailey Persona + 妙妙时刻 全文

**Bailey Marquis-Wu**
- Senior Manager E-commerce at CPG (SharkNinja 式)
- 3 年经验, 熟 Excel, 见过 Looker/Tableau 但不会建
- **LLM literacy**: baby-friendly (不是 prompt engineer)
- **权限现状**: 无 Qualtrics API / 无 Salesforce admin / Reddit 个人 account
- **数据接触**: Amazon Seller Central 可查自家 review / 竞品要手动 amazon.com / Reddit 上 Google 搜

**妙妙时刻 (anchor reactive scenario):**

> 周二下午 2 点, Bailey 在做 weekly 排期 / 周报. 扫过 Amazon Seller Central 看到 3-5 条新 review 提同一件诡异事 — "盖子弹开" / "马达噪音" / "保温不够". 她内心 "这是真 pattern 还是噪音?"
>
> **当前 workaround:** 截图 → 贴 Slack # ecomm-team channel → @ colleague → 等回复. 回复可能 4 小时后, 可能明天. 到时 review 数字可能又变了. Follow-up 难.
>
> **她想要:** 快速判断是 pattern 还是 noise, 拿到 evidence 支撑, 给 Director 一个清晰 "要 action / 先观察" 的建议, 一键生成周报 material.

**Bailey 的 weekly rhythm:**
- **周一**: 扫 weekend Amazon review + Reddit buzz / 看 alerts / 排本周优先级
- **周二**: weekly review, 4 星 prescriptive walkthrough / 做竞品扫视
- **周三-四**: 深度竞品监测 + 跨 SKU 对比 + 准备 Director meeting
- **周五**: 写 CMO-level 周报 narrative / 月度 metric 拼装

**Bailey 无法做的事 (即使她想):**
- 跨多零售商自动数据拉取 (无 API)
- 多平台社交 listening (预算 + 权限限制)
- 实时 Slack / email alert 推送给 C-level (权限)
- Production 数据库查询

---

## 5. Chill Pill Walkthrough 全文 (anchor demo)

**Product:** Ninja Creami NC501 (ASIN B0D9NQX3YV)
**Trigger:** Amazon 4 星 review 占比 14 天内从 32% 升至 41%, 触发 AI signal detection

**AI-drafted Ticket (T-1024):**
- Type: Opportunity / 4-star-drift
- Severity: High
- Title: "Ninja Creami 4-star drift — 隔层难开 + 马达噪音"
- Summary: 4★ 占比升至 41%; 12 Amazon review + 3 r/icecream threads 集中抱怨:
  - (1) 隔层打开力 68% 负评提及
  - (2) 马达噪音 52%
- Prescriptive Action:
  1. 工程评估隔层开启力 (目标 ≤ 2.3 N)
  2. 材料组评估隔音改造可行性
  3. PDP 前置回答 "如何打开隔层" + 30s video demo
  4. 客服话术更新
  5. Amazon Q&A 主动答 3 个高频相关问题
- Expected Impact: 4.0 → 4.1★ (14d) / $24K monthly sales lift / confidence high
- Due: 5 workdays
- Owner: Bailey (assigned by Team Lead)

**Flow 闭环:**
1. AI detect → draft ticket → Lead triage + assign
2. Bailey open → 看 evidence (12 reviews + 3 threads)
3. Bailey edit prescriptive action, 加她的判断
4. Bailey 协调工程 / 客服 / 电商 (链外)
5. Bailey [Mark Review] → 等 signal recovery
6. AI 检测 Amazon rating 2 周后反弹至 4.1 → suggest close with evidence
7. Bailey [Confirm Close] → status Resolved
8. 30 天 → Archived
9. 本周 weekly narrative 自动 pick up this resolved ticket 作为"achievements"段落

**凌喵 why Chill Pill 是核心 demo anchor:**
- 真实 pain (Amazon rating 敏感度高)
- AI 价值直观 (aspect cluster + prescriptive 一次产出)
- Expected impact 量化 ($24K)
- Closed-loop (signal recovery auto-close)
- 跨两源 (Amazon review + Reddit thread)

---

## 6. 4 条 Amazon 一手观察 (Vincent 自己在 Amazon 发现的)

1. **早期缺陷升 marketing 预警**: Creami 塑料屑, 早期 review 发现后 marketing 可提前 frame narrative
2. **Gifting "为谁买"**: Amazon 评论中 "I bought this for my mom / husband / coworker" 语料揭示 receiver 特征 → 精准 marketing
3. **Long-term review 时间维度**: Amazon "updated" review + Reddit "6 个月后 / 1 年后" threads, Revuze 只靠 Amazon updated
4. **4 星 prescriptive walkthrough**: 3.9 → 4.0 跨越点价值巨大, 4 星负评最 informative (Mudambi-Schuff 2010 MIS Q)

Vincent 决策:
- 观察 1 选 B (early defect 升 marketing 预警而非仅产品 defect fix)
- 观察 2-4 全部进产品 (gifting / long-term / 4-star 作为独立 ticket subtypes)

---

## 7. 4 条 SharkNinja 内部信号 (Vincent 从面试 + 外部调研得到)

1. **数据 fragmentation** "everywhere but nowhere" (Qualtrics / Salesforce / Analytic Partners 各存一半)
2. **Data security 投入不足** (面试中对方明确表示无人在做)
3. **AI 认知缺位** → baby-friendly 设计是刚需不是 nice-to-have
4. **生产 & 市场竞争**:
   - 关税迁产东南亚
   - 中国本土品牌占优 (九阳 / 苏泊尔)
   - 美式 2-3 系列/年 vs 中国快消文化
   - AI 议程 = automate/enhance existing pipeline (非从 0 到 1 替换)

**implication for v0.5 Compare:** 
- 跨品牌比较必须轻量, 不碰 1st-party 数据
- 设计要 assume Bailey 是非 AI 专家
- Export + embed 比 native dashboard 更适合她实际工作流

---

## 8. Mark Barrocas 战略对齐 (Vincent 从 podcast + 演讲一手听到)

**Mark 原话 (via Vincent):**
- "恨不得每年换 SharkNinja 新产品" (每年 brand freshness)
- "不要让用户忘了 SharkNinja 随机选别家" (mental availability)
- 品类铺广 (category breadth expansion)

**对应学术框架:**
- Byron Sharp / Ehrenberg-Bass: Mental Availability + Physical Availability + Category Entry Points (CEPs)
- Category Expansion per Household

**v0.5 Compare 如何对齐 Mark:**
- Aspect Radar 可暴露 SharkNinja 在某 category 是否"不被想起" (radar 某轴低于竞品)
- Tier 对比揭示"我们在某价位段缺失" → 品类铺广 缺口
- Internal line 对比揭示"每年换新品"策略执行情况 (新 line 是否 freshness 强于老 line)

**不对齐 Mark 的 v0.5 tendency (警惕):**
- 把 compare 做成纯防守性工具 ("我们在这几个轴比 Dyson 强") 是 vanity
- 要做成进攻性工具 ("我们在这几个 CEP / tier / 功能轴缺口明确" → 产 Strategic ticket)

---

## 9. Say-do gap 核心叙事

**数据:** NIQ 2023 — 65% consumers 说会 buy X / 26% 实际 buy (差 39 pts)
**Implication:**
- Survey (solicited) = "说"的数据, 偏差大
- Review + Reddit (unsolicited behavior trace) = "做"的数据
- Revuze 在叙事层不点破, 仍视 survey 和 review 为等价 VoC source
- **我们核心叙事:** Signal Ops 只吃 unsolicited trace, 是 "做"的 signal

**v0.5 Compare 里 say-do gap 如何体现:**
- Radar 显示 review-based vs survey-based 的差异 (若有)
- Comparison 强调 "消费者在哪个 aspect 实际愿意 switch"而非 "声称偏好"
- Internal line 对比用 review 数据, 不用 market research 报告

---

## 10. 数据约束 + 理由

**Data boundary**: Amazon + Reddit public scraping only
- **Why**: Vincent 明确说无 API / 无特制接口 / 无 Qualtrics / Salesforce 接入能力
- **Implication for v0.5**:
  - Tier 定义只能靠 Amazon 价格 + 特征 cluster
  - Equivalence 映射只能靠 Amazon "bought together" + Reddit "I switched" threads
  - 不能依赖 Nielsen / IRI / Circana 等第三方 market data
  - 不能依赖 product taxonomy API (自己从 Amazon 分类构建)

**Reddit 在 v0.5 的作用 (非常重要):**
- Revuze 硬缺 Reddit
- Reddit threads 是 equivalence 映射金矿 ("I switched from Shark to Dyson because...")
- Reddit 是 use-case / tier 语言的来源 ("for a budget option" / "high-end pick")
- Amazon 缺失的 qualitative "why" Reddit 补上

---

## 11. Vibe Kanban 3 借鉴 (why 这三个)

Vibe Kanban = BloopAI (YC) 开源 AI agent 编排工具 (25k GitHub stars). 核心模式与 Signal Ops 完全同构 (AI 生成 → Kanban 可视化 → 人审批).

1. **双字段卡 (Description + Prompt)**
   - Vibe Kanban: Description (人读) + Prompt (AI 可执行)
   - Signal Ops 借鉴: Summary (人读) + Recommended Action (可执行) + Evidence (支撑)
   - **Why:** 分层让 AI 不 hallucinate 关键信息, 人可在不同颗粒度审核

2. **Review 列强制审批**
   - Vibe Kanban: AI 生成不绕过 Review 进 Done
   - Signal Ops 借鉴: Q3-C hybrid close, AI suggest + owner confirm
   - **Why:** AI 错误会发生, 人闸门是 trust 底线

3. **MCP Server auto-create**
   - Vibe Kanban: Agent 通过 MCP 协议创建 ticket
   - Signal Ops 借鉴: 信号采集自动建 ticket, 并预留 MCP 接口供未来其他工具接入
   - **Why:** Architectural 开放性, 日后可让 Salesforce case / Jira issue / Zendesk ticket 反向 push 进 Signal Ops queue

**不借鉴:** "Attempt 模型" (多 agent 并行尝试 side-by-side 比较). 数据驱动确定性推荐不需要 A/B/C 版本对比.

---

## 12. 关键 decision 决策链 (+ why)

**Q1: Ticket visibility / ownership scope**
- Vincent 决定: Team-wide visibility + Team Lead assigns
- Why: 降低"傻问题"门槛 + lead 保留 routing control + knowledge share 自然发生

**Q2: SLA / due-date**
- Vincent 决定: A (AI 建议 + Team Lead confirm on assign)
- Why: AI 降 Lead 认知成本, Lead 保留 final say

**Q3: Close criteria**
- Vincent 决定: C (Hybrid — AI 检测 signal 恢复 suggest close + owner confirm)
- Why: 纯 auto 丢失 "为什么 resolved" 的 narrative (owner 记录 action taken 对 Mark 季报重要)

**数据源 decision:**
- Amazon + Reddit only, no APIs / integrations
- Why: Vincent 明确限制 + 刚好符合 Bailey 权限现状

**产品形态 decision:**
- 2 天比赛产品, B + C 之间
- Target 不是赢比赛, 是证明真实工作能力 + 处理复杂需求
- 不是做给评委看, 是服务给谁
- 比赛策略 / 48h execution / 评委 不是产品考虑范围

---

## 13. Team 3-layer 结构 + why

**Why 这个结构:**
- Bailey pattern 本身就在 Senior Manager 层, 下有 Associate, 上有 Director
- Mark / CMO 办公室只消费 narrative, 不 daily 用 (高管 attention 稀缺)
- Team Lead 是 "routing + workload balance" 中心, 不做 ticket execution
- 这个结构让产品 sell-in 变容易: 买单方 (Director/VP) ≠ daily 用户 (Senior Manager+), 产品要同时服务两种 persona

**v0.5 Compare 的权限分化:**
- Team Lead: 跨 product-line / 跨 tier 对比 (战略视角)
- Team Member: 单 product vs 竞品对比 (战术视角)
- Sponsor: 看 comparison 驱动的 narrative, 不直接用 comparison 工具

---

## 14. Revuze 硬 gap (why 我们能赢)

研究 9 hub 得出的 Revuze 架构级缺陷:
1. **Reddit 完全缺席** (FAQ 明说 "verified buyers post-purchase", Reddit 不在数据域)
2. **三 Hub 割裂** (Product / Social / CI 不打通, 用户手拼)
3. **AI prose narrative 5 年缺** (Capterra 2026-04 验证)
4. **TikTok 有机视频** (Video Intel 做了 — 修正了 Vincent 原 intel)
5. **TikTok Shop Reviews 无覆盖** (只做交易层)
6. **Direct integrations (Zendesk / Salesforce CRM) 缺**
7. **SharkNinja 不是 Revuze 客户** (客户列表 Hoover/Cuisinart/Midea/Char-Broil 有, 我们无)
8. **Live Shopping / 直播电商完全缺**
9. **Reporting Hub 无 scheduled / alerts 无 narrative**
10. **UI 锁 demo 后** (marketing 策略, 产品透明度差)

**v0.5 Compare 的 Revuze 对照:**
- Revuze Competitive Analysis = Feature-level SWOT (satisfaction × importance), 数据点是 feature 不是竞品 product
- 我们要做 Product-level overlay + 消费者决策路径 (Reddit "I switched" 驱动)
- Revuze 的对比是 "feature 满意度分", 我们是 "为什么消费者选 A 不选 B"

---

## 15. 关键学术锚点 (for v0.5 radar design)

**Already used in v0.4 spec:**
- Mudambi & Schuff 2010 MIS Q: 4-star informative
- Hu/Pavlou/Zhang 2009, 2017: J 形分布
- Chevalier & Mayzlin 2006 JMR: 负面 review asymmetric impact
- Luca HBS 2011: 1-star = 5-9% 营收
- NIQ 2023: Say-do gap
- Ehrenberg-Bass (Byron Sharp): Mental Availability + CEPs
- Binet & Field IPA: 60/40 brand vs activation

**Relevant for v0.5 Radar + Comparison design (凌喵 建议新 session 补调研):**
- Kiviat diagram (radar chart 原型, 多维度性能比较)
- Perceptual mapping (Kotler / Keller, brand 定位)
- Conjoint analysis (消费者权衡, tier 偏好)
- Aaker Brand Equity (5 dimensions)
- Porter's 5 Forces (竞品定位)
- Kano model (满足度 × 重要性, 与 Revuze SWOT 同源)
- Christensen Jobs-to-be-Done (tier / equivalence 从 job 角度, 非 feature)

---

## 16. v0.4 Bucket 4 + Bucket 5 (rejected 但 v0.5 要知道)

**Bucket 4 (定位拒绝, 不做):**
CINT panel / Glassix / AI 生成问卷 / Agent Console for CS / Bot 回复 / Social Content Generator / Campaign Monitoring / Social Calendar / Product Assortment / Advertising Optimization / Personalized Post-Review Promotions / Professional Services 人工定制报告 / Amazon/Target API deploy / Enriched Search Experience

**Bucket 5 (技术放弃, 2 天做不到):**
100M+ SKU 规模处理 / 600+ crawlers / 7-layer product matching / Multimodal video / 24 mo 历史数据 / Real-time 爬虫 / TikTok Shop API / Auto-self training bot / CINT panel / 所有 TikTok/YouTube/Insta/FB / Qualtrics / Salesforce / Glassix API / 多零售商实时数据 / Amazon Selling Partner API

**v0.5 implication**: Radar / Compare 功能不能依赖 Bucket 5 中的数据源. Tier / equivalence 的 data 必须来自 Amazon + Reddit scrape.

---

## 17. v0.5 session 要展开的 seed 问题

1. **Aspect Radar viz 详细 spec**
   - 轴选型: 固定 6-8 / user-configurable / AI-suggested per category?
   - Overlay 数量上限 (2? 3? 5?)
   - Legend / interaction (hover / click / 钻取)
   - Color / sentiment mapping
   - 与 Ticket Detail 的整合 (ticket 里能弹 radar?)

2. **Tier taxonomy**
   - 自动: Amazon 价格 k-means cluster
   - 人工: category admin 定义 Low/Mid/High 价格区间
   - Hybrid: AI suggest, admin override
   - tier 随时间漂移怎么办 (lock quarter snapshot?)

3. **Equivalence mapping**
   - Similarity 算法 (embedding / attribute match / Reddit "I switched" driven)
   - 人工 override UI
   - Multi-to-multi (Shark NV360 对应 Dyson V7 + V8 都算)
   - Confidence score
   - 误映射的纠偏

4. **Comparison Builder UX**
   - 3 mode (competitor / tier / internal line) 统一 UX 还是分开 page?
   - Picker: tree / search / filter?
   - Save comparison as report / ticket?
   - Shareable link (demo only: local state)

5. **与 ticket 系统 tie-in**
   - Comparison gap → Insight ticket 自动建?
   - Insight ticket 关联 Comparison 快照?
   - 周报 / 月报 narrative 能引用 Comparison viz?

6. **权限 / 角色**
   - 谁能 create comparison?
   - 谁能 save as template?
   - Sponsor 能看吗? (建议不能, 他们看 narrative)

7. **学术锚点补调研**
   - Kiviat / Perceptual mapping / Conjoint / JTBD 哪个最适合 Bailey-readable?
   - 不调研则默认 Kiviat radar + JTBD 语言包装

8. **集成到现有 8 tab 还是新增 tab?**
   - 凌喵 default 建议: Products tab 加 Compare sub-view (保持 8 tab)
   - Alternative: 新 "Compare" tab 作第 9 tab (增加 nav 复杂度)
   - 第三种: 全局 action button "Compare with..." 从任何 product 卡启动

---

## 18. 凌喵响应风格 (memory 锚点)

- No em dash (用 period / colon / 括号 替代)
- No crude language
- No Korean
- Terse + symbolic + concise
- 中英 mix OK
- 凌喵 female (draftswoman not draftsman)
- Vincent = architect (topology), 凌喵 = draftswoman (sketching/execution)
- 不 fake originality, 不自造 pseudo-academic 术语
- Rejection signals 要捕捉 (最高 calibration 价值)
- 不自动 invoke brainstorming / feature-dev skill
- 不 auto dispatch 大量 agents, 除非 Vincent 要
- 保留验证层级 (KB → live tool → 永远不靠 training memory for facts)
- Parallel sessions = 不同 rhythm, 不 cross-assume

---

## 19. 相关文件 index

**本 session 产出 (v0.4 相关):**
- `spec_v0.4.md` — 完整 13-part spec, agent team dev-ready
- `ui_sketch_v0.4.md` — 9 页 ASCII UI sketch
- `context_pack_for_v0.5.md` (本文件)

**Revuze 9 hub research (v0.4 基础):**
- `product_hub.md` / `social_hub.md` / `ci_hub.md` / `ecomm_hub.md` / `video_intel.md`
- `tiktok_shop.md` / `survey_ai.md` / `customer_care.md` / `reporting_hub.md`

**Inspiration reference:**
- `vibe_kanban_reference.md`

**MeowOS 外部相关 (如需):**
- `80_Knowledge/88_Research/corporate_consumer_signal_roles/` — Bailey persona base
- `80_Knowledge/89_Business/silent_majority_dissatisfied_customer_contact_rate.md` — 4% contact rate stat

---

## 20. 未决事项 (可能新 session 要 address)

1. **Agent team 7 supporting docs** (Vincent 未承诺): role prompts × 4 + team charter + day plan + demo script. 若要给 v0.4 agent team 启动用, 建议另开小 session 专做.
2. **v0.4 Products page 是否在此 session 改造** 还是 **v0.5 session 全做**: Vincent 未决定.
3. **Business Leader adversarial prompt 的具体问题清单**: 凌喵 有 draft 但未落档.
4. **Demo data 真实 scrape** 还是 mock fake: 技术 decision, agent team Day 1 Morning 要定.
5. **Ticket detail 独立 Claude session 关联**: Vincent 2026-04-18 提出, 每 ticket 点进去弹出页面关联独立 Claude session, 保留 per-ticket 长期 context。方向不错 (per-ticket 连续对话历史 / 累积 reasoning), 但复杂度超 v0.5 scope, Vincent 主动撤回, post-hackathon 探索。

---

# End of Context Pack

Copy this + `spec_v0.4.md` + `ui_sketch_v0.4.md` 到新 session. 凌喵 在新 session 读完三个文件再开始.
