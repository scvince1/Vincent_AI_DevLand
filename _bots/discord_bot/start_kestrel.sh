#!/bin/bash
# Kestrel bot Unix launcher (Linux / headless / ssh use).
# chmod +x this file, then run:  ./start_kestrel.sh
set -e

cd "$(dirname "$0")"

if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

PY="${PYTHON_BIN:-/usr/local/bin/python3}"

echo "[Kestrel] Starting bot.py with $PY ..."
exec "$PY" bot.py
