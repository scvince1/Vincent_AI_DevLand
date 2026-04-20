# We Know More Than We Can Tell

*What happens when a historian builds an AI knowledge system*

---

The first time I tried to fit living knowledge into a retrievable shape, I used scissors.

I was writing a novel — a historical story spanning more than a dozen cities, three years of war, and roughly twelve characters whose lives collide at unpredictable intervals. My writing process is experiential. I don't outline functionally. I build each character entirely in my mind — their personality, their body, their complete inner world — and then I watch them move. The story emerges from the collisions.

But when I sat down to write, I discovered their timelines contradicted each other. Events that had to happen simultaneously couldn't have. Lives I had imagined in full turned out to be incompatible the moment they shared the same world.

So I wrote out each character's story from beginning to end — dense, emotionally saturated documents, tens of thousands of words each. Then I transferred everything into a spreadsheet. One row per event, one column per character. Cold, clinical. I printed it out, took a pair of scissors, and cut each row into a strip.

I moved the dining table onto the balcony to make room. I spread every strip across the living room floor — each one a small unit of someone's life — and began rearranging them by hand. Finding contradictions. Tearing the name cell off the leftmost column and pasting it onto a different strip, reassigning a moment from one character to another. When I was finished, I had twenty-some pages of clean, uncontradicted timeline — and a large pile of torn fragments. Moments I had lived inside vividly, but that could not survive contact with structure.

That was years before I had heard of large language models. It happened with scissors and a dining room floor. But it was the same problem that would surface again — in a sharper, more consequential form — when a researcher named Andrej Karpathy published a short document on GitHub, and I realized this had never been just my problem.

## The Blueprint

Three days before I began writing this article, Andrej Karpathy — one of the founding researchers at OpenAI and former head of AI at Tesla — published a brief document on GitHub outlining what he called an "LLM Wiki." The idea was deceptively simple: instead of relying on retrieval-augmented generation systems — the vector databases and embedding pipelines that most enterprise AI deployments depend on — you could build a persistent knowledge layer out of plain markdown files, organized in folders, with a single index file serving as a sparse navigational map. The LLM reads the index first. Then it decides what to read next.

Karpathy framed this deliberately as a conceptual reference — a design pattern, not a deployment manual. But the response was immediate. Within days, developers were replicating and extending it. In the comments, a smaller group said something more interesting: they had already been running systems like this, independently, for months.

I was one of them. But I had arrived at it from a different direction — not from machine learning research, but from the problem I had been wrestling with on my living room floor. The question was the same: how do you make a large, interconnected, constantly evolving body of knowledge navigable without destroying the things that make it alive? Karpathy's answer was architectural. Mine had started as something closer to bodily — cutting, rearranging, discarding. What surprised me was how similar the underlying logic turned out to be, and how quickly the differences began to matter.

## Three Systems, One Architecture

Today I run three separate knowledge systems, each built on the same structural pattern.

Horsys manages an equine import business. Invoices, contracts, veterinary records, regulatory filings, marketing assets, and — less obviously — my accumulated judgments about people: who negotiates honestly, who doesn't, which veterinarian I trust with which kind of horse. NovelOS supports a long-running collaborative science fiction and game design project — hundreds of world-building documents, character profiles, plot mechanics, and a category I came to call Pending Terms: contradictions and unresolved design decisions that I deliberately keep alive rather than forcing to resolution. LifeOS coordinates everything else — my teaching, my writing, my academic research, my job search, my daily schedule — across half a dozen professional roles that share a single calendar and a single person.

Each system follows the same core pattern. At the entry point is what I call the Dump: a folder where anything can be dropped without pre-sorting. Raw documents, voice notes, screenshots, half-formed thoughts. An orchestrator reads each item, classifies it, and routes it to a specialized agent — one handles finance, another archival, another scheduling. An Archive Agent writes the processed knowledge into a structured, markdown-based knowledge base, generating metadata fields and maintaining a tag system that links related concepts across files.

The retrieval logic is where my architecture diverges most sharply from Karpathy's original pattern. His sparse index — a single file listing everything in the knowledge base — works well at moderate scale. But my novel project alone contains several hundred interconnected documents. A single index becomes unreadable, for the machine and for the human who needs to verify it. So I designed a hierarchical search: the system first reads the folder structure itself — which encodes my own categorical thinking about the domain — then reads the relevant index files, then scans the metadata of candidate documents, and only then reads the full text of the files it has identified as relevant. At each stage, irrelevant material is filtered out, reducing both cost and noise.

For LifeOS, where I need approximate awareness rather than surgical precision, I replaced the sparse index entirely with what I call Manifests — compressed, AI-generated summaries of each knowledge cluster. For most queries, the Manifest is the answer. The system never opens the underlying files.

Every one of these design choices was shaped by a single constraint: cost. The first night I cold-started NovelOS — feeding it twenty-odd documents, the shortest a few hundred words, the longest several thousand — the system burned through roughly a hundred dollars in API fees. That is not a sustainable architecture. Over months of iteration, I reduced the per-query cost by a factor of several thousand. My monthly spend across all three systems is now in the low tens of dollars. That reduction did not come from better hardware or cheaper models. It came from architectural discipline — from designing every retrieval path to read only what it must.

## The Articulation Bottleneck

The architecture worked. Retrieval was fast. Cost was manageable. And then I hit a problem that no amount of engineering could solve.

