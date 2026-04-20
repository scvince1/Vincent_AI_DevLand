---
topic: UCSD Amazon Reviews 2023 license clarification — outreach email template for McAuley Lab
gap_closed: Pre-R5 action item from R4 charter §4.2. Before any client-facing demo using UCSD-sourced data, team-lead needs written clarification on commercial-use permission. This file is a ready-to-send template, not the send itself — team-lead (or whoever has a real-name affiliation) sends when appropriate.
date: 2026-04-11
author: business-leader-v2
---

## Why this template exists

The R4 charter §4.2 includes the UCSD Appliances offline corpus as R4-P1-1, with YELLOW LIGHT license posture. Backend-engineer-v3's ingest plan (`contracts/research/orchestrator/ucsd_amazon_ingest_plan.md §6`) documents the ambiguity: the HuggingFace dataset page (`McAuley-Lab/Amazon-Reviews-2023`) lists NO license field, the official project site (`amazon-reviews-2023.github.io`) contains no license statement, and the 2018 predecessor's "for research purposes" language does not appear on the 2023 release page. Internal demo = LOW-MEDIUM risk; commercial/client-facing = MEDIUM-HIGH risk.

The charter's pre-R5 action item is: obtain written clarification from McAuley Lab before any client-facing demo. This file is the template to send.

**Template audience:** Yanping Hou (yphou@ucsd.edu), the contact listed on the dataset landing page. Secondary CC if needed: Julian McAuley (jmcauley@ucsd.edu) as the lab PI.

**Who should actually send this:** team-lead or a human with a real affiliation (SharkNinja or the competition entity). An AI agent should not be the "from" address on a legal-adjacent clarification request — the reply will be consumed by real humans making real licensing decisions.

---

## Template A — Short, direct (recommended)

```
Subject: License clarification request — Amazon Reviews 2023 dataset commercial demo use

Dear Dr. Hou (cc: Dr. McAuley),

I'm writing from [organization / competition team name] regarding the
Amazon Reviews 2023 dataset hosted by the McAuley Lab at
https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023 and
https://amazon-reviews-2023.github.io/.

We are building a consumer sentiment dashboard prototype for a
SharkNinja-facing proof-of-concept. The dashboard ingests a filtered
subset of the dataset (Appliances category, filtered by brand whitelist:
Shark, Ninja, SharkNinja, Dyson, iRobot, Roborock, KitchenAid) as the
historical Amazon-channel coverage source in place of live scraping,
which we understand is not a legally clean path.

We have two use-case questions and would be grateful for written
clarification on each:

1. Internal, non-public demo to SharkNinja stakeholders using the
   filtered subset described above. Our understanding is that this falls
   under research use. Is that correct?

2. A client-billable deliverable built on top of the dashboard that may
   later be productized for commercial use. Our understanding is that
   this likely requires separate permission. Is that also correct, and
   if so, is there a licensing or permissions path available?

We are aware that the 2018 Amazon Reviews release included "for research
purposes" language on its download page and that the 2023 release page
does not repeat this — we want to confirm whether the intent for
non-commercial research use still applies to 2023, or whether the
licensing posture has changed.

Our dashboard pipeline runs NLP on the text field, stores derived
sentiment records, and presents aggregate visualizations. We do not
re-publish raw review text, though drill-through panels surface short
quoted snippets alongside their sentiment scores for evidence
traceability. If this usage pattern affects the answer, we would
appreciate your guidance.

Thank you for your time. We appreciate the work the McAuley Lab has
done in maintaining these datasets for the research community.

Best regards,
[Name]
[Role / Affiliation]
[Email]
```

