# Respecting Human Efforts: What Karpathy's LLM Wiki Doesn't Say

*What happens when a historian builds an AI knowledge system*

---

The first time I tried to fit living knowledge into a retrievable shape, I used scissors.

I was writing a novel — a dozen cities, three years of war, roughly twelve characters whose lives collide at unpredictable intervals. I don't outline. I build each character entirely in my mind and watch them move, and the story is supposed to emerge from the collisions. But when I sat down to write, the timelines contradicted each other. Lives I had imagined in full turned out to be incompatible the moment they shared the same world.

So I wrote out each character's story from beginning to end — dense, emotionally saturated documents, tens of thousands of words each — and then transferred everything into a spreadsheet. One row per event, one column per character. Cold, clinical. I printed it out, took a pair of scissors, and cut each row into a strip.

I moved the dining table onto the balcony to make room. I spread every strip across the living room floor and began rearranging them by hand, tearing the name cell off the leftmost column and pasting it onto a different strip, trying to find an order in which all of these people could exist simultaneously. When I was finished, I had twenty-some pages of clean, uncontradicted timeline — and a large pile of torn fragments. Moments I had lived inside vividly, but that could not survive contact with structure.

That was years before LLMs entered my life. I have encountered versions of this problem again and again since then, and they were never just mine. Most recently, it surfaced when **Andrej Karpathy** published a short document on GitHub.

## The Blueprint

Three days before I began writing this, Karpathy — founding researcher at OpenAI, former head of AI at Tesla — posted what he called an **"LLM Wiki."** The premise was disarmingly simple: instead of vector databases and embedding pipelines, you build a knowledge layer out of plain markdown files organized in folders, with a single index file as a navigational map. The LLM reads the index first, then decides what to read next. He framed it as a design pattern, not a deployment manual. Within days, developers were replicating it. In the comments, a smaller group said something more interesting: they had already been running systems like this, independently, for months.

I was one of them, though I had arrived from a very different direction. I am a historian by training — not of wars or states, but of the everyday technologies that quietly restructure how people live. How flush toilets reshaped domestic architecture. How gas stoves changed not just cooking but the rhythm of a household's day. How electric lighting rewrote labor law long before legislators understood what had happened. My professional reflex, when I encounter any technology, is not to ask what it can do but what it does to the person using it. That reflex led me to the same architectural pattern Karpathy described — not through machine learning research, but through the problem of making my own knowledge navigable without destroying the things that made it alive.

## Three Systems, One Architecture

Today I run three separate knowledge systems, all built on the same structural pattern.

*Horsys* manages our equine import business: invoices, contracts, veterinary records, regulatory filings — and, less formally, my accumulated judgments about the people we work with. Who negotiates honestly. Which veterinarian I trust with which kind of horse. *NovelOS* supports a long-running collaborative science fiction and game design project — hundreds of world-building documents, and a category I came to call **Pending Terms**: contradictions I deliberately keep alive rather than forcing to resolution. *LifeOS* coordinates everything else — teaching, writing, research, job search — across half a dozen professional roles that share a single calendar and a single person.

Each system follows the same core pattern. At the entry point is **the Dump**: a folder where anything can be dropped without pre-sorting — raw documents, voice notes, screenshots, half-formed thoughts. An orchestrator classifies each item and routes it to a specialized agent. An Archive Agent writes the processed knowledge into a markdown-based knowledge base, generating metadata and linking related concepts across files.

Where my architecture diverges from Karpathy's is in retrieval. His sparse index — a single file listing everything — works at moderate scale, but my novel project alone contains several hundred interconnected documents. So I designed a hierarchical search: the system reads the folder structure first, which encodes my own categorical thinking, then the relevant index files, then the metadata of candidate documents, and only then the full text. At each stage, irrelevant material falls away. For *LifeOS*, I replaced the index entirely with **Manifests** — compressed, AI-generated summaries of each knowledge cluster. For most queries, the Manifest is the answer. The system never opens the underlying files.

Every one of these choices was shaped by cost. The first night I cold-started *NovelOS*, the system burned through roughly a hundred dollars in API fees. Over months of iteration, I brought my monthly spend across all three systems into the low tens of dollars — not from better models, but from a single principle: design every retrieval path to read only what it must.

## The Articulation Bottleneck

