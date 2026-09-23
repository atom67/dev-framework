"""What the agent reads: the brief, one block, checklists, the session hook, host-rule conflicts, the devlog."""
from __future__ import annotations

from contextlib import closing
from datetime import date
import json
import os
import sqlite3
import stat
import subprocess
import sys
from unittest.mock import patch

from common import ROOT, WorkspaceTest
import hostcheck
import transcript
from verification import doctor

UC = """
## Module A

#### UC-101 — Add a note
- **Trigger:** Interactive
- **Test:** `covered` — `tests/test_a.py::T.test_add`

#### UC-102 — List notes
- **Trigger:** Interactive
- **Test:** gap — no test yet
"""
KE = """
## Open

### KE-2026-09-21-DEMO-SLUG — demo defect

**Status:** not fixed

## Fixed

### KE-2026-09-20-OLD-SLUG — old defect

**Status:** fixed in abc123
"""
SOUL = """# Test profile
1. Прочитай скилл `commit-everything` перед любой задачей.
В конце каждого ответа добавляй блок `🟢 Простыми словами:`.
"""
TODAY = date.today()


def unlock(*roots):
    for root in roots:  # git objects are read-only; Linux also needs the directory x-bit to delete them
        for path in root.rglob("*"):
            os.chmod(path, stat.S_IRWXU if path.is_dir() else stat.S_IWRITE | stat.S_IREAD)


