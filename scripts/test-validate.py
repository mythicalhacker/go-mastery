#!/usr/bin/env python3
"""
Must-fail fixture for validate-index.py — confirms the checker goes red
on a broken anchor and stays green on a valid one.

Run: python3 scripts/test-validate.py
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "validate-index.py"


def run_checker(tmp: Path) -> tuple[int, str, str]:
    """Run validate-index.py with REPO_ROOT pointed at tmp."""
    env = os.environ.copy()
    env["VALIDATE_INDEX_ROOT"] = str(tmp)
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def make_repo(tmp: Path, index_content: str, ref_name: str, ref_content: str):
    """Build a minimal repo structure under tmp."""
    (tmp / "references").mkdir(exist_ok=True)
    (tmp / "INDEX.md").write_text(index_content)
    (tmp / "references" / ref_name).write_text(ref_content)


def test_valid_anchor():
    """A valid {#id} anchor must pass."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        make_repo(
            tmp,
            "- **Topic** → test.md#valid-section (description)\n",
            "test.md",
            "## Some Heading {#valid-section}\n\nContent here.\n",
        )
        rc, _, _ = run_checker(tmp)
        assert rc == 0, f"expected exit 0 on valid anchor, got {rc}"
    print("  PASS: valid anchor resolves")


def test_broken_anchor():
    """A missing {#id} anchor must fail."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        make_repo(
            tmp,
            "- **Topic** → test.md#nonexistent (description)\n",
            "test.md",
            "## Some Heading {#different-id}\n\nContent here.\n",
        )
        rc, _, _ = run_checker(tmp)
        assert rc == 1, f"expected exit 1 on broken anchor, got {rc}"
    print("  PASS: broken anchor caught")


def test_fence_not_parsed():
    """An anchor inside a fenced code block must not count."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        make_repo(
            tmp,
            "- **Topic** → test.md#only-in-fence (description)\n",
            "test.md",
            "## Real Heading {#real}\n\n```markdown\n## Example {#only-in-fence}\n```\n",
        )
        rc, _, _ = run_checker(tmp)
        assert rc == 1, f"expected exit 1 (anchor only inside fence), got {rc}"
    print("  PASS: fenced anchor ignored")


def test_missing_file():
    """A reference to a nonexistent file must fail."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        make_repo(
            tmp,
            "- **Topic** → missing.md#section (description)\n",
            "other.md",
            "## Heading {#section}\n",
        )
        rc, _, _ = run_checker(tmp)
        assert rc == 1, f"expected exit 1 on missing file, got {rc}"
    print("  PASS: missing file caught")


def test_no_refs_warns():
    """An INDEX.md with no references must exit 1 (fail-closed)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        make_repo(
            tmp,
            "# Index\n\nNo references here.\n",
            "test.md",
            "## Heading {#section}\n",
        )
        rc, _, _ = run_checker(tmp)
        assert rc == 1, f"expected exit 1 on empty refs, got {rc}"
    print("  PASS: no-refs fail-closed")


if __name__ == "__main__":
    print("validate-index fixture tests:")
    test_valid_anchor()
    test_broken_anchor()
    test_fence_not_parsed()
    test_missing_file()
    test_no_refs_warns()
    print(f"\nAll 5 tests passed.")
