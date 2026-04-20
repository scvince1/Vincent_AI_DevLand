# Research Output — Round 3 Reference Material
Generated: 2026-04-11
Purpose: feed business-leader-v2's deep-rethink task and v3 engineer spawn prompts for Round 3 of the SharkNinja Challenge 5 v2 project.

---

## 1. MiroFish

**Source:** https://github.com/666ghj/MiroFish (fetched successfully; mirofish.us URL was permission-blocked)

### What is MiroFish?
MiroFish is an open-source AI prediction engine that uses multi-agent swarm simulation to model future scenarios. It ingests real-world seed data (news, policy documents, financial data), builds a knowledge graph, instantiates thousands of autonomous AI agents, runs them through social interaction simulations, and generates prediction reports plus an interactive environment where users can query simulated agents.

### "Swarm Intelligence Prediction Engine" Explained
The "swarm intelligence" framing refers to emergent collective behavior arising from thousands of individual agent interactions — capturing second-order social dynamics that traditional statistical or regression-based forecasting misses entirely. It is not a traditional ML model; it is a social sandbox.

### Core Technical Architecture
| Stage | What Happens |
|---|---|
| 1. Graph Building | GraphRAG extracts entities and constructs knowledge graph from seed documents |
| 2. Environment Setup | Entity relationships extracted; agent personas generated with behavioral profiles |
| 3. Simulation | OASIS engine (from CAMEL-AI) runs dual-platform parallel sim with temporal memory |
| 4. Report Generation | ReportAgent queries the simulation via toolset and produces structured insights |
| 5. Deep Interaction | Users chat with simulated agents or the report layer via natural language |

**Stack:** Python 3.11-3.12 backend, Vue.js frontend, Node.js 18+, Zep Cloud (long-term agent memory), OpenAI SDK-compatible LLM interface (tested with Alibaba Qwen-plus).

### Applicability to Consumer-Electronics Sentiment Dashboard
MiroFish's architecture suggests three concrete integration ideas for a SharkNinja-style dashboard:

1. **Forward-looking implication panel:** Instead of showing only historical sentiment curves, seed a lightweight MiroFish-style GraphRAG pipeline with current review corpus + supply chain news, then project sentiment trajectory for next 4-8 weeks. Framed as "predicted sentiment index" with confidence bands.
2. **Scenario simulator (SKU launch):** User defines a hypothetical (new product, price change, competitor entry), seeds the simulation, and sees "simulated community reaction" 30 days out — comparable to Aaru's product research use case but open-source.
3. **Trend contagion detection:** OASIS simulations model how sentiment spreads across agent social graphs, which maps directly to platform virality modeling (TikTok vs. Reddit diffusion patterns differ structurally).

**Usability for this project:** MiroFish is a full open-source system (not an API), so integrating it directly is heavy lift for a dashboard sprint. The *concepts* (GraphRAG seeding, agent memory, emergent social simulation) are directly applicable to framing narrative around a "prediction" feature. A lighter proxy: use the GraphRAG pattern on the existing corpus to generate forward-looking summaries without running full simulation.

---

## 2. Aaru

**Source:** https://aaru.com — main site access permission-blocked; sourced via WebSearch and secondary coverage.

### What is Aaru?
Aaru is a synthetic population simulation platform that recreates entire demographic populations as orchestrated AI agents to predict human behavioral outcomes. It is NOT a traditional survey tool or focus group replacement via simple LLM prompting — it models agent behavioral architectures with decision-making traits, cognitive preferences, and social interaction dynamics at scale.

**Valuation / Traction (as of late 2025):** $1B valuation at Series A ($50M raised). Partners include Accenture, EY, IPG. EY replicated a 6-month market research study in one day with 90% median correlation.

### Inputs
- Demographic data: national censuses, financial records, social platform data
- Behavioral priors: proprietary datasets encoding decision-making tendencies
- Research question: user provides the stimulus (campaign concept, product idea, policy) in natural language

### Simulation Process
Aaru deploys thousands of AI agents, each endowed with demographic labels (age, income, geography) plus behavioral profiles (cognitive preferences, decision motives, risk tolerance). These agents interact with a simulated environment and with each other, then respond to the research stimulus. Simulations run in minutes.

### Outputs
- Predicted behavior distributions across audience segments
- Campaign/product reaction forecasts (sentiment, adoption likelihood, purchase intent)
- Segmented breakdowns: "how will 25-34 urban women react vs. 50+ suburban men"
- Scenario comparison: test multiple creative executions or product positionings side-by-side

### Applicability to Consumer-Electronics Sentiment Dashboard
Aaru is a *research platform* (API/enterprise), not an open library. But its framework maps cleanly to two dashboard enhancements:

1. **"What-if" SKU positioning simulator:** On the insight detail panel, add a module: "How would a repositioning of [product] toward [segment] affect sentiment trajectory?" Frame it as a synthetic audience preview backed by either Aaru API (if licensed) or a lighter prompt-based simulation using existing review segment data.
2. **Platform reaction curve forecasting:** Aaru models platform-specific diffusion. A dashboard could display: "based on current sentiment composition, a [feature X] launch would generate peak reaction on TikTok at T+3 days, plateau on Amazon at T+14 days." This is the "reaction curve" use case directly.

