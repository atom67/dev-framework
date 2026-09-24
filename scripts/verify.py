"""One local/CI command for this package; never installs into a live project."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def doc_link_errors(root: Path, check_links) -> list[str]:
    """Broken links in maintainer docs. The self-hosted .devframework/ is generated and git-ignored, so a
    fresh clone lacks it; links into it are skipped then. Its source, template/.devframework, is link-checked
    by the package tests. A local Devlog is a dialogue record, not maintainer documentation."""
    generated = (root / ".devframework").resolve()
    config = {}
    try:
        config = json.loads((root / ".devframework" / "project.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    sys.path.insert(0, str(ROOT / "template" / ".devframework"))
    from verification import in_devlog
    errors = []
    for path in [root / "README.md", root / "AGENTS.md", *root.joinpath("docs").rglob("*.md")]:
        relative = path.relative_to(root).as_posix()
        if "archive" in path.relative_to(root).parts or in_devlog(relative, config):
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
    runner = ROOT / "template" / ".devframework" / "run_unittest.py"  # fails on zero tests itself
    if subprocess.run([sys.executable, "-B", str(runner), "--start", "tests", "--jobs", "auto"], cwd=ROOT).returncode:
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
