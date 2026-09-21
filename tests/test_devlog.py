"""Optional Devlog rule: naming (date + agent + codes), header, public-repo gitignore, install opt-in."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from common import ROOT, WorkspaceTest

sys.path.insert(0, str(ROOT / "template" / ".devframework"))
import devlog  # noqa: E402


class DevlogPure(WorkspaceTest):
    def test_file_name_agent_and_code_validation(self):
        self.assertEqual(devlog.file_name(date(2026, 9, 20), ["claudecode-OPUS5"], ["FR-005", "UC-004"]),
                         "2026-09-20_claudecode-OPUS5_FR-005_UC-004.md")
        self.assertEqual(devlog.file_name(date(2026, 9, 20), ["claudecode-OPUS5", "hermes-gpt5.6terra"], ["UC-007"]),
                         "2026-09-20_claudecode-OPUS5+hermes-gpt5.6terra_UC-007.md")
        self.assertEqual(devlog.validate_codes([" fr-005", "UC-004", "FR-005"]), ["FR-005", "UC-004"])
        self.assertEqual(devlog.validate_agents(["claudecode-OPUS5", "claudecode-OPUS5"]), ["claudecode-OPUS5"])
        with self.assertRaises(ValueError):
            devlog.validate_codes(["feature-x"])
        with self.assertRaises(ValueError):
            devlog.validate_agents(["Claude Code / Opus 5"])
        with self.assertRaises(ValueError):
            devlog.validate_agents(["a-A", "b-B", "c-C"])  # more than the two dominant models

    def test_header_lists_agent_commits_and_rejects_long_summary(self):
        text = devlog.header(date(2026, 9, 20), ["claudecode-OPUS5"], ["UC-004"],
                             [("abc1234", "Added the pane. Fed by cli.exec.")], "public repository: local")
        self.assertIn("| Agent(s) | claudecode-OPUS5 |", text)
        self.assertIn("| `abc1234` | Added the pane. Fed by cli.exec. |", text)
        self.assertIn("## Dialogue (verbatim)", text)
        with self.assertRaises(ValueError):
            devlog.header(date(2026, 9, 20), ["claudecode-OPUS5"], ["UC-004"], [("abc1234", "One. Two. Three. Four.")], "x")

    def test_gitignore_added_once(self):
        self.target.mkdir(parents=True)
        self.assertTrue(devlog.ensure_gitignored(self.target, "docs/devlog"))
        self.assertFalse(devlog.ensure_gitignored(self.target, "docs/devlog"))
        self.assertEqual((self.target / ".gitignore").read_text(encoding="utf-8"), "/docs/devlog/\n")


class DevlogInstall(WorkspaceTest):
    def test_install_default_off(self):
        self.init(scale="1,000 users")
        cfg = json.loads((self.target / ".devframework" / "project.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["devlog"], {"enabled": False, "dir": "docs/devlog", "commit": False})
        ignore = (self.target / ".gitignore").read_text(encoding="utf-8")  # seeded, but no devlog line
        self.assertIn("__pycache__/", ignore)
        self.assertNotIn("devlog", ignore)

    def test_opt_in_without_remote_keeps_local_and_ignores_dir(self):
        self.init(scale="1,000 users", devlog=True)
        cfg = json.loads((self.target / ".devframework" / "project.json").read_text(encoding="utf-8"))
        self.assertTrue(cfg["devlog"]["enabled"])
        # No git remote -> visibility unknown -> local only from the first minute.
        self.assertIn("/docs/devlog/", (self.target / ".gitignore").read_text(encoding="utf-8"))

    def test_entry_created_with_header_and_reminder_cleared(self):
        self.init(scale="1,000 users", devlog=True)
        self.assertIsNotNone(devlog.missing_today(self.target))
        path = devlog.new_entry(self.target, date.today(), ["claudecode-OPUS5"], ["UC-009"], [("deadbee", "Devlog rule added.")])
        self.assertTrue(path.name.endswith("_claudecode-OPUS5_UC-009.md"))
        text = path.read_text(encoding="utf-8")
        self.assertIn("| `deadbee` | Devlog rule added. |", text)
        self.assertIn("unknown repository: devlog stays local", text)
        self.assertIsNone(devlog.missing_today(self.target))
        with self.assertRaises(ValueError):
            devlog.new_entry(self.target, date.today(), ["claudecode-OPUS5"], ["UC-009"], [])

    def test_disabled_rule_refuses_entry_and_is_silent(self):
        self.init(scale="1,000 users")
        self.assertIsNone(devlog.missing_today(self.target))
        with self.assertRaises(ValueError):
            devlog.new_entry(self.target, date.today(), ["claudecode-OPUS5"], ["UC-009"], [])

    def test_check_py_devlog_subcommand(self):
        self.init(scale="1,000 users", devlog=True)
        result = subprocess.run([sys.executable, "-B", str(self.target / ".devframework" / "check.py"),
                                 "devlog", "--agent", "claudecode-OPUS5", "--codes", "FR-015,UC-009",
                                 "--commit", "abc1234=Rule wired.", "--date", "2026-09-20"],
                                capture_output=True, text=True, timeout=60, cwd=self.target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DEVLOG CREATED: docs/devlog/2026-09-20_claudecode-OPUS5_FR-015_UC-009.md", result.stdout)
        self.assertTrue((self.target / "docs" / "devlog" / "2026-09-20_claudecode-OPUS5_FR-015_UC-009.md").exists())
