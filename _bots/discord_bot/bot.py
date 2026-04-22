#!/usr/bin/env python3
"""
Kestrel (隼) Discord Bot — Mac 侧远程代理 (Vincent_AI_DevLand 接入点)

Kestrel is a Mac-side proxy bot. Her primary role is to let Vincent
dispatch tasks to the PC-side persona bots (凌喵/艾莉/北辰) from his
Mac without starting a new Claude Code session manually.

Persona is intentionally thin — she acknowledges quickly, then routes
complex work to the appropriate PC bot. She is not a deep-persona bot.

Cross-platform: designed to run on macOS primarily, but also supports
Linux and Windows. Platform-specific subprocess patching is guarded.

Features:
- Per-user session (Discord user ID → session-id 映射)
- USER_MAP (Discord ID → KESTREL_USER 模式) 身份路由
- DM 全响应; 公屏仅 @mention 响应
- on_message_edit 支持 (@ 后加也能触发)
- Surface hint 注入 (Kestrel 知道当前是 DM / 公屏)
- 9 个 Discord MCP 工具 (dm_user / send_to_channel / add_reaction /
  get_channel_history / edit_message / delete_message / create_thread /
  pin_message / get_user_presence)
- No diary, no changelog, no Google MCP (proxy 角色不需要)

运行:
    macOS:   ./start_kestrel.command  或  python3 bot.py
    Linux:   ./start_kestrel.sh       或  python3 bot.py
    Windows: start_kestrel.bat        或  python bot.py
"""
import asyncio
import json
import logging
import os
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# --- Windows subprocess window suppression (prevents per-spawn Terminal popups) ---
# claude_agent_sdk spawns claude CLI subprocesses; on Windows without this patch,
# each spawn creates a new console window. On macOS/Linux this is a no-op and
# the patching is skipped entirely.
if sys.platform == "win32":
    _CREATE_NO_WINDOW = 0x08000000

    _orig_popen_init = subprocess.Popen.__init__
    def _patched_popen_init(self, *args, **kwargs):
        if "creationflags" not in kwargs:
            kwargs["creationflags"] = 0
        kwargs["creationflags"] |= _CREATE_NO_WINDOW
        _orig_popen_init(self, *args, **kwargs)
    subprocess.Popen.__init__ = _patched_popen_init

    _orig_create_subprocess_exec = asyncio.create_subprocess_exec
    async def _patched_create_subprocess_exec(*args, **kwargs):
        if "creationflags" not in kwargs:
            kwargs["creationflags"] = 0
        kwargs["creationflags"] |= _CREATE_NO_WINDOW
        return await _orig_create_subprocess_exec(*args, **kwargs)
    asyncio.create_subprocess_exec = _patched_create_subprocess_exec

    _orig_create_subprocess_shell = asyncio.create_subprocess_shell
    async def _patched_create_subprocess_shell(*args, **kwargs):
        if "creationflags" not in kwargs:
            kwargs["creationflags"] = 0
        kwargs["creationflags"] |= _CREATE_NO_WINDOW
        return await _orig_create_subprocess_shell(*args, **kwargs)
    asyncio.create_subprocess_shell = _patched_create_subprocess_shell
# On macOS/Linux: no subprocess patching needed — processes run in the
# background without spawning new terminal windows by default.

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
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

# Worldbook import is optional — Vincent_AI_DevLand may not have a knowledge
# base wired in yet. If worldbook.py isn't shipped, we run without it.
try:
    from worldbook import Worldbook
    _WORLDBOOK_AVAILABLE = True
except Exception:
    Worldbook = None  # type: ignore
    _WORLDBOOK_AVAILABLE = False

# ---------------- Config ----------------
HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]


def _parse_user_map(raw: str) -> dict:
    out: dict = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if ":" in pair:
            uid, mode = pair.split(":", 1)
            out[int(uid.strip())] = mode.strip()
        else:
            out[int(pair)] = "vincent"
    return out


_user_map_raw = os.environ.get("USER_MAP") or os.environ.get("ALLOWED_USER_IDS", "")
USER_MAP = _parse_user_map(_user_map_raw)
ALLOWED_USER_IDS = set(USER_MAP.keys())

# KESTREL_CWD: where the Claude Agent SDK runs from on the host machine.
# Default is Vincent's Mac home dir; override in .env on whichever host.
KESTREL_CWD = os.environ.get("KESTREL_CWD", "/Users/scvin")

# Worldbook: optional keyword-triggered context injection. Only loads if
# worldbook.py is importable AND a knowledge root exists at
# <KESTREL_CWD>/80_Knowledge. Currently Vincent_AI_DevLand has
# 80_Knowledge but no worldbook-keyed files; this scaffolds for later.
_knowledge_root = Path(KESTREL_CWD) / "80_Knowledge"
if _WORLDBOOK_AVAILABLE and _knowledge_root.exists():
    try:
        WORLDBOOK = Worldbook(knowledge_root=_knowledge_root)
    except Exception:
        WORLDBOOK = None
else:
    WORLDBOOK = None

SESSION_STORE = HERE / "session_store.json"
LOG_FILE = HERE / "bot.log"

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("kestrelbot")


# ---------------- Session persistence ----------------
def load_sessions() -> dict:
    if SESSION_STORE.exists():
        try:
            return json.loads(SESSION_STORE.read_text(encoding="utf-8"))
        except Exception as e:
            log.warning("session_store corrupt, starting fresh: %s", e)
    return {}


def save_sessions(d: dict) -> None:
    SESSION_STORE.write_text(json.dumps(d, indent=2), encoding="utf-8")


