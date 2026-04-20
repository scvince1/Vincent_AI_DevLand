# Jailbreak Challenge #5: Consumer Sentiment Dashboard - Social Listening MVP

## Challenge Spec
- **Category:** NLP / Data Science
- **Task:** Scrape public Reddit, TikTok, and Amazon review data for a defined product category. Apply NLP sentiment analysis and build a working insight dashboard.
- **Deliverable:** Working dashboard
- **Strategic Priority:** High CEO attention. Company wants something deployable ASAP with tangible outcomes.

## Why This Challenge Matters to SharkNinja Right Now

### The Quality Control Imperative
- **May 2025:** SharkNinja recalled 1.8 million Foodi pressure cookers after 106 burn injury reports (50+ second/third-degree burns, 26 lawsuits). This was a PR and financial crisis.
- **Ongoing:** Consumer complaints about product failures, replacement units failing within months, refund processing delays. Trustpilot/BBB/PissedConsumer reviews are harsh.
- **Current initiative:** SharkNinja is actively trying to empower their quality control pipeline with AI.
- **The gap:** There is no early warning system that surfaces emerging product quality signals from public consumer data BEFORE they become recalls, lawsuits, and headlines.

### The Perception Layer Problem
This challenge maps directly onto Vincent's "Alignment Tax" framework:
- **Information misalignment:** Consumer complaints exist across Reddit, TikTok, Amazon - but no one at SharkNinja sees the full picture in one place.
- **Progress misalignment:** QC teams don't have a live view of emerging failure patterns.
- **Ignorance misalignment:** Product teams don't know what they don't know about how consumers are experiencing their products in the wild.

## Winning Strategy: Not Just Sentiment - Early Warning System

### What most submissions will do (commodity)
- Scrape reviews, run sentiment analysis, show positive/negative/neutral percentages
- Pretty charts, basic word clouds, maybe trending topics
- This is a tutorial project. It won't win.

### What Vincent should build (differentiated)
A dashboard that answers questions the CEO actually asks:
1. **Anomaly detection:** "Is there an emerging product failure mode we haven't seen in QC reports yet?"
2. **Complaint clustering:** "What are the TOP 3 specific failure types for [product X] this month, and are they increasing?"
3. **Cross-platform signal aggregation:** Same complaint surfacing on Reddit AND Amazon AND TikTok = higher confidence signal
4. **Time-series tracking:** "When did complaints about [specific issue] start spiking? Does it correlate with a manufacturing batch or a product launch?"
5. **Actionable output:** Each insight links to "what should we do about this" - not just "here's the data"

### Technical Approach (to be developed in separate session)
- **Data sources:** Amazon reviews API/scrape, Reddit API (pushshift or similar), TikTok comments (public scrape)
- **Product category to focus on:** Choose one SN product category with known issues (e.g., Ninja pressure cookers, Shark vacuums, or Ninja blenders - all have documented complaint patterns)
- **NLP pipeline:** 
  - Sentiment analysis (basic layer)
  - Topic modeling / complaint clustering (differentiation layer)
  - Anomaly detection over time (winning layer)
- **Dashboard:** Streamlit or similar lightweight framework. Must be deployable, not just a notebook.
- **Key design principle:** This must be baby-friendly to use. Non-technical QC managers need to understand it at a glance.

## Vincent's Unique Angle
- His knowledge architecture expertise means the dashboard won't just SHOW data - it will STRUCTURE information in a way that makes patterns visible to decision-makers
- His "Human Sloppiness" design principle means the tool will be designed for people who are busy, who skim, who need the insight surfaced rather than buried in charts
- His Alignment Tax framework provides the conceptual backbone: this dashboard reduces the alignment tax SharkNinja is paying on quality control
- He has actually built self-updating dashboards before (Belmont)

## Connection to Interview Prep
This challenge should be an underlying current in the interview:
- When discussing "What value would you bring?" - the three-step Marketing team example can subtly gesture toward the kind of observational, data-infrastructure thinking that this challenge requires
- When discussing AI experience - Horsys' data pipeline work is directly relevant to scraping/processing/structuring consumer data
- When discussing "Why SharkNinja?" - genuine excitement about the Jailbreak program and the kind of problems the company is solving
- The Alignment Tax framework directly applies: consumer sentiment data exists but is invisible to the people who need it
- **Do NOT mention the specific challenge in the interview** - but let the underlying thinking show through naturally

## Company Context for Reference
- SharkNinja: NYSE SN, $6.4B revenue (2025), 4,200+ employees, 38 international markets
- CEO: Mark Barrocas
- 25 new products/year, 35+ product categories
- Jailbreak AI program: $1M total awards, weekly executive panel reviews, $2.5K-$25K per win, $100K grand prize
- International revenue growing 20.8% YoY, faster than domestic (13.5%)
- Working with Salesforce on AI agent implementation for consumer experience
- BU Questrom AI & Analytics Lab partnership

## Files to Read for Full Context
- Vincent's articles: `D:\Ai_Project\MeowOS\99_MyFiles\respecting-human-efforts-final.md` and `the_alignment_tax.md`
- Vincent's intellectual themes: memory file `user_intellectual_themes.md`
- Vincent's profile: memory file `user_vincent.md`
- Interview prep doc: `D:\Ai_Project\MeowOS\99_MyFiles\Interview Material\SharkNinja_Interview_Prep.md`
- SharkNinja company research embedded in the interview prep doc above

---
*Created: 2026-04-10*
*Status: Initial brief. Full technical design to be developed in dedicated session.*
