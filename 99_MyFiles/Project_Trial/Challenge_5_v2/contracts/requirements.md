# Consumer Sentiment Dashboard — Requirements (v1)

**Project:** SharkNinja Challenge 5 v2 — Consumer Sentiment Dashboard MVP
**Owner:** business-leader
**Status:** Active contract. Any change requires a new review round.
**Last updated:** 2026-04-11

---

## 0. North Star

SharkNinja's Consumer Intelligence team currently pays six figures/year to Brandwatch, Meltwater, or Talkwalker for social listening that treats a $600 Shark PowerDetect stick vac the same way it treats a hotel chain or a political candidate. Those tools are built for brand reputation; they are not built for **product reviews from people who actually own the appliance**. That mismatch is where this dashboard wins.

Our wedge is a **consumer-electronics-aware NLP layer** that correctly handles sarcasm, comparative claims, aspect-level sentiment, and the domain vocabulary of vacuums, blenders, air fryers and coffee machines. The dashboard is the delivery vehicle; the NLP is the product. A demo that shows pretty charts but a generic sentiment engine will lose this competition — and the edge-case test suite is how we prove the engine is real.

---

## 1. Personas

### P1 — Maya Chen, Consumer Insights Manager (SharkNinja HQ, Needham MA)
- **Scope:** Owns the monthly Consumer Sentiment Readout delivered to the Shark and Ninja GMs. Currently manually tags a sample of 500 reviews per SKU in a Google Sheet because Brandwatch keeps miscategorizing "the brushroll is jammed" as positive (it matches "the" + neutral VADER score).
- **Needs:** One dashboard that gives her a defensible top-line sentiment score per SKU per week, the ability to drill into the aspects driving movement (suction vs dustbin vs noise), and exportable evidence (quoted mentions) so she can defend the numbers in a room full of skeptical PMs.
- **Success for Maya:** She can kill the Google Sheet.

### P2 — Darius Okafor, Senior PM, Shark Robot Vacuums
- **Scope:** Owns the P&L for the Matrix, IQ and PowerDetect UV Reveal lineups. Every launch week he is on Slack asking "are people mad about X?" and waiting two days for insights to come back.
- **Needs:** Real-time view of sentiment on HIS SKUs, broken down by aspect (navigation, suction, app, self-empty base, mop function), with an alert the first time a new negative theme crosses threshold. He does not care about Ninja products. He does not care about aggregate brand sentiment.
- **Success for Darius:** The dashboard tells him a week before Twitter does that the UV Reveal's mopping pad is leaving streaks.

### P3 — Priya Ramanathan, Competitive Intelligence Lead
- **Scope:** Tracks Dyson, iRobot, Roborock, KitchenAid, Breville, De'Longhi. Reports into strategy. Today she builds decks by hand from Reddit threads because Brandwatch's "share of voice" metric is useless without quality context — 10,000 Dyson mentions of "my vacuum died" is a very different signal than 10,000 mentions of "so quiet".
- **Needs:** Head-to-head comparative sentiment that correctly credits WHICH brand "better" refers to in a comparison review, share-of-aspect (not just share-of-voice), and topic-level trend lines. The NLP must not be fooled by "Shark is way better than my old Dyson at edge cleaning."
- **Success for Priya:** Her quarterly competitive deck takes four hours instead of four days, and the numbers hold up in legal review.

### P4 — Terri Williams, Director of Customer Experience
- **Scope:** Runs the CX org that handles returns, warranty claims, and the 1-star reviews queue. Needs early warning on quality issues *before* they become a return spike.
- **Needs:** An alerts page that fires on rising negative aspects (e.g., "battery" sentiment dropping on the IP1251 cordless stick), with a severity score and direct links to the underlying mentions. She does not want to look at dashboards daily — she wants the dashboard to look at itself and interrupt her when something is wrong.
- **Success for Terri:** She gets paged about the dustbin latch issue a week before the support ticket volume spikes.

