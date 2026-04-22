"""
kestrel_mcp — Kestrel bot 自举能力的 MCP 工具集 (portal of MeowOS v1.7)

提供 4 个 tool, 给 Kestrel bot 桥接主 session 同级的能力:

1. save_memory — 写入 user/feedback/project/reference 记忆到
   C:/Users/scvin/.claude/projects/d--Ai-Project-Vincent-AI-DevLand/memory/, 登 MEMORY.md 索引
2. stage_observation — 追加观察到 _staging.md (ACED A, DevLand 保留)
3. todo_write — per-channel todo list 读写 (replace_all / add / update_status / list)
4. spawn_agent — 启动 DevLand subagent (shell-runner / knowledge-agent)

4 个 tool 装进 MCP server, prefix = `mcp__kestrel__*`.

跨平台: Mac / Linux / Windows 一律 graceful, memory_dir 不存在时 build_memory_block 返回空串,
save_memory 拒绝写入. staging_path 的 parent dir 用 mkdir(parents=True, exist_ok=True) 创建.
"""
from __future__ import annotations

import asyncio
import contextvars
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

log = logging.getLogger("kestrel_mcp")

current_channel_ctx: contextvars.ContextVar = contextvars.ContextVar(
    "current_channel_ctx", default=None
)
current_session_key_ctx: contextvars.ContextVar = contextvars.ContextVar(
    "current_session_key_ctx", default=None
)

_subagent_locks: dict[str, asyncio.Lock] = {}


def _get_subagent_lock(key: str) -> asyncio.Lock:
    lock = _subagent_locks.get(key)
    if lock is None:
        lock = asyncio.Lock()
        _subagent_locks[key] = lock
    return lock


def load_memory_index(memory_dir: Path) -> str:
    """Read MEMORY.md verbatim. Returns empty string if dir or file missing.
    IMPORTANT: Does NOT create memory_dir — that's reserved for Claude Code session."""
    memory_dir = Path(memory_dir)
    if not memory_dir.exists():
        return ""
    idx = memory_dir / "MEMORY.md"
    if not idx.exists():
        return ""
    try:
        return idx.read_text(encoding="utf-8")
    except Exception as e:
        log.warning("load_memory_index failed: %s", e)
        return ""


def load_channel_todos(todos_dir: Path, session_key: str) -> list[dict]:
    f = todos_dir / session_key / "todos.json"
    if not f.exists():
        return []
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        items = data.get("todos", [])
        if isinstance(items, list):
            return items
    except Exception as e:
        log.warning("load_channel_todos(%s) failed: %s", session_key, e)
    return []


def _save_channel_todos(todos_dir: Path, session_key: str, todos: list[dict]) -> None:
    d = todos_dir / session_key
    d.mkdir(parents=True, exist_ok=True)
    f = d / "todos.json"
    f.write_text(json.dumps({"todos": todos}, indent=2, ensure_ascii=False), encoding="utf-8")


