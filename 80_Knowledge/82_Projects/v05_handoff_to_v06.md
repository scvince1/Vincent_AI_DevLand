# Radar v0.5 → v0.6 Handoff
*2026-04-19 · for the incoming team*

---

## 一句话总览

**Radar** 是一个 **Signal Ops 平台**:把 Amazon 评论 + Reddit 讨论 → 规则引擎 + LLM → 带证据链的优先级工单 → 团队看板 → 解决追踪。目标用户是 Category Manager,他们当前分散在"Amazon 后台 / Reddit / Slack"三处看信号,Radar 把它们合并为一条优先级队列。

---

## 架构速览

| 层 | 栈 | 入口 |
|----|-----|------|
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, Anthropic SDK | `server/app/main.py` → :8000 |
| **Frontend** | Next.js 14 (app router), React 18.3, TypeScript 5.5, Tailwind, Vitest | `web/app/` → :3000 |
| **DB** | SQLite (demo),PostgreSQL-ready (ORM 已抽象) | 23 张表,见下文数据模型 |
| **LLM** | Claude Opus 4-7(推理/轴挖掘/工单起草) + Sonnet 4-6(NL 查询/CRP 标签) | `server/app/llm/*` |

---

## 功能模块一览

### A. Dashboard / Inbox(工单中枢)
- `/dashboard` — 4 张 KPI 卡(OPEN / OVERDUE / RESOLVED/WEEK / IMPACT)+ 优先队列 + CEP 微地图 ✅
- `/inbox` — 卡片式工单列表 ✅;**点击详情 4-tab modal 未接通**(INT-39 blocker)
- 工单生命周期:`New → In Review → Blocked → Resolved → Closed`,支持去重(dedup-check 阈值 0.85)和 cluster-merge
- 五种类型:`Opportunity / Threat / Insight / Strategic / Question`

### B. Products / Compare(产品对比)
- `/products/browse` — 产品目录,支持 brand/category/price_tier 筛选 ✅
- `/products/compare` — **核心差异化功能**:SKU × 评价轴矩阵 → Gap 列高亮 → 一键生成 Insight Ticket ✅(INT-33 刚修完)
- `/products/[brand]` — **Halo 品牌页缺失**(INT-40,v0.6 要么补,要么把 demo 第 6 节改写)❌

### C. Evidence(证据聚合)
- `/evidence` — 筛选(source/category/日期/严重度),每条评论/帖子带 **CRP 三标签**(Complaint / Root-Cause / Problem) ✅
- "Create Insight from this" 一键从单条证据起草工单 ✅

### D. Team Queue(看板)
- `/team` — 四栏看板(New / In Review / Blocked / Resolved)+ 拖拽 + WIP 计数 + assignee 切换 ✅
- **依赖风险**:`@dnd-kit/core`、`@dnd-kit/utilities` 曾一度丢失,现已补回

### E. Signal Engine(信号引擎)
- 四类规则:`RatingDrop` / `VolumeSpike` / `KeywordMatch` / `CRP`(跨平台回声)
- `POST /api/signal/detect/run` → 扫规则 → 生成 `signal_events` → 可 one-click 转工单
- **隐患 INT-34**:`signal_events` 表有两份 schema(ORM vs `signal/db.py` raw SQL),重启顺序不对会 insert 失败

### F. Aspect Axes + Radar(评价轴挖掘)
- LLM 从评论语料挖掘出类目评价轴(durability / suction-quiet / battery-life …)
- `/admin/aspect-axes` — 草稿 → 逐个/批量 approve → 出现在 Compare 选择器 ✅
- Category Radar:类目中位数轮廓,供品牌页 + CEP micromap 使用

### G. Tier Taxonomy(价格段分层)
- k-means 自动聚类出 Low/Mid/High 三档,管理员可 override 区间
- `/admin/tier-config` — 按 `(category, quarter)` 维度的 3 档配置 ✅
- 供 What-if 模拟器 + Gap 检测使用

### H. Watched Groups(关注组)
- 用户自定义产品组合(items_json),用于持续对比 ✅ CRUD 完整