### P5 — Jordan Liu, Marketing Ops Analyst
- **Scope:** Plans campaigns across Shark + Ninja, needs to understand which aspects resonate in earned media (organic reviews/social) to shape paid messaging. Today relies on Sprout Social which blends owned + earned and doesn't break sentiment by aspect.
- **Needs:** Platform comparison (Reddit vs Amazon reviews vs YouTube comments vs Trustpilot) because the tone and topics differ wildly by channel — Reddit skews technical and sarcastic, Amazon skews aspirational, YouTube skews aspect-specific.
- **Success for Jordan:** Can answer "which aspect of the Foodi Dual Zone is driving the Reddit conversation vs the Amazon conversation, and are they the same?"

---

## 2. Requirements (REQ-IDs)

Legend: **P0** = gating, must ship for the entry to count. **P1** = strongly expected by judges. **P2** = nice-to-have, ship if time allows.

### P0 — Gating

- **REQ-001 (P0)** — NLP edge-case test suite MUST exist at `backend/tests/test_nlp_edge_cases.py`, MUST run against the real NLP pipeline (no mocks), and MUST cover the 12+ cases in section 3 of this document. Every case must have a FAILING-BEFORE / PASSING-AFTER record showing VADER-alone fails and the enhanced pipeline passes. **If this suite does not exist and run green, the project fails its own contract.**
- **REQ-002 (P0)** — Enhanced NLP pipeline MUST handle all four categories: sarcasm, comparative sentiment, aspect-based sentiment (ABSA), and consumer-electronics domain terminology. Domain lexicon lives at `backend/app/nlp/domain_lexicon.py` and MUST contain at least 40 terms specific to vacuums, kitchen appliances, coffee, and air care.
- **REQ-003 (P0)** — Backend MUST expose the scraper as a `BaseScraper` ABC with a `CSVAdapter` MVP implementation, wired via FastAPI `Depends(...)`. Routers MUST NOT import `CSVAdapter` by name. Real platform scrapers (Reddit, Trustpilot, etc.) MUST be droppable later without touching router code.
- **REQ-004 (P0)** — Pydantic models in `backend/models/schemas.py` are the single source of truth for API shapes. `contracts/api-contract.yaml` is a generated export of those models. Frontend reads the YAML, never the .py file.
- **REQ-005 (P0)** — Frontend MUST deliver five pages: Overview, Product Analysis, Platform Comparison, Topic Explorer, Alerts & Insights. Each page MUST answer a named business question from section 6.
- **REQ-006 (P0)** — Every sentiment number displayed in the UI MUST be traceable to the underlying mentions (one click to see the source quotes). Judges will test this — a chart without evidence is hand-waving.

### P1 — Strongly expected

- **REQ-010 (P1)** — Product filter hierarchy: Brand (Shark / Ninja / Competitor) → Category (Robot Vac / Cordless Stick / Upright / Air Fryer / Pressure Cooker / Blender / Ice Cream Maker / Coffee / Air Purifier) → Model (e.g., PowerDetect UV Reveal, Creami Scoop & Swirl, Foodi DualZone).
- **REQ-011 (P1)** — Time-range selector (7/30/90 days, custom) driving every chart on every page.
- **REQ-012 (P1)** — Sentiment breakdown per aspect — not just overall. A Shark Matrix with 4.2-star average sentiment but tanking "mop" aspect must be visually obvious.
- **REQ-013 (P1)** — Platform breakdown: Reddit, Amazon reviews, YouTube comments, Trustpilot, Twitter/X. MVP uses CSV fixture data tagged with a `platform` field; real scrapers come later.
- **REQ-014 (P1)** — Competitive view: Shark vs Dyson vs iRobot vs Roborock on vacuums; Ninja vs KitchenAid / Breville / De'Longhi / Keurig on kitchen.
- **REQ-015 (P1)** — Alerts page shows rising negative aspects with a severity score (volume × magnitude × recency) and links to exemplar mentions.
- **REQ-016 (P1)** — Topic Explorer surfaces emerging themes via aspect clustering (not just word clouds — word clouds are the Brandwatch default and visibly lazy).

