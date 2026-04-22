"""worldbook.py — MeowOS keyword-triggered context injection + relation layer

Dependencies:
    pip install PyYAML>=6.0.2 claude-agent-sdk>=0.1.64

Usage (scanning with owner filter):
    wb = Worldbook(knowledge_root=..., owner="lingmiao")

Usage (relation MCP):
    relation_mcp = create_relation_mcp_server(
        owner="lingmiao",
        relations_dir=DEVLAND_80K / "85_System" / "relations",
    )
"""

from __future__ import annotations

import datetime
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError as e:
    raise RuntimeError("worldbook.py requires PyYAML. pip install PyYAML>=6.0.2") from e

try:
    from claude_agent_sdk import tool, create_sdk_mcp_server
except ImportError:
    tool = None
    create_sdk_mcp_server = None

log = logging.getLogger("worldbook")

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SKIP_NAMES = {"_staging.md"}
SKIP_DIR_NAMES = {"_inbox", "_templates", "Done", "00_Dump"}


@dataclass
class LoreEntry:
    path: Path
    title: str
    keys: list[str]
    summary: Optional[str] = None
    order: int = 100
    status: str = "confirmed"
    private_to: Optional[str] = None
    sticky: bool = False

    def load_content(self) -> str:
        if self.summary:
            return self.summary.strip()
        try:
            text = self.path.read_text(encoding="utf-8")
        except OSError as e:
            log.warning("Failed to read %s: %s", self.path, e)
            return ""
        m = FRONTMATTER_RE.match(text)
        if m:
            text = text[m.end():]
        return text.strip()


def parse_frontmatter(text: str) -> Optional[dict]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        log.warning("YAML parse error: %s", e)
        return None
    return data if isinstance(data, dict) else None


def should_skip(path: Path) -> bool:
    if path.name in SKIP_NAMES:
        return True
    parts = set(path.parts)
    return bool(parts & SKIP_DIR_NAMES)


