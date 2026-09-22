from __future__ import annotations

import subprocess
import sys

from common import WorkspaceTest
import navigate

UC = """
## Module A

#### UC-101 — Add a note
- **Trigger:** Interactive
- **Test:** covered — `tests/test_a.py::T.test_add`

#### UC-102 — List notes
- **Trigger:** Interactive
- **Test:** gap — no test yet
"""
KE = """
## Open

### KE-2026-09-21-DEMO-SLUG — demo defect

**Where:** app.py:1
**Status:** not fixed

## Fixed

### KE-2026-09-20-OLD-SLUG — old defect

**Status:** fixed in abc123
"""


class NavigateTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.git_init()
        self.init()
        self.configure()
        uc = self.target / "docs/USE_CASES.md"
        text = uc.read_text(encoding="utf-8")
        head, trace = text.split("## Traceability", 1)
        rows = "|---|---|---|---|---|\n| UC-101 | Interactive | FR-001 | app | covered |\n| UC-102 | Interactive | FR-001 | app | gap |"
        uc.write_text(head + UC + "\n## Traceability" + trace.replace("|---|---|---|---|---|", rows, 1), encoding="utf-8")
        ke = self.target / "docs/KNOWN_ERRORS.md"
        ke.write_text(ke.read_text(encoding="utf-8").split("## Open")[0] + KE, encoding="utf-8")

    def nav(self, *args):
        run = subprocess.run([sys.executable, "-B", str(self.target / ".devframework/navigate.py"), *args],
                             cwd=self.target, capture_output=True, text=True, encoding="utf-8", timeout=60)
        return run.returncode, run.stdout

    def test_blocks_skip_template_examples_and_fenced_code(self):
        ids = [ident for _, ident, _, _ in navigate.blocks(self.target)]
        self.assertEqual(ids, ["UC-101", "UC-102", "KE-2026-09-21-DEMO-SLUG", "KE-2026-09-20-OLD-SLUG"])

    def test_brief_reports_gaps_open_errors_and_git(self):
        code, out = self.nav("brief")
        self.assertEqual(code, 0, out)
        self.assertIn("use cases: 2, without covering test: UC-102", out)
        self.assertIn("open known errors: 1", out)
        self.assertIn("KE-2026-09-21-DEMO-SLUG", out)
        self.assertNotIn("OLD-SLUG", out)
        self.assertIn("git: main", out)
        self.assertLess(out.count("\n"), 25, "the brief must stay one screen")

    def test_brief_reports_commits_behind_upstream(self):
        self.git("add", "."); self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
        bare = self.base / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", "--initial-branch=main", str(bare)], check=True, timeout=30)
        self.addCleanup(self.unlock, bare, self.base / "other")  # git objects are read-only; cleanup must delete them
        self.git("remote", "add", "origin", str(bare)); self.git("push", "-q", "-u", "origin", "main")
        self.assertIn("remote: up to date with origin/main", self.nav("brief")[1])
        other = self.base / "other"
        subprocess.run(["git", "clone", "-q", str(bare), str(other)], check=True, timeout=30)
        (other / "teammate.txt").write_text("hello\n", encoding="utf-8")
        for args in (["add", "."], ["-c", "user.name=o", "-c", "user.email=o@o", "commit", "-q", "-m", "teammate change"], ["push", "-q"]):
            subprocess.run(["git", "-C", str(other), *args], check=True, timeout=30, capture_output=True)
        out = self.nav("brief")[1]
        self.assertIn("BEHIND origin/main by 1 commit(s)", out)
        self.assertIn("teammate change", out)

    def test_brief_keeps_non_ascii_commit_subjects_readable(self):
        subject = "fix: em dash — тест"  # git writes UTF-8; a cp1251 console must not mangle it
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", subject)
        self.assertIn(subject, self.nav("brief")[1])

    @staticmethod
    def unlock(*roots):
        import os, stat
        for root in roots:
            for path in root.rglob("*"):
                # directories keep the execute bit: without it Linux cannot enter them to delete anything
                os.chmod(path, stat.S_IRWXU if path.is_dir() else stat.S_IWRITE | stat.S_IREAD)

    def test_find_returns_one_block_or_hits(self):
        code, out = self.nav("find", "UC-102")
        self.assertEqual(code, 0)
        self.assertIn("List notes", out)
        self.assertIn("gap", out)
        self.assertNotIn("UC-101", out)
        _, out = self.nav("find", "note")
        self.assertIn("UC-101", out)
        self.assertIn("UC-102", out)
        _, out = self.nav("find", "zzz-nothing")
        self.assertIn("no match", out)

    def test_index_is_deterministic_and_regenerated_by_finish(self):
        navigate.index(self.target)
        first = (self.target / "docs/INDEX.md").read_bytes()
        self.assertIn(b"| UC-102 | List notes | gap", first)
        self.assertNotIn(b"\r\n", first)
        self.git("add", ".")
        self.assertEqual(self.checker("finish").returncode, 0)
        self.assertEqual((self.target / "docs/INDEX.md").read_bytes(), first)

    def test_checklist_lifecycle_and_handoff(self):
        self.assertEqual(self.nav("checklist", "show")[1].strip(), "no active checklist")
        self.assertEqual(self.nav("checklist", "new", "v1", "first programme")[0], 0)
        self.nav("checklist", "add", "v1", "write the parser")
        self.nav("checklist", "add", "v1", "write the tests")
        code, out = self.nav("checklist", "tick", "v1", "1")
        self.assertEqual(code, 0, out)
        self.assertIn("1 open: write the tests", out)
        code, out = self.nav("handoff", "v1", "--note", "parser done")
        self.assertEqual(code, 0, out)
        self.assertIn("next: [2] write the tests", out)
        self.assertIn("parser done", (self.target / "docs/v1.md").read_text(encoding="utf-8"))
        _, out = self.nav("brief")
        self.assertIn("checklist docs/v1.md: 1 open", out)
        self.assertEqual(self.nav("checklist", "archive", "v1")[0], 1, "open items block archiving")
        self.nav("checklist", "tick", "v1", "2")
        self.assertEqual(self.nav("checklist", "archive", "v1")[0], 0)
        self.assertTrue((self.target / "docs/archive/v1.md").exists())
        self.assertFalse((self.target / "docs/v1.md").exists())

    def test_selftest_proves_gates_fire(self):
        self.git("add", ".")
        run = self.checker("selftest")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(run.stdout.count("PASS"), 2, run.stdout)

    def test_quiet_finish_logs_child_output_and_shows_tail_on_failure(self):
        self.git("add", ".")
        self.write("tests/test_fixture.py", "import unittest\nclass F(unittest.TestCase):\n    def test_bad(self):\n        self.fail('planted')\n")
        run = self.checker("finish")
        self.assertEqual(run.returncode, 1)
        self.assertIn("planted", run.stderr)
        self.assertIn("full output: .devframework/last_run.log", run.stderr)
        self.assertIn("planted", (self.target / ".devframework/last_run.log").read_text(encoding="utf-8", errors="replace"))
        self.assertNotIn("planted", run.stdout)