### P2 — Nice-to-have

- **REQ-020 (P2)** — Export to CSV/PNG for any chart.
- **REQ-021 (P2)** — Sentiment confidence score displayed alongside each score (not just a number, but a "how sure" annotation — this is meaningful differentiation from incumbents who ship opaque numbers).
- **REQ-022 (P2)** — Language detection flag (P2 because MVP is English-only, but flagging non-English mentions as out-of-scope is better than silently mis-scoring them).
- **REQ-023 (P2)** — Dark mode.

---

## 3. NLP Edge Cases — Source of Truth for `test_nlp_edge_cases.py`

Every case below MUST become a test case in `backend/tests/test_nlp_edge_cases.py`. Input strings are verbatim. Expected outputs describe the business-correct behavior — the backend engineer decides the exact assertion shape but the semantics below are non-negotiable.

### 3.1 Sarcasm (must not score positive)

| # | Input | Expected |
|---|---|---|
| S1 | `"Oh great, another vacuum that dies after 3 months. Loving the warranty process."` | `overall_sentiment` label = `negative`. Compound score MUST be negative. VADER alone gets this wrong because of "great" and "loving". |
| S2 | `"Wow, a $400 blender that can't crush ice. Revolutionary."` | `overall_sentiment` = `negative`. "Wow" and "Revolutionary" must not pull the score positive. |
| S3 | `"The Creami is amazing if you enjoy 45 minutes of freezing and a rock-hard puck at the end."` | `overall_sentiment` = `negative`. "Amazing" must be detected as sarcastic given the conditional. |
| S4 | `"Ten out of ten would buy again. If I hated my floors."` | `overall_sentiment` = `negative`. The setup ("ten out of ten") is neutralized by the punchline. |

### 3.2 Comparative sentiment (credit the right brand)

| # | Input | Expected |
|---|---|---|
| C1 | `"Shark is way better than Dyson at edge cleaning."` | Two aspect-brand pairs emitted: `{brand: Shark, aspect: edge_cleaning, polarity: positive}` AND `{brand: Dyson, aspect: edge_cleaning, polarity: negative}` (or at minimum, relatively negative). A single averaged score is WRONG. |
| C2 | `"My old Keurig was louder but the Ninja coffee bar is way slower to brew."` | Keurig: `{aspect: noise, polarity: negative}`. Ninja: `{aspect: brew_speed, polarity: negative}`. Must not conflate. |
| C3 | `"Switched from iRobot to Shark Matrix and honestly I regret it. The iRobot was smarter at mapping."` | Shark: `polarity: negative` (switching regret). iRobot: `{aspect: mapping, polarity: positive}`. |
| C4 | `"Breville pulls a better shot than the Ninja espresso but the Ninja is half the price."` | Breville: `{aspect: shot_quality, polarity: positive}`. Ninja: `{aspect: price, polarity: positive}`, `{aspect: shot_quality, polarity: negative}`. |

### 3.3 Aspect-Based Sentiment (ABSA) — emit multiple aspects, not one averaged meh

| # | Input | Expected |
|---|---|---|
| A1 | `"Suction is incredible but the dustbin is tiny and the battery is garbage."` | Three aspects: `suction: positive`, `dustbin: negative`, `battery: negative`. NOT one neutral score. |
| A2 | `"The Foodi DualZone cooks fries perfectly but the basket coating started flaking after two months."` | `cooking_performance: positive`, `basket_coating/durability: negative`. |
| A3 | `"App is a mess, navigation is incredible, and the self-empty base is loud as hell but works."` | `app: negative`, `navigation: positive`, `self_empty_base: mixed` (or two sub-aspects: noise=negative, functionality=positive). |
| A4 | `"Coffee is great once you descale it weekly, which gets old fast."` | `coffee_quality: positive`, `maintenance: negative`. Must not average to neutral. |

