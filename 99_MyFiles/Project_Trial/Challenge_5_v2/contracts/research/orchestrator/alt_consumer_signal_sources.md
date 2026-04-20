# Alternative Consumer Signal Sources — Brainstorm

**Author:** backend-engineer-v3 (research window, 2026-04-11)
**Purpose:** Identify public data sources beyond the standard review APIs that reflect consumer sentiment, purchase intent, product quality signals, and defect patterns. Feeds R4+ data diversification strategy.

---

## Tier 1 — High signal, low friction, demo-viable

### Google Trends (pytrends)
**What it reveals:** Search query volume over time for product names and aspects ("Shark vacuum battery", "Ninja Foodi review"). Leading indicator of demand spikes and sentiment shifts — search interest often precedes review volume by 1-2 weeks.
**Access:** `pytrends` Python library (unofficial wrapper around Google Trends). No API key required. Free.
**Rate limits:** Unofficial — Google rate-limits aggressively. 5-10 queries per session, rotate user-agents. Unreliable for high-frequency polling but sufficient for weekly trend snapshots.
**Legal posture:** YELLOW. No official API; pytrends scrapes the UI. Google tolerates low-volume research use. Not suitable for production at scale.
**Demo viability:** GREEN for static snapshots. Show a "search interest" sparkline alongside sentiment — the combination (rising searches + falling reviews) = early warning signal.
**Unique value:** Only source that captures pre-purchase intent. All review APIs capture post-purchase. Google Trends fills the top-of-funnel gap.

---

### CPSC Recalls API + SaferProducts.gov API
**What it reveals:** Official product recalls (CPSC) and consumer harm reports (SaferProducts). For a consumer electronics dashboard, a recall or safety report cluster is the highest-severity alert possible.
**Access:** Both are official US government REST APIs. No API key required. Completely free. JSON/XML. Data from 1973 forward for recalls; SaferProducts uses OData standard.
**Rate limits:** No published limits. Government public API — effectively unthrottled.
**Legal posture:** GREEN. Public government data, no ToS concerns.
**Demo viability:** GREEN. Add a "Safety Recalls" layer to the Alerts page. A recall on a SharkNinja SKU would be the most actionable alert in the entire dashboard. Minimal implementation effort: one HTTP call to `https://www.cpsc.gov/cgi-bin/recalldb/results.aspx` or the recalls API endpoint, filter by brand name.
**Unique value:** No other data source in the current dashboard covers safety/recall signals. This directly supports Terri Williams (P4) use case — "page me before ticket volume spikes." A recall IS the spike.

---

### Reddit Niche Subreddits (beyond r/sharkninja)
**What it reveals:** Long-tail consumer opinion from highly engaged communities. Different signal quality than r/sharkninja — more specific, more expert, more problem-focused.
**Relevant subreddits for SharkNinja:**
- r/BuyItForLife — durability and long-term value signal
- r/Appliances — cross-brand comparison and failure reports
- r/Coffee — Ninja Espresso Bar / Coffee Bar coverage
- r/airfryer — Ninja Foodi DualZone coverage
- r/VacuumCleaners — Shark vs Dyson vs Roborock head-to-head
- r/homeautomation — Shark robot vacuum app/integration complaints
**Access:** Same PRAW OAuth path as r/sharkninja. Zero additional setup once PRAW is implemented.
**Legal posture:** Same as main Reddit integration — YELLOW for commercial use, non-commercial demo low risk.
**Demo viability:** GREEN. Expand subreddit query list in the `RedditScraper` implementation. High ROI addition.

---

## Tier 2 — High signal, moderate friction

### YouTube Review Channel Comments (Data API v3)
**What it reveals:** Consumer-facing review opinions from Wirecutter, MKBHD, Vacuum Wars, Consumer Reports YouTube channels. Comment sections on review videos contain high-quality comparative sentiment ("switched from Dyson to Shark after this video").
**Access:** YouTube Data API v3 — official, free up to 10,000 units/day. Already covered in `real_api_integration_proposal.md`.
**Unique angle here:** Target comments on specific SharkNinja competitor review videos (e.g. "Shark vs Dyson" comparisons) rather than only SharkNinja's own channel. Captures consideration-stage sentiment.
**Demo viability:** GREEN (already in R4 plan).

---

