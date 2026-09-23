#!/usr/bin/env python3
"""SessionStart hook: print the project's DEV Framework brief so the agent starts from context, not archaeology.

Silent (exit 0, no output) when the working directory is not a framework project — a hook must never
add noise to an unrelated session. Standard library only.

The brief is produced by the plugin's own copy of navigate.py, pointed at the project with --root.
The project supplies only data (Markdown, project.json, git state); no code from the opened
repository runs at session start, so opening a cloned stranger's repository is safe.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

MAX_CHARS = 4000
NAVIGATE = Path(__file__).resolve().parents[1] / "template" / ".devframework" / "navigate.py"  # plugin-owned code


def project_root() -> Path | None:
    start = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / ".devframework" / "navigate.py").is_file():
            return candidate
        if (candidate / ".git").exists():  # the project ends at its git root: a parent's framework is not ours
            return None
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    root = project_root()
    if root is None:
        return 0
    try:
        run = subprocess.run([sys.executable, "-B", str(NAVIGATE), "--root", str(root), "brief"],
                             cwd=str(root), capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=60)
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"DEV Framework brief unavailable ({error}); run `python .devframework/navigate.py brief` by hand.")
        return 0
    if run.returncode != 0:
        return 0
    print("DEV Framework — session brief (read this before opening documents; "
          "`python .devframework/navigate.py find <ID|keyword>` returns one block, not a file):")
    print(run.stdout.strip()[:MAX_CHARS])
    return 0


if __name__ == "__main__":
    sys.exit(main())