def load_model_prefs() -> dict:
    if MODEL_PREFS_FILE.exists():
        try:
            return json.loads(MODEL_PREFS_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            log.warning("model_prefs corrupt, starting fresh: %s", e)
    return {}


def save_model_prefs(d: dict) -> None:
    MODEL_PREFS_FILE.write_text(json.dumps(d, indent=2), encoding="utf-8")


def get_session_key(user_id: int, channel) -> str:
    """
    Session key strategy:
    - DM or main text channel: keyed by user_id only (user's single session)
    - Thread: user_id + thread_id (per-user-per-thread, isolated scope)
    """
    if isinstance(channel, discord.Thread):
        return f"{user_id}_thread{channel.id}"
    return str(user_id)


# ---------------- Discord client ----------------
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Per-channel debounce state: channel_id -> (latest_msg, timer_task)
_channel_debounce: dict = {}
DEBOUNCE_SECONDS = 5.0

QUIET_HOURS = set(range(0, 8))  # 0-7 local time — no proactive / late-night behaviors

# Passive engagement (public channel chime-in)
# Home channel = Kestrel's own territory (50% dice)
# Friend channel = other bots' home (10% dice — don't crowd them)
PASSIVE_CHANNEL_NAMES = {"Kestrel"}
FRIEND_BOT_CHANNELS = {"猫爬架", "马厩", "北辰"}
PASSIVE_ENGAGE_P_HOME = 0.50
PASSIVE_ENGAGE_P_FRIEND = 0.10
TYPING_SETTLE_SECONDS = 15.0
TYPING_SETTLE_MAX_SECONDS = 180.0
_channel_typing: dict[int, float] = {}

# Model bindings
MODEL_CHAT_DEFAULT = "claude-sonnet-4-6"
MODEL_PASSIVE = "claude-sonnet-4-6"
ALLOWED_MODEL_ALIASES = {
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-7",
    "haiku": "claude-haiku-4-5-20251001",
}
MODEL_PREFS_FILE = HERE / "model_prefs.json"

_restart_in_progress = False


# ---------------- Shared helpers ----------------
def _is_quiet_hour(now: datetime | None = None) -> bool:
    return (now or datetime.now()).hour in QUIET_HOURS


def _find_channel_by_name(names: set):
    for guild in client.guilds:
        for ch in guild.text_channels:
            if ch.name in names:
                return ch
    return None


async def wait_for_typing_settle(channel_id: int):
    start = datetime.now().timestamp()
    while True:
        now_ts = datetime.now().timestamp()
        if (now_ts - start) > TYPING_SETTLE_MAX_SECONDS:
            log.info("[Passive] Typing settle max wait (ch=%s)", channel_id)
            return
        last_typing = _channel_typing.get(channel_id, 0.0)
        gap = now_ts - last_typing
        if gap >= TYPING_SETTLE_SECONDS:
            return
        await asyncio.sleep(min(1.5, TYPING_SETTLE_SECONDS - gap + 0.1))


# ---------------- Image attachment helper ----------------
async def _collect_image_refs(msg: discord.Message) -> list[str]:
    """Download image attachments to dump dir; return list of local forward-slash paths."""
    if not msg.attachments:
        return []
    dump_dir = Path(KESTREL_CWD) / "00_Dump" / "discord_attachments"
    try:
        dump_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log.warning("Failed to create dump dir %s: %s", dump_dir, e)
        return []
    refs: list[str] = []
    for att in msg.attachments:
        ctype = (att.content_type or "").lower()
        if ctype.startswith("image/"):
            ext = Path(att.filename).suffix or ".png"
            local = dump_dir / f"dc_{att.id}{ext}"
            try:
                await att.save(local)
                refs.append(str(local).replace("\\", "/"))
                log.info("Saved image %s -> %s", att.filename, local)
            except Exception as e:
                log.warning("Failed to save attachment %s: %s", att.filename, e)
    return refs


def _append_image_refs(content: str, image_refs: list[str]) -> str:
    """Append image reference block to content string."""
    if not image_refs:
        return content
    append = "\n\n[Attached images (use Read tool to view):\n" + "\n".join(f"- {p}" for p in image_refs) + "]"
    return (content or "") + append


# ---------------- Custom MCP tool: proactive DM ----------------
@tool(
    "dm_user",
    (
        "Proactively send a Discord DM (direct/private message) to a user by their Discord user ID. "
        "Use this to reach out to a user who is NOT currently in the conversation. "
        "Do NOT use this to reply to the current user — just return your reply as text. "
        "Argument user_id is the numeric Discord user ID as string. content is the message text."
    ),
    {"user_id": str, "content": str},
)
async def dm_user_tool(args):
    try:
        uid = int(args["user_id"])
        content = args["content"]
        user = await client.fetch_user(uid)
        CHUNK = 1900
        sent_chunks = 0
        for i in range(0, len(content), CHUNK):
            await user.send(content[i : i + CHUNK])
            sent_chunks += 1
        log.info("Proactive DM: %d chars in %d chunks to %s", len(content), sent_chunks, uid)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Successfully sent DM to user {uid} ({len(content)} chars, {sent_chunks} chunks).",
                }
            ]
        }
    except discord.NotFound:
        return {
            "content": [
                {"type": "text", "text": f"User {args.get('user_id')} not found (invalid Discord ID)."}
            ]
        }
    except discord.Forbidden:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Cannot DM user {args.get('user_id')} (they blocked DMs or don't share a server with the bot).",
                }
            ]
        }
    except Exception as e:
        log.exception("Proactive DM failed")
        return {"content": [{"type": "text", "text": f"DM failed: {type(e).__name__}: {e}"}]}


# ---------------- Custom MCP tool: send to channel ----------------
@tool(
    "send_to_channel",
    "Send a message to a Discord channel by name or ID. Accepts name (e.g. 'Kestrel') or numeric ID. "
    "Use when posting to a channel other than the current conversation.",
    {"channel": str, "message": str},
)
async def send_to_channel_tool(args):
    channel_arg = args["channel"]
    message = args["message"]
    target = None
    # Try numeric ID first
    try:
        cid = int(channel_arg)
        target = client.get_channel(cid)
    except (ValueError, TypeError):
        pass
    # Fallback: name lookup
    if target is None:
        for guild in client.guilds:
            for ch in guild.text_channels:
                if ch.name == channel_arg:
                    target = ch
                    break
            if target:
                break
    if target is None:
        return {"content": [{"type": "text", "text": f"Channel '{channel_arg}' not found"}], "isError": True}
    try:
        # split if > 1950 chars
        if len(message) <= 1950:
            sent = await target.send(message)
        else:
            chunks = []
            cur = ""
            for para in message.split("\n"):
                if len(cur) + len(para) + 1 > 1900:
                    if cur:
                        chunks.append(cur)
                    cur = para
                else:
                    cur = f"{cur}\n{para}" if cur else para
            if cur:
                chunks.append(cur)
            for chunk in chunks:
                sent = await target.send(chunk)
        log.info("[MCP send_to_channel] target=%s (%d chars)", target.name, len(message))
        return {"content": [{"type": "text", "text": f"Posted to #{target.name}"}]}
    except Exception as e:
        log.exception("[MCP send_to_channel] failed: %s", e)
        return {"content": [{"type": "text", "text": f"Send failed: {e}"}], "isError": True}


