# Real API Integration Proposal — Round 4 Execution Plan

**Author:** backend-engineer-v3
**Date:** 2026-04-11
**Status:** Proposal (Round 4 execution target)
**Audience:** team-lead, business-leader-v2, future backend-engineer-v4

---

## Purpose

This document specifies how Round 4 will replace the 300-row CSV fixture data with live platform data via legal-safe integration paths. It covers all five platforms present in the current fixture data (Reddit, Amazon, YouTube, Trustpilot, Twitter/X) plus recommended supplemental sources (Hacker News, GNews) identified in the API landscape audit (`contracts/research/orchestrator/real_api_landscape.md`).

This document does NOT include any implementation code. It is a planning document only. Round 4 engineers execute from this spec.

---

## Primary Recommendation: Reddit + Hacker News (2-source combo)

**Recommended combo score: 21/25 (Reddit) + 23/25 (HN) = best achievable without paid commitments.**

These two sources are the priority R4 integration target. Together they provide:
- High-volume organic consumer sentiment (Reddit, 100K+ SharkNinja subreddit members)
- Tech-media and analyst signal layer (Hacker News, Wirecutter coverage, product recalls)
- Zero cost, zero paid-tier requirements
- Complementary audience profiles (mass consumer vs. tech-savvy early adopter)
- Combined implementation effort: 3-5 hours from zero to 100+ mentions

**Optional secondary:** GNews for press/media and product recall coverage (~1 additional hour, 20/25 score).

---

## Platform Coverage

---

### 1. Reddit

**Access Method**
- Library: PRAW (Python Reddit API Wrapper), v7.x, available via `pip install praw`
- Auth: OAuth 2.0 client credentials flow
- Setup: Register app at `reddit.com/prefs/apps` (script type), obtain `client_id`, `client_secret`, `user_agent` string
- Implementation: ~10 lines of Python to authenticate and query

**Rate Limits**
- Authenticated (OAuth 2.0): 100 requests per minute (QPM), averaged over 10-minute rolling window
- Rate limit applies per OAuth client ID
- Unauthenticated access: blocked entirely as of Reddit's 2023 API changes
- 100 mentions achievable in under 30 minutes of fetch time

**Legal Posture**
- Risk level: **MEDIUM** for demo/commercial use
- Non-commercial research/demo: Low risk under Reddit's API ToS
- Commercial product or investor demo framed as production SaaS: Medium-High — Reddit ToS prohibits commercial use of the free tier without explicit Reddit approval and possible licensing fees
- **Action required before Round 4 production deploy:** obtain Reddit's commercial API approval OR limit demo to clearly non-commercial research framing
- Scraping without OAuth: prohibited and blocked — do not use

**Historical Data Alternatives**
- Pushshift: **Dead.** Shut down for public access by Reddit in 2023. Access now restricted to Reddit-approved moderators only. Do NOT use.
- PullPush (pullpush.io): Community successor to Pushshift. Currently disabled/intermittent as of 2026-04-11. **Unreliable — do not depend on it.**
- Arctic Shift (arctic-shift.photon-reddit.com): More stable alternative for historical data. Handles simple per-subreddit queries. Limitation: no full-text search without specifying a subreddit; no filtering by score or comment count. Use only for historical backfill, not primary query path.

**Estimated Cost**
- Free tier (non-commercial): $0
- Commercial licensing: contact Reddit Developer Platform (no published price as of research date)

**Schema Additions Required (backend/models/schemas.py)**

The current `Mention` model already covers most Reddit fields. Additions needed:
```python
# On Mention model, optional fields to add:
reddit_score: Optional[int] = Field(default=None, description="Upvote score (post or comment)")
reddit_num_comments: Optional[int] = Field(default=None, description="Comment count (posts only)")
reddit_subreddit: Optional[str] = Field(default=None, description="Subreddit name without r/ prefix")
reddit_flair: Optional[str] = Field(default=None, description="Post flair label if present")
```

**Target subreddits for SharkNinja:** r/sharkninja, r/airfryer, r/instantpot, r/RoombaCombo, r/homeautomation, r/VacuumCleaners

**Round 4 Scope Estimate:** 3-4 hours (OAuth setup + PRAW scraper class implementing BaseScraper ABC + subreddit query + field mapping)

---

### 2. Amazon

**IMPORTANT: There is no official Amazon reviews API.**