### I. What-If Simulator(情景模拟 — INT-32 刚上)
- `POST /api/whatif/new_product` — 假设新 SKU:自动划档、预估信号量、生成草稿工单
- `POST /api/whatif/marketing` — 假设营销动作(降价 / 加功能)→ Gap 闭合预测
- 所有 run 入 `whatif_scenarios` 表,可回放

### J. NL Query / Steward(自然语言查询 + 每日通讯)
- `POST /api/nl/query` — 问 "为什么 V15 上周五评分掉了?" → Claude Sonnet 基于工单语料回答并引证 ticket ID
- `/steward/daily` — 昨日摘要 + 事件时间线(评分跌 → 抓取 → 规则触发 → 工单 → 解决)
- `/steward/cep` — **CEP 热力图**(Category × Event-Phase,红=问题多)

### K. Narratives(周报/品牌故事)
- 自动生成 `weekly / monthly / quarterly / event` 四种叙事,Markdown 起草 → 可编辑 → PDF 导出
- **九宫格护城河图**(3×3 类目-竞品矩阵)已实现

### L. Admin Panel(运营后台)
- 已完成:`/admin/aspect-axes`、`/admin/tier-config`
- **部分存根**:`/admin/team`、`/admin/signal-rules`(endpoint 已通,表单 UI 未完成)
- **占位**:`/admin/integrations`、`/admin/data-sources`

---

## 数据模型(23 张表)

```
products        ── amazon_products / amazon_reviews / amazon_qa
                 └─ reddit_threads / reddit_comments / subreddits
signals         ── signal_rules / signal_events
tickets         ── tickets / activity_log / related_ticket_ids_json
radar           ── aspect_axes / sku_aspect_scores / comparison_snapshots
tier & groups   ── tier_configs / skus / watched_groups
narratives      ── narratives / team_members / users
what-if         ── whatif_scenarios
```

关键枚举:`Ticket.type(5)`、`Ticket.severity(3)`、`Ticket.status(5)`、`TierName(3)`、`AutoRefreshMode(4)`。

---

## 数据来源

| 源 | 脚本 | 说明 |
|----|------|------|
| **Amazon 商品/评论** | `scripts/scrape_amazon.py` | 爬详情页 + McAuley 2023 数据集导入;支持 `--amazon-window` 时间窗 |
| **Amazon Q&A** | INT-20 McAuley importer | 产品级问答入 `amazon_qa` |
| **Reddit** | `scripts/scrape_reddit.py` | PRAW OAuth(首选)+ 公共 JSON 降级;10 个订阅种子列表;合成语料兜底 |
| **Reddit 增量** | INT-28 pullpush.io | v0.5 后加入,实时增量(post-merge) |
| **LLM** | `ANTHROPIC_API_KEY` | 缺失时 aspect 挖掘 / CRP / NL 查询会**静默降级到 fixture**(坑,见下) |

---

## v0.6 接手必读:高优先级 TODO

### 🔴 HIGH(阻塞 demo 或核心流程)

| 编号 | 问题 | 文件定位 | 预估 |
|------|------|----------|------|
| **INT-39** | 工单详情 4-tab modal 未接通(Evidence / Related / History / Activity);History 端点还没做 | `web/components/ticket-detail/*`、新建 `GET /api/tickets/{id}/history` | 50 min |
| **INT-40** | Halo 品牌页缺失(`/products/[brand]`);`GET /api/brands/{brand}/halo` 未定义。**Option A**=补页面 / **Option B**=改写 demo_flow.md 第 6 节 | `web/app/products/[brand]/` | A: 90 min / B: 15 min |
| **INT-36** | CORS 写死 `["http://localhost:3000", …]` | `server/app/main.py:45` → 读 `CORS_ORIGINS` env | 20 min |
| **INT-37** | `POST /api/tickets` 不接受 seed fixture shape(list→TEXT 列没有 Pydantic coerce) | 加 `TicketCreate` schema + service 转换 | 40 min |
| **Schema drift** | `TierConfigRow` TS interface 少字段(`approved_by_admin_at`、`cluster_size`、`is_override`);`PATCH` 缺 `clear_price_max` | `web/lib/api.ts:140` | 15 min |
| **Missing exports** | `SEVERITIES / TICKET_TYPES / ActivityLogEntry / Ticket / ComparisonSnapshotRef / EvidenceItem / searchEntities` 未导出 → TS 编译不过 | `web/lib/types.ts`、`web/lib/compare/api.ts` | 30 min |

