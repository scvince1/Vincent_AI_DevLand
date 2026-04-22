#!/usr/bin/env python3
"""
diff_indexes.py — 对比 scan_report.json vs 实际三张 Index, 输出 diff。

用法: python diff_indexes.py scan_report.json > diff_report.md
"""
import sys
import json
import re
from pathlib import Path

KB_ROOT = Path(r"D:\Ai_Project\MeowOS\80_Knowledge")


def extract_index_ids(index_path):
    """提取 Index 表格中所有 id 列的值"""
    if not index_path.exists():
        return set()
    text = index_path.read_text(encoding="utf-8", errors="replace")
    ids = set()
    for line in text.split("\n"):
        if line.startswith("|") and "|" in line[1:]:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells and cells[0] and cells[0] not in ("id", "---", "ID"):
                ids.add(cells[0])
    return ids


def main():
    scan_path = sys.argv[1] if len(sys.argv) > 1 else "scan_report.json"
    with open(scan_path, encoding="utf-8") as f:
        scan = json.load(f)

    print("# Index Diff Report\n")
    print(f"- Total files scanned: {scan['scanned_files']}")
    print(f"- Skipped (meta/log): {len(scan['skipped'])}")
    print(f"- No frontmatter: {len(scan['no_frontmatter'])}")
    print(f"- Unrouted: {len(scan['unrouted'])}\n")

    for index_name in ("Entity_Index", "Knowledge_Index", "Meta_Index"):
        print(f"## {index_name}\n")
        index_ids = extract_index_ids(KB_ROOT / f"{index_name}.md")
        scan_entries = scan["by_target_index"][index_name]
        scan_ids = {e["id"] for e in scan_entries if e["id"]}

        missing = [e for e in scan_entries if e["id"] and e["id"] not in index_ids]
        stale = index_ids - scan_ids
        no_id = [e for e in scan_entries if not e["id"]]
        incomplete = [e for e in scan_entries if e["missing_fields"]]

        print(f"- Index registered: {len(index_ids)}")
        print(f"- KB files routed here: {len(scan_entries)}")
        print(f"- **MISSING** (file exists, index absent): {len(missing)}")
        for e in missing:
            print(f"  - `{e['path']}` — id=`{e['id']}` — {e.get('title', '')}")
        print(f"- **STALE** (index has id, no matching file): {len(stale)}")
        for sid in sorted(stale):
            print(f"  - `{sid}`")
        print(f"- **NO_ID** (file has frontmatter but no id field): {len(no_id)}")
        for e in no_id:
            print(f"  - `{e['path']}`")
        print(f"- **INCOMPLETE** (missing required fields): {len(incomplete)}")
        for e in incomplete:
            print(f"  - `{e['path']}` missing: {e['missing_fields']}")
        print()

    print("## Files with no frontmatter\n")
    for e in scan["no_frontmatter"]:
        print(f"- `{e['path']}` (expected target: {e['target_index']})")

    print("\n## Unrouted files\n")
    for p in scan["unrouted"]:
        print(f"- `{p}`")

    # === Own registry section ===
    own = scan.get("own_registry", {})
    if own.get("exists"):
        print("\n## 88_Research Own Registry\n")
        print(f"- Declared concepts: {len(own['declared_concepts'])}")
        print(f"- Actual concept dirs: {len(own['actual_concept_dirs'])}")
        print(f"- **MISSING** (dir exists, registry absent): {len(own['missing_in_registry'])}")
        for c in own['missing_in_registry']:
            print(f"  - `{c}`")
        print(f"- **STALE** (registry has, dir absent): {len(own['stale_in_registry'])}")
        for c in own['stale_in_registry']:
            print(f"  - `{c}`")

    # === ID uniqueness check ===
    print("\n## ID Uniqueness Check\n")
    all_ids = {}
    for index_name, entries in scan["by_target_index"].items():
        for e in entries:
            if e["id"]:
                all_ids.setdefault(e["id"], []).append(e["path"])
    collisions = {k: v for k, v in all_ids.items() if len(v) > 1}
    if collisions:
        print(f"- **{len(collisions)} ID collisions detected**:")
        for id_val, paths in sorted(collisions.items()):
            print(f"  - `{id_val}` in {len(paths)} files:")
            for p in paths:
                print(f"    - {p}")
    else:
        print("- No ID collisions")

    # === Ghost reference detection ===
    print("\n## Ghost Reference Detection\n")
    # 构建所有现有文件路径的集合（相对 KB_ROOT）
    existing_paths = set()
    existing_ids = set()
    for entries in scan["by_target_index"].values():
        for e in entries:
            existing_paths.add(e["path"])
            if e["id"]:
                existing_ids.add(e["id"])

    ghost_refs = []
    for entries in scan["by_target_index"].values():
        for e in entries:
            for ref in e.get("related", []):
                # 尝试按 path 解析
                path_resolved = any(ref in p or p.endswith(ref) for p in existing_paths)
                # 尝试按 id 解析
                id_resolved = ref in existing_ids
                if not path_resolved and not id_resolved:
                    ghost_refs.append({"source": e["path"], "ref": ref})

    print(f"- Total ghost references: {len(ghost_refs)}")
    if ghost_refs:
        # 按 source 分组
        by_source = {}
        for g in ghost_refs:
            by_source.setdefault(g["source"], []).append(g["ref"])
        for source, refs in sorted(by_source.items()):
            print(f"  - `{source}`:")
            for r in refs:
                print(f"    - `{r}`")
    else:
        print("- No ghost references")


if __name__ == "__main__":
    main()
