#!/usr/bin/env python3
"""Objective numbers for one Hermes session: tool calls, API calls, reasoning, seconds.

Reads the Hermes profile's state.db (read-only). Usage:

    python evals/measure.py --profile dftest-s1a --last
    python evals/measure.py --profile dftest-s1a --session 20260920_105046_cf3690
    python evals/measure.py --db /path/to/state.db --last
    python evals/measure.py --selftest

Prints a Markdown table row for RESULTS.md plus a per-tool breakdown.
"""
import argparse
import json
import os
import sqlite3
import sys
from collections import Counter

REASONING_COLS = ("reasoning", "reasoning_content", "reasoning_details", "codex_reasoning_items")
OUR_SKILLS = {"import-dev-framework", "catch-up", "df-import", "df-catch-up"}  # framework-owned skill names


def db_path(profile):
    root = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~/.local/share")
    cand = [os.path.join(root, "hermes", "profiles", profile, "state.db"),
            os.path.expanduser(f"~/.hermes/profiles/{profile}/state.db")]
    if os.environ.get("HERMES_HOME"):  # HERMES_HOME may point at the root install or at a profile
        cand = [os.path.join(os.environ["HERMES_HOME"], "profiles", profile, "state.db")] + cand
    for p in cand:
        if os.path.exists(p):
            return p
    sys.exit(f"state.db not found for profile {profile!r}: tried {cand}")


def measure(conn, session_id=None):
    conn.row_factory = sqlite3.Row
    if session_id is None:
        row = conn.execute("SELECT id FROM sessions ORDER BY started_at DESC LIMIT 1").fetchone()
        if not row:
            sys.exit("no sessions in db")
        session_id = row["id"]
    s = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    if not s:
        sys.exit(f"session {session_id} not found")
    msgs = conn.execute("SELECT * FROM messages WHERE session_id=? ORDER BY timestamp", (session_id,)).fetchall()
    roles = Counter(m["role"] for m in msgs)
    tools = Counter(m["tool_name"] for m in msgs if m["role"] == "tool" and m["tool_name"])
    thinking = sum(1 for m in msgs if m["role"] == "assistant" and any(m[c] for c in REASONING_COLS))
    last_ts = max([m["timestamp"] for m in msgs] + [s["started_at"]])
    end = s["ended_at"] or last_ts
    tool_calls = s["tool_call_count"] or sum(tools.values())
    # Questions reach the user either as a plain assistant turn (next message is a user turn) or via the
    # `clarify` tool; time between asking and the answer is the user's, not the agent's.
    waiting = 0.0
    prev = None
    for m in msgs:
        if m["role"] == "tool" and m["tool_name"] == "clarify" and prev is not None:
            waiting += m["timestamp"] - prev["timestamp"]
        prev = m
    questions = tools.get("clarify", 0) + max(roles.get("user", 0) - 1, 0)
    # Foreign skills = skill_view results whose name is not ours: the host profile context the framework must coexist with.
    foreign = Counter()
    for m in msgs:
        if m["role"] == "tool" and m["tool_name"] == "skill_view" and m["content"]:
            try:
                name = json.loads(m["content"]).get("name", "?")
            except (ValueError, AttributeError):
                name = "?"
            if name not in OUR_SKILLS:
                foreign[name] += len(m["content"])
    return {
        "foreign_skill_bytes": sum(foreign.values()),
        "foreign_skills": ", ".join(f"{k}({v // 1000}k)" for k, v in foreign.most_common()) or "-",
        "session": session_id,
        "seconds": round(end - s["started_at"]),
        "active_seconds": round(end - s["started_at"] - waiting),
        "api_calls": s["api_call_count"],
        "tool_calls": tool_calls,
        "assistant_msgs_with_reasoning": thinking,
        "reasoning_tok": s["reasoning_tokens"],
        "in_tok": s["input_tokens"],
        "out_tok": s["output_tokens"],
        "user_turns": roles.get("user", 0),
        "questions_to_user": questions,
        "tools": tools,
    }


