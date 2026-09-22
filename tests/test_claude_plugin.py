from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from common import ROOT, WorkspaceTest

HOOK = ROOT / "scripts" / "claude_session_start.py"


class ManifestTests(unittest.TestCase):
    def test_plugin_and_marketplace_manifests_agree_with_the_package(self):
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        hermes = (ROOT / "plugin.yaml").read_text(encoding="utf-8")
        self.assertEqual(plugin["name"], "dev-framework")
        self.assertEqual(plugin["version"], (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        self.assertIn(f"version: {plugin['version']}", hermes, "Hermes and Claude Code manifests must ship the same version")
        self.assertEqual([p["name"] for p in market["plugins"]], ["dev-framework"])
        self.assertEqual(market["plugins"][0]["source"], "./", "the repository is its own marketplace")
        self.assertTrue(market["owner"]["name"])

    def test_components_exist_where_claude_code_discovers_them(self):
        for relative in ("skills/df-import/SKILL.md", "skills/df-catch-up/SKILL.md",
                         "commands/init.md", "commands/check.md", "commands/nav.md", "hooks/hooks.json"):
            self.assertTrue((ROOT / relative).is_file(), relative)
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        command = hooks["hooks"]["SessionStart"][0]["hooks"][0]
        self.assertEqual(command["type"], "command")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", command["command"])
        self.assertIn("claude_session_start.py", command["command"])


class SessionStartHookTests(WorkspaceTest):
    def run_hook(self, cwd: Path, project_dir: Path | None = None):
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        env["CLAUDE_PROJECT_DIR"] = str(project_dir) if project_dir else str(cwd)
        return subprocess.run([sys.executable, "-B", str(HOOK)], cwd=str(cwd), env=env,
                              capture_output=True, text=True, encoding="utf-8", timeout=120)

    def test_silent_outside_a_framework_project(self):
        run = self.run_hook(self.base)
        self.assertEqual(run.returncode, 0)
        self.assertEqual(run.stdout.strip(), "", "a hook must add nothing to an unrelated session")

    def test_prints_the_brief_from_a_subdirectory_of_a_framework_project(self):
        self.init()
        nested = self.target / "docs"
        run = self.run_hook(nested, project_dir=nested)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("session brief", run.stdout)
        self.assertIn("doctor:", run.stdout)
        self.assertLess(len(run.stdout), 4500, "the injected brief stays one screen")