### eBay / Second-Hand Resale Prices
**What it reveals:** Resale price premium or discount as a quality proxy. High resale value = product holds quality perception. Flooded secondary market (many listings, low prices) = quality concerns or model discontinuation.
**Access:** eBay Finding API (official, free with developer account). Alternatively scrape completed listings.
**Legal posture:** GREEN for official API. Rate limits: 5,000 calls/day on free tier.
**Demo viability:** YELLOW. Interesting as a data signal story but requires an additional data model (price trend, not sentiment text). Non-trivial to integrate into the existing NLP pipeline. Better as a future standalone widget.

---

### Question Sites (Quora, Home Improvement StackExchange)
**What it reveals:** Pre-purchase questions and post-purchase problem reports. "My Shark Navigator is making a grinding noise" on StackExchange is a high-signal defect indicator.
**Access:**
- StackExchange: official API, free, 10,000 requests/day unauthenticated
- Quora: no official API; scraping is ToS violation
**Demo viability:** GREEN for StackExchange (home-improvement, cooking tags). YELLOW-RED for Quora.

---

### Discord Community Sentiment (Public Servers)
**What it reveals:** Real-time discussion in brand or category Discord servers. Faster-moving than Reddit, more conversational.
**Access:** Discord API requires bot registration. Public servers only — no auth required to read public message history via bots. Rate limits: 50 requests/second burst, 50 requests/second sustained per bot.
**Legal posture:** YELLOW. Discord ToS allows bots reading public messages for non-commercial research. Commercial use requires review.
**Relevant servers:** SharkNinja does not appear to have an official Discord. Relevant community servers: r/SharkRoboVacuums Discord, various coffee enthusiast servers.
**Demo viability:** YELLOW. Interesting signal but low SharkNinja-specific volume and requires server discovery step.

---

## Tier 3 — Niche, high-uniqueness signals

### Class-Action Lawsuit Patterns (CourtListener / PACER)
**What it reveals:** Legal filings are lagging but high-conviction quality signals. A class action about battery fires or motor failures is the most serious possible product quality signal.
**Access:** CourtListener (free REST API, no key required). PACER requires paid account ($0.10/page).
**Demo viability:** GREEN for CourtListener for the demo story ("we even monitor legal filings"). Query: `party_name:"SharkNinja"` or `docket_text:"vacuum"`.
**Unique value:** No social listening tool currently monitors legal filings. Genuine competitive differentiation story.

---

### Retail POS Data (Numerator / Nielsen)
**What it reveals:** Actual purchase data — units sold, price points, basket composition. Ground truth for demand.
**Access:** No public API. Nielsen and Numerator are paid enterprise data providers ($tens of thousands/year). Some partial public fragments appear in press releases and earnings calls.
**Demo viability:** RED for implementation. GREEN as a data story ("in production, we would integrate with Numerator for POS validation of our sentiment-demand correlation model").

---

### Warranty / Return Pattern Signals
**What it reveals:** Retailer-reported return rates and warranty claim spikes as defect leading indicators.
**Access:** No public API. Best Buy, Amazon, Walmart do not expose return data. Some inferred from review text ("returned it", "warranty claim") — already capturable from existing review pipeline with keyword extraction.
**Demo viability:** YELLOW — extract from existing review text as a derived signal rather than a new data source.

---

## Priority Recommendations for R4+

| Source | Round | Effort | Unique value |
|---|---|---|---|
| CPSC Recalls API | R4 | Low (1-2h) | Safety/recall alerts — unmatched urgency signal |
| Google Trends (pytrends) | R4 | Low (1-2h) | Pre-purchase demand leading indicator |
| Reddit niche subreddits | R4 | Minimal (add to PRAW query list) | Long-tail expert sentiment |
| StackExchange (Home Improvement) | R4 | Low (2-3h) | Pre-purchase problem discovery |
| CourtListener | R5 | Low (1h) | Legal filing monitoring — demo story value |
| eBay resale prices | R5 | Medium (3-4h) | Quality proxy signal |
| YouTube competitor video comments | R4 | Already planned | Consideration-stage sentiment |
| Discord | R5 optional | Medium | Real-time but low SharkNinja volume |
| TikTok Research API | R4 (if academic) | Medium | Gen-Z + viral product moments |
| Retail POS (Numerator) | Not in scope | Enterprise cost | Data story only |

---

*Research conducted 2026-04-11.*
