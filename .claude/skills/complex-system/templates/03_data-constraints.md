# Data Constraint Scoping · Step 5

**Project**: <PROJECT_NAME>
**Gates**: Step 6 (no design spec work until this file is locked)
**Inherits**: `01_research-brief.md`, `02_review-notes.md`

---

## Data source inventory

Every data source the product might need. One row per source.

| Data | Source | Obtainable (Y / Partial / N) | Cost | Latency | Legal | Notes |
|------|--------|------------------------------|------|---------|-------|-------|
|      |        |                              |      |         |       |       |
|      |        |                              |      |         |       |       |
|      |        |                              |      |         |       |       |

**Column rubric:**

- **Obtainable**:
  - `Y` · we can get this cleanly
  - `Partial` · we can get some of it (sample-size, freshness, coverage, or reliability limited)
  - `N` · blocked (no source, legal wall, or cost-prohibitive)
- **Cost**: `$0` / `< $100` / `$100-1k` / `> $1k` / `ongoing subscription`
- **Latency**: `realtime` / `hourly` / `daily` / `weekly` / `snapshot`
- **Legal**: `OK` / `ToS concern` / `regulated (specify)` / `requires partnership`

---

## Design Constraint Summary (lock at end of Step 5)

### In scope (data we can reliably get)

- 

### Out of scope (data we cannot get; features depending on it are dropped)

- 

### Deferred / conditional (Partial sources; revisit after prototype)

- 

---

*Exit criterion*: Vincent confirms the three Summary sections. **Step 6 cannot start until this file is committed to the build repo.**