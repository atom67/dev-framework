"""The dialogue for a devlog entry, read from the host's own session log — an agent cannot recall its transcript.

Claude Code writes one JSONL file per session under ~/.claude/projects/<folder>/ (entries carry the session's
cwd); Hermes keeps sessions and messages in state.db. User and assistant text is kept verbatim, tool calls are
summarized as one bracketed line, system reminders are dropped and secret-shaped lines are redacted.
Standard library only.
"""
from __future__ import annotations

from collections import Counter
from datetime import date
import json
import os
from pathlib import Path
import re
import sqlite3

from secrets_check import findings

NOISE = re.compile(r"<(system-reminder|local-command-caveat|command-name|command-message|command-args|"
                   r"local-command-stdout|task-notification)>.*?</\1>", re.S)
HEAD_LINES = 200  # enough of a transcript to find its cwd without reading a long session twice


def redact(text: str) -> str:
    lines = text.split("\n")
    for number, kind in findings(text):
        lines[number - 1] = f"[line redacted: possible {kind}]"
    return "\n".join(lines)


def render(turns: list[tuple[str, str]]) -> str:
    """turns: ("User" | "Assistant" | "tools", text) in order → Markdown."""
    return "\n\n".join(f"[{text}]" if who == "tools" else f"**{who}:** {text}" for who, text in turns)


def _merge(turns: list[tuple[str, str]], who: str, text: str) -> None:
    text = text.strip()
    if not text:
        return
    if turns and turns[-1][0] == who:
        turns[-1] = (who, turns[-1][1] + "\n\n" + text)
    else:
        turns.append((who, text))


def _flush_tools(turns: list[tuple[str, str]], tools: Counter) -> None:
    if tools:
        turns.append(("tools", "tools: " + ", ".join(f"{name}×{count}" for name, count in tools.most_common())))
        tools.clear()


def claude_turns(path: Path, day: date | None = None) -> list[tuple[str, str]]:
    turns, tools = [], Counter()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") not in ("user", "assistant") or entry.get("isSidechain"):
                continue  # sidechains are subagents; their work shows up as the parent's tool call
            if day and not str(entry.get("timestamp", "")).startswith(day.isoformat()):
                continue
            content = (entry.get("message") or {}).get("content")
            blocks = [{"type": "text", "text": content}] if isinstance(content, str) else (content or [])
            for block in blocks:
                if block.get("type") == "tool_use":
                    tools[block.get("name", "tool")] += 1
                elif block.get("type") == "text":
                    text = NOISE.sub("", block.get("text", "")).strip()
                    if text:
                        _flush_tools(turns, tools)
                        _merge(turns, "User" if entry["type"] == "user" else "Assistant", text)
    _flush_tools(turns, tools)
    return turns


def claude_session(root: Path) -> Path | None:
    """The newest Claude Code session whose working directory is the project, above it or inside it."""
    base = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"
    root = root.resolve()
    for path in sorted(base.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:50]:
        with path.open(encoding="utf-8") as handle:
            for number, line in enumerate(handle):
                if number > HEAD_LINES:
                    break
                try:
                    cwd = json.loads(line).get("cwd")
                except ValueError:
                    continue
                if cwd:
                    cwd = Path(cwd).resolve()
                    if cwd == root or cwd in root.parents or root in cwd.parents:
                        return path
                    break
    return None


def hermes_turns(session: str | None = None, day: date | None = None) -> list[tuple[str, str]]:
    db = Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes") / "state.db"
    if not db.is_file():
        return []
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)  # `with connect()` only ends a transaction; close it
    try:
        conn.row_factory = sqlite3.Row
        if not session:
            row = conn.execute("SELECT id FROM sessions ORDER BY started_at DESC LIMIT 1").fetchone()
            session = row["id"] if row else None
        rows = conn.execute("SELECT * FROM messages WHERE session_id=? ORDER BY timestamp", (session,)).fetchall()
    finally:
        conn.close()
    turns, tools = [], Counter()
    for row in rows:
        if day and not str(row["timestamp"]).startswith(day.isoformat()):
            continue
        if row["role"] == "tool":
            tools[row["tool_name"] or "tool"] += 1
        elif row["role"] in ("user", "assistant") and row["content"]:
            _flush_tools(turns, tools)
            _merge(turns, row["role"].title(), NOISE.sub("", row["content"]))
    _flush_tools(turns, tools)
    return turns


def dialogue(root: Path, source: str = "auto", day: date | None = None) -> tuple[str | None, str]:
    """(Markdown dialogue or None, where it came from). source: auto | none | <file.jsonl> | hermes[:<session>].

    auto reads only a Claude Code session whose cwd matches the project; Hermes must be named explicitly,
    because "the latest Hermes session" may be an unrelated conversation.
    """
    if source == "none":
        return None, "not requested"
    if source.startswith("hermes"):
        turns = hermes_turns(source.partition(":")[2] or None, day)
        return (redact(render(turns)), "Hermes state.db") if turns else (None, "no Hermes messages found")
    path = Path(source) if source != "auto" else claude_session(root)
    if path and path.is_file():
        turns = claude_turns(path, day)
        if turns:
            return redact(render(turns)), f"session log {path.name}"
    return None, "no session log found for this project — paste the dialogue by hand"