**Official API Reality**
- Amazon Product Advertising API (PA API): Does NOT return review text. Returns product metadata, pricing, and ASIN lookup only. Requires an active Amazon affiliate account with qualifying sales. Zero sentiment value.
- Amazon has no public review API endpoint. Their Terms of Service explicitly prohibit programmatic access to review content.
- Direct scraping: clear ToS violation, actively enforced, legal exposure risk. Do NOT implement.
- Third-party scraping services (Bright Data, Apify, Canopy API, ScrapeHero): ToS violation outsourced, legal gray zone, cost $0.002-0.01 per review, not suitable for a production dashboard for a public company demo.

**Legal Posture**
- Direct scraping: HIGH risk — ToS violation, legal exposure
- PA API for review text: NOT POSSIBLE (endpoint does not exist)
- Third-party scraper API: MEDIUM-HIGH risk (ToS violation outsourced)
- UCSD academic dataset: LOW risk (see Offline Corpora section below)

**Round 4 Amazon Coverage Path**
Amazon brand coverage in the dashboard MUST use the UCSD Amazon Reviews academic corpus as the historical baseline. Live Amazon review data cannot be obtained via a clean legal path without paid third-party intermediary and legal sign-off.

**Schema Additions Required**
No new fields needed for the offline corpus path. The existing `rating` field on `Mention` maps to Amazon star ratings. `source_platform = "amazon"` already exists in the `SourcePlatform` enum.

**Round 4 Scope Estimate:** 1-2 hours for CSV/JSONL ingest adapter reading the UCSD dataset (offline only, no live scraper)

---

### 3. YouTube

**Access Method**
- API: YouTube Data API v3 (official Google API)
- Library: `google-api-python-client` or direct REST calls
- Auth: API key (for public data reads) or OAuth 2.0 (for user-specific data)
- Registration: Google Cloud Console, create project, enable YouTube Data API v3, generate API key

**Rate Limits**
- Free quota: **10,000 units per day**
- Comment list request: 1 unit per page (up to 100 comments per page)
- Video search: 100 units per request
- At 10,000 units/day: approximately 100 searches or 10,000 comment pages per day
- Sufficient for demo volume; insufficient for high-frequency production polling

**Legal Posture**
- Risk level: **LOW** for reading public video comments
- YouTube Data API is an official Google API with permissive terms for non-commercial and commercial use at reasonable scale
- Must comply with YouTube API Services Terms of Service: no storing data beyond policy limits, must delete on user request
- Scraping YouTube without the API is prohibited

**Estimated Cost**
- Free quota (10,000 units/day): $0
- Exceeding quota: $0.003 per 1,000 additional units

**Data Available**
- `commentId`, `textDisplay` (comment text), `authorDisplayName`, `likeCount`, `publishedAt`, `updatedAt`
- Video metadata: `title`, `description`, `statistics.viewCount`, `statistics.likeCount`, `publishedAt`, `channelTitle`
- Target query: search for "SharkNinja", "Shark vacuum", "Ninja Foodi", "Shark IQ robot" etc.
- Comment threads on SharkNinja official channel and major tech review channels (Wirecutter, Consumer Reports, MKBHD)

**Schema Additions Required**
```python
# On Mention model, optional fields to add:
youtube_video_id: Optional[str] = Field(default=None, description="YouTube video ID (e.g. 'dQw4w9WgXcQ')")
youtube_channel_id: Optional[str] = Field(default=None, description="Channel ID for provenance")
youtube_like_count: Optional[int] = Field(default=None, description="Comment like count")
```

**Round 4 Scope Estimate:** 2-3 hours (API key setup + search + comment list scraper implementing BaseScraper ABC + field mapping)

---

### 4. Trustpilot

**Access Method**
- API: Trustpilot Business API (private, paid)
- Public Business Units API: API key (client_id) only — easy setup, but returns aggregate stats only, NOT individual review text
- Private API (full review text): OAuth 2.0 — requires a paid Trustpilot business account

**Rate Limits**
- Public API: not published; typical developer usage is unthrottled for aggregate queries
- Private API (paid): quota depends on plan tier

**Legal Posture**
- Risk level: **LOW** if using official API
- Scraping Trustpilot: MEDIUM-HIGH — their ToS prohibits it and they actively pursue scraping operations
- **CRITICAL CONSTRAINT: Review text access requires a paid business account.** The free plan returns aggregate statistics (average rating, review count) only. No review text, no sentiment signal without paid plan.

**Estimated Cost**
- Free plan: $0, but NO review text access
- Paid business plan: contact Trustpilot sales (no published pricing)

**Round 4 Coverage Decision**
Trustpilot cannot be integrated as a live review text source without a paid Trustpilot business account. Two options for Round 4:

