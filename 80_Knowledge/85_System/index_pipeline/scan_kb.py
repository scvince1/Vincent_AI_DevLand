#!/usr/bin/env python3
"""
scan_kb.py — 扫描 80_Knowledge/ 全库，提取 frontmatter，按路由规则分类。

输出: JSON 到 stdout，结构:
{
  "scanned_files": N,
  "by_target_index": {
    "Entity_Index": [{"path": ..., "id": ..., "title": ..., "frontmatter_complete": bool, "missing_fields": [...]}],
    "Knowledge_Index": [...],
    "Meta_Index": [...]
  },
  "skipped": [{"path": ..., "reason": ...}],
  "no_frontmatter": [...]
}
"""
import os
import sys
import json
import re
from pathlib import Path

KB_ROOT = Path(r"D:\Ai_Project\MeowOS\80_Knowledge")

ROUTING = [
    # (path_prefix_regex, target_index)
    (r"^81_Identity/", "Entity_Index"),
    (r"^82_Projects/", "Entity_Index"),
    (r"^87_People/", "Entity_Index"),
    (r"^88_Plants/knowledge/", "Entity_Index"),
    (r"^82_Health/", "Knowledge_Index"),
    (r"^84_AI_Tech/", "Knowledge_Index"),
    (r"^84_Fitness/", "Knowledge_Index"),
    (r"^85_System/harness_engineering/", "Knowledge_Index"),
    (r"^88_Learned/", "Knowledge_Index"),
    (r"^88_Research/", "Knowledge_Index"),
    (r"^89_Business/", "Knowledge_Index"),
    (r"^83_Observations/", "Meta_Index"),
    (r"^85_System/dreamwalk/", "Meta_Index"),
    (r"^85_System/", "Meta_Index"),  # 非 harness 的 85_System
    (r"^86_AI_Systems/", "Meta_Index"),
    (r"^90_Deprecated/", "Meta_Index"),
]

REQUIRED_FIELDS = ["id", "title", "tags", "status", "last_modified"]

SKIP_FILENAMES = {
    "README.md", "80_Knowledge_frontmatter_schema.md",
    "Entity_Index.md", "Knowledge_Index.md", "Meta_Index.md",
}
SKIP_FILENAME_PATTERNS = [
    r"^_", r"log\.md$", r"daily-log\.md$", r"_log\.md$",
]


def should_skip(rel_path):
    name = Path(rel_path).name
    if name in SKIP_FILENAMES:
        return True, "meta_filename"
    for pat in SKIP_FILENAME_PATTERNS:
        if re.search(pat, name):
            return True, "skip_pattern"
    return False, None


def classify(rel_path):
    rp = rel_path.replace("\\", "/")
    for prefix_re, target in ROUTING:
        if re.match(prefix_re, rp):
            return target
    return None


def extract_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    block = m.group(1)
    fm = {}
    current_array_key = None
    current_array = []
    for line in block.split("\n"):
        if not line.strip():
            continue
        # multi-line array item
        if line.startswith("  - ") or line.startswith("- "):
            if current_array_key is not None:
                current_array.append(line.lstrip("- ").strip())
            continue
        # close previous array
        if current_array_key is not None and ":" in line:
            fm[current_array_key] = current_array
            current_array_key = None
            current_array = []
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip()
        v = v.strip()
        # inline array
        if v.startswith("[") and v.endswith("]"):
            items = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
            fm[k] = items
        # empty → maybe multi-line array follows
        elif not v:
            current_array_key = k
            current_array = []
        else:
            fm[k] = v.strip("'\"")
    # close any remaining array
    if current_array_key is not None:
        fm[current_array_key] = current_array
    return fm


def scan_own_registry():
    """扫描 88_Research/_registry.md 的 concept 登记情况 vs 实际目录"""
    registry_path = KB_ROOT / "88_Research" / "_registry.md"
    research_root = KB_ROOT / "88_Research"
    if not registry_path.exists():
        return {"exists": False}

    # 提取 registry 声明的 concept（从 table 行里取第一列）
    declared = set()
    text = registry_path.read_text(encoding="utf-8", errors="replace")
    for line in text.split("\n"):
        if line.startswith("| ") and "|" in line[2:]:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells and cells[0] and cells[0] not in ("Concept", "---", "---|"):
                # skip header/separator rows
                if not re.match(r"^-+$", cells[0]):
                    declared.add(cells[0])

    # 扫描实际 concept 目录
    actual_concepts = set()
    for item in research_root.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            actual_concepts.add(item.name)

    return {
        "exists": True,
        "declared_concepts": sorted(declared),
        "actual_concept_dirs": sorted(actual_concepts),
        "missing_in_registry": sorted(actual_concepts - declared),
        "stale_in_registry": sorted(declared - actual_concepts),
    }


def main():
    result = {
        "scanned_files": 0,
        "by_target_index": {"Entity_Index": [], "Knowledge_Index": [], "Meta_Index": []},
        "skipped": [],
        "no_frontmatter": [],
        "unrouted": [],
    }

    for md in KB_ROOT.rglob("*.md"):
        rel = md.relative_to(KB_ROOT).as_posix()
        result["scanned_files"] += 1

        skip, reason = should_skip(rel)
        if skip:
            result["skipped"].append({"path": rel, "reason": reason})
            continue

        target = classify(rel)
        if not target:
            result["unrouted"].append(rel)
            continue

        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            result["skipped"].append({"path": rel, "reason": f"read_error: {e}"})
            continue

        fm = extract_frontmatter(text)
        if not fm:
            result["no_frontmatter"].append({"path": rel, "target_index": target})
            continue

        missing = [f for f in REQUIRED_FIELDS if f not in fm]
        entry = {
            "path": rel,
            "id": fm.get("id"),
            "title": fm.get("title"),
            "frontmatter_complete": len(missing) == 0,
            "missing_fields": missing,
            "related": fm.get("related", []) if isinstance(fm.get("related"), list) else [],
        }
        result["by_target_index"][target].append(entry)

    result["own_registry"] = scan_own_registry()

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
