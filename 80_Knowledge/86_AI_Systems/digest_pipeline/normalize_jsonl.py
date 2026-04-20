"""Claude Code JSONL normalizer v3.

Extracts pure conversation text from Claude Code session .jsonl files,
dropping tool calls, tool results, timestamps, uuids, and other metadata.
v2: replaces fenced code blocks with a placeholder to save tokens.
v3: strips system injections from user turns, filters intermediate assistant turns.

Usage:
    python normalize_jsonl.py <input.jsonl>              # single file -> <input>.txt
    python normalize_jsonl.py <input.jsonl> <output.txt> # single file, explicit output
    python normalize_jsonl.py <folder>                   # batch: all *.jsonl in folder
    python normalize_jsonl.py <folder> <out_folder>      # batch with output folder
"""
import json
import re
import sys
from pathlib import Path


USER_LABEL = "═══ Vincent ═══"
ASSISTANT_LABEL = "═══ 凌喵 ═══"

CODE_BLOCK_RE = re.compile(
    r"```([a-zA-Z0-9_+\-]*)\n(.*?)```",
    re.DOTALL,
)

# --- v3: system injection patterns to strip from user turns ---
SYSTEM_TAG_PATTERNS = [
    re.compile(r"<ide_opened_file>.*?</ide_opened_file>", re.DOTALL),
    re.compile(r"<ide_selection>.*?</ide_selection>", re.DOTALL),
    re.compile(r"<task-notification>.*?</task-notification>", re.DOTALL),
    re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL),
    re.compile(r"<local-command-caveat>.*?</local-command-caveat>", re.DOTALL),
    re.compile(r"<command-name>.*?</command-name>", re.DOTALL),
    re.compile(r"<command-message>.*?</command-message>", re.DOTALL),
]

# User turns matching these patterns are dropped entirely
DROP_USER_TURN_PATTERNS = [
    re.compile(r"^\s*Base directory for this skill:", re.MULTILINE),
    re.compile(r"^\s*\[Request interrupted by user\]\s*$"),
]

# System error lines to strip from assistant turns
SYSTEM_NOISE_LINES = [
    "Credit balance is too low",
]


def strip_code_blocks(text: str) -> str:
    """Replace fenced code blocks with a short placeholder."""
    def replace(match):
        lang = match.group(1) or "unknown"
        body = match.group(2)
        line_count = body.count("\n")
        if body and not body.endswith("\n"):
            line_count += 1
        return f"<code block: {line_count} lines of {lang}, 省略>"

    return CODE_BLOCK_RE.sub(replace, text)


def strip_system_injections(text: str) -> str:
    """Remove system-injected XML tags from user turn text."""
    for pattern in SYSTEM_TAG_PATTERNS:
        text = pattern.sub("", text)
    return text.strip()


def should_drop_user_turn(text: str) -> bool:
    """Check if an entire user turn should be discarded."""
    for pattern in DROP_USER_TURN_PATTERNS:
        if pattern.search(text):
            return True
    return False


def strip_system_noise(text: str) -> str:
    """Remove known system noise lines from assistant turns."""
    lines = text.split("\n")
    filtered = [ln for ln in lines if ln.strip() not in SYSTEM_NOISE_LINES]
    return "\n".join(filtered).strip()


def content_line_count(text: str) -> int:
    """Count non-empty lines in text."""
    return sum(1 for ln in text.split("\n") if ln.strip())


def filter_intermediate_assistant_turns(turns: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Remove short intermediate assistant turns from consecutive assistant sequences.

    In a run of consecutive assistant turns (no user turn in between):
    - Keep turns with > 3 non-empty content lines
    - Keep the last turn in the run (even if short)
    - Drop short turns (<=3 lines) that are followed by another assistant turn
    """
    result = []
    n = len(turns)
    for i, (role, text) in enumerate(turns):
        if role != "assistant":
            result.append((role, text))
            continue

        # Check if next turn is also assistant
        next_is_assistant = (i + 1 < n) and (turns[i + 1][0] == "assistant")

        if next_is_assistant and content_line_count(text) <= 3:
            # Short intermediate turn followed by another assistant turn -> drop
            continue

        result.append((role, text))

    return result


def normalize_jsonl(jsonl_path: Path):
    lines_total = 0
    turns = []

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            lines_total += 1
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = entry.get("type")
            if msg_type not in ("user", "human", "assistant"):
                continue

            message = entry.get("message") or {}
            content = message.get("content")

            text_parts = []
            if isinstance(content, str):
                text_parts.append(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))

            text = "\n".join(t for t in text_parts if t).strip()
            if not text:
                continue

            text = strip_code_blocks(text)

            role = "user" if msg_type in ("user", "human") else "assistant"

            # --- v3: clean up turns ---
            if role == "user":
                # Check if entire turn should be dropped before stripping
                if should_drop_user_turn(text):
                    continue
                text = strip_system_injections(text)
                if not text:
                    continue
            else:
                text = strip_system_noise(text)
                if not text:
                    continue

            turns.append((role, text))

    # --- v3: filter intermediate assistant turns ---
    turns = filter_intermediate_assistant_turns(turns)

    out_lines = []
    for role, text in turns:
        label = USER_LABEL if role == "user" else ASSISTANT_LABEL
        out_lines.append(label)
        out_lines.append("")
        out_lines.append(text)
        out_lines.append("")

    output = "\n".join(out_lines).rstrip() + "\n"

    stats = {
        "original_bytes": jsonl_path.stat().st_size,
        "lines_total": lines_total,
        "turns": len(turns),
        "output_bytes": len(output.encode("utf-8")),
        "output_chars": len(output),
    }
    return output, stats


def process_one(in_path: Path, out_path: Path) -> dict:
    output, stats = normalize_jsonl(in_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")
    stats["input"] = str(in_path)
    stats["output"] = str(out_path)
    return stats


def print_stats(stats: dict):
    ratio = stats["output_bytes"] / stats["original_bytes"] if stats["original_bytes"] else 0
    name = Path(stats["input"]).name
    print(f"  {name}: {stats['original_bytes']:>10,} -> {stats['output_bytes']:>9,} bytes  ({ratio:5.1%})  {stats['turns']} turns  {stats['output_chars']:>7,} chars")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    in_arg = Path(sys.argv[1])
    out_arg = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not in_arg.exists():
        print(f"Error: {in_arg} does not exist")
        sys.exit(1)

    if in_arg.is_file():
        out_path = out_arg if out_arg else in_arg.with_suffix(".txt")
        stats = process_one(in_arg, out_path)
        print_stats(stats)
        return

    jsonls = sorted(in_arg.glob("*.jsonl"))
    if not jsonls:
        print(f"No .jsonl files found in {in_arg}")
        sys.exit(1)

    out_dir = out_arg if out_arg else in_arg / "normalized"
    print(f"Processing {len(jsonls)} files from {in_arg}")
    print(f"Output dir: {out_dir}\n")

    total_in = 0
    total_out = 0
    total_turns = 0
    for jsonl in jsonls:
        out_path = out_dir / (jsonl.stem + ".txt")
        try:
            stats = process_one(jsonl, out_path)
            print_stats(stats)
            total_in += stats["original_bytes"]
            total_out += stats["output_bytes"]
            total_turns += stats["turns"]
        except Exception as e:
            print(f"  {jsonl.name}: ERROR - {e}")

    ratio = total_out / total_in if total_in else 0
    print(f"\nTotal: {total_in:,} -> {total_out:,} bytes  ({ratio:.1%})  {total_turns} turns across {len(jsonls)} files")


if __name__ == "__main__":
    main()