The architecture worked. Then I hit a problem that no amount of engineering could solve.

When I built the metadata schema, I listed every category I thought I would need. The AI suggested additions. Between us, we produced something that looked comprehensive. It was not. The AI had generated fields that were technically plausible but practically useless. Worse, it had missed fields that turned out to be essential — and I couldn't have told it what was missing, because I didn't know myself. I only discovered what I needed when I searched for something and failed, and then asked: *why didn't the system surface this?* Each time, the knowledge existed but had been filed without the one category that would have made it findable. A category I hadn't known to create, because I hadn't known I thought in those terms.

Michael Polanyi called this tacit knowledge — *we know more than we can tell.* But his formulation misses a second face of the same problem: we also need more than we can describe. I built an email assistant and told it to fetch my messages every hour. What I actually needed was not to be overwhelmed at the start of a new day. A system that takes the first instruction literally satisfies the specification while failing the person who wrote it.

The things we know but cannot articulate, the things we need but cannot describe, the ways our requirements contradict themselves over time — I came to see all of these as faces of a single constraint, and I began calling it ***Human Sloppiness.*** Not a deficiency. A design condition. Human knowledge is contradictory and contextual. Human needs are legible only in retrospect. Any architecture that demands perfect specification will fail, because the human cannot provide what the system requires. The question is not how to overcome this sloppiness. It is how to respect it.

So I designed around it. **Pending Terms** holds contradictions I cannot yet resolve. Most knowledge systems demand resolution; mine allows ambiguity to persist, and that ambiguity has proven generative — contradictions revisited months later often split into two productive paths rather than collapsing into one forced answer. The human checkpoints I built into the retrieval chain exist because a system that never asks for help silently gets things wrong.

None of this is optimization in the engineering sense. It is accommodation — architecture shaped around what the human cannot cleanly express. And the process of building it changed me in ways I did not expect. Every folder encoded a judgment about how my own knowledge is structured. Every metadata field I kept or discarded reflected a priority I had never articulated. Every unresolved contradiction was an acknowledgment that premature closure would cost me more than ambiguity.

Most writing about AI asks whether the system is better. Building these systems forced me to ask a different question: what happened to me — to my self-knowledge, my awareness of my own patterns — in the process?

And the systems also showed me, with uncomfortable clarity, where that self-knowledge stops.

## Walking Into the Barn

Our company has been switching stables — the facility where imported horses are housed, trained, and cared for between transactions. Over two weeks, we visited four operations. All credible. At this level of the market, any barn on our shortlist has already cleared the basic thresholds: acreage, infrastructure, credentials, competitive record. On paper, the differences are marginal.

I walked into one of those four barns and knew it was right. Not after the tour. Not after comparing notes with my team. During the first walk through the property, before anyone had made a pitch.

I could not, at that moment, have told you why. It was only later — weeks later, while maintaining my knowledge base and working through the decision with my staff and business partner — that the reasons began to surface, one by one, as if they had been waiting to be named.

The flies. Or rather, the absence of them. The barn had lizards along the fence line and almost no mosquitoes. The fly count was remarkably low for a facility housing that many horses. What this meant, I realized afterward, was that the property's ecosystem had been deliberately managed — the barn owner had designed the environment to be robust against pests, not just treated the symptoms. At the time, I did not consciously think *there are very few flies here.* I did not notice a ladybug and draw a conclusion. But the accumulated absence registered somewhere below conscious attention, in the part of the mind that reads an environment before the analytical mind catches up.

The horses themselves. How they stood in their stalls — calm, unbothered by strangers walking through. This is not nothing. A horse that startles when unfamiliar people enter its space is telling you something about how it is handled on the days when no visitors come.

The way the barn owner talked about individual animals. Every owner we met was in sales mode — that is the nature of these meetings, and I expect it. But within that register, there were differences that no pitch could disguise. One owner, asked about a particular horse, answered immediately: its name, its quirks, the small behavioral details that make it a specific animal and not a line item. Another owner paused — just slightly, just long enough — and you could feel a mental spreadsheet being consulted. Both could produce the information. The difference was where it lived in them.

