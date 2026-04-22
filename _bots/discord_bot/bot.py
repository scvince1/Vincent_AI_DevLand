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
    from worldbook import Worldbook, create_relation_mcp_server
    _WORLDBOOK_AVAILABLE = True
except Exception:
    Worldbook = None  # type: ignore
    create_relation_mcp_server = None  # type: ignore
    _WORLDBOOK_AVAILABLE = False

# kestrel_mcp: Auto-memory + ACED A + TodoWrite + subagent spawn (ported from MeowOS v1.7).
# DevLand DOES have staging, so stage_observation is included (unlike Horsys / NovelOS).
from kestrel_mcp import (
    build_memory_block,
    build_todos_block,
    create_kestrel_mcp_server,
    current_channel_ctx,
    current_session_key_ctx,
)

# ---------------- Config ----------------
HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

# Bot-wide static config (checked into git, no secrets).
# Controls identity, home channel, optional integration paths, and UX knobs.
BOT_CONFIG_FILE = HERE / "bot_config.json"
_DEFAULT_BOT_CONFIG = {
    "bot_name": "Kestrel",
    "bot_discord_id": "1496272385215824083",
    "home_channel": "Kestrel",
    "system_path": "",
    "knowledge_root": "",
    "knowledge_agent_path": "",
    "peer_notes_dir": "_bots/discord_bot/peer_notes",
    "channel_history_window": 20,
    "reaction_palette": {"seen": "🦅", "done": "⚡", "error": "❌"},
}
try:
    if BOT_CONFIG_FILE.exists():
        _loaded = json.loads(BOT_CONFIG_FILE.read_text(encoding="utf-8"))
        BOT_CONFIG = {**_DEFAULT_BOT_CONFIG, **_loaded}
    else:
        BOT_CONFIG = dict(_DEFAULT_BOT_CONFIG)
except Exception as _e:
    BOT_CONFIG = dict(_DEFAULT_BOT_CONFIG)

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

# Vincent's Discord ID — derived from USER_MAP; used for privileged ops
# like !restart-all (fleet-wide graceful exit → launchd auto-respawn).
VINCENT_DISCORD_ID = next((uid for uid, mode in USER_MAP.items() if mode == "vincent"), None)

# KESTREL_CWD: where the Claude Agent SDK runs from on the host machine.
# Default is Vincent's Mac home dir; override in .env on whichever host.
KESTREL_CWD = os.environ.get("KESTREL_CWD", "/Users/scvin")

# Bot identity for Worldbook private_to filter + relation MCP routing.
BOT_OWNER = "kestrel"

# DEVLAND_80K: repo-side 80_Knowledge, resolved from this file's location.
# Used for the relation layer (peers files live in the repo, not the host
# home dir) so it works identically on Mac and Windows.
DEVLAND_80K = Path(__file__).resolve().parent.parent.parent / "80_Knowledge"

# Worldbook: optional keyword-triggered context injection. Knowledge root
# is resolved repo-relative (DEVLAND_80K) so it works identically on Mac
# and Windows — Kestrel ships inside Vincent_AI_DevLand and reads the
# shared 80_Knowledge layer. private_to=kestrel entries stay visible;
# other bots' private entries are filtered out by owner.
WORLDBOOK_ROOT = DEVLAND_80K
if _WORLDBOOK_AVAILABLE and WORLDBOOK_ROOT.exists():
    try:
        WORLDBOOK = Worldbook(knowledge_root=WORLDBOOK_ROOT, owner=BOT_OWNER)
    except Exception:
        WORLDBOOK = None
else:
    WORLDBOOK = None

# Relation layer: bot-to-bot relation log MCP server. Independent of
# WORLDBOOK scan init — relations live in the repo (DEVLAND_80K), not
# the host knowledge root.
RELATION_DIR = DEVLAND_80K / "85_System" / "relations"
if _WORLDBOOK_AVAILABLE and create_relation_mcp_server is not None and RELATION_DIR.exists():
    try:
        RELATION_MCP = create_relation_mcp_server(
            owner=BOT_OWNER, relations_dir=RELATION_DIR
        )
    except Exception:
        RELATION_MCP = None
else:
    RELATION_MCP = None

SESSION_STORE = HERE / "session_store.json"
LOG_FILE = HERE / "bot.log"