def approx_tokens(text: str) -> int:
    return max(1, len(text) // 2)


class Worldbook:
    def __init__(
        self,
        knowledge_root: Path,
        extra_roots: Optional[list[Path]] = None,
        owner: Optional[str] = None,
    ):
        self.roots: list[Path] = [knowledge_root]
        if extra_roots:
            self.roots.extend(extra_roots)
        self.owner = owner
        self.entries: list[LoreEntry] = []
        self.build_index()

    def build_index(self) -> None:
        self.entries.clear()
        for root in self.roots:
            if not root.exists():
                log.warning("Worldbook root does not exist: %s", root)
                continue
            for md_path in root.rglob("*.md"):
                if should_skip(md_path):
                    continue
                try:
                    text = md_path.read_text(encoding="utf-8")
                except OSError:
                    continue
                fm = parse_frontmatter(text)
                if not fm:
                    continue
                keys = fm.get("worldbook_keys", [])
                if not isinstance(keys, list):
                    keys = []
                clean_keys = [str(k).strip() for k in keys if str(k).strip()]

                is_sticky = bool(fm.get("worldbook_sticky", False))

                # Entry must have keys (for scan) OR be sticky (always-on)
                if not clean_keys and not is_sticky:
                    continue

                # Private filter: private_to-scoped entries only visible to matching bot.
                # (Field name is private_to to avoid collision with file's human owner
                # field, e.g. pet profile has owner: Vincent for human caretaker.)
                entry_private_to = fm.get("private_to")
                if entry_private_to is not None and entry_private_to != self.owner:
                    continue

                entry = LoreEntry(
                    path=md_path,
                    title=str(fm.get("title", md_path.stem)),
                    keys=clean_keys,
                    summary=fm.get("worldbook_summary"),
                    order=int(fm.get("worldbook_order", 100)),
                    status=str(fm.get("status", "confirmed")),
                    private_to=entry_private_to,
                    sticky=is_sticky,
                )
                self.entries.append(entry)
        log.info(
            "Worldbook index built: %d entries from %d root(s), owner=%r",
            len(self.entries), len(self.roots), self.owner,
        )

    def match_entry(self, text: str, entry: LoreEntry) -> bool:
        text_lower = text.lower()
        for key in entry.keys:
            k = key.lower()
            if k.isascii():
                if re.search(rf"\b{re.escape(k)}\b", text_lower):
                    return True
            else:
                if k in text_lower:
                    return True
        return False

    def _effective_order(self, entry: LoreEntry) -> int:
        if entry.status == "deprecated":
            return -9999
        if entry.status == "stale":
            return entry.order - 100
        return entry.order

    def scan(self, text: str, budget_tokens: int = 800) -> str:
        if not self.entries or not text:
            return ""
        hits = [e for e in self.entries if self.match_entry(text, e)]
        if not hits:
            return ""
        hits.sort(key=lambda e: -self._effective_order(e))
        used = 0
        blocks: list[str] = []
        for entry in hits:
            if entry.status == "deprecated":
                continue
            content = entry.load_content()
            if not content:
                continue
            tokens = approx_tokens(content)
            if used + tokens > budget_tokens:
                continue
            used += tokens
            blocks.append(f"### {entry.title}\n{content}")
        if not blocks:
            return ""
        header = (
            "<worldbook>\nContext relevant to the current message, injected from "
            "MeowOS knowledge base. Use as background; do not recap these entries "
            "verbatim unless asked.\n\n"
        )
        return header + "\n\n---\n\n".join(blocks) + "\n</worldbook>\n"

    def dump_all(self, budget_tokens: int = 1500) -> str:
        if not self.entries:
            return ""
        entries = [e for e in self.entries if e.status != "deprecated"]
        if not entries:
            return ""
        entries.sort(key=lambda e: -self._effective_order(e))
        used = 0
        blocks: list[str] = []
        for entry in entries:
            content = entry.load_content()
            if not content:
                continue
            tokens = approx_tokens(content)
            if used + tokens > budget_tokens:
                continue
            used += tokens
            blocks.append(f"### {entry.title}\n{content}")
        if not blocks:
            return ""
        header = (
            "<worldbook>\nCore entities in MeowOS knowledge base (full roster "
            "injected for context-free flows like diary / proactive ping). "
            "Use these facts.\n\n"
        )
        return header + "\n\n---\n\n".join(blocks) + "\n</worldbook>\n"

    def dump_sticky(self, budget_tokens: int = 500) -> str:
        """Return sticky entries (worldbook_sticky: true) as always-on injection
        block. Used for Discord-shared protocols/rules that must appear in every
        prompt regardless of keyword match."""
        if not self.entries:
            return ""
        sticky_entries = [
            e for e in self.entries if e.sticky and e.status != "deprecated"
        ]
        if not sticky_entries:
            return ""
        sticky_entries.sort(key=lambda e: -self._effective_order(e))
        used = 0
        blocks: list[str] = []
        for entry in sticky_entries:
            content = entry.load_content()
            if not content:
                continue
            tokens = approx_tokens(content)
            if used + tokens > budget_tokens:
                continue
            used += tokens
            blocks.append(f"### {entry.title}\n{content}")
        if not blocks:
            return ""
        header = (
            "<worldbook_sticky>\n"
            "Always-on shared protocols/rules. Apply these in every Discord "
            "interaction.\n\n"
        )
        return header + "\n\n---\n\n".join(blocks) + "\n</worldbook_sticky>\n"

    def __repr__(self) -> str:
        return (
            f"<Worldbook entries={len(self.entries)} "
            f"roots={len(self.roots)} owner={self.owner!r}>"
        )


# ---------------------------------------------------------------------------
# Relation layer: bot-to-bot relation log MCP tools
# ---------------------------------------------------------------------------

H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
H3_RE = re.compile(r"^###\s+", re.MULTILINE)
B_HEADER_RE = re.compile(r"^###\s+当前\s*\(B\)\s*$", re.MULTILINE)
E_HEADER_RE = re.compile(r"^###\s+最近.*?$", re.MULTILINE)


def _split_body_into_peer_sections(body: str):
    matches = list(H2_RE.finditer(body))
    if not matches:
        return body, []
    preamble = body[:matches[0].start()]
    sections = []
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections.append((name, body[start:end]))
    return preamble, sections


def _join_peer_sections(preamble: str, sections: list) -> str:
    return preamble + "".join(s for _, s in sections)


def _modify_e_subsection(section: str, observation: str, max_entries: int = 10) -> str:
    m = E_HEADER_RE.search(section)
    if not m:
        return section
    after = section[m.end():]
    next_m = H3_RE.search(after)
    if next_m:
        e_body = after[:next_m.start()]
        rest = after[next_m.start():]
    else:
        e_body = after
        rest = ""
    lines = [l.rstrip() for l in e_body.strip().split("\n")]
    obs_lines = [l for l in lines if l.strip().startswith("-") and "(empty)" not in l]
    today = datetime.date.today().isoformat()
    obs_lines.append(f"- {today} {observation}")
    obs_lines = obs_lines[-max_entries:]
    new_e_body = "\n" + "\n".join(obs_lines) + "\n"
    if rest:
        new_e_body += "\n"
    return section[:m.end()] + new_e_body + rest


def _modify_b_subsection(section: str, new_state: str) -> str:
    m = B_HEADER_RE.search(section)
    if not m:
        return section
    after = section[m.end():]
    next_m = H3_RE.search(after)
    rest = after[next_m.start():] if next_m else ""
    return section[:m.end()] + "\n" + new_state.strip() + "\n\n" + rest


def _modify_peers_file(file_path: Path, peer_name: str, op: str, content: str) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"Peers file not found: {file_path}")
    raw = file_path.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\s*\n.*?\n---\s*\n", raw, re.DOTALL)
    if fm_match:
        frontmatter = fm_match.group(0)
        body = raw[fm_match.end():]
    else:
        frontmatter = ""
        body = raw
    preamble, sections = _split_body_into_peer_sections(body)
    target_idx = None
    for i, (name, _sec) in enumerate(sections):
        if name.lower() == peer_name.lower():
            target_idx = i
            break
    if target_idx is None:
        raise ValueError(
            f"Peer section '{peer_name}' not found in {file_path.name}. "
            f"Available: {[n for n, _ in sections]}"
        )
    peer_section_name, peer_section = sections[target_idx]
    if op == "append_e":
        peer_section = _modify_e_subsection(peer_section, content)
    elif op == "replace_b":
        peer_section = _modify_b_subsection(peer_section, content)
    else:
        raise ValueError(f"Unknown op: {op}")
    sections[target_idx] = (peer_section_name, peer_section)
    file_path.write_text(frontmatter + _join_peer_sections(preamble, sections), encoding="utf-8")
    return f"{op} applied to peer '{peer_section_name}' in {file_path.name}"