### 3.4 Domain terminology (must recognize, not drop)

The domain lexicon MUST recognize at least these terms and preserve them through tokenization/lemmatization. Terms dropped as stopwords or mis-POS-tagged are a bug.

| # | Input | Expected |
|---|---|---|
| D1 | `"The HEPA filter needs replacing way too often and the brushroll tangles on long hair."` | Aspects extracted: `hepa_filter: negative`, `brushroll: negative`. Neither term silently dropped. |
| D2 | `"Cyclonic suction is great but the carafe is impossible to clean."` | Aspects: `cyclonic_suction: positive`, `carafe: negative`. "Cyclonic" and "carafe" both recognized as domain terms, not unknown tokens. |
| D3 | `"Descaling takes forever and the pod compartment jams."` | Aspects: `descaling: negative`, `pod_compartment: negative`. "Descaling" is coffee-domain; "pod" is coffee-domain. |
| D4 | `"The agitator bar picks up pet hair but the roller stops spinning when you hit a rug edge."` | Aspects: `agitator: positive`, `roller: negative`. Both vacuum-domain terms. |

**Required domain lexicon coverage (minimum 40 terms, non-exhaustive seed list):**
- Vacuums: `suction`, `brushroll`, `dustbin`, `HEPA`, `cyclonic`, `agitator`, `roller`, `canister`, `self-empty base`, `mop pad`, `edge cleaning`, `tangle`, `navigation`, `lidar`
- Kitchen: `carafe`, `descale`, `pod`, `basket`, `nonstick`, `crisper plate`, `dual zone`, `preset`, `blade assembly`, `pitcher`, `tamper`, `steam wand`, `portafilter`, `bean hopper`, `grinder`
- Air care: `HEPA`, `prefilter`, `CADR`, `ionizer`, `activated carbon`
- Hair: `barrel`, `plate`, `heat setting`, `ionic`
- General: `warranty`, `app`, `firmware`, `battery`, `runtime`, `charging dock`, `replacement part`

---

## 4. Competitive Benchmark

How our NLP layer beats the incumbents. Specific, not hand-wavy.

| Platform | Strength | Consumer-electronics weakness | How we win |
|---|---|---|---|
| **Brandwatch** | Huge data coverage (web, forums, news, 5yr history). Strong topic taxonomy for brand-level monitoring. | Sentiment engine is general-purpose and lexicon-heavy — treats "brushroll jammed" as neutral (dictionary miss) and "love this piece of junk" as positive (sarcasm miss). No native ABSA; aspects are surfaced only via topic clouds, which require manual curation. Default dashboards treat a $600 vacuum review the same as a hotel review. | Our ABSA is structural (dependency parsing + aspect classifier), not keyword-matching. Our domain lexicon means "brushroll" and "descale" are first-class entities. Our sarcasm heuristics catch the "love this piece of junk" case that Brandwatch scores +0.6. |
| **Sprout Social** | Excellent UX, tight integration with publishing/engagement workflows, good for marketing teams that also post content. | Listening is a bolt-on, not the core product. Sentiment is coarse (positive/negative/neutral, no aspects). Competitive analysis is share-of-voice only, no comparative sentiment within a mention. Heavy reliance on keyword rules — brittle for sarcastic reviewers. | We return per-aspect polarity and we correctly attribute comparative claims ("Shark is better than Dyson") to the right brand. Sprout will lump both brands into one score. |
| **Meltwater** | Best-in-class for PR and earned media: 270K+ news sources, deep archive, strong media contacts database. | Optimized for press mentions and executive briefings, not product review analysis. Sentiment model is tuned on news-article style text, not informal review text. Reddit/Amazon review coverage is shallow and the sarcasm/comparative problems compound on informal text. | Our pipeline is trained (and tested!) on informal product-review text. Our test suite explicitly catches the sarcasm cases that trip news-tuned models. |
| **Talkwalker (Hootsuite)** | 187-language coverage, 30+ social networks, decent AI-themed dashboards, visual listening (image/logo detection). | Strong on brand reputation, weak on aspect-level product sentiment. Generic sentiment model — does not distinguish "the app is bad" from "the vacuum is bad" in the same review. No domain lexicon for home appliances. Visual listening is a distraction for this use case. | Our Topic Explorer clusters by aspect, not by token frequency. Our test suite demonstrates — with failing-before/passing-after evidence — that we handle the cases generic engines miss. |

