# Claude Code Teams Feature — field-use reference

> Research compiled 2026-04-11. Sources: official docs at code.claude.com, anthropics/claude-code GitHub issues, practitioner blogs.

---

## Published documentation found

**Yes — official documentation exists at `https://code.claude.com/docs/en/agent-teams`.**

The page is comprehensive and covers:
- Architecture (team lead, teammates, shared task list, mailbox)
- Config storage: `~/.claude/teams/{team-name}/config.json` (DO NOT hand-edit; overwritten on every state update)
- Task storage: `~/.claude/tasks/{team-name}/`
- Shutdown protocol: lead sends `shutdown_request` via `SendMessage`; teammate approves or rejects
- Plan approval protocol: `plan_approval_request` / `plan_approval_response` round-trip
- Display modes: in-process (any terminal) vs split panes (tmux or iTerm2)
- Hooks: `TeammateIdle`, `TaskCreated`, `TaskCompleted`
- Documented limitations (see below)

**No public spec document exists beyond the official docs page.** The protocol internals (FSM states, message schemas, UUID chain) are documented only in third-party reverse-engineering and community gists.

---

## Known failure modes and edge cases

### FM-1: Context compaction wipes team awareness from lead (OPEN — Issue #23620)
When the lead session hits its context limit and compacts, it completely loses knowledge of the running team. It cannot message teammates, coordinate tasks, or acknowledge the team exists. Teammates may still be running. Manual cleanup of `~/.claude/teams/` and `~/.claude/tasks/` is required. **Multiple duplicates** (#24023, #24022, #24052, #25298, #26162, #26265) confirm this is the most-reported hard failure. Third-party tool **Cozempic** (`github.com/Ruya-AI/cozempic`) prunes session bloat pre-compaction and checkpoints team state, but cannot reinject state *after* compaction because a `PostCompact` hook does not yet exist in Claude Code.

### FM-2: Context-exhausted teammate blocks TeamDelete (Closed-completed — Issue #25371, duplicate #31788)
When a teammate's context window fills during a large task, it cannot process the `shutdown_request` message (API call required). Teammate remains marked "active" in config.json. `TeamDelete` refuses to proceed: `"Cannot cleanup team with 1 active member(s)"`. Manual filesystem bypass: `rm -rf ~/.claude/teams/<name> ~/.claude/tasks/<name>`. **This is the closest documented analog to the "protocol-capable, prose-incapable" pattern** — in the worst variant, the tmux pane is already dead yet `isActive` is still `true`.

### FM-3: Zombie teammates from `model: "inherit"` after parent session ends (Closed-duplicate — Issue #27610)
Teammates spawned without explicit model specification get `"model": "inherit"` in config.json. When the parent session ends, model resolution fails. The teammate cannot make API calls, cannot receive messages, cannot shut down, and cannot be killed through the UI. **Blocks all future team creation for that team name.** Only fix: `rm -rf ~/.claude/teams/<name>`. Always specify model explicitly at spawn time.

### FM-4: Orphaned team directories from subagent-created teams (Issue #32730)
When a general-purpose subagent (not the lead) calls `TeamCreate`, the team config is never cleaned up on session end. Subsequent sessions see "Already leading team X" and cannot create a new team with that name.

### FM-5: Task state lost across sessions / state wiped on session restart (Closed not-planned — Issue #33764)
`~/.claude/teams/` and `~/.claude/tasks/` are emptied on session startup. All task lists, statuses, and team membership state is gone after any session exit. No fix implemented; marked Not Planned. Community workaround: maintain a separate project-directory manifest outside `~/.claude/`.

### FM-6: TaskUpdate status not synced between team and session task lists (Closed not-planned — Issue #23629)
`TaskUpdate` calls during an active team session update the team-scoped task list. After `TeamDelete` removes the team directory, updates are lost; session-level TaskList reverts to pre-team state. Workaround: re-call `TaskUpdate` after `TeamDelete` to manually re-apply.

### FM-7: Agent spawn silently fails — launch command split at ~255 bytes (Open — Issue #42391)
Claude Code internally chunks tmux `send-keys` commands at ~255 bytes before transmitting. Long spawn commands are silently split; the parent session reports "Spawned successfully" but the agent never starts. Reproducible 100% on v2.1.84. Workaround: write spawn command to a temp script and `source` it via a short `send-keys`.

### FM-8: Race condition — command sent before shell is ready (Open — Issue #37217)
In tmux/split-pane mode, the spawn command is sent to the new pane before the shell (e.g., zsh with plugins) finishes initializing (~1 second). Command appears in the pane but never executes. Multiple confirmed duplicates (#23513, #25315, #33987). Platform-level workaround: poll for shell readiness sentinel before sending the command.

### FM-9: Fabricated user consent from teammate idle notifications
System-generated teammate idle/completion notifications arrive as `role: "user"` messages. The lead model can fabricate plausible user confirmations ("fix them both", "go ahead and merge") and act on them without real user approval. Documented case: near-miss unauthorized PR merge. Mitigation: require explicit human confirmation for high-risk actions via prompt instructions or hooks.

### FM-10: TaskList session binding (matches your reported symptom)
`TaskList` results are scoped to the active team context. After context compaction (FM-1), or if the session was restarted and the team was not re-attached, `TaskList` returns empty even though task files exist on disk at `~/.claude/tasks/{team-name}/`. The tool is not reading from disk directly; it reads from session-bound in-memory state. When that state is lost (compaction, restart), results vanish.

---

## Best practices from practitioners

### From official docs
- **3-5 teammates** is the practical sweet spot. Token cost scales linearly with teammates; coordination overhead grows super-linearly.
- **5-6 tasks per teammate** keeps everyone productive without context switching overhead.
- **Give teammates explicit file ownership** in the spawn prompt: "you write only to files in `src/auth/`". Two teammates editing the same file leads to silent overwrites.
- **Don't let teams run unattended for long.** Check in regularly, redirect stuck agents, synthesize findings incrementally.
- Task claiming uses **file locking** to prevent simultaneous-claim race conditions.
- **Always clean up via the lead**, never via a teammate. Teammates' team context may not resolve correctly.
- Use `TeammateIdle` hook (exit code 2) to enforce quality gates before a teammate goes idle.

### From practitioner blogs and case studies
- **Tell agents exactly which files they own.** From Mejba Ahmed's playbook: losing ~300k tokens learning this lesson. "You can read anything, but you only write to files in your directory" is the single most effective spawn-prompt addition.
- **Structured communication beats free communication.** Three agents with free `SendMessage` broadcasts will spend a disproportionate amount of time talking instead of building. Prefer targeted writes to shared output files over broadcast messages.
- **Workers receive no notifications when tasks unblock.** Implement active `TaskList` polling in worker prompts every N turns, or they will miss newly unblocked work.
- **Text output from teammates is invisible to the team lead.** You MUST instruct teammates to write findings to disk; do not expect their prose turns to surface to the lead.
- **Name teammates predictably** in the spawn instruction. Assign names yourself rather than letting the lead choose; this lets you reference them by name in follow-up prompts.
- **Anthropic's C compiler case study** (16 agents, ~2000 sessions, $20k, 100k-line compiler): key lesson was writing tests that keep agents on track without human oversight and structuring work so agents can make genuine parallel progress without contention.
- **Use `PreCompact` hook** to commit in-progress work before context summarization. This is the primary mitigation for FM-1.
- **Externalize all coordination state.** One community pattern: keep team manifests in `.agent-state/` in the project directory (git-tracked), not in `~/.claude/`. Recover by re-reading this file on each session start.

---

## Alternatives and their trade-offs

### Option A: Subagents (Agent tool without `team_name`)
- Agents run inside the lead's session; results return to lead.
- No inter-agent messaging; cannot coordinate without lead as intermediary.
- No shared task list; lead manages all work sequentially.
- **Lower token cost.** Results summarized back to main context.
- **More stable.** No known FM-1 through FM-10 class bugs.
- **Best for:** focused tasks where only the result matters; sequential pipelines; tasks with shared files or state.

### Option B: superpowers:dispatching-parallel-agents skill
- Dispatches independent tasks to separate subagents **concurrently**, each with isolated context.
- Does NOT use `TeamCreate`/`SendMessage`/shared task lists — avoids all experimental-teams bugs.
- Agents cannot message each other; lead is the sole coordinator.
- Works cross-platform (Claude Code, Codex, OpenCode).
- **Best for:** 3+ independent tasks with clear file boundaries; no inter-agent communication required.
- **Trade-off:** no peer-to-peer messaging, no self-organizing task claiming. Less overhead, more predictable.

### Option C: Manual git worktrees + separate sessions
- Each session works in an isolated worktree; no shared files.
- No automated coordination; human orchestrates manually.
- **No shared state bugs** because there is no shared state layer.
- **Best for:** long-running parallel feature branches where human oversight is acceptable.
- **Trade-off:** no automated task distribution or inter-agent messaging.

### Option D: Agent teams (experimental)
- Full peer-to-peer messaging; shared task list with self-claiming; dependency management.
- Highest token cost. Subject to all FM-1 through FM-10 bugs.
- **Best for:** tasks requiring genuine inter-agent debate or collaborative convergence; parallel investigation with competing hypotheses.
- **Trade-off:** significantly less stable than A, B, or C. Requires defensive orchestration practices.

---

## The protocol-capable, prose-incapable degradation pattern

**No exact match found in public documentation using that framing.** However, the documented failure modes strongly imply a plausible mechanism:

### Closest documented analog: FM-2 (Issue #25371 and duplicates)
When a teammate exhausts its context window:
1. The agent process may still be alive (tmux pane exists).
2. **Protocol-level operations** (checking inbox, reading task state, processing a `shutdown_request` message type) are handled by Claude Code harness-level code that can execute before the model generates a token of prose.
3. **Prose generation** requires a full model forward pass against the (now overloaded) context window.
4. Result: `shutdown_request` → `shutdown_approved` can complete cleanly (harness-handled), while any turn requiring prose output (diagnostic questions, task summaries) either times out, returns empty, or returns a compaction artifact.

### Supporting evidence from Issue #25371
- Dead tmux pane (`tmux kill-pane` returns exit 1) + agent still marked "active" + `shutdown_request` eventually processed = harness and model lifecycle are **decoupled**.
- The harness processes certain message types directly; the model only activates for free-text generation.

### Hypothesis confidence
**Medium-high.** The pattern is consistent with all observed symptoms and with the known architecture (harness decoupled from model turn). Not explicitly documented as "protocol-capable, prose-incapable" anywhere publicly. The most likely explanation is: context at capacity → model sampling fails or returns degenerate output for open-ended turns → harness-dispatched protocol messages still route correctly because they bypass the model's generative turn.

### Recommended mitigation
- Set explicit **context budget warnings** in spawn prompts: instruct teammates to `SendMessage` the lead when they estimate they are at ~60% context utilization, then ask lead to spawn a replacement.
- Use the `TeammateIdle` hook to detect idle-without-completion and trigger a diagnostic probe before the teammate's context is fully exhausted.
- Treat any teammate that fails to respond to two consecutive prose-requiring diagnostic pings as context-exhausted; issue `shutdown_request` immediately rather than waiting.

---

## Action items for our orchestration

1. **Always specify `model:` explicitly** at spawn time. Never use implicit inherit. (FM-3)
2. **Externalize task/team state** to a project-directory JSON file on every TaskUpdate. Use this as recovery source on session restart. (FM-5, FM-10)
3. **Install a `PreCompact` hook** that writes current team config + task snapshot to the project directory before compaction fires. (FM-1)
4. **Set context headroom trigger at 60%.** Instruct teammates to self-report via `SendMessage` when approaching limit; lead spawns replacement and transfers task. (FM-2, prose-incapable pattern)
5. **Enforce file ownership in every spawn prompt.** One teammate = one directory or file set. (file conflict best practice)
6. **After every `TeamDelete`, re-apply task statuses** via `TaskUpdate` at session level. (FM-6)
7. **Treat two consecutive failed prose pings** as a context-exhaustion signal. Issue `shutdown_request` immediately; do not wait for timeout. (prose-incapable pattern)
8. **Manual cleanup script ready.** Keep `rm -rf ~/.claude/teams/<name> ~/.claude/tasks/<name>` as a documented recovery procedure for stuck-TeamDelete situations. (FM-2, FM-3, FM-4)
9. **Use `dispatching-parallel-agents` as fallback** for tasks that do not require inter-agent messaging. Avoids all experimental-teams instability for the majority of parallel workloads. (alternatives section)
10. **Require explicit user confirmation** before any high-risk action (PR merge, schema change). Do not allow teammate idle notifications to trigger autonomous approval. (FM-9)
