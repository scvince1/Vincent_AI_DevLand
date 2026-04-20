---
topic: B2B SaaS pitch deck narrative structure — problem → wedge → proof
gap_closed: Defends the README polish structure against Vincent's likely pushback: "does this match how successful B2B consumer-insights vendors actually structure their problem-to-proof narrative?"
date: 2026-04-11
reviewer: business-leader-v2
---

## Question
What narrative structure does the B2B SaaS sales-deck genre actually use for problem → wedge → proof, and how should the README polish round sequence its sections to match those conventions for a CGO-level consumer audience?

## Sourced facts
1. **Lead with workflow, not market size.** The consensus in 2026 B2B SaaS sales-deck guidance is: "make buyers viscerally understand the pain of the status quo before showing how your product eliminates it." Market-size slides are investor deck, not sales deck. For a CGO audience the equivalent is "show her what Maya Chen's Monday morning actually looks like today, and how your tool changes it by Monday afternoon."
2. **Before/after as the primary visual device.** Effective pitches rely on "a before-and-after comparison that makes the pain tangible" — screenshots, workflow diagrams, and customer testimonials. The before side is intentionally more detailed than the after side, to force the audience to feel the friction.
3. **Demo narrative = 1-3 features, not a tour.** The Product Demo section should be "focused on the one to three features that drive the strongest customer retention." For us that's (a) aspect-level sentiment with drill-through, (b) cross-platform confirmation, (c) novelty alerts on rising negative clusters. NOT all 5 pages.
4. **Proof via case studies, testimonials, reviews, badges, logos.** Credibility is earned through concrete external references, not self-congratulation. For us: the pytest suite is our badge/certification proxy (judges respect green tests), and the CPSC Foodi record is our case-study proxy (external source, high authority, unignorable).
5. **14-slide optimal length** is the high-performer consensus for B2B SaaS sales decks (Kolide's "My Perfect B2B SaaS Sales Deck Is 14 Slides Long" is a widely-circulated data point). For a README this maps to roughly 14 sections — which is close to the current README's 9 sections + the 5 I've reserved for the polish round.
6. **Narrative framework:** "Begin with a relatable problem, introduce your solution as the hero, and illustrate the transformation it brings." The hero is NOT a product name — it is a shift in how the audience understands their own situation.

## Implications for the SharkNinja pitch narrative
- **README polish section order** should follow this skeleton: (1) the problem Maya Chen faces on Monday morning, in her own voice; (2) the gap Agentforce cannot cover (survivorship bias); (3) the Foodi counterfactual as proof-of-cost; (4) our wedge — aspect-level CE sentiment with drill-through; (5) the demo script, focused on 3 features; (6) the pytest receipts; (7) out-of-scope honest statements.
- **Pain-first, not feature-first:** current README §2 opens with the bulleted competitive gap list, which is good. Polish round should add a **before-and-after workflow** vignette before that list: "Today Maya Chen tags 500 reviews per SKU by hand in Google Sheets because Brandwatch scores 'brushroll is jammed' as neutral. On this dashboard she clicks Product Analysis, picks PowerDetect UV Reveal, and sees the brushroll aspect dropping 12% WoW with 47 traceable quotes. She kills the Google Sheet."
- **Proof hierarchy**: (a) pytest green (technical badge), (b) CPSC Foodi public record (external authority), (c) Crossan-Matos own language about consumer obsession (operator resonance). Use all three, in that order.
- **Demo-script rewrite**: the current demo script closes with pytest. For a CGO audience that's inverted priority — she wants the Maya Chen workflow demo first and the pytest at the end as the "but don't take our word for it, the tests are green too" close. Flip the order.
- **Avoid**: wall-of-features slides, roadmap promises, pricing, team slides. This is a pitch artifact, not a contract deck.

## Reference URLs
- https://www.kolide.com/blog/my-perfect-b2b-saas-sales-deck-is-14-slides-long
- https://www.dock.us/library/sales-deck-examples
- https://pitchbob.io/blog/b2b-saas-sales-deck
- https://www.storydoc.com/blog/saas-pitch-deck-examples
