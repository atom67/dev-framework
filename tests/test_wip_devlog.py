from __future__ import annotations

from contextlib import closing
from datetime import date, timedelta
import json
import os
import sqlite3
from unittest import mock

from common import WorkspaceTest
import navigate
import transcript
from verification import doctor, under_construction

TODAY = date.today()


class UnderConstructionTests(WorkspaceTest):
    def mark(self, until: date):
        path = self.target / "docs/ARCHITECTURE.md"
        text = path.read_text(encoding="utf-8")
        body = text.split("\n", 1)[1] if text.startswith("<!--") else text
        path.write_text(f"<!-- under-construction: waits for the storage rework (until {until.isoformat()}) -->\n" + body,
                        encoding="utf-8")

    def test_marker_skips_checks_is_named_everywhere_and_expires(self):
        self.init()
        fill = "Fill project facts in docs/ARCHITECTURE.md"
        self.assertTrue(any(fill in s.replace("\\", "/") for s in doctor(self.target)["setup"]))

        self.mark(TODAY + timedelta(days=30))
        report = doctor(self.target)
        self.assertFalse(any(fill in s.replace("\\", "/") for s in report["setup"]), "checks of a marked document are skipped")
        self.assertIn("docs/ARCHITECTURE.md", report["under_construction"])
        self.assertTrue(any("UNDER CONSTRUCTION" in w and "storage rework" in w for w in report["warnings"]))
        self.assertIn("under construction: docs/ARCHITECTURE.md", navigate.doctor_line(self.target))

        self.mark(TODAY - timedelta(days=1))
        report = doctor(self.target)
        self.assertTrue(any(fill in s.replace("\\", "/") for s in report["setup"]), "an expired marker no longer hides anything")
        self.assertTrue(any("expired" in w for w in report["warnings"]))

        marker = "<!-- under-construction: anything -->"
        self.assertIsNone(under_construction("AGENTS.md", marker), "framework-owned files cannot be marked")
        self.assertIsNone(under_construction(".devframework/VERIFICATION.md", marker))
        self.assertIsNotNone(under_construction("PROJECT.md", marker))


class DevlogDialogueTests(WorkspaceTest):
    def test_claude_session_log_becomes_a_clean_verbatim_dialogue(self):
        self.target.mkdir(parents=True)
        stamp = TODAY.isoformat() + "T10:00:00Z"
        planted = "gh" + "p_" + "A" * 36  # synthetic, split so the secret gate does not flag this file
        entries = [
            {"type": "user", "cwd": str(self.target), "timestamp": stamp, "message": {"content":
                "<command-message>df:init</command-message>\n<command-name>/dev-framework:init</command-name>"}},
            {"type": "user", "isMeta": True, "cwd": str(self.target), "timestamp": stamp,
             "message": {"content": [{"type": "text", "text": "EXPANDED COMMAND PROMPT"}]}},
            {"type": "assistant", "cwd": str(self.target), "timestamp": stamp,
             "message": {"content": [{"type": "text", "text": "Question 1: the name?"}]}},
            {"type": "user", "cwd": str(self.target), "timestamp": stamp,
             "message": {"content": "<system-reminder>noise</system-reminder>count the words please"}},
            {"type": "assistant", "cwd": str(self.target), "timestamp": stamp,
             "message": {"content": [{"type": "thinking", "thinking": "hidden"},
                                     {"type": "tool_use", "name": "Bash", "input": {}}]}},
            {"type": "assistant", "isSidechain": True, "cwd": str(self.target), "timestamp": stamp,
             "message": {"content": [{"type": "text", "text": "subagent chatter"}]}},
            {"type": "assistant", "cwd": str(self.target), "timestamp": stamp,
             "message": {"content": [{"type": "text", "text": f"done, the key was {planted}"}]}},
            {"type": "user", "cwd": str(self.target), "timestamp": "2000-01-01T00:00:00Z",
             "message": {"content": "an older day"}},
        ]
        logs = self.base / "claude" / "projects" / "some-project"
        logs.mkdir(parents=True)
        (logs / "session.jsonl").write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": str(self.base / "claude")}):
            text, source = transcript.dialogue(self.target, "auto", TODAY)
        self.assertIn("session.jsonl", source)
        self.assertTrue(text.startswith("**User:** /dev-framework:init\n\n**Assistant:** Question 1"), text[:120])
        self.assertIn("**User:** count the words please", text)
        self.assertIn("[tools: Bash×1]", text)
        self.assertIn("redacted", text)
        for leaked in ("noise", "hidden", "subagent chatter", planted, "an older day", "EXPANDED", "df:init"):
            self.assertNotIn(leaked, text)

    def test_hermes_state_db_is_read_only_when_named(self):
        home = self.base / "hermes"
        home.mkdir()
        with closing(sqlite3.connect(home / "state.db")) as conn, conn:
            conn.execute("CREATE TABLE sessions (id TEXT, started_at TEXT)")
            conn.execute("CREATE TABLE messages (session_id TEXT, role TEXT, content TEXT, tool_name TEXT, timestamp TEXT)")
            conn.execute("INSERT INTO sessions VALUES ('s1', ?)", (TODAY.isoformat(),))
            conn.executemany("INSERT INTO messages VALUES ('s1', ?, ?, ?, ?)", [
                ("user", "make the tool", None, TODAY.isoformat() + " 10:00"),
                ("tool", "ok", "terminal", TODAY.isoformat() + " 10:01"),
                ("assistant", "made it", None, TODAY.isoformat() + " 10:02")])
        self.target.mkdir(parents=True)
        with mock.patch.dict(os.environ, {"HERMES_HOME": str(home), "CLAUDE_CONFIG_DIR": str(self.base / "none")}):
            self.assertIsNone(transcript.dialogue(self.target, "auto", TODAY)[0], "auto never guesses a Hermes session")
            text, source = transcript.dialogue(self.target, "hermes", TODAY)
        self.assertEqual(source, "Hermes state.db")
        self.assertEqual(text, "**User:** make the tool\n\n[tools: terminal×1]\n\n**Assistant:** made it")
