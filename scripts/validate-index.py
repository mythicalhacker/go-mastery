#!/usr/bin/env python3
"""
Validate that every file.md#anchor reference in INDEX.md points to an anchor
that is actually declared in the target file.

Reference files declare section ids explicitly:

    ## Creational Patterns {#creational}

so an anchor is checked against those declarations, not against a slug derived
from the heading text. There is deliberately no text-search fallback: matching
an anchor anywhere in the file body would resolve almost any string (`#the`,
`#go`) and report success for broken links.

Exit 0 = every reference resolves. Exit 1 = broken references (printed to stderr).
No dependencies beyond Python 3.9+.
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(os.environ.get("VALIDATE_INDEX_ROOT",
                                Path(__file__).resolve().parent.parent))
INDEX = REPO_ROOT / "INDEX.md"
REFS_DIR = REPO_ROOT / "references"

ANCHOR_RE = re.compile(r"\{#([A-Za-z0-9][\w.-]*)\}")
REF_RE = re.compile(r"([A-Za-z0-9][\w.-]*\.md)#([A-Za-z0-9][\w.-]*)")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
ITEM_RE = re.compile(r"^\s*[-*+]\s")


def prose_lines(text: str):
    """Yield (line_no, line) for lines outside fenced code blocks.

    Snippets legitimately contain heading-shaped and reference-shaped text;
    scanning them produces phantom anchors and phantom references.

    Fence tracking follows CommonMark 4.5: a closing fence uses the same
    character as the opener and is at least as long. A three-backtick closer
    does not close a five-backtick opener.
    """
    fence = ""
    for n, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line)
        if m:
            token = m.group(1)
            if not fence:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = ""
            continue
        if not fence:
            yield n, line


def extract_refs(index_text: str):
    """Pull (file, anchor, line_no) triples from INDEX.md list entries."""
    refs = []
    for n, line in prose_lines(index_text):
        if not ITEM_RE.match(line):
            continue
        refs.extend((m.group(1), m.group(2), n) for m in REF_RE.finditer(line))
    return refs


def collect_anchors(filepath: Path):
    """Return the explicit {#id} anchors declared in a markdown file."""
    text = filepath.read_text(encoding="utf-8", errors="replace")
    anchors = set()
    for _, line in prose_lines(text):
        anchors.update(ANCHOR_RE.findall(line))
    return anchors


def main() -> int:
    if not INDEX.exists():
        print(f"ERROR: {INDEX} not found", file=sys.stderr)
        return 1

    refs = extract_refs(INDEX.read_text(encoding="utf-8"))
    if not refs:
        print("ERROR: no references found in INDEX.md", file=sys.stderr)
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
