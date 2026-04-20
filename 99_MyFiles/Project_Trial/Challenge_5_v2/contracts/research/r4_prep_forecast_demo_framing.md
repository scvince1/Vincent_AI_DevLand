---
topic: R4 Trend Forecast demo framing — what a convincing executive-pitch forecast looks like
gap_closed: Gives team-lead (writing the R4 charter) and me (reviewing R4) a concrete rubric for what "pass" looks like on the forecast feature, before engineers build it
date: 2026-04-11
reviewer: business-leader-v2
---

## Question
When we ship the MiroFish-style Trend Forecast panel in R4, what specific language, visual conventions, and honesty disclaimers are needed so that a CGO-level exec takes it seriously rather than classifying it as AI theater?

## Key findings

### Finding 1 — Incumbents keep predictive-feature specifics vague; we should not
Brandwatch's Iris AI marketing for 2026 describes "AI Query Writer" and "AI Dashboards" and "Ask Iris" but **does not publicly show an actual forecast chart with confidence bands** in any public marketing material I could reach. Signal AI's "decision augmentation" and "spot critical signals in external noise" language is similarly abstract. The **marketing pattern** in the category is: name the capability, show a polished UI screenshot that implies forecasting, avoid committing to a specific forecast methodology that a skeptic can attack.

**Implication for us:** this is a gap we can exploit. Our forecast should be specific about its method, modest about its confidence, and honest about its limits. That positions us as credible in a category full of marketing vagueness.

### Finding 2 — Borrow honesty-disclaimer conventions from finance dashboards, not martech
The finance/trading dashboard space has mature conventions for forward-looking data: "past performance is not indicative of future results," explicit confidence bands, shaded uncertainty cones, "indicative only" labels. Forex and SentimenTrader-style tools have been iterating on these for years precisely because users can lose real money on misleading forecasts. Martech/consumer-intel has no such discipline because the consequences are softer.

**Borrowable conventions for our Trend Forecast panel:**
- **Dashed line** for the projected segment (solid line for historical). Dashed-line convention comes from both finance and scientific plotting; it reads as "we are extrapolating, not measuring."
- **Shaded confidence band** widening as projection horizon grows. Narrow at T+1 week, wide at T+4 weeks. The band itself communicates uncertainty without needing prose.
- **Subtitle line** below the chart title: "Projected based on 30 days of review velocity and aspect trajectory. Not a model-based forecast. Revise as new data arrives."
- **Footer disclaimer** at the panel bottom: "Heuristic projection — not a substitute for judgment."
- **Tooltip on the projected region** that surfaces the inputs: "Projection inputs: 47 mentions in last 7d, momentum +0.12, confidence band width ±18%."

### Finding 3 — Executives respect specific numbers MORE than big claims
A CGO who came from Ulta and Samsung (Crossan-Matos context per `crossan_matos_public_positioning.md`) has sat through hundreds of vendor pitches where "AI-powered predictive insights" meant nothing specific. She will respond to concrete numbers she can interrogate. A demo that says "we project the `mop_pad` aspect will drop 12% more over the next 4 weeks based on a current velocity of +3 complaints/week against a 14-day baseline of +1.2/week" is MORE convincing than "our AI predicts mopping-pad sentiment will continue declining." The first invites questions ("what counts as a complaint?"). The second invites dismissal ("sure, that's what all AI vendors say").

**Demo language rubric for R4:**
- Always state the inputs (how many mentions, what window, what metric)
- Always state the method ("linear decay-weighted projection," not "AI")
- Always state the limits ("not modeled for supply-chain events, media cycles, or competitor launches")
- Offer to show the math ("I can walk through how the confidence band is computed")

### Finding 4 — Visual conventions that signal "mature product" in this space
- **Y-axis labels in decimals with tick marks at -1, -0.5, 0, +0.5, +1** (consumer-electronics sentiment range, matching our `compound_score`)
- **X-axis shows both the historical window AND the projection window, separated by a vertical gridline** at "today" so the boundary is unmissable
- **Hover states reveal the underlying mentions that drove the point** — this ties back to REQ-006 drill-through and makes the forecast inherit our existing defensibility
- **Legend entry for "projection" uses an explicit label**, not just a dashed-line glyph — "Projected (heuristic)"
- **The chart's overall card title uses the word "Forecast" sparingly** — prefer "Trajectory outlook" or "30-day outlook" which implies less commitment

## Strategic recommendation for the R4 charter

When team-lead writes the R4 charter, the Trend Forecast feature spec should require:
1. Method transparency (engineers must document the projection formula in a comment block the user can surface via a "How is this computed?" link)
2. Honest labeling (all 5 visual conventions above are MUSTs, not nice-to-haves)
3. Drill-through integration (hover on projected segment shows which recent mentions drove the projection — ties into REQ-006)
4. A demo script that includes the phrase "we projected this would happen, and then it did" as the pitch close — but ONLY if we have a real historical backtest to cite. If we do not, the demo script should instead say "here is our projection with honest confidence bands; the way to evaluate us is to watch and verify over the next 30 days."

**The highest-leverage single sentence for the R4 demo:** "This is a heuristic projection, not a simulation. The point is not that we predict the future — it is that we surface the signal 4 weeks before volume alone would."

That sentence inoculates against skeptics AND lands the Darius-persona value proposition simultaneously.

## Reference URLs
- https://www.brandwatch.com/suite/consumer-intelligence/
- https://www.prnewswire.com/news-releases/brandwatch-strengthens-ai-leadership-with-deeper-insights-and-expanded-data-coverage-302621990.html
- https://signal-ai.com/solutions/advanced-dashboards/
- https://www.forex.com/en-us/trading-tools/client-sentiment/
- https://sentimentrader.com/
