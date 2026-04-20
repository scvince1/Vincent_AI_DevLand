"""Scan Claude Code project session directory and update manifest.

For each .jsonl file with mtime > last_processed_at and not already in manifest:
  1. Normalize to text (via normalize_jsonl)
  2. Measure character count
  3. Classify as 'fragment' (<1500 chars) or 'pending' (>=1500 chars)
  4. Add row to manifest

Does NOT update last_processed_at — that's update_watermark.py's job,
called AFTER Pass 1/2/3 complete successfully.

Usage:
    python manifest_scan.py --project MeowOS
"""
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from normalize_jsonl import normalize_jsonl

FRAGMENT_THRESHOLD_CHARS = 1500

MEOWOS_ROOT = Path(r"D:\Ai_Project\MeowOS")
CLAUDE_PROJECTS = {
    "MeowOS": Path(r"C:\Users\scvin\.claude\projects\d--Ai-Project-MeowOS"),
}
NORMALIZED_DIR = MEOWOS_ROOT / "99_MyFiles" / "Normalized_Session_History"
DIGEST_ROOT = MEOWOS_ROOT / "80_Knowledge" / "86_AI_Systems" / "Session_Digests"


def read_manifest_watermark(manifest_path: Path) -> datetime:
    if not manifest_path.exists():
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    text = manifest_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("last_processed_at:"):
            value = line.split(":", 1)[1].strip()
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return datetime(1970, 1, 1, tzinfo=timezone.utc)
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def ensure_manifest_header(manifest_path: Path, project: str):
    if manifest_path.exists():
        return
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    content = f"""---
project: {project}
last_processed_at: 1970-01-01T00:00:00+00:00
---

# {project} Session Digest Manifest

本文件由 `manifest_scan.py` 和 `update_watermark.py` 维护。不要手动编辑除了 `Notes` 列以外的字段。

| Session UUID | Date | Chars | Status | Pass 1 | Pass 2 Batch | Notes |
|---|---|---|---|---|---|---|
"""
    manifest_path.write_text(content, encoding="utf-8")


def existing_session_ids(manifest_path: Path) -> set:
    ids = set()
    if not manifest_path.exists():
        return ids
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("|") and "Session UUID" not in line and "---" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if parts and parts[0]:
                ids.add(parts[0])
    return ids


def append_manifest_row(manifest_path: Path, row: dict):
    existing = manifest_path.read_text(encoding="utf-8")
    if not existing.endswith("\n"):
        existing += "\n"
    new_line = f"| {row['uuid']} | {row['date']} | {row['chars']:,} | {row['status']} | {row['pass1']} | {row['pass2_batch']} | {row.get('notes', '')} |\n"
    manifest_path.write_text(existing + new_line, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, choices=list(CLAUDE_PROJECTS.keys()))
    args = ap.parse_args()

    project = args.project
    jsonl_dir = CLAUDE_PROJECTS[project]
    manifest_path = DIGEST_ROOT / project / "manifest.md"

    ensure_manifest_header(manifest_path, project)
    watermark = read_manifest_watermark(manifest_path)
    seen_ids = existing_session_ids(manifest_path)

    jsonls = sorted(jsonl_dir.glob("*.jsonl"))
    pending = []
    fragment_count = 0
    skipped_count = 0

    for jsonl in jsonls:
        uuid = jsonl.stem
        if uuid in seen_ids:
            skipped_count += 1
            continue
        mtime = datetime.fromtimestamp(jsonl.stat().st_mtime, tz=timezone.utc)
        if mtime <= watermark:
            skipped_count += 1
            continue

        txt_path = NORMALIZED_DIR / f"{uuid}.txt"
        try:
            output, stats = normalize_jsonl(jsonl)
            txt_path.parent.mkdir(parents=True, exist_ok=True)
            txt_path.write_text(output, encoding="utf-8")
        except Exception as e:
            print(f"ERROR normalizing {uuid}: {e}", file=sys.stderr)
            continue

        chars = stats["output_chars"]
        status = "fragment" if chars < FRAGMENT_THRESHOLD_CHARS else "pending"

        row = {
            "uuid": uuid,
            "date": mtime.strftime("%Y-%m-%d"),
            "chars": chars,
            "status": status,
            "pass1": "-",
            "pass2_batch": "-",
            "notes": "",
        }
        append_manifest_row(manifest_path, row)

        if status == "fragment":
            fragment_count += 1
        else:
            pending.append(uuid)

    print(f"Scanned: {len(jsonls)} jsonl files")
    print(f"Already processed (skipped): {skipped_count}")
    print(f"Fragments (auto-archived): {fragment_count}")
    print(f"Pending Pass 1: {len(pending)}")
    if pending:
        print("\nPending UUIDs:")
        for uuid in pending:
            print(f"  {uuid}")


if __name__ == "__main__":
    main()
