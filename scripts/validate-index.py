#!/usr/bin/env python3
"""
Validate that every file.md#anchor reference in INDEX.md points to
an existing file with a matching heading. Catches silent breakage
when a reference section is renamed or moved.

Exit 0 = all links resolve. Exit 1 = broken links found (printed to stderr).
No dependencies beyond Python 3.8+.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX = REPO_ROOT / "INDEX.md"
REFS_DIR = REPO_ROOT / "references"


def slugify(text: str) -> str:
    """GitHub-style heading → anchor slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text.strip("-")


def extract_refs(index_text: str) -> list[tuple[str, str, int]]:
    """Pull (file, anchor, line_no) triples from INDEX.md."""
    refs = []
    for i, line in enumerate(index_text.splitlines(), 1):
        for m in re.finditer(r"([\w][\w-]*\.md)#([\w-]+)", line):
            fname, anchor = m.group(1), m.group(2)
            if fname == "file.md" and anchor == "section-anchor":
                continue  # skip the format-example line
            refs.append((fname, anchor, i))
    return refs


def collect_anchors(filepath: Path) -> set[str]:
    """Return the set of heading-derived anchors in a markdown file."""
    anchors = set()
    text = filepath.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"^#{1,6}\s+(.+)", text, re.MULTILINE):
        anchors.add(slugify(m.group(1)))
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

    # cache anchors per file
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
            # fallback: raw text search (some anchors use underscores
            # or abbreviations that slugify differently)
            content = fpath.read_text(encoding="utf-8", errors="replace").lower()
            if anchor.replace("-", " ") in content or anchor in content:
                ok += 1
            else:
                broken.append((lineno, fname, anchor, "anchor not found"))

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
