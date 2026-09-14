from __future__ import annotations

import shutil
import subprocess
import sys

from common import ROOT, WorkspaceTest
from verification import doctor


class PackageTests(WorkspaceTest):
    def test_knowledge_map_ids_sources_and_destinations(self):
        import re
        self.init()
        text = (self.target / ".devframework/KNOWLEDGE_MAP.md").read_text(encoding="utf-8")
        rows = re.findall(r"(?m)^\| (K-\d{3}) \| (.+)$", text)
        self.assertEqual(len(rows), 24)
        self.assertEqual(len({key for key, _ in rows}), len(rows))
        sources = re.findall(r"(?m)^\| (S\d{2}) \|.*? ([0-9a-f]{64}) \|$", text)
        self.assertEqual(len(sources), 5)
        for _, row in rows:
            self.assertTrue(re.search(r"\[[^]]+\]\([^)]+\)", row))
            for source in re.findall(r"\bS\d{2}\b", row):
                self.assertIn(source, {name for name, _ in sources})
        self.assertEqual(doctor(self.target)["errors"], [])

    def test_each_profile_installs_consistent_documents(self):
        import install
        for profile in install.PROFILES:
            with self.subTest(profile=profile):
                target = self.base / profile
                install.install(target, name="Profile fixture", profile=profile)
                self.assertEqual(doctor(target)["errors"], [])

    def test_python_cli_preview(self):
        run = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/install.py"), "--target", str(self.target),
                              "--name", "CLI fixture", "--dry-run"], capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("PREVIEW ONLY", run.stdout)
        self.assertFalse(self.target.exists())

    def test_powershell_wrapper_preview(self):
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("PowerShell wrapper unavailable on this test host")
        run = subprocess.run([pwsh, "-NoProfile", "-File", str(ROOT / "install.ps1"), "-Target", str(self.target),
                              "-ProjectName", 'Wrapper "quotes" fixture', "-ScaleTarget", "50,000 users", "-DryRun"],
                             capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("PREVIEW ONLY", run.stdout)
        self.assertFalse(self.target.exists())

    def test_no_reference_to_uninstalled_external_knowledge(self):
        self.init()
        import verification
        self.assertEqual(verification.doctor(self.target)["errors"], [])
        self.assertIn("12. Clearing an outbox", (self.target / ".devframework/LESSONS.md").read_text(encoding="utf-8"))
        self.assertNotIn("reflectively instead", (self.target / ".devframework/LESSONS.md").read_text(encoding="utf-8"))

    def test_wrapper_install_and_update(self):
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("PowerShell wrapper unavailable on this test host")
        base = [pwsh, "-NoProfile", "-File", str(ROOT / "install.ps1"), "-Target", str(self.target)]
        run = subprocess.run(base + ["-ProjectName", "Wrapper fixture", "-Profile", "service"],
                             capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        run = subprocess.run(base + ["-Update"], capture_output=True, text=True, timeout=30)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn('"backup": null', run.stdout)

    def test_protocol_section_references_exist(self):
        import re
        protocol = (ROOT / "template/AGENTS.md").read_text(encoding="utf-8")
        sections = set(re.findall(r"(?m)^## (\d+)\.", protocol))
        for path in (ROOT / "template/docs").glob("*.md"):
            for reference in re.findall(r"`AGENTS\.md`\s+section (\d+)", path.read_text(encoding="utf-8")):
                self.assertIn(reference, sections, str(path))
