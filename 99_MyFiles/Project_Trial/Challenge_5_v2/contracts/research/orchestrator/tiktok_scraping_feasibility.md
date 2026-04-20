# TikTok Signal Extraction — Feasibility Assessment

**Author:** backend-engineer-v3 (research window, 2026-04-11)
**Purpose:** Assess viability of TikTok as a consumer sentiment data source for the SharkNinja dashboard in R4/R5.

---

## Summary Verdict

TikTok has three potential signal vectors. Only the official Research API is legally clean; the others carry meaningful ToS/legal risk. For a SharkNinja demo, TikTok is a **supplemental source only** — lower volume for kitchen appliances than Reddit, but valuable for viral product moments and Gen-Z audience signal.

---

## Vector 1: Video Comments via TikTok Research API

**Access:** Official API. Requires application at `developers.tiktok.com/products/research-api/`. Approval restricted to researchers at **non-profit academic institutions in the US and Europe**. Not available to commercial developers.

**What you get:** Comment text, like counts, reply counts, timestamp. Video metadata: title, description, view count, like count, voice-to-text captions, creation time.

**Rate limits:** 1,000 requests/day, 100 records/request = 100,000 records/day maximum.

**Legal posture:** GREEN for academic/research orgs. RED for commercial entities — the Research API is explicitly non-commercial and institution-restricted. A commercial dashboard for SharkNinja cannot use this API unless an academic partner is involved.

**Demo viability:** YELLOW. If the team has an academic affiliation, this is the correct path. If not, this vector is blocked for commercial use.

---

## Vector 2: Video Transcripts via yt-dlp + Whisper

**Access:** yt-dlp can download TikTok videos and extract auto-generated captions. OpenAI Whisper can transcribe audio if captions are unavailable.

**What you get:** Video transcript text — effectively what the creator said in the video. For unboxing/review videos, this captures opinions, product names, aspect mentions.

**Rate limits:** No official limit — but TikTok employs advanced anti-bot measures (encrypted headers, behavioral detection, real-time fraud scoring). Automated extraction is unstable and degrades over time as defenses update.

**Legal posture:** RED. TikTok's ToS explicitly prohibits unauthorized scraping. They actively pursue enforcement and have published anti-scraping measures. yt-dlp usage for programmatic content extraction is a ToS violation. Legal risk is higher than Google Play scraper (which Google tolerates at low volume) — TikTok has a documented history of anti-scraping action.

**Demo viability:** RED. Do not use for client-facing or production demo. Internal prototyping only with explicit legal sign-off.

---

## Vector 3: TikTok Shop Sales Signals

**Access:** No official API for TikTok Shop sales or review data. Third-party analytics tools (TikApi, Kalodata, Echotik) offer scraping-as-a-service for TikTok Shop metrics.

**What you get:** Product listing prices, estimated sales volume, review counts, seller ratings. Useful as a demand proxy — high TikTok Shop sales velocity for a SharkNinja SKU = strong Gen-Z purchase intent signal.

**Cost:** $50-500/month depending on provider and volume. Paid service, not free.

**Legal posture:** YELLOW-RED. Third-party scrapers operate in the same legal gray zone as Amazon review scrapers. ToS violation outsourced. Not suitable for client-deliverable without legal review.

**Demo viability:** YELLOW (conditional on budget + legal sign-off).

---

## Tool Ecosystem Summary

| Tool | Vector | Legal | Cost | Demo viable? |
|---|---|---|---|---|
| TikTok Research API | Comments + video metadata | GREEN (academic only) | Free | Yellow (institution required) |
| yt-dlp + Whisper | Video transcripts | RED | Free | No |
| TikApi / Kalodata | Shop sales signals | Yellow-Red | $50-500/mo | Conditional |
| Unofficial mobile API scrapers | Any | RED | Variable | No |

---

## Recommendation for R4/R5

- If SharkNinja or the demo org has an academic partner: apply for Research API access. 100K records/day is sufficient for demo-scale comment extraction.
- Without academic affiliation: skip TikTok entirely for R4. Data volume for kitchen appliances on TikTok is lower than Reddit anyway.
- TikTok Shop sales velocity (via paid scraper service) is the most unique signal not available elsewhere — consider for R5 if budget is available and legal signs off.
- Do NOT implement yt-dlp transcript extraction in any round without explicit legal approval.

---

*Research conducted 2026-04-11. TikTok Research API: https://developers.tiktok.com/products/research-api/*
