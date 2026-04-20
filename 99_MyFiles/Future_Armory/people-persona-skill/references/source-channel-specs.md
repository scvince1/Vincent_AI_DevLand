# Source Channel Specifications

Skill declares field requirements. Deployments write adapters that conform.

## Channel 1: Email

Each message object provides:

| Field | Type | Required | Notes |
|---|---|---|---|
| `from` | str | yes | Email address |
| `to` | list[str] | yes | Recipient addresses |
| `cc` | list[str] | no | CC addresses |
| `timestamp` | str (ISO 8601) | yes | |
| `subject` | str | yes | |
| `body` | str | yes | Plain text or HTML cleaned to text |
| `thread_id` | str | yes | For grouping conversation threads |

**Time window**:
- Cold start default: 60 days
- Extended: 90 days (prompt user after first run whether to extend)
- Window applies from target's involvement (either as sender or recipient)

**Scope**:
- Target's sent messages
- Target's received messages (inbox + cc)
- Reply-all threads where target is a participant

---

## Channel 2: IM (Teams / Slack / etc.)

Each message object provides:

| Field | Type | Required | Notes |
|---|---|---|---|
| `sender` | str | yes | User identifier |
| `timestamp` | str (ISO 8601) | yes | |
| `channel_or_DM` | str | yes | Channel name / "DM:{other_user}" |
| `body` | str | yes | |
| `thread_id` | str | no | For threaded replies |
| `mentions` | list[str] | no | @-mentioned users |
| `message_type` | str | yes | `"message"` / `"reply"` / `"system"` / `"call_start"` / etc. |
| `attachments_meta` | list | no | Filename + shared_at; no file contents |
| `reactions` | list | no | Optional |

**Filtering (performed by adapter before skill receives)**:
- Drop `message_type: system / call_start` (system noise)
- Drop bot messages
- Drop pure-emoji-only or @-only messages

**Time window**: user-defined; skill does not impose a default. Adapter may default to "full relevant" (all channels where target appears).

---

## Channel 3: Org Data

Single record object per target:

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | str | yes | Authoritative display name |
| `title` | str | yes | Current job title |
| `level` | str | yes | Internal level designation (e.g., "VP", "L6") |
| `department` | str | yes | Department or division |
| `manager_chain` | list[str] | no | Manager name chain up N levels |
| `direct_reports` | list[str] | no | Names of direct reports |
| `team` | str | no | Team within department |
| `start_date` | str (ISO 8601 date) | no | Current role start date |
| `location` | str | no | Office location or "remote" |
| `snapshot_date` | str (ISO 8601 date) | yes | When this record was pulled |

**One-shot query**: adapter queries by email or display_name; returns single record.

**Snapshot semantics**: org data is time-sensitive. New snapshot with changed fields does NOT overwrite old; new snapshot appends per invariant 7.

---

## Channel 4: Public Web

Two-phase structure.

### Phase A: Discovery (always runs when `public_domain_mode != "hibernating"`)

Input: `{name} + {company}` query via WebSearch.

Each result:

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | str | yes | Search result title |
| `url` | str | yes | Result URL |
| `snippet` | str | yes | Search result snippet |
| `source_type` | str | no | If identifiable: "linkedin" / "news" / "podcast" / "exec_page" / "wikipedia" / "social" / "other" |

Maximum 10 results. Token budget ≤10k per call.

### Phase B: Full Fetch (only when `public_domain_mode == "full"`)

For each URL user approved:

| Field | Type | Required | Notes |
|---|---|---|---|
| `url` | str | yes | |
| `title` | str | yes | |
| `full_text` | str | yes | Extracted text content |
| `publish_date` | str (ISO 8601) | no | When available |
| `source_type` | str | yes | Categorization for tier weighting |

**Source type tiering** (for confidence calibration in `#15 诚实边界`):
- Tier 1: books, academic papers, primary transcripts
- Tier 2: long-form interviews, podcasts with transcripts
- Tier 3: news articles, exec biography pages
- Tier 4: social media posts, short statements
- Tier 5 (blacklisted by default): Zhihu, WeChat public articles, Baidu Baike, low-quality content farms

Adapter should prefer tier 1-3 sources. Tier 4 acceptable with explicit flag. Tier 5 should be excluded.

---

## Channel 5: Meeting Transcripts

Each transcript object:

| Field | Type | Required | Notes |
|---|---|---|---|
| `meeting_id` | str | yes | Unique identifier |
| `title` | str | yes | Meeting title |
| `start_time` | str (ISO 8601) | yes | |
| `duration` | int | no | Seconds |
| `attendees` | list[object] | yes | Each: `{name, email?, role?}` |
| `body` | str | yes | Speaker-attributed lines: `[Name]: "..."` |
| `source_platform` | str | no | "Zoom" / "Teams" / etc. |

**Preprocessing expectation**:
- Speaker attribution done UPSTREAM by external pipeline (voice ID, or manual annotation)
- Skill consumes structured transcripts only; does not handle raw audio
- Each speaker line in `body` is already attributed

**Usage**:
- Target's quoted utterances → fact layer for #5 (only if email insufficient) and #14
- Observed behaviors → staging for #3, #4, #6, #8
- Target's interactions with other attendees → staging for #6

---

## Adapter Implementation Guidelines

Deployment-specific. Skill does not prescribe.

Typical adapters:
- Microsoft 365 / Outlook Connect: Graph API pulls for email + Teams
- Google Workspace: Gmail API + Calendar (if calendar included) + Meet transcripts
- Slack: Conversations API with bot token
- LDAP / Active Directory: for Org data
- Company HR system: for richer org data (start_date, reporting lines)
- LinkedIn scraping (where terms permit) for public web
- WebSearch API for Phase A discovery

Each adapter must:
- Authenticate with deployment-specific credentials (never stored in skill)
- Return data conforming to field schemas above
- Handle rate limits and retries internally
- Not include data from outside the target's participation