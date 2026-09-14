"""Shared local-path and atomic-write helpers. No network or shell execution."""
from __future__ import annotations

import hashlib
from contextlib import contextmanager
import os
from pathlib import Path, PurePosixPath
import stat
import tempfile


def digest(data: bytes, *, text: bool = False) -> str:
    # Git autocrlf must not turn an untouched managed text file into an upgrade conflict.
    return hashlib.sha256(data.replace(b"\r\n", b"\n") if text else data).hexdigest()


def checked_path(path: Path) -> Path:
    """Reject symlinks/junctions in every existing ancestor, before resolving paths."""
    path = Path(os.path.abspath(path))
    for part in [*reversed(path.parents), path]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Symlink/reparse point is not allowed: {part}")
        if part != path and not stat.S_ISDIR(info.st_mode):
            raise ValueError(f"Path ancestor is not a directory: {part}")
        if stat.S_ISREG(info.st_mode) and info.st_nlink > 1:
            raise ValueError(f"Hard-linked file is not allowed: {part}")
    return path


def child(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ValueError("Invalid relative path")
    parts = PurePosixPath(relative).parts
    if any(p.lower() in ("..", ".git") for p in parts) or PurePosixPath(relative).is_absolute():
        raise ValueError("Path escapes the project or targets Git metadata")
    if any(ord(c) < 32 for c in relative):
        raise ValueError("Control character in path")
    result = checked_path(root / relative)
    if result == root or not result.is_relative_to(root):
        raise ValueError("Path must name a child of the project")
    return result


def disjoint(source: Path, target: Path) -> None:
    if source == target or source.is_relative_to(target) or target.is_relative_to(source):
        raise ValueError("Source and target must be disjoint directories")
    if target == Path(target.anchor) or target == Path.home():
        raise ValueError("A filesystem root or home directory is not a project target")
    if target.exists() and not target.is_dir():
        raise ValueError("Target is not a directory")


@contextmanager
def project_lock(root: Path):
    """OS lock is released on process death. Keep the inode to avoid unlink races."""
    path = child(root, ".devframework/install.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        if path.stat().st_size == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ValueError("Another installer/recovery owns this project") from error
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def atomic_write(path: Path, data: bytes) -> None:
    checked_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Same-directory replacement: readers see one complete file. Multi-file recovery
    # belongs to the install journal; power-loss durability depends on the filesystem.
    descriptor, temporary = tempfile.mkstemp(prefix=".devframework-write-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        checked_path(path)
        os.replace(temporary, path)
    finally:
        leftover = Path(temporary)
        if leftover.exists():
            leftover.unlink()
