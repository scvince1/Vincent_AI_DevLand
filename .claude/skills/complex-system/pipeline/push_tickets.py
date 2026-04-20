#!/usr/bin/env python3
"""
push_tickets.py

Push ticket markdowns from a build repo to GitHub issues.

Usage:
    python push_tickets.py <build-repo-path> [--dry-run]

Behavior:
    Reads all ticket files under <build-repo-path>/04_tickets/*.md
    (skipping files starting with `_`). For each ticket:
      * If frontmatter issue_number is already set, skip (idempotent).
      * Otherwise, topologically sort by depends_on so blockers are created first.
      * Create GitHub issue via `gh issue create`:
          Title: [<ticket_id>] <title>
          Body:  ticket body (everything after the frontmatter, including `## Agent Prompt`)
                 plus auto-appended "**Blocked by**: #X, #Y" footer if deps have issue_numbers
          Labels: phase:<phase>, version:<version>
      * Write the returned issue number back into the ticket's frontmatter.

On failure, aborts; already-pushed tickets keep their issue_number so re-run is safe.

Cross-platform: uses only Python stdlib + `gh` CLI (must be on PATH).
No external dependencies.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse_frontmatter(text):
    """Minimal YAML frontmatter parser for our known schema.

    Returns (frontmatter_dict, body_str). Raises ValueError on malformed input.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("missing or malformed YAML frontmatter")
    fm_text, body = m.group(1), m.group(2)
    fm = {}
    lines = fm_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                items = []
                j = i + 1
                while j < len(lines) and lines[j].lstrip().startswith("- "):
                    items.append(lines[j].lstrip()[2:].strip())
                    j += 1
                if items:
                    fm[key] = items
                    i = j
                    continue
                else:
                    fm[key] = None
                    i += 1
                    continue
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                if inner == "":
                    fm[key] = []
                else:
                    fm[key] = [x.strip().strip('"').strip("'") for x in inner.split(",")]
                i += 1
                continue
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            if value.lower() in ("null", "~", ""):
                fm[key] = None
            elif value.isdigit():
                fm[key] = int(value)
            else:
                fm[key] = value
            i += 1
        else:
            i += 1
    return fm, body


def serialize_frontmatter(fm):
    """Serialize frontmatter dict back to YAML (compatible with parse_frontmatter)."""
    lines = []
    for key, value in fm.items():
        if value is None:
            lines.append(f"{key}: null")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif isinstance(value, int):
            lines.append(f"{key}: {value}")
        elif isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
        else:
            s = str(value)
            if any(c in s for c in ":#[]{}|>*&!%@`,'\"") or s.strip() != s:
                s = '"' + s.replace('"', '\\"') + '"'
            lines.append(f"{key}: {s}")
    return "\n".join(lines)


def rewrite_ticket_with_issue_number(path, fm, body, issue_number):
    fm["issue_number"] = int(issue_number)
    new_text = "---\n" + serialize_frontmatter(fm) + "\n---\n" + body
    path.write_text(new_text, encoding="utf-8")


def topo_sort(tickets):
    """Return ticket list in topological order (deps before dependents)."""
    by_id = {t["ticket_id"]: t for t in tickets}
    visited = set()
    order = []
    visiting = set()

    def visit(tid):
        if tid in visited:
            return
        if tid in visiting:
            raise ValueError(f"circular dependency involving {tid}")
        if tid not in by_id:
            return
        visiting.add(tid)
        for dep in by_id[tid].get("depends_on") or []:
            visit(dep)
        visiting.discard(tid)
        visited.add(tid)
        order.append(by_id[tid])

    for t in tickets:
        visit(t["ticket_id"])
    return order


def gh_issue_create(repo, title, body, labels, dry_run=False):
    cmd = [
        "gh", "issue", "create",
        "--repo", repo,
        "--title", title,
        "--body", body,
    ]
    for label in labels:
        cmd.extend(["--label", label])
    if dry_run:
        print(f"[dry-run] would run: gh issue create --repo {repo} --title {title!r} (body {len(body)} chars, {len(labels)} labels)")
        return None
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh issue create failed:\n{result.stderr}")
    url = result.stdout.strip().splitlines()[-1]
    m = re.search(r"/issues/(\d+)", url)
    if not m:
        raise RuntimeError(f"could not parse issue number from gh output: {url}")
    return int(m.group(1))


def get_repo_slug(build_repo_path):
    """Infer owner/repo from git remote origin."""
    result = subprocess.run(
        ["git", "-C", str(build_repo_path), "remote", "get-url", "origin"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("could not read git remote origin; is this a git repo?")
    url = result.stdout.strip()
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
    if not m:
        raise RuntimeError(f"could not parse GitHub owner/repo from remote: {url}")
    return m.group(1)


def main():
    parser = argparse.ArgumentParser(description="Push ticket markdowns to GitHub issues.")
    parser.add_argument("build_repo", type=Path, help="Path to the build repo (contains 04_tickets/)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen without calling gh")
    args = parser.parse_args()

    tickets_dir = args.build_repo / "04_tickets"
    if not tickets_dir.is_dir():
        print(f"error: {tickets_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    repo_slug = get_repo_slug(args.build_repo)
    print(f"build repo: {args.build_repo}")
    print(f"GitHub repo: {repo_slug}")
    if args.dry_run:
        print("(dry-run mode)")
    print()

    tickets = []
    for path in sorted(tickets_dir.glob("*.md")):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8")
        try:
            fm, body = parse_frontmatter(text)
        except ValueError as e:
            print(f"error in {path.name}: {e}", file=sys.stderr)
            sys.exit(1)
        tickets.append({
            "path": path,
            "ticket_id": fm.get("ticket_id"),
            "title": fm.get("title"),
            "phase": fm.get("phase"),
            "version": fm.get("version"),
            "depends_on": fm.get("depends_on") or [],
            "issue_number": fm.get("issue_number"),
            "frontmatter": fm,
            "body": body,
        })

    ordered = topo_sort(tickets)

    pushed, skipped = 0, 0
    for t in ordered:
        if t["issue_number"]:
            skipped += 1
            continue
        title = f"[{t['ticket_id']}] {t['title']}"
        labels = [f"phase:{t['phase']}", f"version:{str(t['version']).lower()}"]
        body = t["body"]
        if t["depends_on"]:
            dep_numbers = []
            for dep_id in t["depends_on"]:
                dep = next((x for x in tickets if x["ticket_id"] == dep_id), None)
                if dep and dep["issue_number"]:
                    dep_numbers.append(f"#{dep['issue_number']}")
            if dep_numbers:
                body = body.rstrip() + "\n\n---\n\n**Blocked by**: " + ", ".join(dep_numbers) + "\n"
        try:
            issue_number = gh_issue_create(repo_slug, title, body, labels, dry_run=args.dry_run)
        except RuntimeError as e:
            print(f"\nFAILED on {t['ticket_id']}: {e}", file=sys.stderr)
            print(f"already pushed: {pushed}, skipped: {skipped}", file=sys.stderr)
            sys.exit(2)
        if args.dry_run:
            print(f"  [dry-run] {t['ticket_id']} would create issue")
        else:
            rewrite_ticket_with_issue_number(t["path"], t["frontmatter"], t["body"], issue_number)
            print(f"  {t['ticket_id']} -> issue #{issue_number}")
        pushed += 1

    print()
    print(f"done. pushed: {pushed}, skipped (already had issue_number): {skipped}")


if __name__ == "__main__":
    main()
