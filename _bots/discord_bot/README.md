# Kestrel Discord Bot

Mac-side remote proxy bot for Vincent. Kestrel lets you dispatch tasks to
the PC-side persona bots (凌喵 / 艾莉 / 北辰) from your Mac via Discord,
without starting a new Claude Code session manually.

Kestrel's persona is intentionally thin — she acknowledges quickly, then
routes complex work to the appropriate PC bot.

## Architecture

- Runs on Mac (primary) or any Unix / Windows host
- Uses `claude_agent_sdk` to spawn Claude subprocesses per trigger
- Discord MCP server exposes 9 tools (DM / send / react / history / edit / delete / thread / pin / presence)
- Platform-specific subprocess patching is guarded (`sys.platform == "win32"`)
- No diary / no changelog / no Google MCP (proxy role is lean)

## Mac deployment

1. Clone / pull the repo on Mac:
   ```
   git clone https://github.com/scvince1/Vincent_AI_DevLand.git
   cd Vincent_AI_DevLand
   # or, if already cloned:
   git pull
   ```

2. Enter the bot directory:
   ```
   cd _bots/discord_bot
   ```

3. Create `.env` from template and fill in real values:
   ```
   cp .env.example .env
   nano .env   # or: open -e .env
   ```
   Required fields:
   - `DISCORD_TOKEN` — the Kestrel bot token (from Discord Developer Portal)
   - `USER_MAP` — Vincent's Discord ID (already pre-filled)
   - `KESTREL_CWD` — where the Claude Agent SDK should cwd into
     (default `/Users/scvin/`; you may want to change this once Mac-side
     knowledge base exists)
   - `PYTHON_BIN` — absolute path to Python 3.14+

4. Install Python dependencies:
   ```
   pip3 install -r requirements.txt
   ```
   If you hit permission errors, try `pip3 install --user -r requirements.txt`
   or use a venv.

5. Make launcher executable:
   ```
   chmod +x start_kestrel.command start_kestrel.sh
   ```

6. Start Kestrel:
   - Double-click `start_kestrel.command` in Finder, or
   - Run in terminal: `./start_kestrel.command`

   The command window will stream logs. Close it to stop the bot.

## Optional: macOS auto-start via launchd

To have Kestrel run on login, create
`~/Library/LaunchAgents/com.kestrel.bot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.kestrel.bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/scvin/Vincent_AI_DevLand/_bots/discord_bot/start_kestrel.command</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/scvin/Vincent_AI_DevLand/_bots/discord_bot</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key>
    <string>/Users/scvin/Vincent_AI_DevLand/_bots/discord_bot/bot.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/scvin/Vincent_AI_DevLand/_bots/discord_bot/bot.log</string>
</dict>
</plist>
```

Then:
```
launchctl load ~/Library/LaunchAgents/com.kestrel.bot.plist
launchctl list | grep kestrel
```

Unload when done:
```
launchctl unload ~/Library/LaunchAgents/com.kestrel.bot.plist
```

Adjust paths above to match the actual clone location.

## Checking bot status

```
# Is bot.py running?
ps aux | grep bot.py | grep -v grep

# Tail recent logs
tail -n 50 bot.log

# Kill a specific PID
kill <pid>
```

## Linux / headless use

Use `start_kestrel.sh` instead of `.command`. Same `.env` schema applies.
For systemd service setup, adapt the launchd plist above into a
`.service` unit.

## Windows (debug / dev only)

`start_kestrel.bat` is included for smoke testing on Vincent's PC.
Production runs on Mac; Windows path not maintained.

## Slash commands

Available once bot is running and registered with the guild:

| Command | Purpose |
|---|---|
| `/new` / `/reset` | Clear current session |
| `/restart` | Self-restart the bot process |
| `/model` | Override chat model (sonnet / opus / haiku / default) |
| `/lock` | Lock current channel (bot-only send) |
| `/unlock` | Unlock channel |

Text commands (works in DM or `@Kestrel`):
`/whoami`, `/status`, `/help`.

## Security

- `.env` is gitignored (root `.gitignore` + nested pattern); never commit it.
- The Discord token lives only in `.env` on each host — not in code,
  not in logs, not in this README.
- Bot code runs Claude Agent SDK with `permission_mode="acceptEdits"`;
  the host machine does see writes from Kestrel's SDK subprocess, so
  `KESTREL_CWD` should be set to a directory you're OK with edits.

## Troubleshooting

- **ModuleNotFoundError for discord / claude_agent_sdk** — run `pip3 install -r requirements.txt`.
- **Slash commands don't show up** — wait 1-2 minutes after first run
  (Discord global-sync delay). Check log for "Slash synced GLOBALLY".
- **Bot doesn't respond** — check Discord Developer Portal: `MESSAGE CONTENT INTENT` must be ON.
- **Token rejected** — double-check `.env` has no trailing whitespace / quotes.

## See also

- Top-level repo: `Vincent_AI_DevLand`
- Sibling PC bots:
  - `D:\Ai_Project\MeowOS\_bots\discord_bot\` (凌喵)
  - `D:\Ai_Project\Horsys\_bots\discord_bot\` (艾莉)
  - `D:\NovelOS\_bots\discord_bot\` (北辰, planned)
- Persona-bot architecture reference:
  `~/.claude/agents/persona-bot-engineer.md`