**Option A (Recommended):** Keep Trustpilot coverage via existing CSV fixtures only; display a note in the dashboard UI explaining Trustpilot data is from a sampled snapshot due to API access limitations.

**Option B (If budget available):** Obtain a paid Trustpilot business account, implement OAuth 2.0 private API integration. Scope estimate: 3-4 hours once account is provisioned.

**Schema Additions Required**
```python
# On Mention model, optional field to add:
trustpilot_review_id: Optional[str] = Field(default=None, description="Trustpilot reviewId for deduplication")
```

**Round 4 Scope Estimate:** 1 hour (ingest adapter for existing snapshots, OR 3-4 hours with paid account)

---

### 5. Twitter / X

**IMPORTANT: Free tier is nonfunctional for search. This platform is not viable for demo integration without paid budget.**

**Current Pricing Structure (2025-2026)**
- Free tier: ~1 GET request per 15 minutes, no search endpoint, posting only at meaningful volume. Not usable for pulling SharkNinja mentions.
- Basic tier: $100/month — 10,000 tweet reads/month. Limited search. ~330 reads/day at this limit is marginal for dashboard use.
- Pro tier: $5,000/month — 1,000,000 tweet reads/month
- Enterprise: $42,000+/month
- Pay-as-you-go (launched broadly Feb 2026): credit-based, variable per-endpoint pricing, $10 voucher for free-tier users switching over

**Legal Posture**
- Risk level: **LOW** for official API use
- Scraping X/Twitter: **HIGH** — active legal enforcement, Cloudflare protection, history of legal action against scrapers

**Round 4 Coverage Decision**
Twitter/X integration is **not recommended for Round 4** unless the team has explicit budget approval for the Basic tier minimum ($100/month). The free tier cannot support search at any useful volume.

**If budget is approved for Round 4:** implement via official X API v2, `tweepy` library, Bearer Token auth, search endpoint filtered for "SharkNinja" and product-specific terms. Estimated effort: 2-3 hours once API access is confirmed.

**Schema Additions Required (if implemented)**
```python
# On Mention model, optional fields to add:
twitter_tweet_id: Optional[str] = Field(default=None, description="Twitter/X tweet ID for deduplication")
twitter_retweet_count: Optional[int] = Field(default=None)
twitter_like_count: Optional[int] = Field(default=None)
```

**Round 4 Scope Estimate:** NOT IN SCOPE unless $100/month budget approved. Flag to team-lead before Round 4 kickoff.

---

## Offline Corpora (Historical Baseline)

---

### UCSD Amazon Reviews Dataset

**Source:** Julian McAuley / UCSD CSE lab — publicly released academic corpus
- Dataset v2023: https://amazon-reviews-2023.github.io/ (Amazon Reviews '23)
- Dataset v2018: https://nijianmo.github.io/amazon/ (legacy, smaller)

**Nature:** One-time static download. NOT a live API. This is a pre-collected, publicly released research corpus. It sidesteps Amazon's ToS prohibition on scraping live reviews because the data was collected under academic research authorization, not production scraping.

**License:** Research use only. Non-commercial. Cannot be used in a production commercial product or client-billable dashboard without separate legal review.

**Data Characteristics**
- Amazon Reviews '23: 571.5M reviews across 33 product categories, covering Jan 1996 to Sep 2023
- Amazon Reviews 2018: 233M reviews, similar category coverage
- Format: JSONL, one review per line
- Fields: `rating`, `title`, `text`, `parent_asin`, `user_id`, `timestamp`, `helpful_vote`, `verified_purchase`
- Relevant categories for SharkNinja: Home & Kitchen, Appliances, Vacuum & Floor Care, Coffee, Tea & Espresso
- Download size (Home & Kitchen + Appliances 2023): approximately 12-20 GB compressed JSONL
- Last update: September 2023 (no live updates)

**Integration Pattern**
Use as "offline historical baseline + live current" combo:
- UCSD dataset: historical coverage pre-2023, training/calibration data, NLP benchmarking
- PRAW (Reddit): live current data, real-time signal
- This combo provides Amazon brand coverage historically without live scraping risk

**Round 4 Implementation:** Ingest script reads UCSD JSONL for relevant ASINs (SharkNinja, Dyson, iRobot, Roborock, KitchenAid products), maps to existing `Mention` schema, writes to CSV or directly to in-memory store. Estimated 2-3 hours.

---

## Supplemental Sources (Recommended)

---

### Hacker News (Algolia Search API)

**Score:** 23/25 — highest-scoring source in the audit