**The honest version:** Brandwatch / Meltwater / Talkwalker are not wrong for enterprise brand monitoring. They are wrong for consumer-electronics product sentiment at the SKU + aspect level. That is the gap we fill.

---

## 5. Judge-facing Success Criteria

Judges will evaluate this entry on five axes. Each axis maps directly to deliverables:

1. **NLP Quality (40%)** — does the edge-case test suite actually run, and does it actually pass on the enhanced pipeline while failing on VADER-alone baseline? REQ-001, REQ-002.
2. **Architecture Cleanliness (20%)** — is the scraper swappable, are the Pydantic models authoritative, is the contract versioned? REQ-003, REQ-004.
3. **Dashboard Utility (20%)** — do the five pages answer the five business questions in section 6? REQ-005, REQ-010 through REQ-016.
4. **Evidence & Traceability (10%)** — can any number on screen be traced back to the raw mentions with one click? REQ-006.
5. **Competitive Story (10%)** — does the README land the punch on why incumbents lose? Section 1 of README + section 4 of this doc.

**Demo script (suggested, non-binding):** open Overview, filter to Shark Robot Vacuums last 30 days, drill to PowerDetect UV Reveal, show aspect breakdown with mop streaking as a rising negative theme, click through to the sarcasm-laden Reddit exemplar, then switch to the test runner and show `pytest backend/tests/test_nlp_edge_cases.py` passing with 12+ cases green.

---

## 6. Dashboard UX — Pages and Business Questions

Every page answers exactly one named question. Frontend engineer should put the question in the page header as a subtitle.

### Page 1 — Overview
**Business question:** *"What is the state of consumer sentiment across our portfolio right now, and what changed this week?"*
- Top strip: total mentions, overall sentiment score, week-over-week delta, top 3 rising negative aspects, top 3 rising positive aspects.
- Main chart: sentiment time series, filterable by brand/category.
- Side panel: exemplar mentions (3 positive, 3 negative, quoted).
- Who it's for: Maya (P1) and executive read-outs.

### Page 2 — Product Analysis
**Business question:** *"For a specific SKU, what are people saying about each aspect of the product, and how is each aspect trending?"*
- Selector: brand → category → model (REQ-010).
- Main view: aspect table — rows are aspects (suction, dustbin, navigation, battery, app, self-empty, etc.), columns are mention count, sentiment score, 30-day trend sparkline, severity.
- Drill-through: click an aspect to see quoted mentions filtered to that aspect.
- Who it's for: Darius (P2).

### Page 3 — Platform Comparison
**Business question:** *"How does the conversation about this product differ across Reddit vs Amazon vs YouTube vs Trustpilot, and are the aspects the same?"*
- Grid: rows are platforms, columns are aspects. Cell color = sentiment, cell number = mention volume.
- Chart: top topics per platform side-by-side, clearly showing that (e.g.) Reddit cares about firmware while Amazon cares about packaging.
- Who it's for: Jordan (P5).

### Page 4 — Topic Explorer
**Business question:** *"What aspects are people talking about that we didn't pre-define — and are any of them gaining or losing ground?"*
- Emerging topics list (clustered aspects, not word clouds), sorted by momentum.
- Each topic: mention count, sentiment, trend, exemplar quotes.
- Comparative view: Shark vs Dyson (or Ninja vs Breville) on shared topics — SHARE OF ASPECT, not share of voice.
- Who it's for: Priya (P3).

