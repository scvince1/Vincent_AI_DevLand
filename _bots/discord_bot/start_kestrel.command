#!/bin/bash
# Kestrel bot Mac launcher (manual start).
# chmod +x this file, then double-click in Finder or run:  ./start_kestrel.command
set -e

cd "$(dirname "$0")"

# Load .env (exports are optional; read via python-dotenv inside bot.py)
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

# Python binary (overridable via .env PYTHON_BIN)
PY="${PYTHON_BIN:-/usr/local/bin/python3}"

echo "[Kestrel] Starting bot.py with $PY ..."
exec "$PY" bot.py
