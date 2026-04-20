# Interview Answers v2
## SharkNinja Round 0 — Post-Joyce Rewrite
## 2026-04-12

These answers were rebuilt from scratch after mock interview feedback. They replace the corresponding answers in Locked_Interview_Answers.md for Round 0 delivery.

---

## 1. Tell Me About Yourself (~75 seconds)

> I'm Vincent. I'm from Beijing, China. Came to Minnesota in 2018 for college. I started doing Economics and Geology, and eventually got my Master degree from the University of Chicago, focusing on the history of technology: how we confront, resist, and transform with tech.
>
> My life has been living on this tripod. One leg is the intellectual journey. The second one is just survival, doing multiple jobs at the same time, learning across fields, working with people across the social ladder. The last one is building, for people's needs.
>
> I started off in a village near the Myanmar civil war zone, where I spent five summers and winters building schools, farms, and water dams. Then, in my PM role, I built curriculum and school reform. At UChicago I built business solutions and AI adoptions. Now, I build AI systems making businesss to make better decisions.
>
> Through this journey, the common drive I have is not just building the tool, but also building the people. We need to make the best technical tools that fit the people, and also empower the people with a culture to learn the tool. It's a bilateral process that I think many companies are failing to recognize. When I saw the Jailbreak program at SharkNinja, I believe I found a company that shares a similar vision. Hence, here I am.

**Myanmar follow-up bridge (if asked):**
> "It was a nonprofit education program in a remote area near the border. We were about 100 miles from the combat zones. I was one of the deployment coordinators and managed four deployments over five years. We built with whatever we had and we had to make it work. It made me hardy, and it taught me to see hardiness in people."

---
                 
## 2. Why SharkNinja? (~80 seconds)

> Honestly, I really appreciate the working culture I'm noticing. In my eyes, SharkNinja is a fast-paced, scrappy company. Where everyone's hands are dirty, ideas touch the ground, and people actually support each other in getting things done. I listened to Mark on Masters of Scale, and a few things stood out. He said the company was built "one five-star review at a time" and they've never acquired a dollar of revenue in their history. Everything is organic. That tells me this is a company that builds, not buys. And when I saw the Jailbreak program, his point was: who better to revolutionize the business than the people inside the business? That's exactly how I think about AI. Don't ask for some outside miracle AI solution and hope it works. Watch what our people have already been doing, find the real problem, and build from there, from within.
>
> And honestly, I have a bit of a chip on my shoulder about this. A lot of the industry still thinks AI means hiring more engineers to write more code. I see it differently. When the technology is strong enough that the technical barriers are disappearing on their own, the real work shifts to understanding people. I build tools to make people better, not to make people unnecessary. Building them up, not replacing them out. I'm not naive. AI will replace some jobs. That's how the world works. But I'd rather be the person who makes sure the people around me are thriving into the new world, not the one building the thing that catches them off guard. SharkNinja is one of the few places I've talked to that genuinely gets this. I want to be here to prove it right.

---

## 3. What have you been doing with AI? — Horsys (~57 seconds)

> I built an agentic AI system called Horsys for the horse import business I manage. When I arrived, data was everywhere and nowhere. Different formats, different languages, different places, and it wastes too much time when we need to make a decision or act on an emergency. It was a lot to handle, so I built a system to help us.
>
> I used Claude Code to build the whole thing. It's a centralized knowledge base with specialized agent teams on top, each handling a different function: financials, people profiling, horse tracking. The key design decision was the interface. People in this business are non-technical people, so I want to give them something they would use on a daily basis. Guess what, I hooked everything into WhatsApp. They just message me, can be a note on the horse, training schedule, PDF of an invoice, voice memo reminder, etc., and the system captures it, syncs the knowledge base, and updates the financial model automatically.
>
> Next, I'm building a client prediction layer. Input a potential client's description, upload some chat history, and the system predicts whether this is a real prospect, a tire kicker, or a hidden competitor.
>
> Most companies face the same fragmented data problem. And most importantly, most companies have tiered AI users. While we don't have to make everyone equally capable at using AI and writing code, we don't want people to be left behind. I believe my solution is a proof of concept that can scale in bigger companies.

---

## 4. What have you been doing with AI? — BaseOS (~70 seconds)

