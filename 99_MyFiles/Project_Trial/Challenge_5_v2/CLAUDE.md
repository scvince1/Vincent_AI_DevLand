# Project: Consumer Sentiment Dashboard — Social Listening MVP
**Competition:** SharkNinja Challenge 5 v2
**Stack:** FastAPI (backend) + React/TS/Vite (frontend), fully decoupled.

This CLAUDE.md is project-local. It is loaded by EVERY teammate the moment they spawn into the `sharkninja-sentiment` team. Read it first, every time. The rules below are hard constraints, not suggestions.

---

## 1. The NLP Differentiator (the whole point of this project)

We are competing against social listening tools (Brandwatch, Sprout Social, Meltwater, Talkwalker). Our wedge is **NLP quality on consumer-electronics reviews**. This is the evaluation criterion judges will actually look at.

**VADER alone is NOT ACCEPTABLE as the competitive story.** VADER is the baseline, nothing more. On top of VADER we must ship an **enhanced NLP layer** that demonstrably handles ALL FOUR of the following, verified by an edge-case test suite living in `backend/tests/test_nlp_edge_cases.py`:

1. **Sarcasm** — e.g. "Oh great, another vacuum that dies after 3 months" must not score as positive.
2. **Comparative sentiment** — e.g. "Shark is way better than Dyson at edge cleaning" must credit Shark positively and Dyson negatively (or at least relatively), not lump them together.
3. **Aspect-level sentiment (ABSA)** — e.g. "Suction is incredible but the battery is garbage" must emit TWO aspect scores, not one averaged meh-neutral.
4. **Consumer-electronics domain terminology** — "dustbin", "HEPA", "brushroll", "cyclonic", "pod", "carafe", "descale", "steam wand", "roller", "agitator" etc. must be recognized and not dropped as noise. Domain lexicon lives in `backend/app/nlp/domain_lexicon.py`.

Every edge case claimed in `contracts/requirements.md` must have at least one failing-before / passing-after test in the edge-case suite. **"We shipped an enhanced NLP layer" is a claim that must be defensible with tests.**

P0 REQ-IDs include the edge-case suite — do not descope it.

---

## 2. Hard File Ownership (overwrites = failure)

Each teammate writes ONLY the paths listed next to their name. If you feel the urge to touch a path you don't own, stop and SendMessage to the owner instead. Overwriting another teammate's file is a project-level failure — no exceptions, no "just a small fix".

| Teammate | Owns (write) | May read |
|---|---|---|
| **business-leader** | `contracts/requirements.md`, `contracts/review-round-*.md`, `README.md` | everything |
| **backend-engineer** | `backend/**`, `contracts/api-contract.yaml` | everything |
| **frontend-engineer** | `frontend/**` | everything |

`CLAUDE.md` (this file) is owned by the orchestrator (team lead). Teammates do not edit it.

### The schema source-of-truth rule

`backend/models/schemas.py` is the **single source of truth** for API shapes (request/response Pydantic models). `contracts/api-contract.yaml` is an **export snapshot** of those schemas — backend-engineer generates it from schemas.py and commits it so frontend-engineer can read a stable contract without touching Python.

- Frontend reads `contracts/api-contract.yaml` to build TS types. Frontend does NOT read `schemas.py` directly.
- Backend is the only one who may edit either file. If the contract changes, backend updates schemas.py, regenerates the YAML, and notifies frontend via SendMessage.
- Frontend may request contract changes by SendMessage, never by editing the YAML.

---

## 3. Scraper Abstraction (non-negotiable shape)

Backend must ship a `BaseScraper` ABC plus a `CSVAdapter` implementation. Routers depend on the ABC, never on CSVAdapter directly. Real scrapers (Reddit, Twitter/X, Trustpilot, etc.) must be droppable later via dependency injection without any router changes. If the router imports CSVAdapter by name, that's a bug.

```
backend/app/scrapers/
    base.py          # BaseScraper ABC
    csv_adapter.py   # CSVAdapter(BaseScraper) for the MVP demo data
    __init__.py      # factory / registry
```

The factory is wired into FastAPI via `Depends(...)` so swapping is a one-line config change.

---

## 4. Pydantic = API contract

Pydantic models in `backend/models/schemas.py` ARE the canonical API shapes. FastAPI response_model / request body annotations must reference them directly. Don't hand-roll dicts in routers. Don't duplicate the shapes in docstrings. If you change a Pydantic model, you have changed the contract — regenerate the YAML and ping frontend.

---

## 5. Workflow and communication

- Use **TaskList / TaskUpdate** for work tracking. Claim tasks by setting `owner` to your name.
- Use **SendMessage** to talk to teammates (by name, not UUID). Plain text output is NOT visible to other agents.
- backend-engineer and frontend-engineer **require plan approval** before writing any code. Submit your plan, wait for approval, then execute.
- business-leader does not require plan approval for research/doc work, but must use SendMessage to notify backend/frontend when `contracts/requirements.md` is ready.
- Review rounds: business-leader inspects backend and frontend deliverables, writes `contracts/review-round-N.md` with findings, SendMessages the owner with action items.
- When you finish a task, mark it completed via TaskUpdate, then TaskList to find the next.

## 6. Forbidden

- Editing files outside your ownership column.
- Shipping the "enhanced NLP layer" as VADER with a wrapper. If the edge-case tests don't exercise real behavior, it doesn't count.
- Hand-rolling API response dicts instead of Pydantic models.
- Hard-coding CSVAdapter in routers.
- Silent contract changes (changing schemas.py without regenerating YAML + notifying frontend).
- Mocking the edge-case test suite. Those tests must run against the real NLP pipeline.
