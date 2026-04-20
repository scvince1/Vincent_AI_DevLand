# Real API Landscape for Consumer Product Sentiment — audit reference

> **Purpose:** Team-lead audit reference for backend-engineer-v3's Round 3 API integration proposal.
> **Project:** SharkNinja consumer sentiment dashboard. Goal: replace 75 CSV rows with live data, small-scale, for demo + Round 4 validation.
> **Platforms in scope per fixture data:** Reddit, Amazon, YouTube, Trustpilot, Twitter.
> **Researched:** 2026-04-11

---

## Scoring Rubric

Each source is scored 1-5 on five criteria:

| Criterion | 1 (Worst) | 5 (Best) |
|---|---|---|
| **Access Ease** | Multi-step approval, scraping, or paid-only | API key only, instant, free |
| **Data Quality** | No sentiment signal, no text, no metadata | Full review text, rating, timestamp, author |
| **Rate Limit Viability** | Unusable for demo volume (<10 req/day) | Generous (100+ req/min or no limit) |
| **Legal Safety** | Clear ToS violation or scraping risk | Official API, permissive ToS |
| **Demo Speed** | 8+ hours to first data | <2 hours from zero to 100 items |

**Maximum score: 25. Recommended threshold for demo use: ≥15.**

---

## Per-Source Assessment

---

### 1. Reddit

**Official API: PRAW (Python Reddit API Wrapper) + OAuth 2.0**

#### Free Tier & Rate Limits (2025/2026 reality)
- Free tier exists but is non-commercial only. Commercial use requires Reddit approval + possible fees.
- Authenticated (OAuth 2.0): **100 requests per minute (QPM)**, averaged over a 10-minute rolling window.
- Unauthenticated: blocked entirely as of 2023 API changes.
- Rate limit applies per OAuth client ID.

#### Pushshift / Archive Status
- **Pushshift is effectively dead for public use.** Reddit shut it down in 2023; it now only serves Reddit-approved moderators for community moderation.
- **PullPush** (pullpush.io): Community successor, currently disabled/intermittent as of research date. API is Pushshift-compatible but unreliable.
- **Arctic Shift** (arctic-shift.photon-reddit.com): More stable alternative. Handles simple queries well. Rate limits reportedly ~2,000 req/min. Limitation: no full-text search without subreddit specified; no search by score/comment count.

#### Data Schema
Fields available via PRAW: `post_id`, `subreddit`, `title`, `selftext`, `score`, `num_comments`, `created_utc`, `author`, `url`, `flair`. Comments include `body`, `score`, `created_utc`, `author`.

#### Authentication Complexity
OAuth 2.0 required. PRAW handles this with ~10 lines of Python: register app at reddit.com/prefs/apps, get client_id + client_secret + user_agent. **Low complexity.**

#### Legal / ToS Risk
- Non-commercial use: Low risk.
- Commercial/dashboard product: Medium-High. Reddit ToS prohibits commercial use of free tier without approval.
- Scraping without OAuth: High risk (blocked + ToS violation).
- **For SharkNinja demo:** Medium risk if framed as commercial product.

#### Demo Integration Effort
~2-4 hours from zero: register app, install PRAW, query r/sharkninja or r/airfryer, done.

#### Recommended for 48-hour demo?
**YES** — Best organic consumer sentiment source. Large SharkNinja subreddits exist. PRAW is mature and well-documented. Achieves 100 real mentions in under 30 minutes of fetch time.

#### Scores
| Access Ease | Data Quality | Rate Limit | Legal Safety | Demo Speed | **Total** |
|---|---|---|---|---|---|
| 4 | 5 | 4 | 3 | 5 | **21/25** |

---

### 2. Hacker News

**Official API: Firebase Realtime Database (no key, no auth)**

#### Free Tier & Rate Limits
- **Completely free, no authentication required, no published rate limit.**
- Hosted on Google Firebase; practically no throttling observed in practice.
- Returns JSON. Stable since 2013.