# Auto-memory dir (Claude Code session dir, NOT pre-created by bot).
# graceful: if absent (DevLand hasn't been a CC project yet), build_memory_block
# returns empty, save_memory rejects. Override via KESTREL_MEMORY_DIR in .env
# for Mac/Linux hosts where the CC project dir naming may differ.
MEMORY_DIR = Path(os.environ.get(
    "KESTREL_MEMORY_DIR",
    r"C:\Users\scvin\.claude\projects\d--Ai-Project-Vincent-AI-DevLand\memory",
))
# Staging path — DevLand has 80_Knowledge/83_Observations, so ACED A is enabled.
# On Mac repo clone this resolves inside the cloned Vincent_AI_DevLand dir.
STAGING_PATH = Path(__file__).resolve().parent.parent.parent / "80_Knowledge" / "83_Observations" / "_staging.md"
TODOS_DIR = HERE / "sessions"  # per-channel todos

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


def get_session_key(channel) -> str:
    """
    Session key strategy (per-channel, not per-user):
    - Thread: keyed by thread id
    - DM / text channel: keyed by channel id
    All participants in the same channel/thread share one Claude session.
    """
    if isinstance(channel, discord.Thread):
        return f"thread_{channel.id}"
    return f"ch_{channel.id}"


# ---------------- Discord client ----------------
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Per-channel debounce state: channel_id -> (latest_msg, timer_task)
_channel_debounce: dict = {}

# Session-level msg.id dedupe. Prevents double-processing from WS reconnect / SDK resume edges.
# on_message_edit intentionally bypasses this (edits SHOULD reprocess).
_processed_msg_ids: set = set()
_processed_msg_lock = asyncio.Lock()
_PROCESSED_MSG_TRIM_THRESHOLD = 2000
_PROCESSED_MSG_KEEP_SIZE = 1000

# DM = longer pause (user is often mid-thought in private chat)
# Public = shorter pause (others may be waiting, don't lag the channel)
DM_DEBOUNCE_SECONDS = 15.0
PUBLIC_DEBOUNCE_SECONDS = 5.0
# Back-compat alias; guild path uses PUBLIC_DEBOUNCE_SECONDS directly.
DEBOUNCE_SECONDS = PUBLIC_DEBOUNCE_SECONDS

QUIET_HOURS = set(range(0, 8))  # 0-7 local time — no proactive / late-night behaviors

# Peer bot registry — other persona bots in the Vincent ecosystem.
# Kestrel may receive messages from them (cross-bot routing) or @ them
# to dispatch work. Her own id is excluded from PEER_BOT_IDS.
PEER_BOT_META = {
    1495949198976221204: {"name": "凌喵", "system": "MeowOS (Vincent 的个人 AI 助手)"},
    1496244303834648596: {"name": "艾莉", "system": "Horsys (Belmont Equine 马术业务)"},
    1496284605194436768: {"name": "北辰", "system": "NovelOS (写作项目调度)"},
    1496272385215824083: {"name": "Kestrel", "system": "Mac 侧代理"},
}
PEER_BOT_IDS = {1495949198976221204, 1496244303834648596, 1496284605194436768}

# Passive engagement (public channel chime-in)
# Home channel = Kestrel's own territory (50% dice)
# Friend channel = other bots' home (10% dice — don't crowd them)
_home_ch = BOT_CONFIG.get("home_channel", "watch-tower")
PASSIVE_CHANNEL_NAMES = {_home_ch, f"🦅-{_home_ch}", "watch-tower", "🦅-watch-tower"}
FRIEND_BOT_CHANNELS = {"猫爬架", "😺-猫爬架", "马厩", "🐎-马厩", "正北", "🧭-正北"}
# Commons channels = shared public where all bots chime in at 30% each (independent rolls)
COMMONS_CHANNELS = {"🏛️-公会大厅", "公会大厅"}
PASSIVE_ENGAGE_P_HOME = 0.50
PASSIVE_ENGAGE_P_FRIEND = 0.10
PASSIVE_ENGAGE_P_COMMONS = 0.30
TYPING_SETTLE_SECONDS = 15.0
TYPING_SETTLE_MAX_SECONDS = 180.0
_channel_typing: dict[int, float] = {}

