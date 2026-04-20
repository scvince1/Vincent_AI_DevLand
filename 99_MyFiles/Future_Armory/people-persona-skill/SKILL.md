---
name: people-persona-extraction
description: Use when host agent needs to extract a structured persona dossier (fact layer + flagged inference layer) for a specific person from scattered source materials (email, IM, org directory, meeting transcripts, public web). Never auto-invoke; requires explicit call from archival or synthesis agent with target identifier and source data. Returns updated dossier content as a string, not direct file writes.
---

# People Persona Extraction Skill

**STATUS: ARMORY. Shelved for future deployment. Not registered in any current system.**

To deploy: copy this directory into `.claude/skills/` of the target host. Verify source adapters exist for needed channels. Do not deploy without a host people-agent responsible for KB maintenance.

---

## Purpose

Extract structured persona dossiers for individuals from scattered source materials. Produces single-file output per person with explicit fact / inference separation. Transferable across deployments; invoked by host agents maintaining a people knowledge base.

## Core Principle

精准性优先 > token 成本. Facts (verbatim quotes, timestamped events, authoritative records) are separated from inferences (personality patterns, style descriptions, decision heuristics). Downstream consumers read Fact only by default. Inferences are flagged until user confirms.

## Scope

**This skill does**:
- Extract fact-layer content from adapter outputs
- Generate inference-layer characterizations (flagged)
- Manage staging threshold for inference promotion (N=3, T=90d)
- Run discovery search when public-domain assessment requested
- Honor existing PART 1 content (sacred rule)
- Return structured dossier content

**This skill does NOT**:
- Own KB storage or write files directly
- Provide source adapters (each deployment implements these)
- Own user-confirmation UI (host responsibility)
- Handle retrieval, cross-reference, staleness
- Run autonomous iteration or scoring
- Role-play or impersonate the subject

## Invocation Protocol

Host agent invokes with:
- `target`: `{email, display_name, slug?}`
- `sources`: one or more channels with per-channel data (see `references/source-channel-specs.md`)
- `existing_record`: raw content of existing `{slug}.md` if any
- `params`: optional overrides for `time_windows`, `staging_threshold`, `public_domain_mode`

Returns:
- `dossier_md`: full updated file content
- `staging_state`: persisted between calls by caller
- `discovery_report`: present when discovery ran

Full I/O contract: see `references/invariants.md`.

## Reference Layout

- `references/dimension-spec.md` — 15 dimensions with Tier + Source Preference
- `references/file-format-spec.md` — PART 1 / PART 2 output layout and conventions
- `references/invariants.md` — 8 invariants + full I/O contract
- `references/source-channel-specs.md` — per-channel field schemas
- `prompts/fact-extractor.md` — fact-layer extraction prompt
- `prompts/inference-extractor.md` — inference generation prompt
- `prompts/discovery-summarizer.md` — WebSearch metadata parser
- `prompts/conflict-resolver.md` — public / private conflict handler
- `examples/sample-dossier.md` — reference output format

## Design Lineage

Derived from:
- `titanwings/colleague-skill`: Persona 5-layer, Work 5-section, conflict detection, versioning concepts
- `alchaincyf/nuwa-skill`: cognitive framework extraction, honest-boundary discipline, source quality gate

Key divergences from sources:
- No role-play activation (skill is extraction-only, not an invokable persona)
- No KB ownership (skill is stateless)
- No hardcoded model (harness decides)
- No private-data OAuth channels in core (adapters are deployment-specific)
- Fact / Inference stratification as architectural first-class, not metadata tag

## Do Not

- Deploy without verifying host adapter availability for required source channels
- Modify invariants without tracing impact through all 15 dimensions
- Auto-invoke from voice or text triggers; this is host-agent-called only
- Mix fact and inference content in the same section
- Overwrite PART 1 content, including user-confirmed items