def report(r):
    print("| session | seconds | active s | api calls | tool calls | assistant msgs w/ reasoning | reasoning tok | in tok | out tok | questions to user |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    print(f"| {r['session']} | {r['seconds']} | {r['active_seconds']} | {r['api_calls']} | {r['tool_calls']} | {r['assistant_msgs_with_reasoning']} | "
          f"{r['reasoning_tok']} | {r['in_tok']} | {r['out_tok']} | {r['questions_to_user']} |")
    print("\ntools:", ", ".join(f"{k}={v}" for k, v in r["tools"].most_common()) or "-")
    print(f"foreign skills: {r['foreign_skill_bytes'] // 1000}k — {r['foreign_skills']}")


def selftest():
    c = sqlite3.connect(":memory:")
    c.executescript("""
    CREATE TABLE sessions(id TEXT, started_at REAL, ended_at REAL, tool_call_count INT, api_call_count INT,
      reasoning_tokens INT, input_tokens INT, output_tokens INT);
    CREATE TABLE messages(session_id TEXT, role TEXT, timestamp REAL, tool_name TEXT, reasoning TEXT,
      reasoning_content TEXT, reasoning_details TEXT, codex_reasoning_items TEXT, content TEXT);
    INSERT INTO sessions VALUES('old',100,150,1,1,0,0,0),('new',1000,NULL,0,3,42,10,20);
    INSERT INTO messages(session_id,role,timestamp,tool_name,reasoning) VALUES
      ('new','user',1000,NULL,NULL),('new','assistant',1001,NULL,'think'),('new','tool',1002,'terminal',NULL),
      ('new','tool',1003,'terminal',NULL),('new','assistant',1004,NULL,NULL),('new','user',1010,NULL,NULL),
      ('new','assistant',1030,NULL,'more'),('new','tool',1090,'clarify',NULL),('new','assistant',1100,NULL,NULL);
    INSERT INTO messages(session_id,role,timestamp,tool_name,content) VALUES
      ('new','tool',1005,'skill_view','{"name": "known-errors", "content": "xxxxxxxxxx"}'),
      ('new','tool',1006,'skill_view','{"name": "catch-up", "content": "yyyy"}');
    """)
    r = measure(c)
    assert r["session"] == "new", r
    assert r["seconds"] == 100 and r["active_seconds"] == 40 and r["assistant_msgs_with_reasoning"] == 2, r
    assert r["tool_calls"] == 5 and r["questions_to_user"] == 2 and r["tools"]["terminal"] == 2, r
    assert r["foreign_skills"].startswith("known-errors(") and r["foreign_skill_bytes"] == 49, r
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile")
    ap.add_argument("--db")
    ap.add_argument("--session", help="one session id")
    ap.add_argument("--sessions", help="comma-separated ids: each row printed, then a TOTAL row")
    ap.add_argument("--last", nargs="?", const=1, type=int, help="the newest N sessions (default 1)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(); sys.exit(0)
    path = a.db or db_path(a.profile or sys.exit("--profile or --db required"))
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    if a.sessions or (a.last and a.last > 1):
        ids = a.sessions.split(",") if a.sessions else [r[0] for r in conn.execute(
            "SELECT id FROM sessions ORDER BY started_at DESC LIMIT ?", (a.last,))][::-1]
        rows = [measure(conn, s.strip()) for s in ids]
        for r in rows:
            report(r)
        total = {k: sum(r[k] for r in rows) for k in ("seconds", "active_seconds", "api_calls", "tool_calls",
                 "assistant_msgs_with_reasoning", "reasoning_tok", "in_tok", "out_tok", "questions_to_user", "foreign_skill_bytes")}
        total.update(session="TOTAL", tools=sum((r["tools"] for r in rows), Counter()),
                     foreign_skills="; ".join(r["foreign_skills"] for r in rows))
        print()
        report(total)
    else:
        report(measure(conn, None if a.last or not a.session else a.session))