### Page 5 — Alerts & Insights
**Business question:** *"What should I be paying attention to right now that I don't already know about?"*
- Alert list: rising negative aspects crossing severity threshold, sorted by urgency.
- Each alert: what changed (aspect X sentiment dropped Y%), when, which product, links to exemplar mentions, one-click acknowledge.
- Historical alerts view: recently fired alerts with disposition.
- Who it's for: Terri (P4).

---

## 7. Business-Level Data Model

Fields every mention/review object MUST carry. The backend engineer translates this into Pydantic at `backend/models/schemas.py` — do not treat this as a Python spec, treat it as a business-level contract the Pydantic must satisfy.

| Field | Type | Required | Notes |
|---|---|---|---|
| `mention_id` | string (uuid) | yes | Stable unique identifier. |
| `source_platform` | enum | yes | `reddit` / `amazon` / `youtube` / `trustpilot` / `twitter` / `other`. Extend via enum, never free-string. |
| `source_url` | string (url) | no (P1) | Where the original mention lives; null for closed sources. |
| `author_handle` | string | no | Anonymize/hash if GDPR-relevant. |
| `posted_at` | datetime (ISO-8601, UTC) | yes | When the mention was published. |
| `ingested_at` | datetime | yes | When our pipeline saw it. |
| `brand` | enum | yes | `shark` / `ninja` / `dyson` / `irobot` / `roborock` / `kitchenaid` / `breville` / `cuisinart` / `keurig` / `delonghi` / `other`. |
| `category` | enum | yes | `robot_vacuum` / `cordless_stick` / `upright` / `air_fryer` / `pressure_cooker` / `blender` / `ice_cream_maker` / `coffee` / `air_purifier` / `hair_tool` / `other`. |
| `product_model` | string | no (P1) | Specific SKU name, e.g., `PowerDetect UV Reveal`, `Creami Scoop & Swirl`, `Foodi DualZone`. Optional because platform scrapers don't always know the exact model. |
| `text` | string | yes | Raw mention text, pre-NLP. |
| `rating` | float | no | Source-provided star rating if available (Amazon, Trustpilot). |
| `language` | string (ISO-639-1) | yes | MVP assumes `en`; non-English mentions are flagged out of scope. |
| `derived.overall_sentiment` | enum | yes | `positive` / `negative` / `neutral` / `mixed`. |
| `derived.compound_score` | float [-1.0, 1.0] | yes | Single scalar for charting. |
| `derived.confidence` | float [0.0, 1.0] | yes (P1) | How confident the pipeline is. REQ-021 displays this. |
| `derived.sarcasm_flag` | boolean | yes | True if the sarcasm heuristics fired. Judges want to see this exposed. |
| `derived.aspects` | list of aspect objects | yes | Each aspect: `{name: string, polarity: enum, score: float, snippet: string}`. |
| `derived.comparative_pairs` | list | no (P1) | Each pair: `{brand: string, aspect: string, polarity: enum}`. Only populated when a comparative claim is detected. |

**Aspect name normalization:** aspects should be normalized to a canonical vocabulary (`suction`, `battery`, `app`, `navigation`, `dustbin`, `noise`, ...). Free-text aspect names are a bug; they break the Topic Explorer clustering.

---

## 8. Out of Scope for MVP

Not doing these, not apologizing for not doing them:

- Real-time live scraping. MVP uses CSV fixture data shaped like real Reddit/Amazon/Trustpilot/YouTube exports. The `BaseScraper` ABC means we can add real scrapers later — and not touching routers when we do is the whole point of REQ-003.
- Non-English sentiment. Flagged as out-of-scope per REQ-022; we refuse rather than mis-score.
- User authentication / multi-tenant. Single dashboard, single team.
- Writing back to source platforms (replying, engagement). This is a listening tool, not a management tool.
- Image / video sentiment. Text-only.

---

## 9. Change Control

This document is the contract. If backend-engineer or frontend-engineer need a requirement changed, they SendMessage business-leader — they do not edit this file. Review rounds write to `contracts/review-round-N.md`; those are amendments, this remains the source of truth.