**Usability for this project:** Aaru is likely enterprise-priced and API-gated. For Round 3, the *concept* is more valuable than the product — frame the "prediction" quadrant of the dashboard as "Aaru-style synthetic simulation" to signal product maturity, even if the v1 implementation is a simplified prompt chain on historical data.

---

## 3. Claude Code Skills for Frontend Maturity

**Sources:** travisvn/awesome-claude-skills, wilwaldon/Claude-Code-Frontend-Design-Toolkit, ComposioHQ/awesome-claude-skills, rohitg00/awesome-claude-code-toolkit, WebSearch results.

### Top 8 Skills Ranked by Relevance to: React + TS + Vite + Recharts + Zustand Dashboard → Mature Product

| # | Name | Creator | What It Does | Install Command | Relevance |
|---|---|---|---|---|---|
| 1 | **frontend-design** | Anthropic (official) | Forces Claude to pick a real aesthetic direction before writing code; prevents generic bootstrap look; works with React + Tailwind | `claude plugin add anthropic/frontend-design` | **HIGH** — immediate baseline quality lift; 277k+ installs |
| 2 | **Bencium UX Designer** | bencium | Two-mode skill (Controlled for production, Innovative for exploration) with 830+ lines of accessibility guidance baked in; treats WCAG compliance as a design constraint not an afterthought | Manual install via `~/.claude/skills/` | **HIGH** — most thorough accessibility + UX pairing found |
| 3 | **Design Tokens Skill** | phrazzld | Builds an entire color/spacing token system from a single `--brand-hue` variable; outputs Tailwind v4 `@theme` blocks | Available at `claude-plugins.dev` | **HIGH** — prevents the "color chaos" problem that makes dashboards look amateur |
| 4 | **claude-d3js-skill** | Chris von Csefalvay | Expert D3.js data visualization patterns, best practices, and composable chart components | Available via travisvn/awesome-claude-skills | **HIGH** — directly applicable if Recharts is supplemented or replaced with D3 for custom charts |
| 5 | **Wondelai UX/Growth Skills** (25-skill pack) | wondelai | UX design + product strategy based on Don Norman + Cialdini principles; includes growth/CRO patterns | `wondelai/skills` on GitHub | **MEDIUM-HIGH** — product maturity framing beyond visual aesthetics |
| 6 | **Accessibility Agents** | Community-Access | 11-specialist agent suite enforcing WCAG 2.2 AA compliance; runs as review agents across the codebase | `github.com/Community-Access/accessibility-agents` | **MEDIUM-HIGH** — required for any "mature product" claim; catches AI-generated inaccessible code |
| 7 | **UI/UX Pro Max** | nextlevelbuilder | 240+ styles + 127 font pairings with automatic style matching; useful for dashboard theming sprint | `claude plugin add nextlevelbuilder/ui-ux-pro-max-skill` | **MEDIUM** — broad palette tool, good for design iteration speed |
| 8 | **Google Stitch MCP** | Google Labs | MCP toolkit including design-md, react-components, shadcn-ui integration, and stitch-loop for iterative design-to-code | MCP-based; google labs distribution | **MEDIUM** — powerful but requires MCP setup investment |

### Additional Note: Figma MCP (Honorable Mention)
If the project has a Figma source-of-truth for the design system, **Figma's official MCP server** (`claude mcp add --transport sse figma-dev-mode-mcp-server http://127.0.0.1:3845/sse`) reads Figma files directly including components, tokens, and layout. This is the highest-leverage design-to-code pipeline available as of 2026 — but requires an existing Figma file.

---

## Synthesis: Recommended Integration Bets for Round 3

**Bet 1: Add `frontend-design` + `Design Tokens Skill` as baseline skill stack** (source: Anthropic official + phrazzld)
These two together address the single biggest gap between "AI-generated" and "mature product" aesthetics: intentional aesthetic direction plus consistent token-based theming. Low friction to add, immediate visual uplift.

**Bet 2: Frame the "Prediction" quadrant using MiroFish conceptual architecture** (source: MiroFish)
Add a "Trend Forecast" panel that uses a GraphRAG-lite approach on the existing review + news corpus to project sentiment trajectory 4-8 weeks forward. Label it clearly as a simulation-based projection. This is the highest-differentiation feature for SharkNinja dashboard vs. competitors.

**Bet 3: Add "Synthetic Audience Reaction" framing to the insight detail view** (source: Aaru)
Design a "What would happen if..." module on product detail pages, framed as Aaru-style synthetic simulation. Even a v1 backed by prompt-chain heuristics reads as forward-looking and executive-grade.

**Bet 4: Run `Accessibility Agents` as a review pass before final submission** (source: Community-Access)
Any dashboard claiming "mature product" quality that fails basic WCAG 2.2 AA checks will be visibly amateur. This is a low-cost insurance pass.