#### Data Schema
Items: `id`, `type` (story/comment/job/poll), `by` (username), `time` (Unix timestamp), `text` (HTML, comment body), `url`, `score`, `title`, `kids` (child comment IDs), `descendants` (total comment count).

Users: `id`, `karma`, `created`, `about`, `submitted`.

**Limitation:** No full-text search endpoint natively. To find product mentions, must use Algolia HN Search API (also free, unofficial but widely used: `https://hn.algolia.com/api/v1/search?query=sharkninja`).

#### Authentication Complexity
None. Zero setup. Single GET request.

#### Legal / ToS Risk
**Very low.** Public API with open license on data. Explicitly designed for developer use.

#### Demo Integration Effort
**<1 hour.** One `requests.get()` call. Algolia search endpoint returns structured JSON immediately.

#### Signal Relevance for SharkNinja
HN audience is tech-leaning, less consumer-product-oriented. SharkNinja mentions are sparse but high-signal (typically appear around product launches, Wirecutter coverage, or safety recalls). Better for brand/media monitoring than volume sentiment.

#### Recommended for 48-hour demo?
**YES (as secondary source)** — Near-zero cost to add. Useful to demonstrate multi-source architecture and show a second data stream with different audience profile.

#### Scores
| Access Ease | Data Quality | Rate Limit | Legal Safety | Demo Speed | **Total** |
|---|---|---|---|---|---|
| 5 | 3 | 5 | 5 | 5 | **23/25** |

---

### 3. Trustpilot

**Business API (private/authenticated)**

#### Free Tier & Rate Limits
- **Free plan exists** (business.trustpilot.com/pricing/free) but does NOT include API access.
- API access is a paid feature. No public pricing listed; requires contacting Trustpilot sales.
- Public Business Units API (`developers.trustpilot.com/business-units-api-(public)/`) allows reading publicly visible info with API key only — but review text access requires the paid private API with OAuth 2.0.

#### Data Schema
Via paid API: `reviewId`, `title`, `text`, `rating` (1-5), `createdAt`, `consumer` (name, countryCode), `businessUnit`. Public API returns aggregate stats and limited review metadata.

#### Authentication Complexity
Two-tier:
- Public API: API key (client_id) only — easy.
- Private API (full review text): OAuth 2.0 — requires paid business account.

#### Legal / ToS Risk
Low if using official API. Scraping Trustpilot is medium-high risk: their ToS prohibits it and they actively pursue scraping operations.

#### Demo Integration Effort
- Public API only: ~1-2 hours, but limited data.
- Full review text: blocked without paid plan. **Not feasible for demo unless team has a paid account.**

#### Recommended for 48-hour demo?
**NO** — Paid gate blocks access to the actual review text. Cannot complete demo integration in 48h from scratch without budget. Unless team already has a Trustpilot business account.

#### Scores
| Access Ease | Data Quality | Rate Limit | Legal Safety | Demo Speed | **Total** |
|---|---|---|---|---|---|
| 2 | 4 | 3 | 4 | 2 | **15/25** |

---

### 4. App Store / Google Play Reviews

#### Apple App Store RSS Feed
- URL template: `https://itunes.apple.com/rss/customerreviews/id={APP_ID}/sortby=mostrecent/json`
- **Still working in 2025.** No API key required.
- **Hard limit: 10 pages of results, ~500 most recent reviews maximum.**
- Rate limiting: 403 errors reported when many rapid requests sent. No published limit. Treat as ~1 req/10 sec to be safe.
- Data fields: `author.name`, `im:rating`, `title`, `content`, `im:version`, `updated`.
- Limitation: Only returns the app developer's own app. For SharkNinja: must know their specific App Store app IDs.

#### Google Play — google-play-scraper (npm / PyPI)
- Unofficial scraper, not a Google API.
- Works without API key. Fetches review pages HTML and parses.
- Rate limits: Hits 503 + CAPTCHA after burst requests. Practical limit: ~500-1,000 apps/IP/day. Single app reviews: higher tolerance before throttle.
- Legal risk: **Medium.** Google ToS technically prohibits scraping. Enforcement is rare for research/demo scale. Commercial-scale is higher risk.
- Data: `reviewId`, `userName`, `userImage`, `date`, `score`, `scoreText`, `title`, `text`, `replyDate`, `replyText`, `version`.