def create_relation_mcp_server(owner: str, relations_dir: Path):
    """Factory: MCP server bound to <owner>_peers.md under relations_dir.
    Exposes append_to_relation_log and update_relation_snapshot tools."""
    if tool is None or create_sdk_mcp_server is None:
        raise RuntimeError("claude_agent_sdk not available")

    peers_file = relations_dir / f"{owner}_peers.md"

    @tool(
        "append_to_relation_log",
        ("Append a short observation (<200 chars) about a peer bot to your "
         "private relation log. Use sparingly — only when you notice something "
         "worth remembering about how a peer is doing or how you two just "
         "interacted. Auto-timestamped. Auto-trimmed to last 10 per peer. "
         "peer_name must be english slug: lingmiao / ailyin / beichen / kestrel."),
        {"peer_name": str, "observation": str},
    )
    async def append_to_relation_log(args):
        peer = args["peer_name"].strip()
        obs = args["observation"].strip()
        if len(obs) > 200:
            obs = obs[:200] + "…"
        if not obs:
            return {"content": [{"type": "text", "text": "empty observation"}]}
        try:
            msg = _modify_peers_file(peers_file, peer, "append_e", obs)
        except (FileNotFoundError, ValueError) as e:
            return {"content": [{"type": "text", "text": f"error: {e}"}]}
        return {"content": [{"type": "text", "text": msg}]}

    @tool(
        "update_relation_snapshot",
        ("Replace the current relation snapshot (B subsection) for a peer with "
         "a new 1-2 sentence summary. Use at a clear turning point or when a "
         "new pattern has stabilized. peer_name must be english slug."),
        {"peer_name": str, "new_state": str},
    )
    async def update_relation_snapshot(args):
        peer = args["peer_name"].strip()
        new_state = args["new_state"].strip()
        if not new_state:
            return {"content": [{"type": "text", "text": "empty new_state"}]}
        try:
            msg = _modify_peers_file(peers_file, peer, "replace_b", new_state)
        except (FileNotFoundError, ValueError) as e:
            return {"content": [{"type": "text", "text": f"error: {e}"}]}
        return {"content": [{"type": "text", "text": msg}]}

    return create_sdk_mcp_server(
        name="relation",
        version="1.0",
        tools=[append_to_relation_log, update_relation_snapshot],
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _self_test() -> int:
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    root = Path(r"D:\Ai_Project\Vincent_AI_DevLand\80_Knowledge")

    wb_pub = Worldbook(knowledge_root=root, owner=None)
    print(f"\nPublic view: {wb_pub}")
    for e in wb_pub.entries:
        print(f"  - {e.title:30s} private_to={e.private_to!r} keys={e.keys}")

    wb_ling = Worldbook(knowledge_root=root, owner="lingmiao")
    print(f"\nLingmiao view: {wb_ling}")
    private_visible = [e for e in wb_ling.entries if e.private_to == "lingmiao"]
    print(f"  private entries visible: {len(private_visible)}")
    for e in private_visible:
        print(f"    - {e.title} (private_to={e.private_to})")

    wb_elly = Worldbook(knowledge_root=root, owner="elly")
    print(f"\nElly view: {wb_elly}")
    elly_private = [e for e in wb_elly.entries if e.private_to == "elly"]
    print(f"  private entries visible: {len(elly_private)}")
    assert not any(e.private_to == "lingmiao" for e in wb_elly.entries), \
        "BUG: elly view should NOT see lingmiao private entries"
    print("  ✓ elly cannot see lingmiao private entries (private_to filter works)")

    probe = "Joyce 今天忙吗" if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    print(f"\nScan probe (lingmiao view): {probe!r}")
    out = wb_ling.scan(probe, budget_tokens=800)
    print(f"  hit length: {len(out)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(_self_test())