# Model bindings
# Default chat runs Sonnet 4.5 with 1M context + Max effort + extended thinking.
MODEL_CHAT_DEFAULT = "claude-sonnet-4-5"
MODEL_PASSIVE = "claude-sonnet-4-6"
MODEL_SUBAGENT = "claude-sonnet-4-5"
CHAT_BETAS = ["context-1m-2025-08-07"]
CHAT_EFFORT = "max"
ALLOWED_MODEL_ALIASES = {
    "sonnet": "claude-sonnet-4-5",
    "sonnet46": "claude-sonnet-4-6",
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


# ---------------- Attachment helper ----------------
async def _collect_attachment_refs(msg: discord.Message) -> list[str]:
    """Download ALL attachments (not just images) to dump dir; return list of local forward-slash paths."""
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
        ext = Path(att.filename).suffix or ".bin"
        local = dump_dir / f"dc_{att.id}{ext}"
        try:
            await att.save(local)
            refs.append(str(local).replace("\\", "/"))
            log.info("Saved attachment %s -> %s", att.filename, local)
        except Exception as e:
            log.warning("Failed to save attachment %s: %s", att.filename, e)
    return refs


def _append_attachment_refs(content: str, attachment_refs: list[str]) -> str:
    """Append attachment reference block to content string."""
    if not attachment_refs:
        return content
    append = "\n\n[Discord 附件 (用 Read 工具打开):\n" + "\n".join(f"- {p}" for p in attachment_refs) + "]"
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


# ---------------- Custom MCP tool: send file to channel ----------------
@tool(
    "send_file_to_channel",
    (
        "Upload a local file as attachment to a Discord channel. Useful when "
        "reply text is too long for inline, or when you've generated a "
        "markdown/code/csv/image file that should be shared as attachment. "
        "file_path must be a local path the bot host can read. caption is "
        "optional text. Max file size 25MB."
    ),
    {"channel": str, "file_path": str, "caption": str},
)
async def send_file_to_channel_tool(args):
    channel_arg = args["channel"]
    file_path = args["file_path"]
    caption = args.get("caption", "")

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
        return {"content": [{"type": "text", "text": f"channel '{channel_arg}' not found"}], "isError": True}

    p = Path(file_path)
    if not p.exists():
        return {"content": [{"type": "text", "text": f"file not found: {file_path}"}], "isError": True}
    if not p.is_file():
        return {"content": [{"type": "text", "text": f"not a regular file: {file_path}"}], "isError": True}
    size = p.stat().st_size
    if size > 25 * 1024 * 1024:
        return {"content": [{"type": "text", "text": f"file too large ({size} bytes), Discord limit is 25MB"}], "isError": True}

    try:
        await target.send(content=caption if caption else None, file=discord.File(str(p)))
        log.info("[send_file] %s -> #%s (%d bytes)", p.name, target.name, size)
        return {"content": [{"type": "text", "text": f"Sent {p.name} ({size} bytes) to #{target.name}"}]}
    except Exception as e:
        log.exception("[send_file] failed: %s", e)
        return {"content": [{"type": "text", "text": f"send_file failed: {e}"}], "isError": True}


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
@tool(
    "get_channel_history",
    (
        "Fetch recent messages from a Discord channel. Returns up to `limit` most recent messages "
        "(max 50) with author + timestamp + content. Each message line may end with "
        "`[attachment: filename id=<msg_id>; ...]` hint if it has Discord attachments — "
        "use fetch_channel_attachment(channel, message_id) to download the actual files when needed, "
        "then Read tool to view them. Use when you need conversation context beyond what's in the current prompt."
    ),
    {"channel": str, "limit": int},
)
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
            content = (m.content or "(无正文)").replace("\n", " ")
            att_hint = ""
            if m.attachments:
                att_parts = [f"{a.filename} id={a.id}" for a in m.attachments]
                att_hint = " [attachment: " + "; ".join(att_parts) + "]"
            lines.append(f"[{ts}] {author}: {content}{att_hint}")
        result = "\n".join(lines) if lines else "(频道无近期消息)"
        log.info("[MCP get_channel_history] #%s fetched %d messages", target.name, len(messages))
        return {"content": [{"type": "text", "text": result}]}
    except Exception as e:
        log.exception("[MCP get_channel_history] failed: %s", e)
        return {"content": [{"type": "text", "text": f"Fetch failed: {e}"}], "isError": True}


# ---------------- Custom MCP tool: fetch channel attachment ----------------
@tool(
    "fetch_channel_attachment",
    (
        "Download all attachments of a specific Discord message to the local dump dir and return "
        "local file paths. Use this when you see an [attachment: ... id=<msg_id>] hint in "
        "get_channel_history output and need to actually view the attachment content. After getting "
        "back the paths, use the Read tool to open them (Read supports image vision + text file viewing). "
        "Arguments: channel = channel name or ID (same as get_channel_history). message_id = the numeric "
        "Discord message ID from the hint."
    ),
    {"channel": str, "message_id": str},
)
async def fetch_channel_attachment_tool(args):
    channel_arg = args["channel"]
    try:
        mid = int(args["message_id"])
    except (ValueError, TypeError):
        return {"content": [{"type": "text", "text": f"invalid message_id: {args.get('message_id')}"}], "isError": True}

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
        return {"content": [{"type": "text", "text": f"channel '{channel_arg}' not found"}], "isError": True}

    try:
        target_msg = await target.fetch_message(mid)
    except Exception as e:
        return {"content": [{"type": "text", "text": f"fetch_message({mid}) failed: {e}"}], "isError": True}

    if not target_msg.attachments:
        return {"content": [{"type": "text", "text": f"message {mid} has no attachments"}]}

    dump_dir = Path(KESTREL_CWD) / "00_Dump" / "discord_attachments"
    try:
        dump_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return {"content": [{"type": "text", "text": f"failed to create dump dir {dump_dir}: {e}"}], "isError": True}
    paths = []
    for att in target_msg.attachments:
        ext = Path(att.filename).suffix or ".bin"
        local = dump_dir / f"dc_{att.id}{ext}"
        try:
            await att.save(local)
            paths.append(str(local).replace("\\", "/"))
            log.info("[fetch_channel_attachment] Saved %s -> %s", att.filename, local)
        except Exception as e:
            log.warning("[fetch_channel_attachment] save failed %s: %s", att.filename, e)
    if not paths:
        return {"content": [{"type": "text", "text": f"message {mid} had attachments but all saves failed"}], "isError": True}
    return {"content": [{"type": "text", "text": "Saved attachments:\n" + "\n".join(paths)}]}


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
        dm_user_tool, send_to_channel_tool, send_file_to_channel_tool,
        add_reaction_tool,
        get_channel_history_tool, fetch_channel_attachment_tool,
        edit_message_tool, delete_message_tool,
        create_thread_tool, pin_message_tool, get_user_presence_tool,
    ],
)