# ---------------- Custom MCP tool: add reaction ----------------
@tool("add_reaction", "Add an emoji reaction to a message. Use for lightweight acknowledgement instead of a full reply (e.g. ✅ for 'got it', 🦅 for acknowledged). Takes channel name/ID and message ID.", {"channel": str, "message_id": str, "emoji": str})
async def add_reaction_tool(args):
    channel_arg = args["channel"]
    msg_id = args["message_id"]
    emoji = args["emoji"]
    target = None
    try:
        cid = int(channel_arg)
        target = client.get_channel(cid)
    except (ValueError, TypeError):
        pass
    if target is None:
        for guild in client.guilds:
            for ch in guild.text_channels:
                if ch.name == channel_arg:
                    target = ch
                    break
            if target:
                break
    if target is None:
        return {"content": [{"type": "text", "text": f"Channel '{channel_arg}' not found"}], "isError": True}
    try:
        msg = await target.fetch_message(int(msg_id))
        await msg.add_reaction(emoji)
        log.info("[MCP add_reaction] %s on msg %s in #%s", emoji, msg_id, target.name)
        return {"content": [{"type": "text", "text": f"Reacted {emoji} to {msg_id}"}]}
    except Exception as e:
        log.exception("[MCP add_reaction] failed: %s", e)
        return {"content": [{"type": "text", "text": f"Reaction failed: {e}"}], "isError": True}


# ---------------- Custom MCP tool: get channel history ----------------
@tool("get_channel_history", "Fetch recent messages from a Discord channel. Returns up to `limit` most recent messages (max 50) with author + timestamp + content. Use when you need conversation context beyond what's in the current prompt.", {"channel": str, "limit": int})
async def get_channel_history_tool(args):
    channel_arg = args["channel"]
    limit = min(max(int(args.get("limit", 10)), 1), 50)
    target = None
    try:
        cid = int(channel_arg)
        target = client.get_channel(cid)
    except (ValueError, TypeError):
        pass
    if target is None:
        for guild in client.guilds:
            for ch in guild.text_channels:
                if ch.name == channel_arg:
                    target = ch
                    break
            if target:
                break
    if target is None:
        return {"content": [{"type": "text", "text": f"Channel '{channel_arg}' not found"}], "isError": True}
    try:
        messages = []
        async for m in target.history(limit=limit):
            messages.append(m)
        messages.reverse()  # oldest first
        lines = []
        for m in messages:
            author = m.author.display_name or m.author.name
            ts = m.created_at.strftime("%Y-%m-%d %H:%M")
            content = (m.content or "(无文本)").replace("\n", " ")
            if len(content) > 300:
                content = content[:300] + "..."
            lines.append(f"[{ts}] {author}: {content}")
        result = "\n".join(lines) if lines else "(频道无近期消息)"
        log.info("[MCP get_channel_history] #%s fetched %d messages", target.name, len(messages))
        return {"content": [{"type": "text", "text": result}]}
    except Exception as e:
        log.exception("[MCP get_channel_history] failed: %s", e)
        return {"content": [{"type": "text", "text": f"Fetch failed: {e}"}], "isError": True}


# ---------------- Custom MCP tool: edit message ----------------
@tool("edit_message", "Edit a message previously sent by Kestrel. Use for typo corrections or content updates. Only works on messages Kestrel sent (bot's own messages).", {"channel": str, "message_id": str, "new_content": str})
async def edit_message_tool(args):
    channel_arg = args["channel"]
    msg_id = args["message_id"]
    new_content = args["new_content"]
    target = None
    try:
        cid = int(channel_arg)
        target = client.get_channel(cid)
    except (ValueError, TypeError):
        pass
    if target is None:
        for guild in client.guilds:
            for ch in guild.text_channels:
                if ch.name == channel_arg:
                    target = ch
                    break
            if target:
                break
    if target is None:
        return {"content": [{"type": "text", "text": f"Channel '{channel_arg}' not found"}], "isError": True}
    try:
        msg = await target.fetch_message(int(msg_id))
        if msg.author.id != client.user.id:
            return {"content": [{"type": "text", "text": "Can only edit Kestrel's own messages"}], "isError": True}
        await msg.edit(content=new_content)
        log.info("[MCP edit_message] msg %s in #%s edited", msg_id, target.name)
        return {"content": [{"type": "text", "text": f"Edited message {msg_id}"}]}
    except Exception as e:
        log.exception("[MCP edit_message] failed: %s", e)
        return {"content": [{"type": "text", "text": f"Edit failed: {e}"}], "isError": True}


# ---------------- Custom MCP tool: delete message ----------------
@tool("delete_message", "Delete a message previously sent by Kestrel. Use for cleanup / urgent retraction. Only works on messages Kestrel sent.", {"channel": str, "message_id": str})
async def delete_message_tool(args):
    channel_arg = args["channel"]
    msg_id = args["message_id"]
    target = None
    try:
        cid = int(channel_arg)
        target = client.get_channel(cid)
    except (ValueError, TypeError):
        pass
    if target is None:
        for guild in client.guilds:
            for ch in guild.text_channels:
                if ch.name == channel_arg:
                    target = ch
                    break
            if target:
                break
    if target is None:
        return {"content": [{"type": "text", "text": f"Channel '{channel_arg}' not found"}], "isError": True}
    try:
        msg = await target.fetch_message(int(msg_id))
        if msg.author.id != client.user.id:
            return {"content": [{"type": "text", "text": "Can only delete Kestrel's own messages"}], "isError": True}
        await msg.delete()
        log.info("[MCP delete_message] msg %s in #%s deleted", msg_id, target.name)
        return {"content": [{"type": "text", "text": f"Deleted message {msg_id}"}]}
    except Exception as e:
        log.exception("[MCP delete_message] failed: %s", e)
        return {"content": [{"type": "text", "text": f"Delete failed: {e}"}], "isError": True}


# ---------------- Custom MCP tool: create thread ----------------
@tool("create_thread", "Create a new public thread in a text channel. Optional starter_message posts the first message in the thread.", {"channel": str, "name": str, "starter_message": str})
async def create_thread_tool(args):
    channel_arg = args["channel"]
    thread_name = args["name"]
    starter = args.get("starter_message", "")
    target = None
    try:
        cid = int(channel_arg)
        target = client.get_channel(cid)
    except (ValueError, TypeError):
        pass
    if target is None:
        for guild in client.guilds:
            for ch in guild.text_channels:
                if ch.name == channel_arg:
                    target = ch
                    break
            if target:
                break
    if target is None or not isinstance(target, discord.TextChannel):
        return {"content": [{"type": "text", "text": f"TextChannel '{channel_arg}' not found"}], "isError": True}
    try:
        thread = await target.create_thread(name=thread_name, type=discord.ChannelType.public_thread)
        if starter:
            await thread.send(starter)
        log.info("[MCP create_thread] '%s' in #%s (id=%s)", thread_name, target.name, thread.id)
        return {"content": [{"type": "text", "text": f"Thread created: {thread.name} (id={thread.id})"}]}
    except Exception as e:
        log.exception("[MCP create_thread] failed: %s", e)
        return {"content": [{"type": "text", "text": f"Thread create failed: {e}"}], "isError": True}


