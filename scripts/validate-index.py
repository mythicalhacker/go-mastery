#!/usr/bin/env python3
"""
Validate that every file.md#anchor reference in INDEX.md points to
an existing file with a matching anchor declaration.

Anchors are declared as {#id} suffixes on headings:
  ## Creational Patterns {#creational}

Exit 0 = all links resolve. Exit 1 = broken links found (printed to stderr).
No dependencies beyond Python 3.9+.
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(os.environ.get("VALIDATE_INDEX_ROOT", Path(__file__).resolve().parent.parent))
INDEX = REPO_ROOT / "INDEX.md"
REFS_DIR = REPO_ROOT / "references"

ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9][\w.-]*)\}")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")


def extract_refs(index_text: str) -> list[tuple[str, str, int]]:
    """Pull (file, anchor, line_no) triples from INDEX.md."""
    refs = []
    for i, line in enumerate(index_text.splitlines(), 1):
        for m in re.finditer(r"([\w][\w-]*\.md)#([\w.-]+)", line):
            fname, anchor = m.group(1), m.group(2)
            if fname == "file.md" and anchor == "section-anchor":
                continue
            refs.append((fname, anchor, i))
    return refs


def collect_anchors(filepath: Path) -> set[str]:
    """Return the set of explicitly declared {#id} anchors in a markdown file."""
    anchors = set()
    text = filepath.read_text(encoding="utf-8", errors="replace")
    in_fence = False
    for line in text.splitlines():
        fence_match = FENCE_RE.match(line)
        if fence_match:
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in ANCHOR_RE.finditer(line):
            anchors.add(m.group(1))
    return anchors


def main() -> int:
    if not INDEX.exists():
        print(f"ERROR: {INDEX} not found", file=sys.stderr)
        return 1

    index_text = INDEX.read_text(encoding="utf-8")
    refs = extract_refs(index_text)

    if not refs:
        print("WARNING: no references found in INDEX.md", file=sys.stderr)
        return 1

    anchor_cache: dict[str, set[str]] = {}
    broken = []
    ok = 0

    for fname, anchor, lineno in refs:
        fpath = REFS_DIR / fname
        if not fpath.exists():
            broken.append((lineno, fname, anchor, "file not found"))
            continue

        if fname not in anchor_cache:
            anchor_cache[fname] = collect_anchors(fpath)

        if anchor in anchor_cache[fname]:
            ok += 1
        else:
            broken.append((lineno, fname, anchor, "anchor not declared"))

    total = ok + len(broken)
    if broken:
        print(f"\n{len(broken)} broken reference(s) in INDEX.md:\n", file=sys.stderr)
        for lineno, fname, anchor, reason in sorted(broken):
            print(f"  line {lineno}: {fname}#{anchor} — {reason}", file=sys.stderr)
        print(f"\n{ok}/{total} OK, {len(broken)} broken", file=sys.stderr)
        return 1

    print(f"validate-index: {ok}/{total} references OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
