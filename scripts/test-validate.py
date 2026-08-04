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


def test_long_fence():
    """A 5-backtick fence must not be closed by a 3-backtick line."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        make_repo(
            tmp,
            "- **Topic** → test.md#trapped (description)\n",
            "test.md",
            (
                "## Intro {#intro}\n\n"
                "`````markdown\n"
                "## Inner sample {#trapped}\n"
                "```\n"
                "still inside the 5-backtick fence\n"
                "`````\n"
            ),
        )
        rc, _, _ = run_checker(tmp)
        assert rc == 1, f"expected exit 1 (anchor inside long fence), got {rc}"
    print("  PASS: long fence (5-backtick) not closed by short (3-backtick)")


def test_tilde_fence():
    """A ~~~ fence must not be closed by a ``` line."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        make_repo(
            tmp,
            "- **Topic** → test.md#tilde-only (description)\n",
            "test.md",
            (
                "## Intro {#intro}\n\n"
                "~~~\n"
                "## Hidden {#tilde-only}\n"
                "```\n"
                "still inside tilde fence\n"
                "~~~\n"
            ),
        )
        rc, _, _ = run_checker(tmp)
        assert rc == 1, f"expected exit 1 (anchor inside tilde fence), got {rc}"
    print("  PASS: tilde fence not closed by backtick")


def test_indented_fence():
    """A fence indented up to 3 spaces must still be recognized."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        make_repo(
            tmp,
            "- **Topic** → test.md#indented-only (description)\n",
            "test.md",
            (
                "## Intro {#intro}\n\n"
                "   ```\n"
                "## Hidden {#indented-only}\n"
                "   ```\n"
            ),
        )
        rc, _, _ = run_checker(tmp)
        assert rc == 1, f"expected exit 1 (anchor inside indented fence), got {rc}"
    print("  PASS: indented fence (3 spaces) recognized")


def test_ref_in_fenced_index():
    """A reference inside a fenced block in INDEX.md must not be followed."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        make_repo(
            tmp,
            (
                "- **Real** → test.md#real (a real reference)\n"
                "```\n"
                "- **Fake** → test.md#phantom (inside a code block)\n"
                "```\n"
            ),
            "test.md",
            "## Section {#real}\n",
        )
        rc, _, _ = run_checker(tmp)
        assert rc == 0, f"expected exit 0 (phantom ref in fence ignored), got {rc}"
    print("  PASS: reference inside INDEX.md fence ignored")


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
    test_long_fence()
    test_tilde_fence()
    test_indented_fence()
    test_ref_in_fenced_index()
    test_missing_file()
    test_no_refs_warns()
    print(f"\nAll 9 tests passed.")