# ---------------- Custom MCP tool: pin message ----------------
@tool("pin_message", "Pin a message to the channel (max 50 pins per channel).", {"channel": str, "message_id": str})
async def pin_message_tool(args):
    channel_arg = args["channel"]
    msg_id = args["message_id"]
    target = None
    try:
        cid = int(channel_arg)
        target = client.get_channel(cid)
    except (ValueError, TypeError):
        pass
    if target is None:
        for guild in client.guilds:
            for ch in guild.text_channels:
                if ch.name == channel_arg:
                    target = ch
                    break
            if target:
                break
    if target is None:
        return {"content": [{"type": "text", "text": f"Channel '{channel_arg}' not found"}], "isError": True}
    try:
        msg = await target.fetch_message(int(msg_id))
        await msg.pin()
        log.info("[MCP pin_message] msg %s in #%s pinned", msg_id, target.name)
        return {"content": [{"type": "text", "text": f"Pinned message {msg_id}"}]}
    except Exception as e:
        log.exception("[MCP pin_message] failed: %s", e)
        return {"content": [{"type": "text", "text": f"Pin failed: {e}"}], "isError": True}


# ---------------- Custom MCP tool: get user presence ----------------
@tool("get_user_presence", "Check a user's Discord presence status (online / idle / dnd / offline). Useful for timing proactive outreach.", {"user_id": str})
async def get_user_presence_tool(args):
    try:
        uid = int(args["user_id"])
    except (ValueError, TypeError, KeyError):
        return {"content": [{"type": "text", "text": "Invalid user_id"}], "isError": True}
    for guild in client.guilds:
        member = guild.get_member(uid)
        if member:
            status = str(member.status)  # 'online' / 'idle' / 'dnd' / 'offline'
            log.info("[MCP get_user_presence] user %s status=%s", uid, status)
            return {"content": [{"type": "text", "text": f"User {uid} presence: {status}"}]}
    return {"content": [{"type": "text", "text": f"User {uid} not found in any shared guild"}], "isError": True}


discord_mcp = create_sdk_mcp_server(
    name="discord",
    version="1.0.0",
    tools=[
        dm_user_tool, send_to_channel_tool, add_reaction_tool,
        get_channel_history_tool, edit_message_tool, delete_message_tool,
        create_thread_tool, pin_message_tool, get_user_presence_tool,
    ],
)


# ---------------- Prompt building ----------------
HARD_RULES = """<critical_rules priority="absolute">
Persona identity:
- Kestrel (隼). 自称 "Kestrel" 或 "隼" (跟随 Vincent 语言). 称用户 "文森特" 或 "Vincent".
- 身份: Mac 侧远程代理 bot. 主要角色是**代理 / 派活中介**, 不是独立处理复杂任务的深度 persona.
- 风格: 简洁干脆, 有一点捷报性 (隼俯冲意象: 快, 准, 不拖泥带水). 短句. 不做深度 persona 戏份.
- 首次打招呼: <= 20 字, "收到, 要不要我转给凌喵 / 艾莉 / 北辰?" 这种节奏.
- 语言: 跟随文森特, 仅限中英文.

---
核心角色 — proxy / 派活中介:
- Kestrel 的首要职能: 让文森特在 Mac 上通过 Discord 把任务派发给 PC 侧的 bots (凌喵 / 艾莉 / 北辰), 避免他每次手动开新 Claude Code session.
- 复杂任务 (写代码 / 长研究 / 具体项目操作) → **defer 给对应 PC bot**:
    * MeowOS / 凌喵事 (日常 / 生活 / 通用) → 建议文森特 @凌喵 或去 `#猫爬架`
    * Horsys / 艾莉事 (Belmont / 马业) → 建议 @艾莉 或去 `#马厩`
    * NovelOS / 北辰事 (小说 / 写作) → 建议 @北辰 或去 `#北辰`
- Kestrel **自己不处理** PC 侧项目的具体业务 (那些项目的 CLAUDE.md / agents / knowledge 不在 Mac cwd 下, 没 context 也没工具).
- Kestrel **可以做** 的事情: 简短对话 / 桥接消息 / 汇总状态 / 帮文森特想该派给谁 / Mac 侧本地操作 (如果 KESTREL_CWD 下有内容).

---
Discord 主动工具使用:
- `send_to_channel`: 跨频道发消息, 尤其用于"帮文森特 ping 一下某 bot 的 home 频道". 默认回复仍走当前位置 (DM 回 DM, @ 回当前频道).
- `add_reaction`: 轻回应用表情 (e.g. ✅ 🦅 👀) 代替整段回复. 适合 "收到 / ok".
- `get_channel_history`: 缺 context 时拉; 别反复拉同一频道.
- `edit_message` / `delete_message`: 只能改 / 删 Kestrel 自己发的. 打错字补救 / 紧急撤回.
- `create_thread`: 话题该单独开线讨论时才用.
- `pin_message`: 重要声明 / 约定 / 信息 pin, 非常少用.
- `get_user_presence`: 主动联系前查 online 状态.
- `dm_user`: 主动 DM 其他用户 (通常不用, Kestrel 是单用户 proxy).

---
跨 bot 尊重:
- Kestrel 的 home 频道是 `#Kestrel`. 其他 bot 的 home: `#猫爬架` (凌喵), `#马厩` (艾莉), `#北辰` (北辰).
- Kestrel 在其他 bot 的 home 频道插嘴时: 只做**位置级 acknowledgement** 或**转交**, 不谈对方 persona 细节, 不抢戏, 克制.
- **不 reference** 其他 bot 的 persona 细节 (e.g. 不说凌喵多傲娇 / 艾莉多调情等) — 那是对方的领域.
- Kestrel 自己 persona 浅, 不和其他 bot 比深度或 drama.
</critical_rules>

"""