#### Recommended for 48-hour demo?
**Conditional YES (Google Play only, with throttle)** — google-play-scraper is fast to implement (~2 hours), data is rich (text + rating + date), and demo-scale volume is low enough to avoid blocks. Apple RSS is also viable but limited to 500 reviews.

**Condition:** Only if SharkNinja has a notable app presence. If primary use case is physical product reviews, app store data is not representative of consumer sentiment about kitchen appliances.

#### Combined Scores (Google Play)
| Access Ease | Data Quality | Rate Limit | Legal Safety | Demo Speed | **Total** |
|---|---|---|---|---|---|
| 4 | 4 | 3 | 2 | 4 | **17/25** |

---

### 5. News APIs

#### NewsAPI.org
- Free tier: **100 requests/day, 24-hour delay on articles, localhost-only** (cannot deploy to staging/production on free plan).
- Data: `source`, `author`, `title`, `description`, `url`, `publishedAt`, `content` (truncated at 200 chars on free tier).
- Coverage: 150,000+ sources. Good for product launch / recall press coverage.
- **Fatal free-tier flaw:** 24-hour delay + localhost-only makes it unusable for a deployed demo.
- Developer plan: $449/month for real-time + full content.

#### GNews (gnews.io)
- Free tier: **100 requests/day**, max 1 req/sec.
- No production deployment restriction noted (unlike NewsAPI.org).
- Coverage smaller than NewsAPI.org but still useful.
- Non-commercial use only on free plan.

#### Mediastack
- Free tier: **100 requests/month.** Essentially unusable.

#### Recommendation for Demo
**GNews** is the best free-tier news option: no localhost restriction, 100/day sufficient for demo polling. Coverage of product launches and recalls adequate.

#### Recommended for 48-hour demo?
**YES (GNews, as optional enrichment)** — Low effort, adds press/media angle to dashboard. Not a primary sentiment source. 100 req/day limit is fine for demo polling cadence.

#### Scores (GNews)
| Access Ease | Data Quality | Rate Limit | Legal Safety | Demo Speed | **Total** |
|---|---|---|---|---|---|
| 5 | 3 | 3 | 4 | 5 | **20/25** |

---

### 6. Amazon Reviews

**CRITICAL SECTION — Read carefully before accepting any proposal involving Amazon.**

#### Official API Reality
- **Amazon Product Advertising API (PA API):** Does NOT return review text. Returns product metadata, pricing, ASIN info. Requires active affiliate account with qualifying sales. **Zero sentiment value.**
- **No official Amazon reviews API exists.** Amazon explicitly restricts programmatic access to review text.
- Amazon's terms of service explicitly prohibit scraping review content.