When I designed the metadata schema — the structured fields that the AI uses to filter and classify each document — I sat down and listed every category I thought I would need. The AI suggested additions. Between us, we produced something that looked comprehensive. It was not.

In use, I discovered two things. First, the AI had generated fields that were technically plausible but practically useless — categories I would never actually search by. Second, and more troubling, it had missed fields that turned out to be essential. I couldn't have told it what was missing, because I didn't know myself. I only discovered what I needed when I searched for something specific and failed to find it — and then asked: *why didn't the system surface this?* The answer, each time, was that the knowledge existed but had been filed without the one category that would have made it findable. A category I hadn't known to create, because I hadn't known I thought in those terms.

The philosopher Michael Polanyi called this "tacit knowledge" — the things we know but cannot articulate. *We know more than we can tell.* But in practice, the problem has a second face that Polanyi's formulation doesn't quite capture: we also need more than we can describe.

A small example. I built an email assistant as part of LifeOS and instructed it to fetch my messages every hour. What I actually needed — what I could not have specified at the time — was to not be overwhelmed at the start of a new day. These are not the same instruction. A system that takes me literally satisfies the specification and fails the person.

I began calling this gap *Human Sloppiness* — not as a deficiency, but as a design constraint. Human knowledge is contradictory, contextual, emotionally weighted, and constantly evolving. Human needs are often legible only in retrospect. Any architecture that demands perfect specification up front will fail — not because the technology is inadequate, but because the human cannot provide what the system requires.

So I designed around it. The Pending Terms folder in NovelOS holds contradictions I cannot yet resolve — naming decisions, mechanical conflicts, settings that could develop in two incompatible directions. Most knowledge systems demand resolution. Mine allows ambiguity to persist. And that ambiguity turned out to be generative: contradictions revisited months later, with new context, often split into two productive paths rather than collapsing into one forced answer. The human checkpoints in the retrieval chain — moments where the system returns a document and says *I'm not confident this is relevant; you decide* — exist because I learned that a system which never asks for help is a system that silently gets things wrong.

None of this is optimization in the engineering sense. It is accommodation — architecture shaped not around what the machine can do, but around what the human cannot cleanly express.

## The Historian's Lens

People regularly question whether a historian has any business building AI systems. And to a meaningful degree, they are right. I do not have the technical training of a software engineer or a data scientist. I cannot write production code from scratch. When it comes to the mechanics of machine learning, I am genuinely less reliable than the people who do this for a living, and I know it.

But I have spent my career studying something they generally have not: what happens to people when new technologies enter their lives.

My academic field is the history of technology — specifically, the micro-history of everyday objects. How the arrival of flush toilets reshaped domestic architecture and public health. How gas stoves changed not just cooking but the entire rhythm of a household's day. How electric lighting quietly rewrote labor law. These are not the grand inventions that fill textbooks. They are the mundane things that restructure how people live, think, and relate to one another — usually before anyone notices it happening.

That training gave me a specific reflex: when I look at a technology, I do not ask what it can do. I ask what it does to the person using it. And that turned out to be exactly the question that mattered when I sat down to design a system meant to hold my own knowledge.

I tested this against a thought experiment. If my partner — a highly trained business executive, analytically formidable — were to build the exact same system from identical requirements, our end products would likely be roughly equivalent. She would be faster. I might be more precise in certain structural decisions. But the output, the cost, the time — roughly the same.

So the difference is not in the product. It is in what the process of building it does to the person who builds it.

She would walk away with a tool. I walk away having been forced to externalize my own cognitive structure — my contradictions, my judgment patterns, the things I knew but had never made explicit. The system I build is a mirror, not just a machine. And the process of building it changed me, regardless of whether the final product is measurably superior.

Most AI discourse asks: *is the system better?* I am asking a different question: *what happened to the person who built it?*

## Capital H Human

What happened to me is this: I was forced to make my own thinking visible.

Every folder I created encoded a judgment about how my knowledge is structured. Every metadata field I kept or discarded reflected a priority I hadn't previously articulated. Every contradiction I chose to leave unresolved in Pending Terms was an acknowledgment that my understanding was still forming — and that premature closure would cost me more than ambiguity.

The prevailing narrative about AI is about replacement: which jobs it will take, which workflows it will automate, which humans it will render unnecessary. I reject this framing — not because efficiency doesn't matter (my systems save thousands of dollars and countless hours), but because it mistakes the instrument for the purpose.

My framework is relational. I respect what the AI can do — its speed, its consistency, its capacity to hold structure across hundreds of documents without fatigue. In return, I expect it to respect what I bring — my contradictions, my ambiguity, my evolving judgment, my Human Sloppiness. This is not sentimental. It is architectural. Every design decision in my systems reflects this mutual accommodation.

We are not replacing people with AI. We are customizing AI according to the needs of the person — to better respect that person's Human Efforts.

The strips of paper are gone from my living room floor. The dining table is back where it belongs. But the problem they represented — how do you make living knowledge retrievable without killing what makes it alive — is now the central question of a technological era. It is not a question that engineers alone can answer, or humanists alone, or any single discipline working in isolation. It can only be answered by people willing to sit with their own knowledge long enough to discover what they cannot say.

Do you know your own organization well enough to teach it to a machine?

And if you don't — what does that tell you?