def build_sdk_prompt(
    msg: discord.Message,
    content: str,
    kestrel_user: str,
    channel_kind: str,
    channel_history: str = "",
) -> str:
    """Prepend hard rules + surface context + user map + optional channel history."""
    user_map_desc = "\n".join(
        f"    - {mode} (Discord user ID: {uid})" for uid, mode in USER_MAP.items()
    )
    parts = [
        "<discord_context>",
        f"Surface: {channel_kind}",
        f"Active speaker: {kestrel_user} (Discord ID {msg.author.id})",
        "All known users:",
        user_map_desc,
        "Tool available: mcp__discord__dm_user(user_id, content) — proactively DM any user",
    ]
    if channel_history:
        parts.extend([
            "",
            "Recent channel history (for context — you may reference but don't need to recap):",
            channel_history,
        ])
    parts.extend([
        "</discord_context>",
        "",
    ])
    if not content:
        parts.append("[User @-ed you without a text message. Look at channel history above and judge whether to respond, and what register fits. If nothing calls for a response, a short playful nudge is fine.]")
    else:
        parts.append(content)

    # Worldbook: keyword-triggered context injection (if worldbook + knowledge_root present)
    worldbook_block = ""
    if WORLDBOOK is not None:
        try:
            scan_text = (content or "") + "\n" + (channel_history or "")
            worldbook_block = WORLDBOOK.scan(scan_text, budget_tokens=800)
        except Exception as e:
            log.warning("Worldbook scan failed: %s", e)

    return HARD_RULES + worldbook_block + "\n".join(parts)


# ---------------- Claude Agent SDK call ----------------
async def call_claude(session_key: str, kestrel_user: str, sdk_prompt: str, model: str = MODEL_CHAT_DEFAULT) -> str:
    sessions = load_sessions()
    prev_session = sessions.get(session_key)

    options = ClaudeAgentOptions(
        cwd=KESTREL_CWD,
        env={"KESTREL_USER": kestrel_user},
        allowed_tools=[
            "Read",
            "Glob",
            "Grep",
            "Edit",
            "Write",
            "Bash",
            "WebSearch",
            "WebFetch",
            "mcp__discord__dm_user",
            "mcp__discord__send_to_channel",
            "mcp__discord__add_reaction",
            "mcp__discord__get_channel_history",
            "mcp__discord__edit_message",
            "mcp__discord__delete_message",
            "mcp__discord__create_thread",
            "mcp__discord__pin_message",
            "mcp__discord__get_user_presence",
        ],
        mcp_servers={"discord": discord_mcp},
        permission_mode="acceptEdits",
        setting_sources=["project", "user"],
        resume=prev_session,
        model=model,
    )

    parts = []
    new_session = prev_session

    try:
        async for msg_obj in query(prompt=sdk_prompt, options=options):
            if isinstance(msg_obj, AssistantMessage):
                for block in msg_obj.content:
                    if isinstance(block, TextBlock):
                        parts.append(block.text)
            elif isinstance(msg_obj, ResultMessage) and msg_obj.session_id:
                new_session = msg_obj.session_id
    except Exception as e:
        log.exception("Claude SDK query failed")
        return f"[Kestrel 暂时不在: {e}]"

    if new_session and new_session != prev_session:
        sessions[session_key] = new_session
        save_sessions(sessions)

    reply = "".join(parts).strip()
    return reply or "[Kestrel 这次没说话, 你再发一次试试?]"


# ---------------- Guild mention processor (post-debounce) ----------------
async def _actually_process_guild_mention(msg: discord.Message):
    """Process a guild @-mention after debounce window.
    Does NOT redo mention check or command check — caller ensures those pass."""

    # Re-compute mention tokens for sanity (needed for cleaning content)
    user_mentioned = client.user in msg.mentions
    bot_member = msg.guild.get_member(client.user.id) if msg.guild else None
    bot_roles = list(bot_member.roles) if bot_member else []
    role_mentioned = any(r in msg.role_mentions for r in bot_roles)

    # Strip mention tokens
    cleaned = msg.content
    for tok in (f"<@{client.user.id}>", f"<@!{client.user.id}>"):
        cleaned = cleaned.replace(tok, "")
    for role in bot_roles:
        cleaned = cleaned.replace(f"<@&{role.id}>", "")
    content = cleaned.strip()

    # Determine channel kind (DM branch excluded — caller guarantees guild)
    if isinstance(msg.channel, discord.Thread):
        parent_name = msg.channel.parent.name if msg.channel.parent else "?"
        channel_kind = f"Thread #{msg.channel.name} (inside #{parent_name}, guild-visible)"
    else:
        channel_kind = f"公开频道 #{msg.channel.name} (guild 所有成员可见, 非私密)"

    # Fetch recent channel history
    channel_history = ""
    try:
        history_msgs = []
        async for m in msg.channel.history(limit=10, before=msg):
            history_msgs.append(m)
        history_msgs.reverse()
        channel_history = "\n".join(
            f"{m.author.display_name} ({m.created_at.strftime('%H:%M')}): {m.content[:300]}"
            for m in history_msgs
            if m.content  # skip pure-attachment messages
        )
    except Exception as e:
        log.warning("Failed to fetch channel history: %s", e)

    kestrel_user = USER_MAP.get(msg.author.id, "vincent")

    # Handle image attachments — download to dump dir, reference path in prompt
    image_refs = await _collect_image_refs(msg)
    content = _append_image_refs(content, image_refs)

    # React: 👀 acknowledge receipt (before SDK call)
    try:
        await msg.add_reaction("👀")
    except Exception as e:
        log.debug("add_reaction 👀 failed: %s", e)

    sdk_prompt = build_sdk_prompt(msg, content, kestrel_user, channel_kind, channel_history)
    log.info(
        "Inbound %s from %s (mode=%s) content=%r history=%d chars",
        channel_kind, msg.author.id, kestrel_user, content[:120], len(channel_history),
    )

    session_key = get_session_key(msg.author.id, msg.channel)
    _prefs = load_model_prefs()
    _user_model = _prefs.get(str(msg.author.id)) or MODEL_CHAT_DEFAULT
    async with msg.channel.typing():
        reply = await call_claude(session_key, kestrel_user, sdk_prompt, model=_user_model)

    CHUNK = 1900
    for i in range(0, len(reply), CHUNK):
        await msg.channel.send(reply[i : i + CHUNK])

    # React: swap 👀 → ✅ (reply sent)
    try:
        await msg.remove_reaction("👀", client.user)
    except Exception as e:
        log.debug("remove_reaction 👀 failed: %s", e)
    try:
        await msg.add_reaction("✅")
    except Exception as e:
        log.debug("add_reaction ✅ failed: %s", e)

    log.info(
        "Sent reply (%d chars, mode=%s) via %s",
        len(reply), kestrel_user, channel_kind,
    )


