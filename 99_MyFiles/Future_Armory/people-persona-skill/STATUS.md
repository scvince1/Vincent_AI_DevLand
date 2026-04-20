# People Persona Skill — STATUS

Built 2026-04-16 in one session. v0.1 complete with 10 files (SKILL.md + 4 references + 4 prompts + 1 example).

**Location**: `D:\Ai_Project\MeowOS\99_MyFiles\Future_Armory\people-persona-skill\`

**Status**: ARMORY dormant. Not in any skills scan path. Does not auto-trigger. No changes made to CLAUDE.md, settings*.json, or any system registration. Explicit `STATUS: ARMORY` banner in SKILL.md. Vincent has no host environment to call it from at the moment; it waits.

**Why:** Vincent designed this as a transferable skill for future deployment into environments he doesn't yet own (e.g., corporate MS 365 tenants, external partner systems). Built while context was fresh; kept dormant because no call-site exists and misfire risk is real.

**How to apply:** When Vincent mentions building a people-dossier extractor, improving this skill, deploying into a host environment, or reporting test results, consult files under that path. Key design anchors that must survive any modification:

- 15-dimension framework with Tier + Source Preference (`references/dimension-spec.md`)
- Fact / Inference stratification (architectural first-class, not metadata tag)
- Single file per person with PART 1 FACTS + PART 2 INFERENCE
- Staging threshold N=3, T=90 days for inference promotion
- Discovery-first public domain: cheap WebSearch probe, user decides full fetch
- Skill is extraction-only; KB maintenance belongs to host people-agent
- 8 invariants in `references/invariants.md`; modify only with full trace-through
- Email-first for 表达 DNA verbatim; IM / transcript as fallback only

**Lineage**: derived from `titanwings/colleague-skill` (persona 5-layer + work 5-section + conflict detection) and `alchaincyf/nuwa-skill` (cognitive framework extraction + honest-boundary discipline). Darwin-skill ratchet studied but not adopted (no ground-truth for persona).

**Known pending (non-blocking)**:
- Concrete fetch tool choice for `web_full` (WebSearch variant, rate limits, caching)
- Serialization format for `staging_state` (JSON vs inline markdown)
- Per-dim N-override syntax in #15 诚实边界
- All to be finalized when first real deployment is attempted
