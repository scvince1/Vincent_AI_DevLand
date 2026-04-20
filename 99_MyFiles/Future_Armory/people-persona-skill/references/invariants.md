# Invariants and I/O Contract

## 8 Invariants

Skill must guarantee these without exception.

### 1. PART 1 神圣

`existing_record`'s PART 1 entries appear unchanged in output `dossier_md`. Skill never modifies, reorders, or deletes existing PART 1 content.

### 2. 默认 inference

New characterizations always enter PART 2, never PART 1. Only two paths promote content to PART 1:
- External fact evidence (direct to PART 1 on first observation)
- User confirmation (manual move from PART 2 to PART 1 via host interface)

### 3. Staging 隔离

Inference observations below N=3 threshold remain in `staging_state` only. They do NOT appear in `dossier_md` PART 2. Only staged observations that reach N≥3 within T=90-day window are promoted to PART 2 active.

### 4. Email-first 语言

Dimension 5 (表达 DNA) verbatim samples are sourced from email only. IM and transcript quotes are used only as fallback when email evidence is insufficient, and fallback must be explicitly noted in #15 诚实边界.

### 5. 不碰 confirmed

Any PART 1 entry with source `confirmed ... by user` is preserved untouched, regardless of new observations. This takes precedence over all other update rules.

### 6. 诚实边界强制

Dimensions without sufficient evidence are either:
- Omitted from `dossier_md` entirely, OR
- Declared in #15 as a gap with source coverage note

Never filled with speculation to mask absence.

### 7. Fact 层 append-only

New facts append to the top of a dimension (newest first). Old fact entries are preserved with their source date. Skill never replaces or deletes fact entries. The reader infers "current state" by reading the newest-dated entry.

### 8. Supersede 日志

When new fact evidence directly overturns an existing PART 2 inference, the inference is removed from PART 2 active and a single line is logged in #15 诚实边界:

```
- previous inference "{X}" disconfirmed by fact "{Y}" on {YYYY-MM-DD}
```

---

## I/O Contract

### Signature

```python
def extract_persona(
    target: {email, display_name, slug?},
    sources: {email?, im?, org?, transcripts?, web_discovery?, web_full?},
    existing_record: str? = None,
    params: {time_windows?, staging_threshold?, public_domain_mode?} = {}
) -> {
    dossier_md: str,
    staging_state: dict,
    discovery_report: dict? = None
}
```

### Input

| Field | Type | Required | Notes |
|---|---|---|---|
| `target.email` | str | yes | Primary identifier |
| `target.display_name` | str | yes | Human-readable name |
| `target.slug` | str | no | Auto-generated from name if omitted |
| `sources.email` | list | conditional | At least 1 source type required |
| `sources.im` | list | conditional | |
| `sources.org` | object | conditional | |
| `sources.transcripts` | list | conditional | |
| `sources.web_discovery` | list | conditional | |
| `sources.web_full` | list | conditional | Only when user opted in via `public_domain_mode: full` |
| `existing_record` | str | no | Raw content of existing `{slug}.md` if it exists |
| `params.time_windows` | object | no | e.g., `{email: 60}` or `{email: 90}` |
| `params.staging_threshold` | object | no | Default `{N: 3, T: 90}` |
| `params.public_domain_mode` | str | no | `"hibernating"` / `"discovery_only"` / `"full"`. Default `"discovery_only"` |

### Output

| Field | Type | Present When | Notes |
|---|---|---|---|
| `dossier_md` | str | always | Full updated content of `{slug}.md` |
| `staging_state` | dict | always | Structure: `{observations: [...], superseded: [...]}` |
| `discovery_report` | dict | only when discovery ran | Structure: `{found_count, top_results, prompt_user}` |

### Side-Effect Contract

- Skill does NOT write to the filesystem. Caller writes `dossier_md` to `{slug}.md` at host-determined path.
- Skill does NOT modify the input `existing_record`; any PART 1 content from it appears unchanged in output `dossier_md`.
- Skill may include staging items that reached threshold in output `dossier_md` PART 2.
- Skill does not emit side-channel logs; all information for caller is in the three output fields.

## Staging State Format

```python
{
    "observations": [
        {
            "dim": 3,              # dimension number
            "content": "...",      # the observed pattern
            "sources": [            # each observation instance
                {"channel": "email", "id": "msg-abc", "date": "2026-03-12"},
                {"channel": "teams", "id": "msg-xyz", "date": "2026-03-18"},
            ],
            "count": 2              # current observation count
        },
        ...
    ],
    "superseded": [
        {
            "dim": 1,
            "old_inference": "level: VP",
            "disconfirmed_by": "fact from Org directory 2026-04-16 reporting level: SVP",
            "date": "2026-04-16"
        },
        ...
    ]
}
```

Caller persists this verbatim between invocations. Skill reads it on each call to know what's pending promotion.

## Discovery Report Format

```python
{
    "found_count": int,
    "top_results": [
        {"title": str, "url": str, "snippet": str, "source_type": str?},
        ...  # up to 10
    ],
    "prompt_user": bool  # true when ≥3 results look substantive
}
```

Caller is responsible for surfacing this to user and deciding whether to set `public_domain_mode: full` on next invocation.