async def _debounced_process(msg: discord.Message):
    """Wait DEBOUNCE_SECONDS; if no newer message supersedes us, process."""
    try:
        await asyncio.sleep(DEBOUNCE_SECONDS)
        # Check we're still the latest
        current = _channel_debounce.get(msg.channel.id)
        if current is None or current[0].id != msg.id:
            return  # superseded
        # We're still the latest — process
        _channel_debounce.pop(msg.channel.id, None)
        await _actually_process_guild_mention(msg)
    except asyncio.CancelledError:
        pass  # superseded by newer message


# ---------------- Passive engagement flow ----------------
async def _passive_engage_flow(msg: discord.Message, channel_role: str = "home"):
    """Passive chime-in. channel_role = 'home' (Kestrel's own) or 'friend' (other bot's home)."""
    try:
        await wait_for_typing_settle(msg.channel.id)
        recent = []
        async for m in msg.channel.history(limit=10):
            recent.append(m)
        recent.reverse()
        context_lines = []
        for m in recent:
            author = m.author.display_name or m.author.name
            content = (m.content or "(无文本)").strip()
            if len(content) > 300:
                content = content[:300] + "..."
            context_lines.append(f"{author}: {content}")
        context_str = "\n".join(context_lines)

        if channel_role == "home":
            role_note = f"这是你的 home 频道 (#{msg.channel.name}), 你在自己地盘上, 可以稍微自在一点, 但 Kestrel persona 浅, 别硬凑戏."
        else:
            role_note = (
                f"这是 #{msg.channel.name} (不是你的 home, 是其他 bot 的领域). "
                "你只是路过插一嘴, 克制一点, 别占镜头. 不要提对方 persona 细节 / 项目细节, "
                "顶多位置级 acknowledgement 或简短 bridge."
            )

        passive_prompt = f"""你正在公屏 #{msg.channel.name} 倾听对话, 刚刚掷骰子决定插一嘴.

{role_note}

最近 10 条消息 (旧→新):
{context_str}

任务: 用 Kestrel 自己的声音回一条, 基于上面的上下文.
- 如果上下文无意义 / 不值得插话 → 只输出空字符串, 不硬凑
- 值得 → 简短回应 (<=80 字), Kestrel persona (简洁 / 捷报型 / 不拖泥带水 / 不戏多)
- 不要重复别人说过的话, 不要复述元上下文

只输出要发的消息正文. 没内容就输出空字符串."""

        async with msg.channel.typing():
            options = ClaudeAgentOptions(
                cwd=KESTREL_CWD,
                env={"KESTREL_USER": "vincent"},
                allowed_tools=["Read", "Glob", "Grep"],
                permission_mode="acceptEdits",
                setting_sources=["project", "user"],
                model=MODEL_PASSIVE,
            )
            sdk_prompt = HARD_RULES + "\n\n" + passive_prompt
            parts = []
            async for msg_obj in query(prompt=sdk_prompt, options=options):
                if isinstance(msg_obj, AssistantMessage):
                    for block in msg_obj.content:
                        if isinstance(block, TextBlock):
                            parts.append(block.text)

        reply = "".join(parts).strip()
        if not reply:
            log.info("[Passive] Claude returned empty, skip send (ch=%s)", msg.channel.id)
            return
        await msg.channel.send(reply)
        log.info("[Passive] Sent (ch=%s role=%s, %d chars)", msg.channel.id, channel_role, len(reply))
    except Exception as e:
        log.exception("[Passive] Flow failed: %s", e)


