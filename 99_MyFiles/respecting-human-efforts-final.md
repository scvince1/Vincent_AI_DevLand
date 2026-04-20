# Respecting Human Efforts: What Karpathy's LLM Wiki Doesn't Say

*What happens when a historian builds an AI knowledge system*

---

The first time I tried to fit living knowledge into a retrievable shape, I used scissors.

I was writing a novel — a dozen cities, three years of war, roughly twelve characters whose lives collide at unpredictable intervals. I don't outline. I build each character entirely in my mind and watch them move.

But when I sat down to write, the timelines contradicted each other. Lives I had imagined in full turned out to be incompatible the moment they shared the same world.

So I wrote out each character's story from beginning to end — dense, emotionally saturated documents, tens of thousands of words each. Then I transferred everything into a spreadsheet. One row per event, one column per character. Cold, clinical. I printed it out, took a pair of scissors, and cut each row into a strip.

I moved the dining table onto the balcony to make room. I spread every strip across the living room floor and began rearranging them by hand. Tearing the name cell off the leftmost column, pasting it onto a different strip. When I was finished, I had twenty-some pages of clean, uncontradicted timeline — and a large pile of torn fragments. Moments I had lived inside vividly, but that could not survive contact with structure.

That was years before large language models. But the same problem surfaced again when Andrej Karpathy published a short document on GitHub, and I realized it had never been just mine.

## The Blueprint

Three days before I began writing this, Andrej Karpathy — founding researcher at OpenAI, former head of AI at Tesla — published a document on GitHub: the "LLM Wiki." Instead of vector databases and embedding pipelines, you build a knowledge layer out of plain markdown files in folders, with a single index file as a navigational map. The LLM reads the index first. Then it decides what to read next.

Karpathy framed this as a design pattern, not a deployment manual. Within days, developers were replicating it. In the comments, a smaller group said something more interesting: they had already been running systems like this, independently, for months.

I was one of them — arrived not from machine learning research but from the problem on my living room floor. Karpathy's answer was architectural. Mine started as bodily: cutting, rearranging, discarding. The underlying logic was remarkably similar. The differences began to matter quickly.

## Three Systems, One Architecture

Today I run three separate knowledge systems, each built on the same structural pattern.

Horsys manages an equine import business: invoices, contracts, veterinary records, regulatory filings — and my accumulated judgments about people. Who negotiates honestly. Which veterinarian I trust with which kind of horse. NovelOS supports a collaborative science fiction and game design project — hundreds of documents, and a category I came to call Pending Terms: contradictions I deliberately keep alive rather than forcing to resolution. LifeOS coordinates everything else — teaching, writing, research, job search — across half a dozen professional roles that share a single calendar and a single person.

Each follows the same core pattern. At the entry point: the Dump. Anything can be dropped without pre-sorting — raw documents, voice notes, screenshots, half-formed thoughts. An orchestrator classifies each item and routes it to a specialized agent. An Archive Agent writes the processed knowledge into a markdown-based knowledge base, generating metadata and linking related concepts across files.

Karpathy's sparse index — a single file listing everything — works at moderate scale. My novel project alone contains several hundred interconnected documents. So I designed a hierarchical search: the system reads the folder structure first — which encodes my own categorical thinking — then the relevant index files, then the metadata of candidate documents, and only then the full text. At each stage, irrelevant material falls away.

For LifeOS, where I need approximate awareness rather than surgical precision, I replaced the sparse index entirely with what I call Manifests — compressed, AI-generated summaries of each knowledge cluster. For most queries, the Manifest is the answer. The system never opens the underlying files.

Every design choice was shaped by cost. The first night I cold-started NovelOS — twenty-odd documents — the system burned through roughly a hundred dollars in API fees. Over months, I reduced the per-query cost by a factor of several thousand. Monthly spend across all three systems: low tens of dollars. Not from better hardware or cheaper models. From designing every retrieval path to read only what it must.

## The Articulation Bottleneck

The architecture worked. Retrieval was fast. Cost was manageable. And then I hit a problem that no amount of engineering could solve.

When I designed the metadata schema, I listed every category I thought I would need. The AI suggested additions. Between us, we produced something that looked comprehensive. It was not.