**Access Method**
- Firebase Realtime Database: no API key, no auth required, free, stable since 2013
- Algolia HN Search: `https://hn.algolia.com/api/v1/search?query=sharkninja` — unofficial but widely used, free, no auth
- Combined: Firebase for item lookup, Algolia for full-text search

**Rate Limits:** No published limit. Practically unthrottled for reasonable query volumes.

**Legal Posture:** Very low risk. Public API explicitly designed for developer use, open license on data.

**Signal Relevance:** Tech-leaning audience, lower volume for consumer appliances than Reddit, but high-signal for product launches, Wirecutter coverage discussions, and safety recalls.

**Estimated Cost:** $0

**Round 4 Scope Estimate:** 1-2 hours (single HTTP client, Algolia search, Firebase item fetch, field mapping to Mention schema)

---

### GNews

**Score:** 20/25

**Access Method**
- REST API: `https://gnews.io/api/v4/search?q=sharkninja&token={API_KEY}`
- Auth: API key (free registration)
- Coverage: 60,000+ news sources, global

**Rate Limits:** 100 requests/day on free tier, max 1 request/second

**Legal Posture:** Low risk on official API. Non-commercial only on free plan — same commercial caveat as Reddit.

**Estimated Cost:** $0 (free tier, 100 req/day)

**Signal Value:** Press coverage of product launches, safety recalls, competitive announcements. Adds a media-monitoring layer the social sources don't provide.

**Round 4 Scope Estimate:** 1 hour (API key setup + simple HTTP client + field mapping)

---

## Round 4 Execution Summary

| Source | Action | Hours | Cost | Legal Risk |
|---|---|---|---|---|
| Reddit (PRAW) | Implement RedditScraper(BaseScraper) | 3-4h | $0 | Medium (non-commercial safe) |
| HN (Algolia) | Implement HNScraper(BaseScraper) | 1-2h | $0 | Very Low |
| UCSD Amazon | Implement offline JSONL ingest adapter | 2-3h | $0 | Low (research-only) |
| YouTube v3 | Implement YouTubeScraper(BaseScraper) | 2-3h | $0 | Low |
| GNews | Implement GNewsScraper(BaseScraper) | 1h | $0 | Low (non-commercial safe) |
| Trustpilot | Keep existing CSV fixtures; Option B if budget | 1h (A) / 3-4h (B) | $0 (A) / TBD (B) | Low |
| Twitter/X | NOT IN SCOPE unless budget approved | 2-3h | $100/mo minimum | Low (official API) |

**Recommended R4 Priority Order:**
1. Reddit + HN (highest signal, zero cost, proven APIs) — unblocks replacing CSV stubs with real data
2. UCSD Amazon dataset ingest (offline, covers Amazon brand gap cleanly)
3. YouTube v3 (official API, moderate effort, adds video comment signal)
4. GNews (optional enrichment, lowest effort)
5. Trustpilot Option A (keep CSV fixtures, no new code needed)
6. Twitter/X (requires team-lead budget decision before proceeding)

---

## Architecture Notes for Round 4 Engineers

### BaseScraper ABC compliance (CLAUDE.md §3)

Every new source MUST implement the `BaseScraper` ABC in `backend/app/scrapers/base.py`. Routers depend on the ABC via `Depends(...)`, never on concrete adapter classes. Adding a new source = adding a new class in `backend/app/scrapers/`, registering it in `backend/app/scrapers/__init__.py` factory, updating the config to select it. Zero router changes required.

### Schema change protocol (CLAUDE.md §4)

Any new fields added to `Mention` (see per-source schema additions above) require:
1. Edit `backend/models/schemas.py`
2. Run `python scripts/export_openapi.py` to regenerate `contracts/api-contract.yaml`
3. SendMessage `frontend-engineer` with field list and instruction to run `npm run gen:types`

All new Mention fields should be `Optional[T] = Field(default=None, ...)` to maintain backward compatibility with the CSVAdapter and existing fixtures.

### Commercial ToS risk (for SharkNinja demo context)

Reddit and GNews free tiers are non-commercial only. For a demo pitched to SharkNinja as a commercial product or for investor/client demonstration, the team must either:
- Obtain Reddit's commercial API approval before the demo
- Explicitly label the demo as a "research prototype" in all materials
- Or substitute data with the UCSD offline corpus for the demo run

"It worked in testing" is not a substitute for legal clearance.

---

*Research basis: `contracts/research/orchestrator/real_api_landscape.md`, researched 2026-04-11. Rate limits, pricing, and ToS subject to change — verify against official documentation before Round 4 execution.*