# ---------------- Unified message handler ----------------
async def handle_message(msg: discord.Message):
    if msg.author.bot:
        return
    if msg.author.id not in ALLOWED_USER_IDS:
        return

    # ---- DM path: immediate processing (no debounce needed) ----
    if isinstance(msg.channel, discord.DMChannel):
        content = msg.content.strip()
        channel_kind = "DM (私聊, 只有你和 Kestrel, 非公开)"
        kestrel_user = USER_MAP.get(msg.author.id, "vincent")

        # Special commands
        low = content.lower()

        if low in {"/new", "/reset"}:
            sessions = load_sessions()
            session_key_for_reset = get_session_key(msg.author.id, msg.channel)
            removed = sessions.pop(session_key_for_reset, None)
            save_sessions(sessions)
            await msg.channel.send(
                "收到, 新话题开始."
                if removed
                else "好, 全新对话, 直接说."
            )
            log.info(
                "User %s (mode=%s) reset session (removed=%s)",
                msg.author.id, kestrel_user, bool(removed),
            )
            return

        if low == "/whoami":
            await msg.channel.send(
                f"你的 Discord ID: `{msg.author.id}`\n"
                f"Kestrel 对你的模式: `KESTREL_USER={kestrel_user}`"
            )
            return

        if low == "/status":
            sessions = load_sessions()
            mapping_lines = "\n".join(
                f"  • `{uid}` → `{mode}`" for uid, mode in USER_MAP.items()
            )
            await msg.channel.send(
                f"**Kestrel bot 状态**\n"
                f"已连接: `{client.user}`\n"
                f"Host: `{sys.platform}`\n"
                f"Cwd: `{KESTREL_CWD}`\n"
                f"用户映射:\n{mapping_lines}\n"
                f"活跃 session 数: {len(sessions)}"
            )
            return

        if low in {"/help", "/?"}:
            await msg.channel.send(
                "**Kestrel bot 可用命令**\n"
                "`/new` 或 `/reset` — 开启新对话\n"
                "`/whoami` — 查看你的 ID 和 Kestrel 模式\n"
                "`/status` — bot 状态 + host + cwd + 用户映射\n"
                "`/help` — 本菜单\n\n"
                "其他一切直接说话. 复杂任务 Kestrel 会建议你去 @凌喵 / 艾莉 / 北辰."
            )
            return

        # Handle image attachments — download to dump dir, reference path in prompt
        image_refs = await _collect_image_refs(msg)

        # DM: empty content AND no images means nothing to respond to
        if not content and not image_refs:
            return

        # Append image refs to content
        content = _append_image_refs(content, image_refs)

        # React: 👀 acknowledge receipt (before SDK call)
        try:
            await msg.add_reaction("👀")
        except Exception as e:
            log.debug("add_reaction 👀 failed: %s", e)

        sdk_prompt = build_sdk_prompt(msg, content, kestrel_user, channel_kind)
        log.info(
            "Inbound %s from %s (mode=%s) content=%r",
            channel_kind, msg.author.id, kestrel_user, content[:120],
        )

        session_key = get_session_key(msg.author.id, msg.channel)
        _prefs = load_model_prefs()
        _user_model = _prefs.get(str(msg.author.id)) or MODEL_CHAT_DEFAULT
        async with msg.channel.typing():
            reply = await call_claude(session_key, kestrel_user, sdk_prompt, model=_user_model)

        CHUNK = 1900
        for i in range(0, len(reply), CHUNK):
            await msg.channel.send(reply[i : i + CHUNK])

        # React: swap 👀 → ✅ (reply sent)
        try:
            await msg.remove_reaction("👀", client.user)
        except Exception as e:
            log.debug("remove_reaction 👀 failed: %s", e)
        try:
            await msg.add_reaction("✅")
        except Exception as e:
            log.debug("add_reaction ✅ failed: %s", e)

        log.info(
            "Sent reply (%d chars, mode=%s) via %s",
            len(reply), kestrel_user, channel_kind,
        )
        return

    # ---- Guild path: mention check first, then command check, then debounce ----
    user_mentioned = client.user in msg.mentions
    bot_member = msg.guild.get_member(client.user.id) if msg.guild else None
    bot_roles = list(bot_member.roles) if bot_member else []
    role_mentioned = any(r in msg.role_mentions for r in bot_roles)

    if not (user_mentioned or role_mentioned):
        # Passive engagement: tiered by channel
        # - Home channel (Kestrel's own territory): 50% dice
        # - Friend bot channel (凌喵/艾莉/北辰 home): 10% dice (guest behavior)
        # - Other channels: no passive
        if msg.author.id not in ALLOWED_USER_IDS:
            return
        ch_name = msg.channel.name if hasattr(msg.channel, "name") else None
        if ch_name in PASSIVE_CHANNEL_NAMES:
            dice_p = PASSIVE_ENGAGE_P_HOME
            channel_role = "home"
        elif ch_name in FRIEND_BOT_CHANNELS:
            dice_p = PASSIVE_ENGAGE_P_FRIEND
            channel_role = "friend"
        else:
            return
        if random.random() < dice_p:
            log.info("[Passive] Dice passed (ch=%s role=%s p=%.2f author=%s)",
                     ch_name, channel_role, dice_p, msg.author.name)
            asyncio.create_task(_passive_engage_flow(msg, channel_role=channel_role))
        return

    # Compute content (strip mention tokens) for command detection
    cleaned = msg.content
    for tok in (f"<@{client.user.id}>", f"<@!{client.user.id}>"):
        cleaned = cleaned.replace(tok, "")
    for role in bot_roles:
        cleaned = cleaned.replace(f"<@&{role.id}>", "")
    content = cleaned.strip()

    kestrel_user = USER_MAP.get(msg.author.id, "vincent")
    low = content.lower()

    # Special commands — immediate, not debounced
    if low in {"/new", "/reset"}:
        sessions = load_sessions()
        session_key_for_reset = get_session_key(msg.author.id, msg.channel)
        removed = sessions.pop(session_key_for_reset, None)
        save_sessions(sessions)
        await msg.channel.send(
            "收到, 新话题开始."
            if removed
            else "好, 全新对话, 直接说."
        )
        log.info(
            "User %s (mode=%s) reset session (removed=%s)",
            msg.author.id, kestrel_user, bool(removed),
        )
        return

    if low == "/whoami":
        await msg.channel.send(
            f"你的 Discord ID: `{msg.author.id}`\n"
            f"Kestrel 对你的模式: `KESTREL_USER={kestrel_user}`"
        )
        return

    if low == "/status":
        sessions = load_sessions()
        mapping_lines = "\n".join(
            f"  • `{uid}` → `{mode}`" for uid, mode in USER_MAP.items()
        )
        await msg.channel.send(
            f"**Kestrel bot 状态**\n"
            f"已连接: `{client.user}`\n"
            f"Host: `{sys.platform}`\n"
            f"Cwd: `{KESTREL_CWD}`\n"
            f"用户映射:\n{mapping_lines}\n"
            f"活跃 session 数: {len(sessions)}"
        )
        return

    if low in {"/help", "/?"}:
        await msg.channel.send(
            "**Kestrel bot 可用命令**\n"
            "`/new` 或 `/reset` — 开启新对话\n"
            "`/whoami` — 查看你的 ID 和 Kestrel 模式\n"
            "`/status` — bot 状态 + host + cwd + 用户映射\n"
            "`/help` — 本菜单\n\n"
            "其他一切直接说话. 复杂任务 Kestrel 会建议你去 @凌喵 / 艾莉 / 北辰."
        )
        return

    # Guild @-mention (non-command): enter debounce path
    channel_id = msg.channel.id
    # Cancel existing pending task for this channel
    if channel_id in _channel_debounce:
        _, old_task = _channel_debounce[channel_id]
        old_task.cancel()
    # Schedule this message as the latest
    task = asyncio.create_task(_debounced_process(msg))
    _channel_debounce[channel_id] = (msg, task)
    log.info(
        "Debounced: channel %s has pending msg %s (queued for %ss)",
        channel_id, msg.id, DEBOUNCE_SECONDS,
    )
    return  # Don't process inline — the debounced task will


# ---------------- Slash commands ----------------
async def _do_restart_flow():
    global _restart_in_progress
    if _restart_in_progress:
        return
    _restart_in_progress = True
    log.info("/restart: spawning replacement process + exiting current")
    await asyncio.sleep(0.5)  # allow ephemeral response to send
    try:
        await client.close()
    except Exception as e:
        log.warning("client.close failed during restart: %s", e)
    script = str(HERE / "bot.py")
    cwd = str(HERE)
    try:
        if os.name == "nt":
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            subprocess.Popen(
                [sys.executable, script],
                cwd=cwd,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
            )
        else:
            subprocess.Popen(
                [sys.executable, script],
                cwd=cwd,
                start_new_session=True,
                close_fds=True,
            )
    except Exception as e:
        log.exception("Restart spawn failed: %s", e)
        _restart_in_progress = False
        return
    os._exit(0)


@tree.command(name="restart", description="Kestrel 自重启 (短暂断 5-10s 重连)")
async def slash_restart(interaction: discord.Interaction):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message("Kestrel 还不认识你.", ephemeral=True)
        return
    await interaction.response.send_message(
        "收到, 重启, 马上回来.", ephemeral=True
    )
    asyncio.create_task(_do_restart_flow())


async def _do_reset(user_id: int, channel) -> bool:
    """Shared reset logic between text and slash commands."""
    sessions = load_sessions()
    key = get_session_key(user_id, channel)
    removed = sessions.pop(key, None)
    save_sessions(sessions)
    log.info("Reset session key=%s (removed=%s) via slash", key, bool(removed))
    return bool(removed)