The AI had generated fields that were technically plausible but useless — categories I would never search by. Worse, it had missed fields that turned out to be essential. I couldn't have told it what was missing. I didn't know myself. I only discovered what I needed when I searched for something and failed — and asked: *why didn't the system surface this?* The knowledge existed, but had been filed without the one category that would have made it findable. A category I hadn't known to create, because I hadn't known I thought in those terms.

Michael Polanyi called this tacit knowledge: *we know more than we can tell.* But his formulation misses a second face. We also need more than we can describe.

I built an email assistant and instructed it to fetch my messages every hour. What I actually needed — what I could not have specified — was not to be overwhelmed at the start of a new day. A system that takes me literally satisfies the specification and fails the person.

These are not separate problems. The things we know but cannot articulate, the things we need but cannot describe, the ways our requirements shift and contradict themselves — all of these are faces of the same constraint. I began calling it *Human Sloppiness.* Not as a deficiency. As a design condition.

Human knowledge is contradictory and contextual. Human needs are legible only in retrospect. Any architecture that demands perfect specification up front will fail, because the human cannot provide what the system requires. The question is not how to overcome this sloppiness. The question is how to respect it.

So I designed around it. The Pending Terms folder holds contradictions I cannot yet resolve — naming decisions, mechanical conflicts, settings that could develop in two incompatible directions. Most knowledge systems demand resolution. Mine allows ambiguity to persist. Contradictions revisited months later, with new context, often split into two productive paths rather than collapsing into one forced answer. The human checkpoints exist because a system that never asks for help silently gets things wrong.

None of this is optimization in the engineering sense. It is accommodation — architecture shaped around what the human cannot cleanly express.

## The Historian's Lens

People question whether a historian has any business building AI systems. To a meaningful degree, they are right. I cannot write production code from scratch. When it comes to machine learning, I am less reliable than the people who do this for a living.

But I have spent my career studying something they generally have not: what happens to people when new technologies enter their lives.

My field is the micro-history of everyday objects. How flush toilets reshaped domestic architecture. How gas stoves changed not just cooking but the rhythm of a household's day. How electric lighting quietly rewrote labor law. Mundane things that restructure how people live — usually before anyone notices.

That training gave me a reflex: when I look at a technology, I do not ask what it can do. I ask what it does to the person using it.

A thought experiment. If my partner — a business executive, analytically formidable — built the same system from identical requirements, she would be faster. I might be more precise in certain structural decisions. The output, the cost, the time: roughly the same.

So the difference is not in the product. It is in what the process of building it does to the person who builds it.

She would walk away with a tool. I walk away having been forced to externalize my own cognitive structure — my contradictions, my judgment patterns, the things I knew but had never said. The system is a mirror, not a machine.

Most AI discourse asks: *is the system better?* I am asking a different question: *what happened to the person who built it?*

## Walking Into the Barn

We are switching stables — the facility where our imported horses are housed, trained, and cared for between transactions. We visited four operations in the span of two weeks. All of them credible. At this level of the market, any barn that makes it onto our shortlist has already cleared the basic thresholds: acreage, infrastructure, credentials, competitive results. On paper, the differences between them are marginal.

The decision does not live on paper.

It lives in questions whose answers I will not have for months or years. Will this barn owner cut costs on feed when margins tighten and no one is watching? When a storm comes through at night, will someone walk out in the rain to check ventilation in the stalls? If a disagreement develops between our team and a trainer over a horse's development strategy, whose side does the barn owner take — ours, or the trainer who is physically present every day and easier to keep happy? These are not hypotheticals. They are the operational reality of every partnership in this industry, and most of them surface only when something goes wrong.

I walked into one of those four barns and knew, before the tour was over, that this was the right place. Not suspected. Knew. The way the horses were standing in their stalls — calm, unbothered by our presence. The condition of the fencing in the back paddock, far from the entrance, where visitors rarely look. The way the barn owner answered a question about a horse that had been injured the previous month: what she said, what she chose not to say, how she held the pause before answering. Small things. Ordinary things. The kind of things you only know to look for after years of looking.

