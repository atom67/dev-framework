"""One local/CI command for this package; never installs into a live project."""
from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


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
    for path in [ROOT / "README.md", ROOT / "AGENTS.md", *ROOT.joinpath("docs").rglob("*.md")]:
        if "archive" in path.relative_to(ROOT).parts:
            continue
        errors = check_links(ROOT, path, path.read_text(encoding="utf-8"))
        if not ROOT.joinpath(".devframework").is_dir():
            # ponytail: the self-hosted .devframework/ is generated and git-ignored, so a fresh clone lacks it;
            # its source (template/.devframework) is link-checked by the package tests
            errors = [e for e in errors if not e.split("link: ", 1)[-1].startswith(".devframework/")]
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
