"""Heuristic staged TEXT scan. Never emits matched values or executes repository code."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess

ASSIGNMENT = re.compile(
    r'''["']?([\w.-]*(?:password|passwd|token|secret|api[_-]?key)[\w.-]*)["']?[ \t]*[:=][ \t]*(?:@?"([^"\r\n]*)"|'([^'\r\n]*)'|(\$\{[A-Z0-9_]+\}|[^\s,;#}\]\r\n]+))''',
    re.IGNORECASE,
)
PLACEHOLDER = re.compile(r"(?:<[^<>]+>|\$\{[A-Z0-9_]+\}|YOUR_[A-Z0-9_]+|REPLACE_ME|EXAMPLE_ONLY|CHANGEME)")
KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")
TOKEN = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-(?:proj-)?[A-Za-z0-9_-]{32,})\b")
MAX_BLOB = 10 * 1024 * 1024
MAX_TOTAL = 100 * 1024 * 1024


def benign(name: str, value: str, quoted: bool) -> bool:
    if not value or PLACEHOLDER.fullmatch(value):
        return True
    key = re.sub(r"[^a-z0-9]", "", name.lower())
    # Exact metadata names + constrained values; not a blanket token_* exemption.
    if key == "tokentype" and value in ("Bearer", "bearer", "MAC", "mac"):
        return True
    if key in ("tokenendpoint", "tokenurl") and re.fullmatch(r"https?://[\w.-]+(?::\d+)?/[\w./-]*", value):
        return True
    if not quoted:
        # Code references/absence are not literal credentials. Unquoted env/YAML
        # strings remain candidates; expressions and other formats need richer scanners.
        if value.lower() in ("none", "null", "true", "false", "{", "["):
            return True
        if re.match(r"[A-Za-z_]\w*(?:\.\w+)*\(", value):
            return True
        if value.startswith(("os.environ", "os.getenv(", "Environment.", "config.", "settings.", "self.", "args.", "re.compile(", "process.env.")):
            return True
    return False


def findings(text: str) -> list[tuple[int, str]]:
    found = []
    for match in ASSIGNMENT.finditer(text):
        if match[4] is not None:
            prefix = text[text.rfind("\n", 0, match.start()) + 1:match.start()].strip()
            if prefix not in ("", "export", "-"):
                continue  # bare dotenv/YAML scalars, not prose or arbitrary code expressions
        value = next(v for v in match.groups()[1:] if v is not None)
        if not benign(match[1], value, match[4] is None):
            found.append((text.count("\n", 0, match.start()) + 1, "credential-like literal"))
    for pattern, label in ((KEY, "private key"), (TOKEN, "token-like literal")):
        for match in pattern.finditer(text):
            found.append((text.count("\n", 0, match.start()) + 1, label))
    return sorted(set(found))


def empty_report() -> dict:
    return {"findings": [], "text_files": 0, "nontext_files": [], "bytes": 0}


def inspect_blob(report: dict, path: str, data: bytes) -> None:
    report["bytes"] += len(data)
    try:
        text = data.decode("utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
        if "\x00" in text:
            raise UnicodeError("Binary content")
    except UnicodeError:
        report["nontext_files"].append(path)
        return
    report["text_files"] += 1
    for line, label in findings(text):
        report["findings"].append({"path": path, "line": line, "kind": label})


def git(root: Path, *args: str) -> bytes:
    run = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=30)
    if run.returncode:
        raise ValueError("Git inspection failed; staged content was NOT verified")
    return run.stdout


def scan_index(root: Path) -> dict:
    # Freeze object IDs, not worktree paths; cat-file --batch uses one subprocess for
    # the whole index rather than spawning Git once per file. Recheck the index at end.
    snapshot = git(root, "ls-files", "--stage", "-z")
    rows = []
    for row in snapshot.split(b"\0"):
        if not row:
            continue
        meta, raw_path = row.split(b"\t", 1)
        mode, oid, stage = meta.split()
        if stage != b"0":
            raise ValueError("Unmerged index; resolve it before checking")
        rows.append((mode, oid, raw_path.decode("utf-8", errors="replace")))
    if not rows:
        raise ValueError("Index is empty; no staged source content was checked")
    report = empty_report()
    process = subprocess.Popen(["git", "-C", str(root), "cat-file", "--batch"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        for mode, oid, path in rows:
            if mode != b"100644" and mode != b"100755":
                raise ValueError(f"Non-file index entry requires separate inspection: {path}")
            process.stdin.write(oid + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) != 3 or header[1] != b"blob":
                raise ValueError("Cannot read staged blob")
            size = int(header[2])
            if size > MAX_BLOB or report["bytes"] + size > MAX_TOTAL:
                raise ValueError("Staged scan size limit exceeded; content NOT fully inspected")
            data = process.stdout.read(size)
            if len(data) != size or process.stdout.read(1) != b"\n":
                raise ValueError("Incomplete staged blob")
            inspect_blob(report, path, data)
    finally:
        process.stdin.close()
        process.stdout.close()
        if process.poll() is None:
            process.terminate()
        process.wait(timeout=10)
    if git(root, "ls-files", "--stage", "-z") != snapshot:
        raise ValueError("Index changed during inspection; run the check again")
    if report["text_files"] == 0:
        raise ValueError("No text files inspected; this is not an artifact scanner")
    return report
