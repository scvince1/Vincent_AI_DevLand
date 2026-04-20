"""Update manifest last_processed_at after pipeline completion.

Usage:
    python update_watermark.py --project MeowOS
    python update_watermark.py --project MeowOS --timestamp 2026-04-08T23:54:00+00:00
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path

MEOWOS_ROOT = Path(r"D:\Ai_Project\MeowOS")
DIGEST_ROOT = MEOWOS_ROOT / "80_Knowledge" / "86_AI_Systems" / "Session_Digests"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--timestamp", default=None, help="ISO 8601 timestamp, defaults to now")
    args = ap.parse_args()

    ts = args.timestamp or datetime.now(timezone.utc).isoformat(timespec="seconds")

    manifest_path = DIGEST_ROOT / args.project / "manifest.md"
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}")
        return 1

    text = manifest_path.read_text(encoding="utf-8")
    new_lines = []
    replaced = False
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("last_processed_at:") and not replaced:
            new_lines.append(f"last_processed_at: {ts}\n")
            replaced = True
        else:
            new_lines.append(line)

    manifest_path.write_text("".join(new_lines), encoding="utf-8")
    print(f"Watermark updated: {args.project} -> {ts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