And then there were things so fine-grained that I hesitate to describe them, because in isolation they sound almost absurd. One barn owner, describing a horse jumping a fence, mentioned the way the animal's neck extended forward on landing — a small thrust, a minor imbalance that most observers would never register. It matters because a rider feels it: that fraction of a second where the balance shifts, where the horse's center of gravity moves slightly ahead of where the rider expects it. No buyer would say "I didn't like this horse because of the forward neck motion on landing." They would say "something felt off" or simply that the horse wasn't for them. But a barn owner who *notices* this — who carries this level of physical attention toward the animals in their care — is a barn owner who will catch the things that never appear on an evaluation form. A barn owner who doesn't notice will let those things persist, invisible and consequential, until they eventually cost a sale or, worse, an injury.

None of this was a checklist I carried into those visits. None of it was a scoring rubric applied after the fact. It was the accumulated effect of years spent in this industry and adjacent ones — knowledge of animal husbandry, of Southern business culture, of ecological systems, of how people perform trustworthiness versus how they practice it. All of it operating as a single integrated act of perception, most of it below the threshold of language.

I want to be precise about what this is, because the easy word — *intuition* — is the wrong one. Intuition implies something approximate, closer to luck than to knowledge. What I am describing is the opposite. It is the most precise thing I do. It is the full weight of everything I have learned, every partnership I have navigated, every failure I have watched unfold — operating not as a sequence of criteria but as a unified whole. It activates when the situation demands it, and it is reliable precisely because it cannot be decomposed. Separate the parts and each one becomes trivial. Together, they constitute something no schema could reproduce.

This is what I mean by ***Human Efforts.*** Not a soft phrase. A precise one. It names the total capacity — judgment, experience, knowledge, moral reasoning, all of it integrated beyond the reach of conscious retrieval — that a person brings to bear in the moments that matter. Most of this capacity cannot be articulated, even by the person who carries it. That is not its weakness. That is the condition of its power.

You cannot teach this to an AI. The most sophisticated self-improving knowledge system can only approach it asymptotically — learning more about how this particular person operates, what patterns their decisions follow, what conditions activate their deepest expertise. A good system can support this capacity. It cannot become it.

## What Gets Freed

If *Human Efforts* name something AI cannot replicate, then the prevailing narrative about replacement is pointed in the wrong direction.

Consider what is actually being replaced when AI enters a workflow. A procurement officer spends four hours a day formatting purchase orders and chasing confirmations by email. She has fifteen years of supply chain experience. She knows which suppliers will deliver and which won't — not from the data, but from watching people keep and break promises across hundreds of transactions. That knowledge lives in her the same way my knowledge of barns lives in me. But her job never asks for it. Her job asks her to format purchase orders. A compliance analyst with a law degree and seven years of regulatory experience spends his days cross-referencing updates against internal policies. He can sense when a new rule will matter and when it won't. His job never engages that capacity. His job asks him to cross-reference.

When AI absorbs the formatting and the cross-referencing — what has been lost? The person is still there. The capacity is still there. What has been removed is work that never required a whole person, assigned to one only because no alternative existed. If there is something troubling here, it is not that AI is coming for these roles. It is that these roles already left so little room for the thing that makes the people in them irreplaceable.

Done right — and everything depends on that qualifier — AI does not diminish *Human Efforts*. It clears the space around them. It absorbs the mechanical layer so that the person can function as a whole person more often, on the problems that genuinely require what only they can bring. But this only works if the AI is built to learn the specific person it serves — how they search, what categories their thinking uses, where their expertise resists clean filing. A system that treats every user identically will produce outputs and quietly lose the trust of the people whose expertise it was supposed to support.

This is the question that Karpathy's **LLM Wiki** opens but does not address. His architecture is the skeleton — markdown files, folder structures, sparse indices, hierarchical retrieval. It is elegant and it works. What it does not ask is whose knowledge this is. Whose categories the folder structure reflects. Whose sloppiness the system must accommodate. Whose efforts it is meant to honor.

We are not replacing people with AI. We are shaping AI to the person — to respect that person's *Human Efforts.*

---

The strips of paper are gone from my living room floor. The dining table is back where it belongs. But the problem they represented — how to make living knowledge retrievable without killing what makes it alive — has become everyone's problem. Every organization deploying AI is standing in some version of that living room, trying to fit what their people know into a shape a machine can navigate.

The architecture exists. The design patterns are not proprietary. The costs are manageable. What remains is the harder question.

Do you know your people well enough to build a system that respects how they think?

And if you don't — what would it take to find out?