> BaseOS started as an academic side project with a friend in cognitive science. We were using ChatGPT to process data and create visualizations, and it turned into a challenge: who can get the exact result in one prompt, one go, everything right? After a few rounds, the question shifted. What if that one prompt could set up an entire AI knowledge system, with self-improving mechanisms built in, and walk any person through the full personalization process for their own needs?
>
> That's what BaseOS is. A single setup process that gives someone a personalized AI system with a knowledge base, expandable agents, and built-in guidance, all from scratch. It's designed to be both the foundation for future AI solutions and the hands-on onboarding experience itself. You learn by building your own system.
>
> I've tested this on a few dozen people. People who were terrified of coding and command lines walked away with a working agentic AI system, personalized to them, with room to grow. The setup prompt still needs work, but it's already the backbone for Horsys and every other AI system I use daily.
>
> I think this has real implications for SharkNinja. You have super users who are already deep in AI, but you also have a lot of capable people who just haven't found their entry point. BaseOS could be that entry point, into personalized AI agents or even vibe coding.

**BaseOS one-liner:**
> "One guided session takes someone who's never touched a command line and walks them out with a personalized AI system they built themselves. The onboarding is the product — you don't learn AI then build, you build and that's how you learn."

---

## 5. What have you been doing with AI? — NovelOS (~50 seconds)

> NovelOS started as a personal project. I needed to organize thousands of pages of historical archival material into something searchable and structured. So I built a knowledge system that takes all of that, raw notes, novels, research papers, and turns it into a systematic knowledge base with built-in drafting capabilities, fact-checking mechanism and self-learning capabilities.
>
> I did a tech demo for a few dozen fellow editors and writers, in academia or literature. They walked away with their own knowledge systems, each one tailored to their projects. Thousands of pages of material, organized and cross-referenceable.
>
> The business use case is straightforward. Any team that sits on a lot of written documents, needs to cross-reference them regularly, and follows manuals or standard procedures for how things get done. The knowledge base doesn't just store the documents, it maps the relationships between them. And everything is still in natural language. If anyone needs to maintain or verify something, they can just read the files directly, no coding, no special syntax. The existing workflow of manual review and memory-based search still works as a fallback, but the system works faster.

---

## 6. How did you build it? — NovelOS (~57 seconds)

> I started from the ground up, with myself as the prototype. How do I actually learn? How do I group knowledge? How do I take notes? I used that reflection to design the skeleton of the knowledge base, then sat down with Claude Code and worked out the folder architecture together.
>
> From there, I broke every process in my workflow into atomic pieces and figured out which ones an AI agent could replicate. People now call this harness engineering. I didn't know the term. All I had was a wide array of field experience and 250,000 years of human technology history telling me how to think about organizing knowledge.
>
> The building itself was pure iteration. Propose a solution, test, fail, learn. Repeat until it works. Once the basics were running and my daily work was automated, I finally had time to study AI properly: architecture, design patterns, skills that don't pay off immediately but compound over time.

---

## 7. How did you build it? — BaseOS (~55 seconds)

> BaseOS is a different kind of build because the product isn't a system, it's a system that builds systems. It started from prompt engineering. My friend and I kept pushing how much a single prompt interaction could accomplish. At some point I realized: if I design this right, one prompt session can walk someone through setting up their own personalized AI knowledge base, with agents, with self-improving mechanisms, all from scratch. So the build process was mostly iteration with real people. A lot of cognitive science and human factors knowledge goes into this. I'd hand someone the setup prompt, watch where they got stuck, understand why they got stuck, and fold the fix back into the prompt. After a few dozen testers, the pattern was clear: people don't fail at the technical part, they fail at knowing what to ask for. So the prompt now guides that.

---

## 8. How would you do it differently? — AI systems (~47 seconds)

> Two things.
>
> First, don't reinvent the wheel. I rebuilt several architectures and features from scratch that already existed. The reinvention taught me a lot — it's a big part of why I pick up AI tools so fast now. But the time cost is real. That's fine for personal projects, not for a work setting. Now I search for existing solutions first and customize from there.
>
> Second, deliver before perfecting. I learned this as a private chef — I never missed a single service, even at peak load. But when I started building AI systems, I caught myself spending hours fixated on small details before the basic functions were even up. I already knew the principle: a delivered good enough beats an undelivered perfection. I just had to relearn it in a new domain.