# Auto-memory + ACED A + TodoWrite + subagent spawn (ported from MeowOS v1.7).
# Subagent whitelist: shell-runner + knowledge-agent (no business agents in DevLand).
KESTREL_MCP = create_kestrel_mcp_server(
    client=client,
    kestrel_cwd=KESTREL_CWD,
    memory_dir=MEMORY_DIR,
    staging_path=STAGING_PATH,
    todos_dir=TODOS_DIR,
    subagent_model=MODEL_SUBAGENT,
    subagent_betas=CHAT_BETAS,
    subagent_effort=CHAT_EFFORT,
    subagent_allowed_tools=[
        "Read", "Glob", "Grep", "Edit", "Write", "Bash",
    ],
    subagent_mcp_servers={},
    subagent_whitelist={"shell-runner", "knowledge-agent"},
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

---
Auto-memory + ACED A + TodoWrite + subagent 工具纪律:

**Auto-memory** (`mcp__kestrel__save_memory`):
- 当你确认学到关于 Vincent 的稳定事实 / 长期偏好 / 风格反馈 / 项目参考 / 外部资源, 用 save_memory 落盘.
- 已经在 `<memory_index>` 块里列出的条目**不要重复保存**; 想补充就用 Read + Edit 直接改.
- type: user / feedback / project / reference. description = 5-15 字一行 hook.
- 如果 memory_dir 还不存在, save_memory 会拒绝 — 正常, 当次跳过即可.

**ACED A (`mcp__kestrel__stage_observation`)**:
- 观察到 Vincent 的新事实 / 身边人 / 风格 / 交互 pattern, 调 stage_observation 追加到 _staging.md. 一句话一条.
- 快捷词: 用户消息以 `obs:` 或 `记住：` 开头时, 立即调 stage_observation (把前缀后的内容当 observation), 然后再回复.

**TodoWrite** (`mcp__kestrel__todo_write`):
- 多步任务 / 跨 session 议程, per-channel list. 状态: pending → in_progress → completed.
- action: 'replace_all' / 'add' / 'update_status' / 'list'.
- 简单问答无需 todo. 三步以上才用.

**subagent spawn** (`mcp__kestrel__spawn_agent`):
- 支持 2 种: shell-runner (文件 / shell) / knowledge-agent (KB 结构化写入).
- 大量文件读写 / 脏输出 bash → 派 shell-runner.
- subagent 跑 30-120s, 期间频道自动发 interim + 持续 typing.
- 同频道同时只能跑一个 subagent. 禁止 subagent 再 spawn.
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

    # Author-dispatch hint: who sent this message, so Kestrel knows
    # whether to answer a human vs a peer bot.
    author_id = msg.author.id
    if author_id in PEER_BOT_IDS:
        peer = PEER_BOT_META[author_id]
        author_hint = (
            f"这条消息来自另一只 AI bot: {peer['name']} ({peer['system']}). "
            f"你是 Kestrel (Vincent 的 Mac 侧代理). 回应简短, "
            f"必要时可以 @ 对方 bot 派活给她们."
        )
    elif author_id == 783473213413523477:
        author_hint = f"来自 Vincent (Discord ID {author_id})."
    elif author_id == 323183052064817154:
        author_hint = f"来自 Joyce (Discord ID {author_id})."
    else:
        author_hint = f"来自 unknown (Discord ID {author_id})."

    parts = [
        "<discord_context>",
        f"Surface: {channel_kind}",
        f"Active speaker: {kestrel_user} (Discord ID {msg.author.id})",
        f"Author: {author_hint}",
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

    # Auto-memory (MEMORY.md) — graceful if memory_dir absent
    memory_block = build_memory_block(MEMORY_DIR, budget_chars=8000)

    # Per-channel TodoWrite list
    session_key = get_session_key(msg.channel)
    todos_block = build_todos_block(TODOS_DIR, session_key)

    # Worldbook: keyword-triggered context injection (if worldbook + knowledge_root present)
    worldbook_block = ""
    sticky_block = ""
    if WORLDBOOK is not None:
        try:
            scan_text = (content or "") + "\n" + (channel_history or "")
            worldbook_block = WORLDBOOK.scan(scan_text, budget_tokens=800)
        except Exception as e:
            log.warning("Worldbook scan failed: %s", e)
        try:
            sticky_block = WORLDBOOK.dump_sticky(budget_tokens=500)
        except Exception as e:
            log.warning("Worldbook dump_sticky failed: %s", e)

    return (
        HARD_RULES
        + memory_block
        + todos_block
        + sticky_block
        + worldbook_block
        + "\n".join(parts)
    )


# ---------------- Claude Agent SDK call ----------------
async def call_claude(session_key: str, kestrel_user: str, sdk_prompt: str, model: str = MODEL_CHAT_DEFAULT) -> str:
    sessions = load_sessions()
    prev_session = sessions.get(session_key)

    _mcp_servers = {"discord": discord_mcp, "kestrel": KESTREL_MCP}
    if RELATION_MCP is not None:
        _mcp_servers["relation"] = RELATION_MCP
    _allowed_tools = [
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
        "mcp__discord__send_file_to_channel",
        "mcp__discord__add_reaction",
        "mcp__discord__get_channel_history",
        "mcp__discord__fetch_channel_attachment",
        "mcp__discord__edit_message",
        "mcp__discord__delete_message",
        "mcp__discord__create_thread",
        "mcp__discord__pin_message",
        "mcp__discord__get_user_presence",
        "mcp__kestrel__save_memory",
        "mcp__kestrel__stage_observation",
        "mcp__kestrel__todo_write",
        "mcp__kestrel__spawn_agent",
    ]
    if RELATION_MCP is not None:
        _allowed_tools.extend([
            "mcp__relation__append_to_relation_log",
            "mcp__relation__update_relation_snapshot",
        ])
    options = ClaudeAgentOptions(
        cwd=KESTREL_CWD,
        env={"KESTREL_USER": kestrel_user},
        allowed_tools=_allowed_tools,
        mcp_servers=_mcp_servers,
        permission_mode="acceptEdits",
        setting_sources=["project", "user"],
        resume=prev_session,
        model=model,
        betas=list(CHAT_BETAS),
        effort=CHAT_EFFORT,
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
        history_lines = []
        for m in history_msgs:
            body = (m.content or "[无正文]").replace("\n", " ")
            att_hint = ""
            if m.attachments:
                att_parts = [f"{a.filename} id={a.id}" for a in m.attachments]
                att_hint = " [attachment: " + "; ".join(att_parts) + "]"
            history_lines.append(
                f"{m.author.display_name} ({m.created_at.strftime('%H:%M')}): {body}{att_hint}"
            )
        # Thread: inject the parent starter message at the top so a fresh
        # session still has the thread's seed context.
        if isinstance(msg.channel, discord.Thread):
            try:
                starter = None
                if msg.channel.parent and msg.channel.id:
                    # Thread starter message has the same id as the thread
                    try:
                        starter = await msg.channel.parent.fetch_message(msg.channel.id)
                    except (discord.NotFound, discord.Forbidden):
                        starter = None
                if starter and starter.content:
                    history_lines.insert(
                        0,
                        f"[thread-parent] {starter.author.display_name} "
                        f"({starter.created_at.strftime('%H:%M')}): {starter.content}",
                    )
            except Exception as e:
                log.debug("Thread starter fetch failed: %s", e)
        channel_history = "\n".join(history_lines)
    except Exception as e:
        log.warning("Failed to fetch channel history: %s", e)

    kestrel_user = USER_MAP.get(msg.author.id, "vincent")

    # Handle Discord attachments — download all to dump dir, reference paths in prompt
    attachment_refs = await _collect_attachment_refs(msg)
    content = _append_attachment_refs(content, attachment_refs)

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

    session_key = get_session_key(msg.channel)
    _prefs = load_model_prefs()
    _user_model = _prefs.get(str(msg.author.id)) or MODEL_CHAT_DEFAULT
    _ch_token = current_channel_ctx.set(msg.channel)
    _sk_token = current_session_key_ctx.set(session_key)
    try:
        async with msg.channel.typing():
            reply = await call_claude(session_key, kestrel_user, sdk_prompt, model=_user_model)
    finally:
        current_channel_ctx.reset(_ch_token)
        current_session_key_ctx.reset(_sk_token)

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
    """Wait PUBLIC_DEBOUNCE_SECONDS; if no newer message supersedes us, process."""
    try:
        await asyncio.sleep(PUBLIC_DEBOUNCE_SECONDS)
        # Check we're still the latest
        current = _channel_debounce.get(msg.channel.id)
        if current is None or current[0].id != msg.id:
            return  # superseded
        # We're still the latest — process
        _channel_debounce.pop(msg.channel.id, None)
        await _actually_process_guild_mention(msg)
    except asyncio.CancelledError:
        pass  # superseded by newer message


async def _actually_process_dm(msg: discord.Message):
    """Run the SDK call for a DM after the debounce window settled."""
    content = msg.content.strip()
    channel_kind = "DM (私聊, 只有你和 Kestrel, 非公开)"
    kestrel_user = USER_MAP.get(msg.author.id, "vincent")

    # Handle Discord attachments — download all to dump dir, reference paths in prompt
    attachment_refs = await _collect_attachment_refs(msg)
    if not content and not attachment_refs:
        return
    content = _append_attachment_refs(content, attachment_refs)

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

    session_key = get_session_key(msg.channel)
    _prefs = load_model_prefs()
    _user_model = _prefs.get(str(msg.author.id)) or MODEL_CHAT_DEFAULT
    _ch_token = current_channel_ctx.set(msg.channel)
    _sk_token = current_session_key_ctx.set(session_key)
    try:
        async with msg.channel.typing():
            reply = await call_claude(session_key, kestrel_user, sdk_prompt, model=_user_model)
    finally:
        current_channel_ctx.reset(_ch_token)
        current_session_key_ctx.reset(_sk_token)

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


async def _debounced_process_dm(msg: discord.Message):
    """Wait DM_DEBOUNCE_SECONDS; if no newer DM supersedes us, process."""
    try:
        await asyncio.sleep(DM_DEBOUNCE_SECONDS)
        current = _channel_debounce.get(msg.channel.id)
        if current is None or current[0].id != msg.id:
            return  # superseded
        _channel_debounce.pop(msg.channel.id, None)
        await _actually_process_dm(msg)
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
            body = (m.content or "[无正文]").strip()
            att_hint = ""
            if m.attachments:
                att_parts = [f"{a.filename} id={a.id}" for a in m.attachments]
                att_hint = " [attachment: " + "; ".join(att_parts) + "]"
            context_lines.append(f"{author}: {body}{att_hint}")
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
            _passive_mcp_servers = {}
            _passive_allowed = ["Read", "Glob", "Grep"]
            if RELATION_MCP is not None:
                _passive_mcp_servers["relation"] = RELATION_MCP
                _passive_allowed.extend([
                    "mcp__relation__append_to_relation_log",
                    "mcp__relation__update_relation_snapshot",
                ])
            options = ClaudeAgentOptions(
                cwd=KESTREL_CWD,
                env={"KESTREL_USER": "vincent"},
                allowed_tools=_passive_allowed,
                mcp_servers=_passive_mcp_servers,
                permission_mode="acceptEdits",
                setting_sources=["project", "user"],
                model=MODEL_PASSIVE,
                betas=list(CHAT_BETAS),
                effort=CHAT_EFFORT,
            )
            sticky_block = ""
            if WORLDBOOK is not None:
                try:
                    sticky_block = WORLDBOOK.dump_sticky(budget_tokens=500)
                except Exception as e:
                    log.warning("Worldbook dump_sticky failed: %s", e)
            sdk_prompt = HARD_RULES + sticky_block + "\n\n" + passive_prompt
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
    # Never respond to ourselves
    if client.user and msg.author.id == client.user.id:
        return

    # Session-level dedupe: each msg.id processed at most once per bot lifetime.
    # Guards against Discord WS reconnect / SDK resume edges that can re-deliver the same event.
    # NOTE: on_message_edit deliberately bypasses this (edits want reprocess).
    global _processed_msg_ids
    async with _processed_msg_lock:
        if msg.id in _processed_msg_ids:
            log.info("[dedupe] msg %s already processed, skipping", msg.id)
            return
        _processed_msg_ids.add(msg.id)
        if len(_processed_msg_ids) > _PROCESSED_MSG_TRIM_THRESHOLD:
            sorted_ids = sorted(_processed_msg_ids, reverse=True)
            _processed_msg_ids = set(sorted_ids[:_PROCESSED_MSG_KEEP_SIZE])
            log.info("[dedupe] trimmed processed set to %d entries", len(_processed_msg_ids))

    # Allow: mapped humans + known peer bots. Skip everyone else (incl. random bots).
    is_peer_bot = msg.author.id in PEER_BOT_IDS
    if not is_peer_bot and msg.author.id not in ALLOWED_USER_IDS:
        return

    # !restart-all: fleet-wide graceful exit. Only Vincent. Each bot exits;
    # host supervisor (launchd on Mac, etc.) auto-respawns it. Text command
    # (not slash) so one message in any channel hits all 4 bots at once.
    if msg.author.id == VINCENT_DISCORD_ID and msg.content.strip() == "!restart-all":
        try:
            await msg.add_reaction("🔄")
        except Exception:
            pass
        log.info("[!restart-all] triggered by Vincent, exiting for auto-respawn...")
        try:
            await client.close()
        except Exception:
            pass
        sys.exit(0)

    # !new-all: batch reset. Each bot in the channel resets its own session independently.
    if not is_peer_bot and msg.content.strip().lower() == "!new-all":
        sessions = load_sessions()
        key = get_session_key(msg.channel)
        removed = sessions.pop(key, None)
        save_sessions(sessions)
        try:
            await msg.add_reaction(REACTION_DONE)
        except Exception:
            pass
        log.info("Channel %s session reset via !new-all by user=%s (removed=%s)", msg.channel.id, msg.author.id, bool(removed))
        return

    # ---- DM path: debounced processing (batch rapid messages) ----
    if isinstance(msg.channel, discord.DMChannel):
        content = msg.content.strip()
        kestrel_user = USER_MAP.get(msg.author.id, "vincent")

        # Special commands — immediate, never debounced
        low = content.lower()

        if low in {"/new", "/reset"}:
            sessions = load_sessions()
            session_key_for_reset = get_session_key(msg.channel)
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

        # DM: empty content AND no attachments means nothing to respond to
        has_attachment = bool(msg.attachments)
        if not content and not has_attachment:
            return

        # Enter DM debounce path — supersede any prior pending DM in this channel.
        channel_id = msg.channel.id
        if channel_id in _channel_debounce:
            _, old_task = _channel_debounce[channel_id]
            old_task.cancel()
        task = asyncio.create_task(_debounced_process_dm(msg))
        _channel_debounce[channel_id] = (msg, task)
        log.info(
            "DM debounced: channel %s has pending msg %s (queued for %ss)",
            channel_id, msg.id, DM_DEBOUNCE_SECONDS,
        )
        return

    # ---- Guild path: mention check first, then command check, then debounce ----
    user_mentioned = client.user in msg.mentions
    bot_member = msg.guild.get_member(client.user.id) if msg.guild else None
    bot_roles = list(bot_member.roles) if bot_member else []
    role_mentioned = any(r in msg.role_mentions for r in bot_roles)

    # Fallback 1: Reply to a bot message counts as mention
    is_reply_to_bot = False
    if msg.reference is not None:
        resolved = msg.reference.resolved
        if resolved is not None and hasattr(resolved, "author"):
            if resolved.author is not None and resolved.author.id == client.user.id:
                is_reply_to_bot = True

    # Fallback 2: Raw mention token in content
    raw_token_mention = False
    if client.user is not None:
        bot_id = client.user.id
        if f"<@{bot_id}>" in msg.content or f"<@!{bot_id}>" in msg.content:
            raw_token_mention = True

    # Fallback 3: Solo-bot thread
    is_solo_bot_thread = False
    if isinstance(msg.channel, discord.Thread):
        try:
            members = msg.channel.members
            bot_members = [m for m in members if m.bot]
            if len(bot_members) >= 1 and all(m.id == client.user.id for m in bot_members):
                is_solo_bot_thread = True
        except Exception as e:
            log.debug("[solo_bot_thread_check] failed: %s", e)

    log.info(
        "[mention_check] msg_id=%s user_mentioned=%s role_mentioned=%s "
        "is_reply_to_bot=%s raw_token=%s solo_bot_thread=%s mentions=%s role_mentions=%s "
        "reference=%s content=%r",
        msg.id, user_mentioned, role_mentioned,
        is_reply_to_bot, raw_token_mention, is_solo_bot_thread,
        [u.id for u in msg.mentions],
        [r.id for r in msg.role_mentions],
        msg.reference.message_id if msg.reference else None,
        msg.content[:200],
    )

    if not (user_mentioned or role_mentioned or is_reply_to_bot or raw_token_mention or is_solo_bot_thread):
        # Passive engagement: tiered by channel
        # - Home channel (Kestrel's own territory): 50% dice
        # - Friend bot channel (凌喵/艾莉/北辰 home): 10% dice (guest behavior)
        # - Other channels: no passive
        # Peer bots never trigger passive (avoid bot-chatter loops).
        if is_peer_bot:
            return
        if msg.author.id not in ALLOWED_USER_IDS:
            return
        ch_name = msg.channel.name if hasattr(msg.channel, "name") else None
        if ch_name in PASSIVE_CHANNEL_NAMES:
            dice_p = PASSIVE_ENGAGE_P_HOME
            channel_role = "home"
        elif ch_name in COMMONS_CHANNELS:
            dice_p = PASSIVE_ENGAGE_P_COMMONS
            channel_role = "commons"
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
        session_key_for_reset = get_session_key(msg.channel)
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
        channel_id, msg.id, PUBLIC_DEBOUNCE_SECONDS,
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


@tree.command(name="shutdown", description="Kestrel shutdown (Mac launchd will auto-restart; use `launchctl unload` for permanent)")
async def slash_shutdown(interaction: discord.Interaction):
    if interaction.user.id not in ALLOWED_USER_IDS:
        await interaction.response.send_message("Kestrel 还不认识你.", ephemeral=True)
        return
    await interaction.response.send_message(
        "收到, 下线. 注意 Mac launchd KeepAlive 会自动拉起 — 真要永久关, terminal 跑 `launchctl unload ~/Library/LaunchAgents/com.kestrel.bot.plist`.",
        ephemeral=True,
    )
    log.info("Shutdown requested by user %s", interaction.user.id)
    async def _exit_soon():
        await asyncio.sleep(1.0)
        os._exit(0)
    asyncio.create_task(_exit_soon())


async def _do_reset(user_id: int, channel) -> bool:
    """Shared reset logic between text and slash commands."""
    sessions = load_sessions()
    key = get_session_key(channel)
    removed = sessions.pop(key, None)
    save_sessions(sessions)
    log.info("Reset session key=%s (removed=%s by user %s) via slash", key, bool(removed), user_id)
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
    bot_id = client.user.id if client.user else 0

    def _mentioned(msg: discord.Message) -> bool:
        if client.user in msg.mentions:
            return True
        if any(r in msg.role_mentions for r in bot_roles):
            return True
        if msg.reference is not None:
            resolved = msg.reference.resolved
            if resolved is not None and hasattr(resolved, "author"):
                if resolved.author is not None and resolved.author.id == bot_id:
                    return True
        if bot_id and (f"<@{bot_id}>" in msg.content or f"<@!{bot_id}>" in msg.content):
            return True
        return False

    if _mentioned(before):
        return  # 已经在 before 里处理过了
    if not _mentioned(after):
        return  # edit 后仍未 @, 忽略
    log.info(
        "[edit] reprocessing msg %s by %s (mention added after edit)",
        after.id, after.author.id,
    )
    async with _processed_msg_lock:
        _processed_msg_ids.discard(after.id)
    await handle_message(after)


if __name__ == "__main__":
    log.info("Starting KestrelBot (host=%s), cwd=%s", sys.platform, KESTREL_CWD)
    client.run(DISCORD_TOKEN, log_handler=None)