def create_kestrel_mcp_server(
    *,
    client: Any,
    kestrel_cwd: str,
    memory_dir: Path,
    staging_path: Path,
    todos_dir: Path,
    subagent_model: str,
    subagent_betas: list[str] | None = None,
    subagent_effort: str = "max",
    subagent_allowed_tools: list[str] | None = None,
    subagent_mcp_servers: dict[str, Any] | None = None,
    subagent_whitelist: set[str] | None = None,
):
    """Build the kestrel MCP server."""
    memory_dir = Path(memory_dir)
    staging_path = Path(staging_path)
    todos_dir = Path(todos_dir)

    if subagent_allowed_tools is None:
        subagent_allowed_tools = [
            "Read", "Glob", "Grep", "Edit", "Write", "Bash",
        ]
    if subagent_whitelist is None:
        subagent_whitelist = {"shell-runner", "knowledge-agent"}

    agents_dir = Path(kestrel_cwd) / "90_Agents"

    ALLOWED_MEMORY_TYPES = {"user", "feedback", "project", "reference"}
    FILENAME_RE = re.compile(r"^[a-z0-9_]+\.md$")

    @tool(
        "save_memory",
        (
            "Save a new persistent memory to Vincent_AI_DevLand auto-memory. Use when you learn "
            "something about Vincent, his feedback, a project, or an external reference "
            "that should persist across future sessions. Creates one .md file under "
            "the memory dir AND appends a one-line bullet to MEMORY.md index. "
            "Args: name (lowercase snake_case, no .md suffix, no path); type (one of: "
            "user | feedback | project | reference); description (short one-line hook "
            "for MEMORY.md, 5-15 words); content (full memory body, markdown). "
            "Will REJECT if file with same name already exists — use Read+Edit on the "
            "existing file instead of overwriting via this tool. "
            "Will also REJECT if memory_dir doesn't yet exist (Claude Code session "
            "must create it first by running at least once in this project)."
        ),
        {"name": str, "type": str, "description": str, "content": str},
    )
    async def save_memory_tool(args):
        raw_name = (args.get("name") or "").strip().lower()
        mem_type = (args.get("type") or "").strip().lower()
        desc = (args.get("description") or "").strip()
        content = args.get("content") or ""

        if mem_type not in ALLOWED_MEMORY_TYPES:
            return {
                "content": [{"type": "text",
                    "text": f"type must be one of {sorted(ALLOWED_MEMORY_TYPES)}; got '{mem_type}'"}],
                "isError": True,
            }

        if raw_name.endswith(".md"):
            fname = raw_name
        else:
            fname = raw_name + ".md"
        if not FILENAME_RE.match(fname):
            return {
                "content": [{"type": "text",
                    "text": f"name must match [a-z0-9_]+ (lowercase snake_case); got '{raw_name}'"}],
                "isError": True,
            }

        if not desc:
            return {"content": [{"type": "text", "text": "description is required (one-line hook)"}], "isError": True}

        if not memory_dir.exists():
            return {
                "content": [{"type": "text",
                    "text": (
                        f"memory_dir does not exist ({memory_dir}). "
                        "Claude Code must run at least once in this project to create it. "
                        "Skipping save_memory this time."
                    )}],
                "isError": True,
            }

        target = memory_dir / fname
        if target.exists():
            return {
                "content": [{"type": "text",
                    "text": f"memory '{fname}' already exists at {target}; use Read+Edit to update instead"}],
                "isError": True,
            }

        now = datetime.now()
        title = desc.split(".")[0][:80]
        frontmatter = (
            "---\n"
            f"name: {title}\n"
            f"description: {desc}\n"
            f"type: {mem_type}\n"
            f"created: {now.strftime('%Y-%m-%d')}\n"
            "---\n"
        )
        body = content.strip()
        try:
            target.write_text(frontmatter + body + "\n", encoding="utf-8")
        except Exception as e:
            log.exception("save_memory write failed")
            return {"content": [{"type": "text", "text": f"write failed: {e}"}], "isError": True}

        idx = memory_dir / "MEMORY.md"
        bullet = f"- [{title}]({fname}) — {desc}"
        try:
            existing = idx.read_text(encoding="utf-8") if idx.exists() else ""
            if existing and not existing.endswith("\n"):
                existing += "\n"
            idx.write_text(existing + bullet + "\n", encoding="utf-8")
        except Exception as e:
            log.exception("save_memory MEMORY.md append failed")
            return {
                "content": [{"type": "text",
                    "text": f"memory file written to {target}, but MEMORY.md index append failed: {e}. Manually add: {bullet}"}],
                "isError": True,
            }

        log.info("[kestrel.save_memory] wrote %s + indexed", fname)
        return {
            "content": [{"type": "text",
                "text": f"Saved memory: {fname} (type={mem_type}) + indexed in MEMORY.md"}],
        }

    @tool(
        "stage_observation",
        (
            "Append a short observation to DevLand _staging.md (ACED A). Use when you "
            "notice something about Vincent (new facts, preferences, habits, style, "
            "interaction patterns, or context about people around him) that's worth "
            "staging for later batch review. Auto-prepends ISO timestamp. "
            "Keep it short — one sentence or two, not a paragraph. "
            "Arg: observation (the one-line observation text)."
        ),
        {"observation": str},
    )
    async def stage_observation_tool(args):
        text = (args.get("observation") or "").strip()
        if not text:
            return {"content": [{"type": "text", "text": "observation is empty"}], "isError": True}
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        line = f"\n- [{ts}] {text}\n"
        try:
            staging_path.parent.mkdir(parents=True, exist_ok=True)
            with staging_path.open("a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            log.exception("stage_observation failed")
            return {"content": [{"type": "text", "text": f"append failed: {e}"}], "isError": True}
        log.info("[kestrel.stage_observation] appended to %s: %r", staging_path.name, text[:80])
        return {"content": [{"type": "text", "text": f"Staged: [{ts}] {text}"}]}

    ALLOWED_STATUSES = {"pending", "in_progress", "completed"}

    @tool(
        "todo_write",
        (
            "Manage a per-channel todo list. Scope: current Discord channel/thread. "
            "actions: 'replace_all' | 'add' | 'update_status' | 'list'. "
            "status: pending | in_progress | completed. "
            "Items are persisted per channel key to disk."
        ),
        {"action": str, "items": list},
    )
    async def todo_write_tool(args):
        action = (args.get("action") or "").strip().lower()
        items = args.get("items") or []
        session_key = current_session_key_ctx.get()
        if session_key is None:
            return {
                "content": [{"type": "text",
                    "text": "no session key in context — todo_write requires a Discord message context"}],
                "isError": True,
            }

        todos = load_channel_todos(todos_dir, session_key)

        if action == "list":
            pass
        elif action == "replace_all":
            if not isinstance(items, list):
                return {"content": [{"type": "text", "text": "items must be a list"}], "isError": True}
            new_todos = []
            for it in items:
                if not isinstance(it, dict):
                    return {"content": [{"type": "text", "text": f"each item must be dict; got {type(it).__name__}"}], "isError": True}
                tid = str(it.get("id") or "").strip()
                content = str(it.get("content") or "").strip()
                status = str(it.get("status") or "pending").strip().lower()
                if not tid:
                    return {"content": [{"type": "text", "text": "item.id required"}], "isError": True}
                if not content:
                    return {"content": [{"type": "text", "text": f"item {tid}: content required"}], "isError": True}
                if status not in ALLOWED_STATUSES:
                    return {"content": [{"type": "text", "text": f"item {tid}: status must be {sorted(ALLOWED_STATUSES)}"}], "isError": True}
                new_todos.append({"id": tid, "content": content, "status": status})
            todos = new_todos
            _save_channel_todos(todos_dir, session_key, todos)
        elif action == "add":
            if not isinstance(items, list):
                return {"content": [{"type": "text", "text": "items must be a list"}], "isError": True}
            existing_ids = {t["id"] for t in todos}
            for it in items:
                tid = str(it.get("id") or "").strip()
                content = str(it.get("content") or "").strip()
                status = str(it.get("status") or "pending").strip().lower()
                if not tid or not content:
                    return {"content": [{"type": "text", "text": "each item needs id + content"}], "isError": True}
                if status not in ALLOWED_STATUSES:
                    return {"content": [{"type": "text", "text": f"item {tid}: bad status"}], "isError": True}
                if tid in existing_ids:
                    return {"content": [{"type": "text", "text": f"id '{tid}' already exists; use update_status"}], "isError": True}
                todos.append({"id": tid, "content": content, "status": status})
                existing_ids.add(tid)
            _save_channel_todos(todos_dir, session_key, todos)
        elif action == "update_status":
            if not isinstance(items, list):
                return {"content": [{"type": "text", "text": "items must be a list"}], "isError": True}
            by_id = {t["id"]: t for t in todos}
            for it in items:
                tid = str(it.get("id") or "").strip()
                status = str(it.get("status") or "").strip().lower()
                if tid not in by_id:
                    return {"content": [{"type": "text", "text": f"id '{tid}' not found"}], "isError": True}
                if status not in ALLOWED_STATUSES:
                    return {"content": [{"type": "text", "text": f"bad status for '{tid}'"}], "isError": True}
                by_id[tid]["status"] = status
            _save_channel_todos(todos_dir, session_key, todos)
        else:
            return {
                "content": [{"type": "text",
                    "text": f"unknown action '{action}'. Must be: list | replace_all | add | update_status"}],
                "isError": True,
            }

        if not todos:
            summary = "(empty todo list)"
        else:
            summary_lines = []
            for t in todos:
                mark = {"pending": "[ ]", "in_progress": "[~]", "completed": "[x]"}.get(t["status"], "[?]")
                summary_lines.append(f"{mark} {t['id']}: {t['content']}")
            summary = "\n".join(summary_lines)
        log.info("[kestrel.todo_write] action=%s key=%s → %d items", action, session_key, len(todos))
        return {"content": [{"type": "text", "text": f"Todo list ({session_key}):\n{summary}"}]}

    async def _post_interim(channel, text: str) -> None:
        if channel is None:
            return
        try:
            await channel.send(text)
        except Exception as e:
            log.debug("interim message send failed: %s", e)

    async def _heartbeat_typing(channel, stop_event: asyncio.Event) -> None:
        if channel is None:
            return
        try:
            while not stop_event.is_set():
                try:
                    async with channel.typing():
                        try:
                            await asyncio.wait_for(stop_event.wait(), timeout=7.0)
                        except asyncio.TimeoutError:
                            pass
                except Exception:
                    return
        except asyncio.CancelledError:
            return

    _whitelist_desc = " | ".join(sorted(subagent_whitelist))

    @tool(
        "spawn_agent",
        (
            f"Spawn a DevLand subagent. Supported agent_types: {_whitelist_desc}.\n"
            "  - shell-runner: file ops / shell commands (clean output)\n"
            "  - knowledge-agent: structured KB writes\n"
            "Subagent is sandboxed: cannot spawn further agents, no web access. "
            "Blocking: 30-120s typical. While running, Kestrel posts an interim message "
            "to the current channel and keeps typing indicator alive.\n"
            "Args: agent_type (one of above), task (full natural-language task spec)."
        ),
        {"agent_type": str, "task": str},
    )
    async def spawn_agent_tool(args):
        agent_type = (args.get("agent_type") or "").strip()
        task = (args.get("task") or "").strip()
        if agent_type not in subagent_whitelist:
            return {
                "content": [{"type": "text",
                    "text": f"agent_type '{agent_type}' not allowed. Must be one of {sorted(subagent_whitelist)}"}],
                "isError": True,
            }
        if not task:
            return {"content": [{"type": "text", "text": "task is empty"}], "isError": True}

        prompt_file = agents_dir / f"{agent_type}.md"
        if not prompt_file.exists():
            user_level = Path.home() / ".claude" / "agents" / f"{agent_type}.md"
            if user_level.exists():
                prompt_file = user_level
        if not prompt_file.exists():
            return {
                "content": [{"type": "text",
                    "text": f"agent prompt missing: checked {agents_dir / (agent_type + '.md')} and ~/.claude/agents/{agent_type}.md"}],
                "isError": True,
            }
        try:
            system_prompt = prompt_file.read_text(encoding="utf-8")
        except Exception as e:
            return {"content": [{"type": "text", "text": f"failed to read {prompt_file}: {e}"}], "isError": True}

        channel = current_channel_ctx.get()
        session_key = current_session_key_ctx.get() or "global"

        lock = _get_subagent_lock(session_key)
        if lock.locked():
            return {
                "content": [{"type": "text",
                    "text": f"another subagent is already running in this channel; wait for it to finish first"}],
                "isError": True,
            }

        async with lock:
            task_preview = task[:100] + ("..." if len(task) > 100 else "")
            await _post_interim(channel, f"🦅 Kestrel 派 `{agent_type}`: {task_preview}")
            stop_ev = asyncio.Event()
            hb_task = asyncio.create_task(_heartbeat_typing(channel, stop_ev))

            sub_options = ClaudeAgentOptions(
                system_prompt=system_prompt,
                cwd=kestrel_cwd,
                allowed_tools=list(subagent_allowed_tools),
                mcp_servers=subagent_mcp_servers or {},
                permission_mode="acceptEdits",
                setting_sources=["project", "user"],
                model=subagent_model,
                betas=list(subagent_betas or []),
                effort=subagent_effort,  # type: ignore[arg-type]
            )

            parts: list[str] = []
            tool_use_count = 0
            try:
                async for msg_obj in query(prompt=task, options=sub_options):
                    if isinstance(msg_obj, AssistantMessage):
                        for block in msg_obj.content:
                            if isinstance(block, TextBlock):
                                parts.append(block.text)
                            elif isinstance(block, ToolUseBlock):
                                tool_use_count += 1
            except Exception as e:
                log.exception("[kestrel.spawn_agent] subagent '%s' failed", agent_type)
                stop_ev.set()
                try:
                    await hb_task
                except Exception:
                    pass
                return {
                    "content": [{"type": "text",
                        "text": f"subagent '{agent_type}' crashed: {type(e).__name__}: {e}"}],
                    "isError": True,
                }
            finally:
                stop_ev.set()
                try:
                    await hb_task
                except Exception:
                    pass

            result_text = "\n".join(p for p in parts if p).strip() or "(subagent returned no text)"
            log.info("[kestrel.spawn_agent] %s completed: %d tool uses, %d chars text",
                     agent_type, tool_use_count, len(result_text))
            return {
                "content": [{"type": "text",
                    "text": f"[{agent_type} result — {tool_use_count} tool calls]\n{result_text}"}],
            }

    return create_sdk_mcp_server(
        name="kestrel",
        version="1.0.0",
        tools=[save_memory_tool, stage_observation_tool, todo_write_tool, spawn_agent_tool],
    )


def build_memory_block(memory_dir: Path, budget_chars: int = 8000) -> str:
    """Render MEMORY.md inside a <memory_index> block. Returns empty if memory_dir or MEMORY.md absent."""
    idx_text = load_memory_index(memory_dir)
    if not idx_text.strip():
        return ""
    body = idx_text.strip()
    if len(body) > budget_chars:
        body = body[:budget_chars] + "\n…[truncated — use Read tool on memory_dir to see more]"
    mem_path = str(memory_dir).replace("\\", "/")
    return (
        "<memory_index>\n"
        f"Auto-memory index (persists across sessions). One-line hooks per memory file.\n"
        f"To open a specific memory, use Read tool on {mem_path}/<filename>.md\n"
        f"To add a new memory, use mcp__kestrel__save_memory.\n"
        "\n"
        f"{body}\n"
        "</memory_index>\n\n"
    )


def build_todos_block(todos_dir: Path, session_key: str) -> str:
    items = load_channel_todos(todos_dir, session_key)
    if not items:
        return ""
    lines = []
    for t in items:
        mark = {"pending": "[ ]", "in_progress": "[~]", "completed": "[x]"}.get(t.get("status", ""), "[?]")
        lines.append(f"{mark} {t.get('id')}: {t.get('content')}")
    body = "\n".join(lines)
    return (
        "<todos>\n"
        "Current channel todo list (shared with Vincent). Use mcp__kestrel__todo_write to update.\n"
        f"{body}\n"
        "</todos>\n\n"
    )