---

## 9. How would you do differently? — Career

> After my bachelor's, I would go into business instead of research for a few years, and probably do an MBA. I realized that to run any organization successfully, I need to have enough business knowledge and experience, in addition to technical capability. I already have the technical side and the people side. The business fundamentals would have gotten me further and sooner. But my past shaped who I am now, and I really cherish all the people and experience along the way.

---

## 10. Where do you see yourself in 5-10 years?

> In five to ten years, I want to be in a position where I'm connecting great people and enabling them to do their best work. There are people out there far better than me in their specialty. I don't need to be them. I know my specialty is to get good enough across the board and stand between those great people and bring them together. That's why I'm looking at an MBA down the line, to sharpen my business side and extend my reach. And I want to do this inside a company like SharkNinja, one that understands the importance of culture, where good ideas are encouraged, not just managed. By doing so, I can happily celebrate the great minds around me and help them work great things out. You see, I've had a lot of experience in education. Empowering people is something I've always tried to do, from education to AI. That won't change.

---

## 11. What if not hired?

> Well, I believe SharkNinja is the fit for me. If not this role, I believe there are plenty of great opportunities in the company, such as L&D or product development, as I see many of these roles are also incorporating AI workflows at SharkNinja. If none of these work, I have to admit it would be a very uneasy evening. But then, some bourbon and a good night's sleep, back on track. Sell some horses, do some research, keep developing AI, and when my visa expires, go back to China and start teaching again. Building the people, through tools.

---

## 12. Weakness (~45 seconds)

> My biggest gap is traditional data science tooling. My SQL is functional, not fluent. I haven't touched enterprise BI platforms in a production setting. A data engineer will outcode me any day of the week.
>
> But I ship effectively and keep improving. Horsys is running in production daily, and everyday people can interact with it. I went from zero coding experience to three production systems in about two weeks. I don't study then build. I build, and study new things to support the building. And honestly, in a space where there's no clear path yet, I think that's an advantage. I don't have a box to trap me, and I have multiple fields of knowledge at my disposal, and I'm always adding more. In execution, this offers me the capability to work alongside software engineers, iterate my version together with software engineers, and make sure it actually lands with the people who aren't software engineers. That's the gap I fill.

---

## 13. What's the first thing you want to build at SharkNinja? (~58 seconds)

> I wouldn't build anything right away. I'd start by observing and talking to people. Targeted interviews for about a week across departments, focused on three things: data fragmentation, the most pressing needs by department, and what already exists from Jailbreak, how those solutions actually landed, and why some worked and some didn't.
>
> Then, I would have enough ground to build. I might start with short-term entry points. Simplest setup, most inviting experience, fits how people already work. Quick wins that lay infrastructure underneath: data collection, logging, the things you need before anything bigger can scale. Additionally, prioritized workflows for the most pressing complex needs. I'm suspecting market intelligence to be the biggest immediate need. Maybe agentic simulations of market responses could help answer the "what if" question.
>
> And I think it's important to be clear about the goal. We're not trying to make everyone into power users. What we need is everyone operating in a collaborative AI network, where everyday users plug in their way, power users plug in and do more, and the culture always encourages people to get their hands dirty, build, and personalize for themselves. So beyond building tools with my team, supporting AI training across the company is just as important. Maybe more.

---

## Reference: SharkNinja Quotes Worth Dropping

| Quote | Attribution | Best used in |
|---|---|---|
| "One five-star review at a time" | Mark Barrocas, Masters of Scale | Why SharkNinja |
| "Never acquired a dollar of revenue" | Mark Barrocas, Masters of Scale | Why SharkNinja |
| "Who better to revolutionize the business than the people inside?" | Mark Barrocas, Jailbreak launch | Why SharkNinja / AI philosophy |
| "Low ego, high empathy" | Mark Barrocas | Culture fit questions |
| "Whitespace is uncovered through behavior, not user requests" | Mark Barrocas | What would you build / AI methodology |
| "Would you want your mom to buy this?" | Mark Barrocas | Product standard |
| "The faster you acknowledge you're losing, the faster you pivot" | Mark Barrocas | Failure stories |

---

*v2 — 2026-04-12 — Post-Joyce mock interview rewrite*