At another barn, I knew within minutes that we would not be signing. Everything was technically correct. The facilities were excellent. But something in the geometry of the interaction was wrong — a pattern I have seen before, in other partnerships and other industries, that reliably predicts a certain kind of problem eighteen months down the road. I could not have written it into a checklist. I could not have explained it to the AI in terms it could operationalize. But I would stake the business on it.

This is not a guess. It is not a lucky read. What I am describing is the most precise thing I do — not the most casual. It is the full weight of everything I have learned, every relationship I have navigated, every failure I have studied, every judgment I have trained through years of action and consequence, operating as a unified whole. It engages my knowledge, my ethics, my sense of how people behave under pressure, my understanding of what horses need and what compromises I am willing to make on their behalf. It activates when the situation demands it, and it is reliable precisely *because* it cannot be decomposed. Break it into parts and each part becomes trivial. Together they constitute something that no list of criteria could reproduce.

This is what I mean by Human Efforts. Not a soft phrase. A precise one. It names the total mechanism — judgment, experience, moral reasoning, knowledge accumulated over a lifetime and integrated beyond conscious retrieval — that a person brings to bear in the moments that matter. Most of this mechanism cannot be articulated, even by the person who carries it. That is not a weakness. It is the source of its power.

You cannot teach this to an AI. You cannot fully decompose it into a schema. The best self-improving knowledge system, the most sophisticated agentic workflow, can only approach it asymptotically — learning more and more about how this person operates, what patterns their decisions follow, what conditions activate their deepest expertise. It can support the mechanism. It cannot become it.

## What Gets Freed

The prevailing narrative about AI is replacement: which jobs it will take, which humans it will render unnecessary. I think this framing is backwards.

Consider what, exactly, is being replaced. A procurement officer spends four hours a day formatting purchase orders, cross-referencing inventory spreadsheets, and chasing confirmations by email. She has fifteen years of experience in supply chain management. She knows which suppliers will actually deliver on time — not from the data, but from watching people keep and break promises across a hundred transactions. That knowledge lives in her the same way my knowledge of barns lives in me. But her job never asks for it. Her job asks her to format purchase orders.

A compliance analyst manually cross-references regulatory updates against internal policy documents, flagging discrepancies in a spreadsheet that someone else reviews. He has a law degree and seven years of experience reading regulatory language. He can sense when a new rule will matter and when it won't — not from keyword matching, but from understanding how enforcement actually works. His job never asks for that. His job asks him to cross-reference.

When AI absorbs the formatting, the cross-referencing, the chasing, the flagging — what exactly has been lost? The person is still there. The mechanism is still there. What has been removed is the work that never needed a whole person in the first place but got assigned to one because there was no alternative. The real question is not whether AI replaces these people. The real question is why these roles had so little room for the thing that makes these people irreplaceable.

Done right — and I want to hold the weight of that phrase, because "done right" is doing all the work — AI does not diminish Human Efforts. It clears the space around them. It absorbs the mechanical layer so that the person beneath it can operate as a whole person more often, in more of their working hours, on the things that actually require what only they can bring.

But this only works if the AI is designed to learn the person it serves. Not people in general. This person. How they search, what categories their thinking actually uses, where their expertise lives in forms that resist clean filing. A system that treats every user identically will function and quietly fail. The people with the deepest expertise will stop trusting it first — because they will feel the gap between what the system considers relevant and what they know actually matters.

This is the design problem that Karpathy's LLM Wiki opens but does not address. His architecture is the skeleton — markdown files, folder structures, sparse indices, hierarchical retrieval. It is elegant and it works. What it does not ask is: whose knowledge is this? Whose categories does the folder structure reflect? Whose sloppiness does the system need to accommodate? Whose efforts is it designed to honor?

We are not replacing people with AI. We are shaping AI to the person — to respect that person's Human Efforts.

## Close

The strips of paper are gone from my living room floor. The dining table is back where it belongs. But the problem they represented — how do you make living knowledge retrievable without killing what makes it alive — has become everyone's problem. Every organization deploying AI is now standing in some version of that living room, trying to fit what their people know into a shape a machine can navigate.

The architecture exists. The design patterns are not proprietary. The costs, after iteration, are manageable. What remains is the harder question — the one that no amount of engineering resolves on its own.

Do you know your people well enough to build a system that respects how they think?

And if you don't — what would it take to find out?
