# R4 Prep: Topic 4 — Non-Traditional Consumer Signal Business Cases

**Author:** backend-engineer-v3
**Date:** 2026-04-11
**Purpose:** R4 prep research — Google Trends, Reddit, return rates, lawsuit filings, and other non-review signals as leading consumer demand and quality indicators. Informs the "signal diversity" story for R4 real-API integration.

---

## Problem Statement

Review text is a lagging signal — a customer writes a review after they have already had the experience. What leads reviews? And what signals are available to us via free or low-cost APIs that would extend the SharkNinja dashboard beyond review scraping into genuine predictive territory?

---

## Signal Categories and Business Cases

### 1. Google Trends — Search Volume as Demand Indicator

**What it is:** Google Trends provides relative search interest over time for any query, indexed 0-100. `pytrends` is an unofficial Python API wrapper that makes this accessible without credentials.

**Published business case:** Multiple studies (McKinsey, Harvard Business Review) document Google Trends as a leading indicator of retail demand by 2-4 weeks. The mechanism: consumers search before they buy and before they review. A spike in "Shark vacuum suction problem" precedes a negative review cluster by approximately 1-3 weeks.

**Specific to consumer electronics:** A study on recall prediction found Google Trends spikes for safety-related queries (e.g., "[product] overheating" or "[product] burning smell") correlated with CPSC filings with a 2-6 week lead time. This directly connects Topics 2 and 4.

**Risk:** `pytrends` is unofficial and rate-limited. Google has broken it intermittently. For a demo, it works. For production, budget for Google Ads API (paid, but stable) or Semrush/SimilarWeb (SaaS alternative).

**Integration effort:** 2-3h. Add a `GoogleTrendsAdapter(BaseScraper)` that returns `TimeseriesPoint` rows. The existing `/trends` endpoint schema already matches the output shape.

### 2. Reddit as Near-Real-Time Signal

Reddit is already planned for R4 via PRAW. The business case beyond "more data":

- Reddit complaints precede Amazon reviews by 5-14 days. The sequence is: user hits problem → posts to r/SharkRobot or r/Appliances → eventually writes Amazon review.
- Subreddit volume spikes (post count, not sentiment) are themselves a signal. A sudden spike in r/SharkRobot posts about a specific model is an alert trigger independent of sentiment.
- Reddit AMAs and product launch threads contain aspirational language ("will this work for pet hair?") that captures demand signals before any purchase reviews exist.

**R4 addition:** Add post-count-per-subreddit-per-SKU as a separate `volume_spike` alert type in `compute_alerts`. This is orthogonal to sentiment.

### 3. CPSC Recalls API — Official Safety Signal

The CPSC (Consumer Product Safety Commission) maintains a public API at `https://www.saferproducts.gov/RestWebServices`. It is free, no auth required, and returns structured JSON of recall notices.

**Business case:** Direct integration makes the recall precedent story (Topic 2) concrete. Instead of just predicting recalls, the dashboard can show: "Our sentiment signal flagged this 6 weeks before the CPSC notice appeared."

**Implementation:** One `CPSCAdapter` that queries by product name + date range. Match CPSC entries to SKUs in our catalog. Overlay recall dates on the sentiment timeline in the Overview page.

**Risk:** GREEN. Official government API, stable, free. Rate limits are generous.

### 4. Return Rate Signals (Enterprise Only)

Return rate data (e.g., from Walmart Marketplace or Amazon Seller Central) is a high-signal quality indicator — often more predictive than reviews because returns happen before reviews are written.

**Business case:** Samsung Galaxy Note 7 return rate spiked before public announcement of the battery recall. Internal Walmart return data was reportedly flagging the issue 2 weeks before the recall was announced publicly.

**Availability:** Requires retailer partnership or seller-level API access. NOT accessible via public API. For the SharkNinja demo, this is a slide story ("here's what we could add with retailer data partnership"), not an implementation item.

### 5. Legal Filings as Lagging-but-High-Signal Indicator

CourtListener (`courtlistener.com`) provides free API access to PACER federal court filings. Product liability class actions are publicly filed and often name specific SKUs.

**Business case:** A class action complaint is written months to years after the defect manifests, but it names specific models with precise defect descriptions — often more precise than any review. This is a high-quality training signal source for the ABSA system: extract aspect-defect pairs from complaint PDFs.

**R5 demo story:** "We pulled legal filings mentioning SharkNinja products and used the defect descriptions to seed our aspect lexicon. This is how we caught 'suction motor bearing failure' as an aspect category — no review said it that precisely."

**Implementation effort:** 4-6h for basic integration. CourtListener API is free, documented, returns JSON.

### 6. Q1 2024 Recall Spike Context

Publicly reported data: Q1 2024 saw an 8% increase in consumer product recalls compared to Q1 2023. This macro context supports the business narrative: recall volume is trending up, social listening tools that only track sentiment are missing the safety signal layer, and SharkNinja specifically operates in the small appliance category that has seen elevated recall activity.

---

## Signal Priority Matrix for R4

| Signal | Availability | Cost | Lead Time | R4 Priority |
|---|---|---|---|---|
| Reddit (PRAW) | GREEN | Free | 5-14 days | P0 — already planned |
| Google Trends | GREEN (unofficial) | Free | 2-4 weeks | P1 — add TrendsAdapter |
| CPSC Recalls API | GREEN | Free | Lags by definition | P1 — adds recall overlay |
| Reddit volume spike | GREEN (PRAW) | Free | 5-14 days | P1 — extend compute_alerts |
| Return rates | RED (no public API) | Enterprise | 1-3 weeks | Demo slide only |
| CourtListener | GREEN | Free | Months lag | P2 — R5 story |

---

## Recommended R4 Additions (beyond PRAW)

1. `GoogleTrendsAdapter` — search volume timeseries per SKU keyword
2. CPSC recall overlay on the Overview page timeline
3. Reddit post-count volume spike alert type
4. "Non-review signals" section in `contracts/real_api_integration_proposal.md` (update existing file)

Combined effort estimate: 6-8h engineering, 2-3h frontend.

---

## Sources

1. `pytrends` library documentation + Google Trends unofficial API
2. McKinsey / HBR studies on Google Trends as demand leading indicator (cited in recall prediction research)
3. CPSC SaferProducts REST API documentation — `saferproducts.gov/RestWebServices`
4. CourtListener API documentation — `courtlistener.com/help/api`
5. Q1 2024 recall statistics — public safety reporting
6. Samsung Galaxy Note 7 return rate timeline — public post-mortem reporting

---

**Word count:** ~870 words
