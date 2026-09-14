"""Bounded Git source snapshots; no staging, checkout or index writes."""
from __future__ import annotations

import hashlib
import json
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


def identity(files: dict[str, bytes | None]) -> str:
    hashes = {name: None if data is None else hashlib.sha256(data).hexdigest()
              for name, data in sorted(files.items())}
    return hashlib.sha256(json.dumps(hashes, sort_keys=True).encode("utf-8")).hexdigest()


def scan_worktree(files: dict[str, bytes | None]) -> dict:
    report = empty_report()
    for name, data in files.items():
        if data is not None:
            inspect_blob(report, name, data)
    if not report["text_files"]:
        raise ValueError("No text source inspected")
    return report


def require_index_parity(root: Path) -> bytes:
    # Git understands autocrlf, attributes and executable bits. Reject flags which can
    # hide changes from diff. Filters/commands are trusted project configuration, not a sandbox.
    flags = git(root, "ls-files", "-v", "-z")
    if any(row and (row[:1].islower() or row[:1] == b"S") for row in flags.split(b"\0")):
        raise ValueError("Index assume-unchanged/skip-worktree flags prevent parity verification")
    if git(root, "ls-files", "--others", "--exclude-standard", "-z"):
        raise ValueError("Commit check requires nonignored untracked files to be resolved")
    if git(root, "diff", "--no-ext-diff", "--no-textconv", "--name-only", "--"):
        raise ValueError("Index differs from working tree; commit content is NOT verified")
    index = git(root, "ls-files", "--stage", "-z")
    if not index:
        raise ValueError("Empty index is not a verified commit")
    return index
