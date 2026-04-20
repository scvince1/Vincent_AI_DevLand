# Backend Spec · Version <V>

**Project**: <PROJECT_NAME>
**Version**: V0 | V0.x | V1 | V1.x | V2
**Previous version file**: <link to prior backend-spec if any>
**Inherits**: `04_design-spec.md`, `03_data-constraints.md`

> **Hard rule**: this spec must be committed to the build repo before any implementation ticket for this version is opened. No spec, no ticket.

---

## Data shapes

Types, schemas, table definitions. Use the style that fits the stack.

```
# Example (adjust to your stack)
class User:
    id: str
    email: str
    created_at: datetime
```

## Methods / endpoints

| Method | Inputs | Outputs | Latency budget | Data source (row in `03_data-constraints.md`) |
|--------|--------|---------|----------------|-----------------------------------------------|
|        |        |         |                |                                               |
|        |        |         |                |                                               |

## Data sources consumed (cross-ref to Step 5)

List which rows from `03_data-constraints.md` this version depends on.

- 

## Batching / ingestion strategy

- **V0**: how is the synthetic dataset generated (script, manual seed, fixture factory)?
- **V1+**: how is real data pulled (batch frequency, transformation, storage, retry policy)?

Details:

- 

## Changes since previous version

- 

---

*Exit criterion*: Vincent signs off. Only after this can implementation tickets for this BE version be emitted.