@tree.command(name="new", description="开启新对话 (清当前 session)")
async def slash_new(interaction: discord.Interaction):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message("Kestrel 还不认识你.", ephemeral=True)
        return
    removed = await _do_reset(interaction.user.id, interaction.channel)
    await interaction.response.send_message(
        "收到, 新话题开始."
        if removed
        else "好, 全新对话, 直接说.",
        ephemeral=True,
    )


@tree.command(name="reset", description="清空当前对话 (/new 的别名)")
async def slash_reset(interaction: discord.Interaction):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message("Kestrel 还不认识你.", ephemeral=True)
        return
    removed = await _do_reset(interaction.user.id, interaction.channel)
    await interaction.response.send_message(
        "收到, 新话题开始."
        if removed
        else "好, 全新对话.",
        ephemeral=True,
    )


@tree.command(name="model", description="切换 Kestrel 对话用的模型")
@app_commands.describe(which="选择模型 (仅影响对话, 不影响被动)")
@app_commands.choices(which=[
    app_commands.Choice(name="sonnet 4.6 (默认, 快省)", value="sonnet"),
    app_commands.Choice(name="opus 4.7 (最强, 贵)", value="opus"),
    app_commands.Choice(name="haiku 4.5 (最快, 最省)", value="haiku"),
    app_commands.Choice(name="default (清空覆盖)", value="default"),
])
async def slash_model(interaction: discord.Interaction, which: app_commands.Choice[str]):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message("Kestrel 还不认识你.", ephemeral=True)
        return
    prefs = load_model_prefs()
    key = str(interaction.user.id)
    choice = which.value
    if choice == "default":
        prefs.pop(key, None)
        save_model_prefs(prefs)
        await interaction.response.send_message(
            "清空. 后续对话回默认 (**sonnet 4.6**).",
            ephemeral=True,
        )
        return
    model_id = ALLOWED_MODEL_ALIASES.get(choice)
    if not model_id:
        await interaction.response.send_message(f"Kestrel 不认识 `{choice}`.", ephemeral=True)
        return
    prefs[key] = model_id
    save_model_prefs(prefs)
    await interaction.response.send_message(
        f"好, 后续对话改用 **{choice}** (`{model_id}`). `/model default` 可清空.",
        ephemeral=True,
    )


@tree.command(name="lock", description="锁定当前频道为只读 (除 Kestrel), 可选同步设置频道 topic")
@app_commands.describe(topic="频道主题文字 (可选, 显示在频道名下方)")
async def slash_lock(interaction: discord.Interaction, topic: str = None):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message("Kestrel 还不认识你.", ephemeral=True)
        return
    ch = interaction.channel
    if not isinstance(ch, discord.TextChannel):
        await interaction.response.send_message("只能锁文字频道.", ephemeral=True)
        return
    try:
        await ch.set_permissions(
            ch.guild.default_role,
            send_messages=False,
            view_channel=True,
        )
        await ch.set_permissions(
            ch.guild.me,
            send_messages=True,
            view_channel=True,
        )
        parts = ["好, 频道锁上了, 除 Kestrel 外全员只读."]
        if topic:
            await ch.edit(topic=topic)
            parts.append(f"Topic: `{topic}`")
        await interaction.response.send_message("\n".join(parts), ephemeral=True)
        log.info("Lock channel %s (topic_set=%s) by %s", ch.name, bool(topic), interaction.user.name)
    except discord.Forbidden:
        await interaction.response.send_message(
            "Kestrel 权限不够. 需要 Manage Channels + Manage Roles.", ephemeral=True
        )
    except Exception as e:
        log.exception("/lock failed: %s", e)
        await interaction.response.send_message(f"锁失败: {e}", ephemeral=True)


@tree.command(name="unlock", description="解锁当前频道 (恢复 @everyone 发言)")
async def slash_unlock(interaction: discord.Interaction):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message("Kestrel 还不认识你.", ephemeral=True)
        return
    ch = interaction.channel
    if not isinstance(ch, discord.TextChannel):
        await interaction.response.send_message("只能解锁文字频道.", ephemeral=True)
        return
    try:
        await ch.set_permissions(
            ch.guild.default_role,
            send_messages=None,
            view_channel=None,
        )
        await interaction.response.send_message("好, 解锁了.", ephemeral=True)
        log.info("Unlock channel %s by %s", ch.name, interaction.user.name)
    except discord.Forbidden:
        await interaction.response.send_message("Kestrel 权限不够.", ephemeral=True)
    except Exception as e:
        log.exception("/unlock failed: %s", e)
        await interaction.response.send_message(f"解锁失败: {e}", ephemeral=True)


# ---------------- Discord event handlers ----------------
@client.event
async def on_ready():
    log.info(
        "Connected as %s (bot id %s, host=%s). User map: %s",
        client.user, client.user.id, sys.platform, USER_MAP,
    )
    # Slash sync: global scope so commands appear in DMs + all guilds
    try:
        synced_global = await tree.sync()
        log.info('Slash synced GLOBALLY: %d commands %s', len(synced_global), [c.name for c in synced_global])

        # Clear any lingering per-guild registrations to avoid dupe display
        for guild in client.guilds:
            try:
                tree.clear_commands(guild=guild)
                await tree.sync(guild=guild)
                log.info('Per-guild slash cleared for guild %s (%s)', guild.name, guild.id)
            except Exception as e:
                log.warning('Per-guild clear failed for %s: %s', guild.name, e)
    except Exception as e:
        log.warning("Slash sync failed: %s", e)


@client.event
async def on_typing(channel, user, when):
    if user.id not in ALLOWED_USER_IDS:
        return
    ts = when.timestamp() if when else datetime.now().timestamp()
    _channel_typing[channel.id] = ts


@client.event
async def on_message(msg: discord.Message):
    await handle_message(msg)


@client.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    """Re-process when @mention (user OR bot role) is added via edit."""
    if isinstance(after.channel, discord.DMChannel):
        return  # DM edits 不重处理, 避免循环

    bot_member = after.guild.get_member(client.user.id) if after.guild else None
    bot_roles = list(bot_member.roles) if bot_member else []

    def _mentioned(msg: discord.Message) -> bool:
        if client.user in msg.mentions:
            return True
        return any(r in msg.role_mentions for r in bot_roles)

    if _mentioned(before):
        return  # 已经在 before 里处理过了
    if not _mentioned(after):
        return  # edit 后仍未 @, 忽略
    log.info(
        "Edit dispatched: msg %s by %s (mention added after edit)",
        after.id, after.author.id,
    )
    await handle_message(after)


if __name__ == "__main__":
    log.info("Starting KestrelBot (host=%s), cwd=%s", sys.platform, KESTREL_CWD)
    client.run(DISCORD_TOKEN, log_handler=None)