**Word count:** ~350 words. Direct, respectful, specific about use cases. Mentions the drill-through-snippet pattern since that is the use case most likely to be objected to (it's closer to "re-publishing" than pure aggregate analysis).

---

## Template B — Longer, with technical context (use if first reply asks for more detail)

If Template A gets a reply asking for more detail on how the data is used, send this as a follow-up rather than leading with it. Template B is held in reserve.

```
Additional technical context per your question:

1. We download only the Appliances category JSONL.gz (~1-2 GB compressed)
   from https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/,
   not the full dataset.

2. We filter at ingest time by parent_asin against a brand whitelist.
   Roughly 2-5% of the category is retained. The rest is discarded
   without being stored.

3. The retained records are passed through an NLP pipeline (spaCy +
   VADER + a custom 75-term domain lexicon) that extracts aspect-level
   sentiment. We store:
   - A stable internal UUID (not derived from Amazon identifiers)
   - The review text (verbatim, necessary for drill-through evidence)
   - The derived aspect-level sentiment records
   - The timestamp, brand, product_model resolved from metadata

4. Drill-through panels in the dashboard display 1-3 short quoted
   snippets (typically 10-40 words each) when a user clicks on a
   sentiment score. This is how we make the numbers defensible. It is
   not a re-publication of the review text — users cannot browse the
   full dataset through the UI.

5. We do NOT expose the raw dataset via any API endpoint. We do NOT
   redistribute the dataset.

If any of the above changes your assessment of the non-commercial vs
commercial question, please let us know. We can adjust the use pattern
if needed — for example, by reducing drill-through to single-phrase
snippets or by paraphrasing rather than quoting.
```

---

## Process recommendations (not part of the email)

1. **Send Template A first.** Do not lead with the technical detail. Researchers receiving these requests appreciate direct questions answered first.
2. **Allow 1-2 weeks for a response.** The McAuley Lab is an academic group; they are not obligated to reply on vendor timelines.
3. **If no response in 2 weeks:** a polite follow-up is appropriate. If still no response in 4 weeks, the team should treat the data as research-use-only per the 2018 precedent language and restrict the dashboard demo accordingly.
4. **Save the reply verbatim.** Whatever Dr. Hou or Dr. McAuley says in writing is the defensible posture. Do NOT summarize or paraphrase their reply into an internal doc without attaching the original email.
5. **If the reply is "we cannot grant commercial permission":** the UCSD layer must be removed from any client-facing build. The R4 dashboard still works — R4-P0-2 Reddit PRAW + HN Algolia is the GREEN-LIGHT primary path. UCSD is strictly the optional Tier 2 add per charter §4.2.
6. **If the reply is "research use is fine, commercial requires separate permission":** proceed with the internal demo, label the client-facing demo path as blocked pending licensing, and decide in R5 whether to pay for separate licensing or remove UCSD.
7. **If the reply is "we do not own the data and cannot license it":** this is the likely outcome based on the 2018 precedent language. The lab's position is that Amazon owns the underlying user content and the lab's role is merely curation. In that case the commercial risk sits with Amazon's own ToS, not with the lab's permission — a completely different legal question that requires counsel, not email.

## Rejected angles (TRIED_AND_REJECTED spirit)

- **Send from an AI-agent-looking email address:** rejected. Real humans making licensing decisions will not respond to anything that looks automated.
- **Request commercial permission upfront:** rejected. Opens with "we want to make money from your data" and lands badly. Template A asks about use cases, not permissions.
- **Offer to pay:** rejected. Academic datasets are typically not licensed this way, and offering payment pre-reply can imply commercial intent for the research use case too.
- **Cite the 2018 "for research purposes" language in the first email:** rejected. It reads as cornering them with their own past phrasing. Better to let them state the current position first.

## Reference

- `contracts/research/orchestrator/ucsd_amazon_ingest_plan.md` — backend-v3's R3 research with the YELLOW LIGHT verdict in §6 and the contact information
- `contracts/round_4_charter.md §4.2` — the R4 charter section that names this as a pre-R5 action item
- `contracts/real_api_integration_proposal.md` line 234 — the original R3 proposal language on UCSD licensing
