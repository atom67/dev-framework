"""Devlog — optional verbatim dialogue log, written at finish/commit time.

Enabled per project in ``.devframework/project.json``::

    "devlog": {"enabled": true, "dir": "docs/devlog", "commit": false}

Rules (see DEVLOG.md): one file per finalized dialogue, named
``<YYYY-MM-DD>_<client>-<MODEL>_<CODE>_<CODE>.md`` (date, the client/model that drove it, codes); an info block
with the commits of that dialogue and a summary of at most three sentences each;
then the dialogue verbatim. If the repository is PUBLIC (or visibility is unknown)
the devlog directory is kept local and git-ignored unless ``commit`` is true AND
the repository is private. Standard library only.
"""
from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from pathlib import Path

DEFAULT_DIR = "docs/devlog"
CODE_RE = re.compile(r"^((FR|NFR|UC|SET|KE|INV)-[A-Za-z0-9-]+|PRODUCT|TOOL|EXPLORE)$")  # a kind stands in when no ids exist
AGENT_RE = re.compile(r"^[a-z0-9]+-[A-Za-z0-9.]+$")   # <client>-<MODEL>, e.g. claudecode-OPUS5
MAX_SUMMARY_SENTENCES = 3
MAX_AGENTS = 2                                        # the two models with the largest share of the dialogue


def settings(root: Path) -> dict:
    try:
        cfg = json.loads((root / ".devframework" / "project.json").read_text(encoding="utf-8"))
    except Exception:
        return {"enabled": False, "dir": DEFAULT_DIR, "commit": False}
    raw = cfg.get("devlog") if isinstance(cfg, dict) else None
    raw = raw if isinstance(raw, dict) else {}
    return {"enabled": bool(raw.get("enabled", False)),
            "dir": str(raw.get("dir") or DEFAULT_DIR).strip("/"),
            "commit": bool(raw.get("commit", False))}


def _git(root: Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=20)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def repo_visibility(root: Path) -> str:
    """'public' | 'private' | 'unknown'. Uses `gh` when the remote is on GitHub; unknown otherwise."""
    remote = _git(root, "remote", "get-url", "origin")
    if not remote:
        return "unknown"
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", remote)
    if not m:
        return "unknown"
    try:
        r = subprocess.run(["gh", "repo", "view", m.group(1), "--json", "visibility", "--jq", ".visibility"],
                           capture_output=True, text=True, timeout=30)
        value = r.stdout.strip().lower()
        return value if value in {"public", "private", "internal"} else "unknown"
    except Exception:
        return "unknown"


def keep_local(root: Path, cfg: dict | None = None) -> tuple[bool, str]:
    """(local_only, reason). Public or unknown visibility -> local only unless commit=true AND private."""
    cfg = cfg or settings(root)
    visibility = repo_visibility(root)
    if visibility == "private" and cfg.get("commit"):
        return False, "private repository, devlog.commit=true"
    if visibility in {"public", "unknown"}:
        return True, f"{visibility} repository: devlog stays local (git-ignored)"
    return True, "devlog.commit is false: devlog stays local (git-ignored)"


def ensure_gitignored(root: Path, directory: str) -> bool:
    """Add ``/<directory>/`` to the root .gitignore once. Returns True when a line was added."""
    line = f"/{directory.strip('/')}/"
    path = root / ".gitignore"
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    if line in existing or line.rstrip("/") in existing:
        return False
    text = "\n".join(existing + [line]) + "\n" if existing else line + "\n"
    path.write_text(text, encoding="utf-8")
    return True


def validate_codes(codes: list[str]) -> list[str]:
    cleaned = [c.strip().upper() for c in codes if c.strip()]
    bad = [c for c in cleaned if not CODE_RE.match(c)]
    if not cleaned or bad:
        raise ValueError("Codes must be FR/NFR/UC/SET/KE/INV identifiers, e.g. FR-005,UC-004; got: " + ", ".join(bad or ["none"]))
    return list(dict.fromkeys(cleaned))


def validate_agents(agents: list[str]) -> list[str]:
    """<client>-<MODEL> tags, at most two: the models that carried most of the dialogue."""
    cleaned = list(dict.fromkeys(a.strip() for a in agents if a.strip()))
    bad = [a for a in cleaned if not AGENT_RE.match(a)]
    if not cleaned or bad or len(cleaned) > MAX_AGENTS:
        raise ValueError("Agents must be 1-2 tags of the form <client>-<MODEL>, e.g. claudecode-OPUS5; got: "
                         + ", ".join(bad or cleaned or ["none"]))
    return cleaned


def sentence_count(text: str) -> int:
    return len([s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s])


def file_name(day: date, agents: list[str], codes: list[str]) -> str:
    return f"{day.isoformat()}_{'+'.join(agents)}_{'_'.join(codes)}.md"


def recent_commits(root: Path, count: int) -> list[tuple[str, str]]:
    out = _git(root, "log", f"-{count}", "--format=%h%x09%s")
    return [tuple(line.split("\t", 1)) for line in out.splitlines() if "\t" in line]


def header(day: date, agents: list[str], codes: list[str], commits: list[tuple[str, str]], visibility_note: str) -> str:
    for sha, summary in commits:
        if sentence_count(summary) > MAX_SUMMARY_SENTENCES:
            raise ValueError(f"Commit {sha}: summary must be at most {MAX_SUMMARY_SENTENCES} sentences")
    rows = "\n".join(f"| `{sha}` | {summary} |" for sha, summary in commits) or "| — | no commits recorded |"
    return (f"# Devlog {day.isoformat()} — {', '.join(codes)}\n\n"
            f"| Field | Value |\n|---|---|\n| Date | {day.isoformat()} |\n| Agent(s) | {', '.join(agents)} |\n"
            f"| Codes | {', '.join(codes)} |\n"
            f"| Storage | {visibility_note} |\n\n"
            f"## Commits\n\n| Commit | Summary (≤ 3 sentences) |\n|---|---|\n{rows}\n\n"
            "## Dialogue (verbatim)\n\n"
            "<!-- Paste the dialogue as it happened: **User:** / **Assistant:** turns, in order, unedited.\n"
            "     Tool outputs may be summarized in [brackets]. Never include secrets. -->\n")


def new_entry(root: Path, day: date, agents: list[str], codes: list[str], commits: list[tuple[str, str]]) -> Path:
    cfg = settings(root)
    if not cfg["enabled"]:
        raise ValueError("Devlog is disabled in .devframework/project.json (devlog.enabled)")
    local_only, reason = keep_local(root, cfg)
    if local_only:
        ensure_gitignored(root, cfg["dir"])
    directory = root / cfg["dir"]
    directory.mkdir(parents=True, exist_ok=True)
    agents, codes = validate_agents(agents), validate_codes(codes)
    path = directory / file_name(day, agents, codes)
    if path.exists():
        raise ValueError(f"Devlog already exists: {path.relative_to(root).as_posix()} — append to it instead")
    path.write_text(header(day, agents, codes, commits, reason), encoding="utf-8")
    return path


def missing_today(root: Path) -> str | None:
    """Reminder text when devlog is enabled and no entry exists for today; None otherwise."""
    cfg = settings(root)
    if not cfg["enabled"]:
        return None
    today = date.today().isoformat()
    directory = root / cfg["dir"]
    if directory.exists() and any(p.name.startswith(today) for p in directory.glob("*.md")):
        return None
    return (f"DEVLOG: enabled but no entry for {today} in {cfg['dir']}/ — create one with "
            "`python .devframework/check.py devlog --agent claudecode-OPUS5 --codes FR-…,UC-… --from-git N` and paste the dialogue")
