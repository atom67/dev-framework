"""One local/CI command for this package; never installs into a live project."""
from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def doc_link_errors(root: Path, check_links) -> list[str]:
    """Broken links in maintainer docs. The self-hosted .devframework/ is generated and git-ignored, so a
    fresh clone lacks it; links into it are skipped then. Its source, template/.devframework, is link-checked
    by the package tests."""
    generated = (root / ".devframework").resolve()
    errors = []
    for path in [root / "README.md", root / "AGENTS.md", *root.joinpath("docs").rglob("*.md")]:
        if "archive" in path.relative_to(root).parts:
            continue
        for error in check_links(root, path, path.read_text(encoding="utf-8")):
            target = (path.parent / error.split("link: ", 1)[-1].split("#")[0]).resolve()
            if generated.is_dir() or not target.is_relative_to(generated):
                errors.append(error)
    return errors


def main() -> int:
    if sys.version_info < (3, 10):
        print("Python 3.10+ is required", file=sys.stderr)
        return 1
    files = [*ROOT.joinpath("scripts").rglob("*.py"),
             *ROOT.joinpath("template", ".devframework").glob("*.py"),
             *ROOT.joinpath("tests").rglob("*.py")]
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    print(f"Syntax: {len(files)} Python files", flush=True)
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    if suite.countTestCases() == 0:
        print("FAILED: no package tests discovered", file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    sys.path.insert(0, str(ROOT / "template" / ".devframework"))
    from source_scope import snapshot, scan_worktree
    from check import show_secrets
    from verification import check_links
    if show_secrets(ROOT, scan_worktree(snapshot(ROOT))):
        return 1
    errors = doc_link_errors(ROOT, check_links)
    if errors:
        print("Maintainer documentation links failed:", *errors, sep="\n")
        return 1
    diff = subprocess.run(["git", "diff", "--check"], cwd=ROOT)
    if diff.returncode:
        return diff.returncode
    print("PACKAGE VERIFIED. No commit/push/deploy. See test output for skips and limits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
