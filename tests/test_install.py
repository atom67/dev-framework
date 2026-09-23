"""Installer and plugin packaging: what a user gets, and that updates never clobber their work."""
from __future__ import annotations

import importlib.util
import json

from common import ROOT, WorkspaceTest, install
from verification import doctor, installed_kind

VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
NEWER = ".".join(str(n + (i == 2)) for i, n in enumerate(map(int, VERSION.split("."))))


class InstallTests(WorkspaceTest):
    def test_preview_seed_update_and_conflicts(self):
        self.assertTrue(self.init(dry_run=True)["dry_run"])
        self.assertFalse(self.target.exists(), "a preview creates nothing")
        with self.assertRaises(ValueError):
            self.init(scale="ten users")
        self.assertFalse(self.target.exists(), "bad parameters fail before any write")

        self.assertFalse(self.init()["conflicts"])
        for relative in ("AGENTS.md", "CLAUDE.md", "PROJECT.md", "docs/USE_CASES.md", ".devframework/check.py",
                         ".devframework/LESSONS.md"):
            self.assertTrue((self.target / relative).is_file(), relative)
        self.assertFalse((self.target / ".hermes.md").exists(), "only the Hermes plugin asks for its context file")
        self.assertIn("**14,400,000 requests/day**", (self.target / "PROJECT.md").read_text(encoding="utf-8"))
        config = json.loads((self.target / ".devframework/project.json").read_text(encoding="utf-8"))
        self.assertEqual(config["testing"], "advanced", "a product at 10,000 users is recommended advanced testing")
        (self.target / ".devframework/project.json").write_text(json.dumps({**config, "testing": "lean"}), encoding="utf-8")
        self.assertTrue(any("advanced is recommended" in w for w in doctor(self.target)["warnings"]),
                        "lean at tens of thousands of users is flagged, not blocked")
        with self.assertRaisesRegex(ValueError, "Already installed"):
            self.init()

        project = self.target / "PROJECT.md"
        project.write_text("Our facts\n", encoding="utf-8")
        source = self.package_copy()  # a newer package in which one framework rule changed
        rule = source / "template/AGENTS.md"
        rule.write_text(rule.read_text(encoding="utf-8") + "\nNew rule.\n", encoding="utf-8")
        (source / "VERSION").write_text(NEWER + "\n", encoding="utf-8")
        self.assertFalse(install.install(self.target, source=source, update=True)["conflicts"])
        self.assertIn("New rule.", (self.target / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual(project.read_text(encoding="utf-8"), "Our facts\n", "project documents are never overwritten")

        self.write("AGENTS.md", "Local rule")
        self.assertIn("AGENTS.md", install.install(self.target, source=source, update=True)["conflicts"])
        self.assertEqual((self.target / "AGENTS.md").read_text(encoding="utf-8"), "Local rule", "a conflict writes nothing")
        backup = install.install(self.target, source=source, update=True, force=True)["backup"]
        self.assertEqual((self.target / backup / "files/AGENTS.md").read_text(encoding="utf-8"), "Local rule")
        self.assertIn("New rule.", (self.target / "AGENTS.md").read_text(encoding="utf-8"))

        legacy = self.base / "legacy"
        self.write("AGENTS.md", "Existing rules", root=legacy)
        self.assertEqual(install.install(legacy, name="Legacy")["conflicts"], ["AGENTS.md"])
        self.assertEqual([p.name for p in legacy.iterdir()], ["AGENTS.md"], "a foreign AGENTS.md stops the install")

    def test_kinds_only_grow_and_old_manifests_still_update(self):
        self.init(kind="explore")
        for absent in ("docs/USE_CASES.md", "docs/GUIDE.html"):
            self.assertFalse((self.target / absent).exists(), absent)
        config = json.loads((self.target / ".devframework/project.json").read_text(encoding="utf-8"))
        self.assertEqual(config["testing"], "lean", "explorations and tools test lean")
        project = self.target / "PROJECT.md"
        project.write_text(project.read_text(encoding="utf-8") + "\nOur intent survives promotion.\n", encoding="utf-8")
        install.install(self.target, update=True, kind="tool")
        self.assertTrue((self.target / "docs/GUIDE.html").exists())
        with self.assertRaisesRegex(ValueError, "scale"):
            install.install(self.target, update=True, kind="product")
        install.install(self.target, update=True, kind="product", scale="100 users")
        self.assertTrue((self.target / "docs/USE_CASES.md").exists())
        self.assertIn("Our intent survives promotion.", project.read_text(encoding="utf-8"))
        self.assertEqual(installed_kind(self.target), "product")
        with self.assertRaisesRegex(ValueError, "never shrinks"):
            install.install(self.target, update=True, kind="tool")

        legacy = self.base / "legacy"  # written before kinds (1.3.0) and the hermes flag (1.5.0), with .hermes.md
        install.install(legacy, name="Old", hermes=True)
        path = legacy / ".devframework/manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        del manifest["parameters"]["kind"], manifest["parameters"]["hermes"]
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(installed_kind(legacy), "product")
        install.install(legacy, update=True)
        updated = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(updated["parameters"]["hermes"] and ".hermes.md" in updated["files"], "a host is never dropped")

    def test_plugin_manifests_agree_and_hermes_tools_work(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], VERSION)
        self.assertIn(f"version: {VERSION}", (ROOT / "plugin.yaml").read_text(encoding="utf-8"))
        self.assertEqual(market["plugins"][0]["source"], "./")
        for name in ("init", "check", "nav"):  # skills hold the procedures; commands are one-line aliases
            skill = (ROOT / f"skills/df-{name}/SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(skill.startswith(f"---\nname: df-{name}\n"), name)
            self.assertIn(f"dev-framework:df-{name}", (ROOT / f"commands/{name}.md").read_text(encoding="utf-8"))
        hook = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]["SessionStart"][0]["hooks"][0]
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/scripts/session_start.py", hook["command"])

        spec = importlib.util.spec_from_file_location("devframework_hermes", ROOT / "__init__.py")
        hermes = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hermes)
        target = str(self.target)
        self.assertTrue(hermes.df_init({"target": target, "kind": "tool"}).startswith("INIT OK"))
        self.assertTrue((self.target / ".hermes.md").is_file(), "the Hermes plugin installs its context file")
        self.assertTrue(hermes.df_check({"target": target, "mode": "doctor"}).startswith("doctor NOT READY"))
        self.assertIn("session brief", hermes.df_nav({"target": target, "command": "brief"}))
