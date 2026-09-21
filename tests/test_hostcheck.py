from __future__ import annotations

import os
from unittest.mock import patch

from common import WorkspaceTest
import hostcheck
from verification import doctor

SOUL = """# Test profile
## Порядок работы
1. Прочитай скилл `commit-everything` перед любой задачей.
## Коммуникация
В конце каждого ответа добавляй блок `🟢 Простыми словами:` из 2–4 фраз.
Для прототипов тесты не нужны.
Commit after every file change and push automatically.
"""
SKILL = """---
name: commit-everything
---
Never edit docs/ without the owner's explicit command. Verify with a throwaway script before finishing.
"""
KEYS = ("footer@SOUL.md", "preread@SOUL.md", "notests@SOUL.md", "commit@SOUL.md",
        "docsban@commit-everything/SKILL.md", "verify@commit-everything/SKILL.md")


class HostcheckTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.init()
        self.home = self.base / "hermes-home"
        skill_dir = self.home / "skills" / "software-development" / "commit-everything"
        skill_dir.mkdir(parents=True)
        (self.home / "SOUL.md").write_text(SOUL, encoding="utf-8")
        (skill_dir / "SKILL.md").write_text(SKILL, encoding="utf-8")
        env = patch.dict(os.environ, {"HERMES_HOME": str(self.home), "HOME": str(self.base), "USERPROFILE": str(self.base)})
        env.start()
        self.addCleanup(env.stop)

    def record(self, *keys):
        project = self.target / "PROJECT.md"
        text = project.read_text(encoding="utf-8").replace("- (none recorded)", "\n".join(f"- {k}: replaced 2026-09-21" for k in keys))
        project.write_text(text, encoding="utf-8")

    def test_conflicts_found_in_soul_and_in_the_skill_it_names(self):
        self.assertEqual({hostcheck.key(c) for c in hostcheck.scan(self.target)}, set(KEYS))

    def test_doctor_warns_until_decisions_are_recorded(self):
        unresolved, resolved = hostcheck.report(self.target)
        self.assertEqual(len(unresolved), 6)
        self.assertTrue(all(w.startswith("HOST CONFLICT") and "Fix:" in w for w in unresolved))
        self.assertEqual(sum(1 for w in doctor(self.target)["warnings"] if w.startswith("HOST CONFLICT")), 6)
        self.record(*KEYS)
        unresolved, resolved = hostcheck.report(self.target)
        self.assertEqual(unresolved, [])
        self.assertEqual(len(resolved), 6)
        self.assertFalse([w for w in doctor(self.target)["warnings"] if w.startswith("HOST CONFLICT")])

    def test_rule_added_after_install_surfaces_again(self):
        self.record(*KEYS)
        self.assertEqual(hostcheck.report(self.target)[0], [])
        with open(self.home / "SOUL.md", "a", encoding="utf-8") as f:
            f.write("\nDo not edit the docs folder.\n")
        unresolved = hostcheck.report(self.target)[0]
        self.assertEqual(len(unresolved), 1)
        self.assertIn("docsban@SOUL.md", unresolved[0])

    def test_opt_out_env(self):
        with patch.dict(os.environ, {"DEVFRAMEWORK_HOSTCHECK": "0"}):
            self.assertEqual(hostcheck.report(self.target), ([], []))
