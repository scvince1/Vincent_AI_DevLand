# Backend Version Plan

**Project**: <PROJECT_NAME>

Running ladder of backend versions. One row per version. Append as versions are bumped. **Each version must have a committed spec before its implementation tickets are opened.**

| Version | Date | Scope / changes | Linked backend-spec file | Status |
|---------|------|-----------------|--------------------------|--------|
| V0.0    |      | Synthetic dataset generator | `03_backend/backend-spec_v0.md` | draft |
| V0.1    |      | Method increments |                          |        |
| V0.x    |      |                 |                          |        |
| V1.0    |      | First real-data integration | `03_backend/backend-spec_v1.md` |   |
| V1.1    |      | Perf / batching |                          |        |
| V2.0    |      | Production hardening | `03_backend/backend-spec_v2.md` |    |

**Version rules:**

- V0 · synthetic data only (frontend dev relies on this)
- V0.x · add methods or refine shapes; still synthetic
- V1.0 · first real-data swap
- V1.x · perf / reliability / batching improvements
- V2.0 · production hardening

**Status values**: `draft` · `in progress` · `locked` · `archived`