#### Third-Party Scrapers
Services like Bright Data, Apify, Canopy API, ScrapeHero, and Decodo offer Amazon review data via paid scraping-as-a-service. These:
- Cost money (typically $0.002-0.01 per review)
- Operate in legal gray zone (ToS violation on Amazon's side)
- Risk IP bans, account bans, and potential legal exposure
- Are not suitable for a production dashboard for a public company demo

#### Legal Status Summary
| Approach | Legal Status | Risk Level |
|---|---|---|
| PA API for reviews | Not possible (no review endpoint) | N/A |
| Direct scraping | Clear ToS violation | High |
| Third-party scraper API | ToS violation (outsourced) | Medium-High |
| Manual export | Gray area (manual only) | Low but not scalable |

#### Recommended for 48-hour demo?
**NO.** Any proposal to include Amazon reviews must either:
1. Use a paid third-party scraper (cost + ToS risk), OR
2. Acknowledge that the PA API cannot provide review text.

**This is the most common mistake in API integration proposals for this type of project.**

#### Scores
| Access Ease | Data Quality | Rate Limit | Legal Safety | Demo Speed | **Total** |
|---|---|---|---|---|---|
| 1 | N/A | N/A | 1 | 1 | **3/25** |

---

### 7. Bluesky

**AT Protocol — open decentralized social network**

#### Free Tier & Rate Limits
- API is open and largely free.
- Firehose (full real-time stream): accessible via WebSocket at `com.atproto.sync.subscribeRepos`, **no authentication required**.
- Jetstream (simplified JSON firehose relay): also free, lower payload size, no auth required.
- Search API (`app.bsky.feed.searchPosts`): requires account authentication (free account) but no paid tier.
- Published rate limits: requests generating "points" per operation. Typical write limit ~5,000 points/hour. Read limits generous and not strictly enforced for public data.

#### Data Schema
Posts: `uri`, `cid`, `author` (handle, displayName), `record.text`, `record.createdAt`, `replyCount`, `repostCount`, `likeCount`, `indexedAt`.

#### Authentication Complexity
Low. Free Bluesky account + app password = Bearer token. Python `atproto` SDK available.

#### Legal / ToS Risk
**Very low.** Bluesky explicitly designed for open developer access. AT Protocol is open standard. Data is public by design.

#### Platform Relevance for SharkNinja
Growing but still niche for consumer appliance discussion. ~28M MAU vs Reddit's 1B+ monthly visits. Sentiment signal exists but volume will be lower than Reddit for a kitchen appliance brand.

#### Recommended for 48-hour demo?
**YES (as optional bonus source)** — Demonstrates awareness of emerging platforms. Low friction. Adds architectural interest. Volume for SharkNinja-specific queries will be modest.

#### Scores
| Access Ease | Data Quality | Rate Limit | Legal Safety | Demo Speed | **Total** |
|---|---|---|---|---|---|
| 4 | 4 | 4 | 5 | 4 | **21/25** |

---

### 8. Twitter / X

**X API (formerly Twitter API)**

#### Current Pricing Structure (2025-2026)
- **Free tier:** Exists but nearly useless for reading. ~1 GET request per 15 minutes. No search endpoint. Only posting allowed at meaningful volume (1,500 tweets/month write).
- **Basic tier:** $100/month — 10,000 tweet reads/month. Search available but limited.
- **Pro tier:** $5,000/month — 1,000,000 tweet reads/month.
- **Enterprise:** $42,000+/month.
- **Pay-as-you-go (November 2025 beta, February 2026 broad launch):** Credit-based. $10 voucher for free-tier users switching over. Variable per-endpoint pricing.

#### Authentication Complexity
Mandatory app registration + OAuth 2.0 or Bearer Token. Multi-step approval process with use-case questionnaire.

#### Legal / ToS Risk
Low if using official API. Scraping X is very high risk — active enforcement, legal action history, Cloudflare protection.

#### Demo Integration Effort
Even on Basic ($100/month), 10K reads/month = ~330 reads/day — marginal for dashboard. Cannot be done meaningfully on free tier.

#### Recommended for 48-hour demo?
**NO.** Free tier is nonfunctional for search. Paid tier requires immediate budget commitment. The 2025/2026 pricing model makes this impractical for a demo/hackathon. **Explicitly exclude from demo scope.**

#### Scores
| Access Ease | Data Quality | Rate Limit | Legal Safety | Demo Speed | **Total** |
|---|---|---|---|---|---|
| 1 | 4 | 1 | 3 | 1 | **10/25** |

---

## Summary Score Table

| Source | Access Ease | Data Quality | Rate Limit | Legal Safety | Demo Speed | **Total** | Demo? |
|---|---|---|---|---|---|---|---|
| Reddit (PRAW) | 4 | 5 | 4 | 3 | 5 | **21** | YES |
| Hacker News | 5 | 3 | 5 | 5 | 5 | **23** | YES |
| Trustpilot | 2 | 4 | 3 | 4 | 2 | **15** | NO |
| Google Play | 4 | 4 | 3 | 2 | 4 | **17** | Conditional |
| GNews | 5 | 3 | 3 | 4 | 5 | **20** | YES (secondary) |
| Amazon | 1 | — | — | 1 | 1 | **3** | NO |
| Bluesky | 4 | 4 | 4 | 5 | 4 | **21** | YES (optional) |
| Twitter/X | 1 | 4 | 1 | 3 | 1 | **10** | NO |

---

## Recommended Picks

### Best Single Source

**Reddit (PRAW)**

Reasoning:
- Largest organic consumer sentiment volume for physical products like kitchen appliances.
- Active subreddits: r/sharkninja (~100K members), r/airfryer, r/instantpot, product-specific communities.
- Free for non-commercial / demo purposes.
- PRAW is the most mature API wrapper in the Python ecosystem — well-documented, actively maintained.
- Returns rich data: post title, body, score, comment threads, flair, timestamp.
- 100 mentions achievable in <30 minutes of fetch time.
- OAuth setup is ~10 lines of code.

**Caveat:** Commercial use requires Reddit approval. For a demo, this is acceptable. For production, must be addressed.

---

### Best 2-Source Combination

**Reddit (PRAW) + Hacker News (Firebase/Algolia)**

Reasoning:
- Complementary audiences: Reddit = mass consumer, HN = tech-savvy early adopters and journalists.
- Both are truly free, open, and legally safe for demo use.
- Combined implementation effort: ~3-5 hours.
- Zero cost.
- Demonstrates multi-source architecture cleanly.
- HN adds media/analyst signal layer (product recalls, Wirecutter-style coverage discussions appear on HN).
- Different data shapes (Reddit = threaded discussion, HN = link aggregator) give the dashboard richer structure.

**Optional third layer:** GNews for press/media mentions of product launches and safety recalls — adds ~1 hour of implementation on top.

---

## Red Flags to Watch For in Backend-Engineer-v3's Proposal

### Red Flag 1: "We'll scrape Amazon reviews"
Any proposal to scrape Amazon directly — or to use a "scraping API" service for Amazon — is a legal and ToS violation. Amazon has no official review API. The PA API does not return review text. If the proposal cites Amazon as a data source without explicitly acknowledging the ToS risk and without a paid third-party intermediary plus legal sign-off, reject it. The fixture data's claim of "Amazon coverage" cannot be replicated with a clean integration.

### Red Flag 2: "We'll use the Twitter/X free tier for search"
The X free tier does not include search functionality. It allows ~1 read per 15 minutes and only posting at volume. Any proposal claiming to pull SharkNinja mentions from Twitter on the free tier is factually incorrect. Basic tier costs $100/month. Reject unless budget is explicitly allocated and approved.

### Red Flag 3: "Pushshift / PullPush provides historical Reddit data"
Pushshift is dead for public access. PullPush is currently disabled/intermittent. If the proposal relies on either for historical Reddit data, it will fail in execution. The valid alternative is Arctic Shift, but it has limitations (no full-text cross-subreddit search). The proposal should use PRAW for recent data and Arctic Shift only for historical enrichment with explicit acknowledgment of its limitations.

### Red Flag 4: "Trustpilot is free to access via their API"
The Trustpilot Business API for review text requires a paid business account. The free plan does not include API access to review content. Any proposal treating Trustpilot as a free source needs to either (a) confirm a paid account exists, or (b) remove Trustpilot from scope. The public Business Units API returns aggregate stats only, not individual review text.

### Red Flag 5: Conflating data source availability with legal clearance for a commercial demo
Several sources (Reddit non-commercial free tier, GNews non-commercial free tier, Google Play scraper) have explicit non-commercial clauses. If the SharkNinja dashboard demo is being built as a commercial product proposal or for investor/client demonstration, the proposal must address whether these sources' ToS allow that use case. "It worked in testing" is not the same as "we have legal clearance for production."

---

*Research conducted 2026-04-11. Rate limits and pricing subject to change. Verify against official documentation before Round 4 execution.*
