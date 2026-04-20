---
id: uchicago_3pl_consulting
title: UChicago Consulting Club — CPG Event-Sponsorship 3PL Engagement
tags: [person, identity, consulting, uchicago, operations]
status: confirmed
last_modified: 2026-04-15
summary: UChicago 咨询社，CPG 校园赞助创业客户 3PL 问题诊断与建议
---
# UChicago Consulting Club - CPG Event-Sponsorship 3PL Engagement
**Time:** UChicago period (graduate)
**Location:** UChicago, Chicago, IL
**Status:** Concluded; client founder gave up on the business

## Real Facts
Engagement via UChicago Consulting Club. The client was a startup in the campus-events CPG sponsorship space — the model was connecting brands with on-campus events to sponsor giveaways and sampling. They had no 3PL; they were paying for direct delivery of product to every event, and the unit economics were broken.

Vincent's analysis was unglamorous: pull the delivery cost logs, compute per-can/per-unit landed cost, compare against simply buying the same product from a nearby Target using sponsor coupon codes. Target buy + local pickup was cheaper per unit than the startup's existing delivery model.

Two real test events validated the mechanism:
1. **McKinsey info session:** 200 cans. Purchased via Target coupon scan (which itself was the sponsor's user-data collection mechanism). Vincent + two friends picked up the order at Target, Uber'd it to the event venue. Verified the delivery-substitution model worked logistically; no consumer-data collection layer was tested on this one.
2. **URock (UChicago Rock Climbing Club, RSO):** 24-can pallet, roughly $40 total. Club members picked up directly from Target and brought it to the climbing gym for an event.

Neither event proceeded to sustained prototype. The founder gave up on the broader business before the model could be rolled out at scale. Vincent's private read: mediocre founder, weak business idea. The insight (use existing infrastructure instead of building a new delivery network) was sound, but the client didn't survive.

## Interview Version(s) Used
- **Story #4** in `Locked_Interview_Answers.md` (Problem Solving).
- Framing: "delivery lead time from 2-3 weeks down to 3 days." Presented as an achieved result.
- Estimated delivery time: 90 seconds to 2 minutes.

## Key Insights Extracted
- The best solution often isn't building something new. Infrastructure already exists (retail chains, coupon systems, local pickup). See it and plug into it.
- Unit-economics-first analysis beats process-redesign analysis for small-scale ops problems.
- Pair the insight with a cheap test before assuming it scales.

## Follow-up Questions (if probed)
1. "How did you measure the sustained improvement?" — Honest fallback: "We validated via two test deployments. The client didn't continue in business long enough for sustained metrics, but the per-unit landed cost delta was clear on the two tests."
2. "Why didn't the client adopt it long-term?" — Founder exited the business. The delivery-substitution was a symptom fix; the core business had other issues.
3. "What about consumer-data collection through the sponsor coupon mechanism?" — On McKinsey test we verified logistics only; on URock, the coupon flow did involve the normal sponsor data loop.
4. "Were there compliance issues with a third party picking up on the sponsor's behalf?" — We used the sponsor's own coupon accounts; the pickup was a delegated task, not an identity question.
5. "Would you do it differently now?" — Lock in a third test with clean measurement of sustained ops cost before calling it a result.

## Sensitivities / Flags
- The "2-3 weeks → 3 days" claim is slightly promotional. Two real test events validated the mechanism; sustained deployment was not proven.
- If asked for measured metrics, the honest truth is: "validated via two test deployments; client didn't continue long enough for sustained data."
- Founder critique ("mediocre founder") and "shitty business idea" are private views. Never voice externally.
