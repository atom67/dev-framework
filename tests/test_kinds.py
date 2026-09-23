from __future__ import annotations

import json

from common import WorkspaceTest
import install
from verification import installed_kind


class KindTests(WorkspaceTest):
    """product / tool / explore: what is being built decides the documents and the proof."""

    def fill(self, *relative):
        for name in relative:
            path = self.target / name
            path.write_text(path.read_text(encoding="utf-8").replace("TODO(project):", "Filled:"), encoding="utf-8")

    def project_json(self, **changes):
        path = self.target / ".devframework/project.json"
        value = {**json.loads(path.read_text(encoding="utf-8")), **changes}
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_tool_is_proven_by_running_it_on_examples(self):
        self.git_init()
        self.init(kind="tool")
        for product_only in ("docs/USE_CASES.md", "docs/BACKLOG.md", "docs/REQUIREMENTS.md", "docs/REGRESSION_TEST.md"):
            self.assertFalse((self.target / product_only).exists(), product_only)
        agents = (self.target / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("docs/GUIDE.html", agents)
        self.assertNotIn("docs/USE_CASES.md", agents)
        doctor = self.checker("doctor").stdout
        self.assertIn("GUIDE.html", doctor)
        self.assertIn("smoke", doctor)

        self.fill("PROJECT.md", "docs/GUIDE.html")
        self.write("tool.py", "import sys\nprint(int(sys.argv[1]) * 2)\n")
        self.project_json(smoke=[{"name": "doubles", "run": ["{python}", "tool.py", "21"], "expect_contains": "42"}])
        run = self.checker("finish")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("1 total, 0 skipped", run.stdout)
        self.project_json(smoke=[{"name": "doubles", "run": ["{python}", "tool.py", "21"], "expect_contains": "43"}])
        self.assertEqual(self.checker("finish").returncode, 1, "a wrong example must fail the gate")

    def test_explore_needs_no_tests_and_says_so(self):
        self.git_init()
        self.init(kind="explore")
        self.assertFalse((self.target / "docs/GUIDE.html").exists())
        self.assertFalse((self.target / "docs/USE_CASES.md").exists())
        self.fill("PROJECT.md")
        run = self.checker("finish")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("behaviour is NOT proven", run.stdout)

    def test_promotion_adds_documents_keeps_project_facts_and_never_goes_back(self):
        self.init(kind="explore")
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

    def test_installation_from_before_kinds_reads_as_product(self):
        self.init()
        manifest_path = self.target / ".devframework/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["parameters"]["kind"]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(installed_kind(self.target), "product")
        install.install(self.target, update=True)  # an older manifest updates cleanly
        self.assertEqual(installed_kind(self.target), "product")