class AgentTests(WorkspaceTest):
    def nav(self, *args):
        run = subprocess.run([sys.executable, "-B", str(self.target / ".devframework/navigate.py"), *args],
                             cwd=self.target, capture_output=True, text=True, encoding="utf-8", timeout=60)
        return run.returncode, run.stdout

    def hook(self, cwd):
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "CLAUDE_PROJECT_DIR": str(cwd)}
        run = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/session_start.py")], cwd=cwd, env=env,
                             capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        return run.stdout

    def test_brief_one_block_remote_state_and_checklist(self):
        self.git_init()
        self.init()
        self.configure()
        cases = self.target / "docs/USE_CASES.md"
        head, trace = cases.read_text(encoding="utf-8").split("## Traceability", 1)
        rows = "|---|---|---|---|---|\n| UC-101 | Interactive | FR-001 | app | covered |\n| UC-102 | Interactive | FR-001 | app | gap |"
        cases.write_text(head + UC + "\n## Traceability" + trace.replace("|---|---|---|---|---|", rows, 1), encoding="utf-8")
        errors = self.target / "docs/KNOWN_ERRORS.md"
        errors.write_text(errors.read_text(encoding="utf-8").split("## Open")[0] + KE, encoding="utf-8")

        code, out = self.nav("brief")
        self.assertEqual(code, 0, out)
        for expected in ("use cases: 2, without covering test: UC-102", "open known errors: 1", "KE-2026-09-21-DEMO-SLUG",
                         "testing: advanced"):
            self.assertIn(expected, out)
        self.assertNotIn("OLD-SLUG", out)
        self.assertLess(out.count("\n"), 25, "the brief stays one screen")
        self.git("add", ".")
        run = subprocess.run([sys.executable, "-B", str(self.target / ".devframework/check.py"), "commit-check"],
                             cwd=self.target, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(run.returncode, 1)
        self.assertIn("COMMIT BLOCKED (advanced testing): use cases without a covering test: UC-102", run.stdout)
        _, out = self.nav("find", "UC-102")
        self.assertIn("List notes", out)
        self.assertNotIn("UC-101", out, "find returns one block, not the file")

        subject = "base — тест"  # git speaks UTF-8; a cp1251 console must not mangle it
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", subject)
        self.assertIn(subject, self.nav("brief")[1])
        bare, other = self.base / "remote.git", self.base / "other"
        subprocess.run(["git", "init", "-q", "--bare", "--initial-branch=main", str(bare)], check=True, timeout=30)
        self.addCleanup(unlock, bare, other)
        self.git("remote", "add", "origin", str(bare))
        self.git("push", "-q", "-u", "origin", "main")
        subprocess.run(["git", "clone", "-q", str(bare), str(other)], check=True, timeout=30)
        (other / "teammate.txt").write_text("hello\n", encoding="utf-8")
        for args in (["add", "."], ["-c", "user.name=o", "-c", "user.email=o@o", "commit", "-q", "-m", "teammate change"], ["push", "-q"]):
            subprocess.run(["git", "-C", str(other), *args], check=True, timeout=30, capture_output=True)
        out = self.nav("brief")[1]
        self.assertIn("BEHIND origin/main by 1 commit(s)", out)
        self.assertIn("teammate change", out)
        self.git("remote", "set-url", "origin", str(self.base / "unreachable.git"))  # offline / sandbox without network
        out = self.nav("brief")[1]
        self.assertIn("remote: NOT CHECKED (fetch failed", out)
        self.assertNotIn("up to date", out)

        self.nav("checklist", "new", "v1", "first programme")
        self.nav("checklist", "add", "v1", "write the parser")
        self.nav("checklist", "add", "v1", "write the tests")
        self.assertIn("1 open: write the tests", self.nav("checklist", "tick", "v1", "1")[1])
        self.assertIn("next: [2] write the tests", self.nav("handoff", "v1", "--note", "parser done")[1])
        self.assertIn("checklist docs/v1.md: 1 open", self.nav("brief")[1])
        self.assertEqual(self.nav("checklist", "archive", "v1")[0], 1, "open items block archiving")
        self.nav("checklist", "tick", "v1", "2")
        self.assertEqual(self.nav("checklist", "archive", "v1")[0], 0)
        self.assertTrue((self.target / "docs/archive/v1.md").exists())

    def test_session_hook_briefs_only_its_own_project_and_runs_no_project_code(self):
        self.assertEqual(self.hook(self.base), "", "silent outside a framework project")
        self.init()
        self.assertIn("session brief", self.hook(self.target / "docs"), "a subdirectory finds its project")
        child = self.target / "other-project"
        (child / ".git").mkdir(parents=True)
        self.assertEqual(self.hook(child), "", "the project ends at its git root")
        marker = self.base / "pwned.txt"
        (self.target / ".devframework/navigate.py").write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('ran')\n", encoding="utf-8")
        self.assertIn("session brief", self.hook(self.target), "the plugin's own navigator reads the documents")
        self.assertFalse(marker.exists(), "code from the opened repository never runs at session start")

    def test_host_rules_that_fight_the_framework_until_the_operator_decides(self):
        self.init()
        home = self.base / "home"
        skill = home / ".hermes/skills/dev/commit-everything"
        skill.mkdir(parents=True)
        (home / ".hermes/SOUL.md").write_text(SOUL, encoding="utf-8")
        (skill / "SKILL.md").write_text("---\nname: commit-everything\n---\nCommit after every file change.\n", encoding="utf-8")
        (home / ".config/opencode").mkdir(parents=True)
        (home / ".config/opencode/AGENTS.md").write_text("Skip the tests, ship fast.\n", encoding="utf-8")
        (self.target / "AGENTS.override.md").write_text("# Local\n", encoding="utf-8")
        with patch.dict(os.environ, {"HOME": str(home), "USERPROFILE": str(home), "HERMES_HOME": ""}):
            keys = {hostcheck.key(c) for c in hostcheck.scan(self.target)}
            self.assertEqual(keys, {"preread@SOUL.md", "footer@SOUL.md", "commit@commit-everything/SKILL.md",
                                    "notests@AGENTS.md", "override@AGENTS.override.md"})
            self.assertEqual(sum(w.startswith("HOST CONFLICT") for w in doctor(self.target)["warnings"]), 5)
            project = self.target / "PROJECT.md"
            project.write_text(project.read_text(encoding="utf-8").replace(
                "- (none recorded)", "\n".join(f"- {k}: kept — test" for k in sorted(keys))), encoding="utf-8")
            unresolved, resolved = hostcheck.report(self.target)
            self.assertEqual((unresolved, len(resolved)), ([], 5), "recorded decisions silence the warnings")

    def test_devlog_is_filled_from_the_session_log_without_noise_or_secrets(self):
        self.init(devlog=True)
        stamp = TODAY.isoformat() + "T10:00:00Z"
        planted = "gh" + "p_" + "A" * 36  # synthetic, split so the secret gate does not flag this file
        entry = lambda kind, content, **extra: {"type": kind, "cwd": str(self.target), "timestamp": stamp,
                                                "message": {"content": content}, **extra}
        logs = self.base / "claude/projects/some-project"
        logs.mkdir(parents=True)
        (logs / "session.jsonl").write_text("\n".join(json.dumps(e) for e in [
            entry("user", "<command-message>x</command-message>\n<command-name>/dev-framework:init</command-name>"),
            entry("user", [{"type": "text", "text": "EXPANDED COMMAND PROMPT"}], isMeta=True),
            entry("assistant", [{"type": "thinking", "thinking": "hidden"}, {"type": "tool_use", "name": "Bash", "input": {}}]),
            entry("assistant", [{"type": "text", "text": "subagent chatter"}], isSidechain=True),
            entry("user", "<system-reminder>noise</system-reminder>count the words please"),
            entry("assistant", [{"type": "text", "text": f"done, the key was {planted}"}]),
            {**entry("user", "an older day"), "timestamp": "2000-01-01T00:00:00Z"},
        ]) + "\n", encoding="utf-8")
        with patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": str(self.base / "claude")}):
            text, source = transcript.dialogue(self.target, "auto", TODAY)
        self.assertIn("session.jsonl", source)
        self.assertTrue(text.startswith("**User:** /dev-framework:init\n\n[tools: Bash×1]"), text[:120])
        self.assertIn("**User:** count the words please", text)
        self.assertIn("redacted", text)
        for leaked in ("EXPANDED", "hidden", "subagent chatter", "noise", planted, "an older day"):
            self.assertNotIn(leaked, text)

        hermes = self.base / "hermes"
        hermes.mkdir()
        with closing(sqlite3.connect(hermes / "state.db")) as conn, conn:
            conn.execute("CREATE TABLE sessions (id TEXT, started_at TEXT)")
            conn.execute("CREATE TABLE messages (session_id TEXT, role TEXT, content TEXT, tool_name TEXT, timestamp TEXT)")
            conn.execute("INSERT INTO sessions VALUES ('s1', ?)", (TODAY.isoformat(),))
            conn.executemany("INSERT INTO messages VALUES ('s1', ?, ?, ?, ?)", [
                ("user", "make the tool", None, TODAY.isoformat() + " 10:00"),
                ("tool", "ok", "terminal", TODAY.isoformat() + " 10:01"),
                ("assistant", "made it", None, TODAY.isoformat() + " 10:02")])
        with patch.dict(os.environ, {"HERMES_HOME": str(hermes), "CLAUDE_CONFIG_DIR": str(self.base / "none")}):
            self.assertIsNone(transcript.dialogue(self.target, "auto", TODAY)[0], "auto never guesses a Hermes session")
            self.assertEqual(transcript.dialogue(self.target, "hermes", TODAY)[0],
                             "**User:** make the tool\n\n[tools: terminal×1]\n\n**Assistant:** made it")

        run = subprocess.run([sys.executable, "-B", str(self.target / ".devframework/check.py"), "devlog",
                              "--agent", "claudecode-OPUS5", "--dialogue", str(logs / "session.jsonl")],
                             cwd=self.target, capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("dialogue filled from the session log", run.stdout)
        self.assertIn("/docs/devlog/", (self.target / ".gitignore").read_text(encoding="utf-8"),
                      "no known remote: the devlog stays local")
