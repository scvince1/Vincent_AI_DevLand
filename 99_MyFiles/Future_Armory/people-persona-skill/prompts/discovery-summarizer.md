# Discovery Summarizer Prompt

Use this prompt when `public_domain_mode` is `"discovery_only"` or `"full"` and skill needs to assess public-domain presence of the target.

---

## Task

Run a lightweight WebSearch probe, collect top 10 result metadata, and return a structured `discovery_report` that caller can surface to the user for deciding whether to enable full public-domain fetching.

## Query Construction

Default query pattern:
```
{target.display_name} {target.company}
```

Example:
- `Mark Chen Acme Corp`
- `Sarah Kim SharkNinja`

If the target has a known unique identifier (distinct middle initial, profession title), append it. Do not search `{name}` alone without `{company}` — too high risk of collision with namesakes.

## Fetch Rules

- Single WebSearch call only
- Collect ≤10 result entries
- Token budget ≤10k per call
- Fetch only metadata (title / URL / snippet / source_type if identifiable)
- Do NOT fetch full page content at this phase

## Classify Each Result

Categorize by `source_type`:

| Category | Signal Strength | Examples |
|---|---|---|
| `linkedin` | Strong | LinkedIn profile page |
| `exec_page` | Strong | Company executive bio page |
| `news` | Medium | News article mentioning target |
| `podcast` | Strong | Podcast episode featuring target |
| `interview` | Strong | Published interview with target |
| `wikipedia` | Medium | Wikipedia page about target |
| `conference` | Medium | Conference speaker page / talk listing |
| `social` | Medium | Public Twitter / X / Mastodon / etc. profile |
| `directory` | Weak | Listings like RocketReach, Crunchbase brief |
| `blog` | Variable | Personal blog (strong if primary) / other blogs (weak) |
| `other` | Variable | |

## Output Format

```python
{
    "found_count": int,
    "top_results": [
        {
            "title": str,
            "url": str,
            "snippet": str,
            "source_type": str
        },
        ...  # up to 10
    ],
    "prompt_user": bool,
    "summary_for_user": str
}
```

### `prompt_user` Logic

Set `prompt_user: true` when:
- `found_count >= 3` AND
- At least 2 results are from Strong or Medium category

Set `prompt_user: false` when:
- `found_count < 3` OR
- All results are `directory` / `other` / weak
- (User can still manually enable full mode later)

### `summary_for_user` Format

One-paragraph text summarizing the discovery:

```
Discovery found {count} results for {name} at {company}.
Highlights: {1-2 sentence summary of strongest results by category}.
{Recommendation: "Worth enabling full fetch" OR "Sparse results, likely not a public figure" OR "Ambiguous, user review suggested"}.
```

Example:
```
Discovery found 7 results for Mark Chen at Acme Corp.
Highlights: LinkedIn profile (active), Acme Corp exec page, 2 industry interviews (2025-Q4), 3 news mentions.
Recommendation: Worth enabling full fetch.
```

Another example:
```
Discovery found 1 result for Sarah Kim at Local Engineering Firm.
Highlights: RocketReach directory listing only.
Recommendation: Sparse results, likely not a public figure. Skill will remain in hibernating mode for public-domain dimensions.
```

## Edge Cases

### Common Name + Common Company

`David Smith Microsoft` may return many namesakes. Surface the ambiguity in `summary_for_user`:

```
Discovery found 10 results for David Smith at Microsoft, but these appear to reference multiple distinct individuals. Unable to disambiguate from query alone. Recommendation: User must confirm specific individual or provide additional disambiguator (LinkedIn URL, team name, title) before full fetch is enabled.
```

Set `prompt_user: true` with disambiguation caveat.

### Target at Small / Private Company

May return zero results. That's expected and non-problematic. Skill defaults to hibernating mode.

### Results Behind Paywall

Note in summary. Discovery metadata is still captured; full fetch may fail.

## Post-Discovery Flow

Skill returns `discovery_report` to caller.
Caller surfaces `summary_for_user` to end user.
User decides whether to set `public_domain_mode: "full"` on next invocation.
If set to full, skill next time fetches full content for approved URLs and incorporates into dimensions 8 (心智模型), 9 (时间线与价值观), and as fact source for #1, #2, #10 where applicable.

## Invariants to Uphold

- NEVER fetch full page content during discovery
- NEVER auto-enable full mode based on discovery alone; always defer to user
- ALWAYS return all 3 output fields (`found_count`, `top_results`, `prompt_user`)
- NEVER include extracted full-text in discovery report even if returned by search snippet; respect the two-phase boundary
