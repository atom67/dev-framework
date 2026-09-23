"""Bounded Git source snapshot for the secret heuristic; no staging, checkout or index writes."""
from __future__ import annotations

from pathlib import Path

from safety import checked_path, child
from secrets_check import git, MAX_BLOB, MAX_TOTAL, inspect_blob, empty_report


def snapshot(root: Path) -> dict[str, bytes | None]:
    root = checked_path(root)
    top = Path(git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip())
    if top.resolve() != root.resolve():
        raise ValueError("Run at this Git repository's root, not a parent or child project")
    names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    files, total = {}, 0
    for raw in sorted(set(names.split(b"\0")) - {b""}):
        name = raw.decode("utf-8", errors="strict")
        path = child(root, name)
        if not path.exists():
            files[name] = None  # tracked deletion is part of the snapshot
            continue
        if not path.is_file() or path.stat().st_size > MAX_BLOB:
            raise ValueError("Unsupported source entry or source size limit exceeded")
        data = path.read_bytes()
        total += len(data)
        if len(data) > MAX_BLOB or total > MAX_TOTAL:
            raise ValueError("Source size limit exceeded; snapshot incomplete")
        files[name] = data
    if not files:
        raise ValueError("No tracked or nonignored untracked source files")
    return files


def scan_worktree(files: dict[str, bytes | None]) -> dict:
    report = empty_report()
    for name, data in files.items():
        if data is not None:
            inspect_blob(report, name, data)
    if not report["text_files"]:
        raise ValueError("No text source inspected")
    return report