### 🟡 MEDIUM(非阻塞但有 WIP)

- **INT-34**:`signal_events` 表双 DDL 源,必须收敛到 ORM。
- **INT-27 残留**:Reddit scraper 写 `url_matched_products`,ORM 要 `url_matched_products_json`,冷启动 race。
- **Admin forms**:`/admin/team`、`/admin/signal-rules` 表单 UI 空壳。
- **Model 重复**:`Sku`、`TierConfig` 在 `app.models` 和 `app.tier.models` 都有定义,靠 `extend_existing=True` 黏合。

### ⚠️ 隐坑(latent)

1. **LLM 静默降级**:没有 `ANTHROPIC_API_KEY` 时 6 个功能(aspect mining / CRP / NL / ticket draft / gap detect / narrative)**无声**走 fixture,用户不会知道。v0.6 应加 banner 或降级提示。
2. **Tier k-means 不稳定**:无固定 seed,重跑 `run_tier_kmeans.py` 会得到不同边界。建议加版本/指纹到 `TierConfig.generated_at`。
3. **信号规则漂移**:规则 seed 时注入,params_json 改了不会回溯匹配历史 `signal_events`,没有迁移路径。
4. **DB 路径解析混乱**:INT-33 已加 `RADAR_DB` env var 规约,但确认所有脚本都用它。

---

## 最近三周做了什么

| 票 | 内容 |
|----|------|
| **INT-31** | 端到端 demo 验证 + 9 页审计报告,发现 20 处 schema drift |
| **INT-32** | What-if 模拟器前端 + McAuley 时间窗 flag + whatif route envelope 修正 |
| **INT-33** | 补齐后端路由(`GET /api/team`、`GET /api/signal/rules`),清掉 UI 的 "API not ready" banner |

当前分支:`vk/a994-`(刚从 `vk/b672-scv-int-33-wire` 合入 main,commit `3cea25c`)。

---

## v0.6 建议路线(推测,待团队确认)

1. **FE-TICKET-02 完工**(INT-39):4-tab 详情
2. **Admin UI 全量化**:Team / SignalRules / Integrations 页面补齐
3. **Signal Rule UX**:从 UI 直接创建/编辑规则,不再只靠 DB seed
4. **Brand/Halo 页**(INT-40):品牌级 radar + Halo score
5. **Schema 收敛**(INT-34):ORM 作为单一 DDL 权威 + Alembic 迁移
6. **Qualtrics 集成 PoC**:NPS + 反馈入 signal 源
7. **性能**:Signal detection 异步队列,aspect mining 结果按 `(category, version)` 缓存
8. **移动适配**:Inbox + Team Queue 目前是 desktop-first

---

## 测试现状

- **后端**:24 个 pytest 文件,核心域覆盖率 ~60–70%。`pytest server/tests/`
- **前端**:Vitest 2.0.5 + RTL 16.0 + jsdom;localStorage mock 已到位(Node 22 兼容)
- **缺口**:admin/integration 层几乎无测试

---

## 关键入口文件速查

| 域 | 核心文件 |
|----|----------|
| Tickets | `server/app/tickets/*`, `web/app/inbox/`, `web/components/ticket-card/` |
| Products & Compare | `server/app/radar/*`, `web/app/products/compare/` |
| Signal | `server/app/signal/*`, `server/app/signal/db.py`(⚠️ 重复 DDL) |
| Tier | `server/app/tier/*`, `scripts/run_tier_kmeans.py` |
| Narrative | `server/app/narrative/*`, `web/app/narratives/` |
| LLM | `server/app/llm/aspect_mining.py`, `ticket_draft.py`, `gap_detect.py`, `nl_query.py`, `crp.py` |
| Scrapers | `scripts/scrape_amazon.py`, `scripts/scrape_reddit.py`, `scripts/demo_seed.py` |
| 配置 | `server/app/main.py`(CORS 硬编码!), `server/app/settings.py`, `.env.example` |

---

*Handoff 作者:Claude (Opus 4.7, 1M context) · 2026-04-19*
