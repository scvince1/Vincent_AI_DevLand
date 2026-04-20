# Frontend Spec · Version <V>

**Project**: <PROJECT_NAME>
**Version**: V0 | V0.x | V1 | V1.x | V2
**Previous version file**: <link to prior frontend-spec if any>
**Inherits**: `04_design-spec.md`

---

## Component inventory

| Component | Used on pages | Props / data shape | Notes |
|-----------|----------------|---------------------|-------|
|           |                |                     |       |
|           |                |                     |       |

## Page inventory

| Page | Route | Components used | Data sources (mock or real) |
|------|-------|-----------------|------------------------------|
|      |       |                 |                              |
|      |       |                 |                              |

## Navigation graph

How pages connect. Use an indented tree, a flat list, or a mermaid graph.

```
Home
  ├── /dashboard
  ├── /settings
  │     └── /settings/account
  └── /about
```

## Data contracts (per page or component)

For each consumer, list what data shape it needs. Reference `mock-data.json` (Step 7.B2 output) or name the backend method it will eventually call (from `06_backend-spec.md`).

| Consumer | Needs (fields / shape) | Source (mock key or method name) |
|----------|-------------------------|-----------------------------------|
|          |                         |                                   |

## HTML preview

- **Live file**: `02_frontend/html-preview.html` (single-file, mock-data driven, hash routing)
- **Archived prior version(s)**: `05_previews/v<N>.html`
- Based on `~/.claude/skills/complex-system/templates/10_html-preview-shell.html`.

## Changes since previous version

- 

---

*Exit criterion*: HTML preview runs and reflects this spec's flows. Vincent confirms before bumping to the next version.