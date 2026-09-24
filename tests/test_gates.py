"""The gates: doctor reads the documents, finish runs the tests, secrets stop both. One scenario per promise."""
from __future__ import annotations

from datetime import date, timedelta
import json
import re
import subprocess
import sys

from common import WorkspaceTest, install
import navigate
from verification import doctor, under_construction

PASSING = "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n"
FAILING = "import unittest\nclass T(unittest.TestCase):\n    def test_bad(self):\n        self.fail('planted')\n"


class GateTests(WorkspaceTest):
    def run_check(self, *args, root=None):
        root = root or self.target
        return subprocess.run([sys.executable, "-B", str(root / ".devframework/check.py"), *args], cwd=root,
                              capture_output=True, text=True, encoding="utf-8", timeout=120)

    def set_test(self, argv, root=None):
        path = (root or self.target) / ".devframework/project.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        config["commands"]["test"] = argv
        path.write_text(json.dumps(config), encoding="utf-8")

    def fill(self, *relative, root=None):
        for name in relative:
            path = (root or self.target) / name
            path.write_text(path.read_text(encoding="utf-8").replace("TODO(project):", "Filled:"), encoding="utf-8")

    def test_doctor_reads_the_documents(self):
        self.init()
        report = doctor(self.target)
        self.assertEqual((report["errors"], report["ready"]), ([], False), "a fresh scaffold is valid but not ready")
        self.assertEqual(self.run_check("doctor").returncode, 2)

        fill = "Fill project facts in docs/ARCHITECTURE.md"
        architecture = self.target / "docs/ARCHITECTURE.md"
        body = architecture.read_text(encoding="utf-8")
        for until, skipped in ((date.today() + timedelta(days=30), True), (date.today() - timedelta(days=1), False)):
            architecture.write_text(f"<!-- under-construction: storage rework (until {until.isoformat()}) -->\n" + body,
                                    encoding="utf-8")
            report = doctor(self.target)
            self.assertEqual(any(fill in s.replace("\\", "/") for s in report["setup"]), not skipped, until)
            self.assertEqual("under construction: docs/ARCHITECTURE.md" in navigate.doctor_line(self.target), skipped)
        architecture.write_text(body, encoding="utf-8")
        self.assertIsNone(under_construction("AGENTS.md", "<!-- under-construction: x -->"), "framework files cannot be marked")
        self.assertIsNone(under_construction("docs/a.md", "- quoted: <!-- under-construction: x -->"), "a quote is not a mark")

        self.configure()
        self.assertTrue(doctor(self.target)["ready"])
        cases = self.target / "docs/USE_CASES.md"
        before = cases.read_text(encoding="utf-8")
        broken = {
            "broken/escaping": ("docs/ARCHITECTURE.md", architecture.read_text(encoding="utf-8") + "\n[missing](missing.md)\n"),
            "Test field": ("docs/USE_CASES.md", before.replace(
                "- **Test:** `covered` (link) | `gap` | `NFV` (reason). See *Identifiers*.", "- **Coverage:** gap.", 1)),
            "traceability table": ("docs/USE_CASES.md", before.replace(
                "| UC-002 | Automatic | FR-0yy | ... | covered / gap / NFV |\n", "", 1)),
            "Duplicate use-case headings": ("docs/USE_CASES.md", before + "\n#### UC-001 — duplicate\n\n- **Test:** gap\n"),
        }
        for expected, (relative, text) in broken.items():
            with self.subTest(expected):
                original = (self.target / relative).read_text(encoding="utf-8")
                self.write(relative, text)
                self.assertTrue(any(expected in e for e in doctor(self.target)["errors"]), expected)
                self.write(relative, original)

    def test_finish_passes_only_when_tests_ran_and_none_failed(self):
        self.git_init()
        self.init()
        self.configure()
        run = self.run_check("finish")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("FINISH PASSED: 2 commands; 1 tests, 0 skipped", run.stdout)
        self.assertTrue((self.target / "docs/INDEX.md").is_file(), "finish regenerates the index")

        self.write("tests/test_fixture.py", FAILING)
        run = self.run_check("finish")
        self.assertEqual(run.returncode, 1)
        self.assertIn("FAILED test", run.stdout)
        self.assertIn("planted", run.stderr, "the tail of a failure is shown")
        (self.target / "tests/test_fixture.py").unlink()
        self.assertIn("FAILED test", self.run_check("finish").stdout, "zero discovered tests is not a pass")
        self.set_test(["{python}", "-c", "print('all good')"])
        self.assertIn("no `TESTS:", self.run_check("finish").stdout, "exit 0 without counts is not a pass")

        self.write("tests/test_a.py", PASSING)
        self.write("tests/test_b.py", PASSING.replace("test_ok", "test_ok_too"))
        self.set_test(["{python}", "-B", ".devframework/run_unittest.py", "--start", "tests", "--jobs", "auto"])
        self.assertIn("2 tests, 0 skipped", self.run_check("finish").stdout, "parallel modules add up")
        self.write("tests/test_b.py", FAILING)
        self.assertEqual(self.run_check("finish").returncode, 1, "one failing module fails the gate")

        # run_pytest.py: a stub `pytest` package stands in for the real one, so CI needs no pytest install
        self.write("pytest/__init__.py", "")
        self.write("pytest/__main__.py", (
            "import pathlib, sys\n"
            "out = next(a.split('=', 1)[1] for a in sys.argv if a.startswith('--junitxml='))\n"
            "pathlib.Path(out).write_text('<testsuites><testsuite tests=\"3\" failures=\"0\" errors=\"0\" skipped=\"0\"/></testsuites>')\n"))
        self.set_test(["{python}", "-B", ".devframework/run_pytest.py"])
        self.assertIn("3 tests, 0 skipped", self.run_check("finish").stdout)

    def test_secrets_stop_finish_and_commit_check(self):
        self.git_init()
        self.init()
        self.configure()
        self.write("settings.env", "API_" + "TOKEN=synthetic-private-0123456789\n")  # split: this file stays clean
        run = self.run_check("finish")
        self.assertEqual(run.returncode, 1)
        self.assertIn("settings.env:1", run.stdout)
        self.assertNotIn("synthetic-private-", run.stdout + run.stderr, "the value is never printed")

        self.git("add", "-A")
        self.write("settings.env", "API_TOKEN=\n")  # clean worktree, but the staged blob still holds the value
        self.assertEqual(self.run_check("finish").returncode, 0)
        self.assertEqual(self.run_check("commit-check").returncode, 1, "commit-check scans what would be committed")
        self.git("add", "-A")
        run = self.run_check("commit-check")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("COMMIT CHECK PASSED", run.stdout)

    def test_a_tool_is_proven_by_examples_and_an_exploration_says_nothing_is_proven(self):
        self.git_init()
        self.init(kind="tool")
        guide = (self.target / "docs/GUIDE.html").read_text(encoding="utf-8")
        self.assertNotIn("TODO(project):", "".join(re.findall(r"(?s)<!--.*?-->", guide)), "markers must be fillable")
        self.fill("PROJECT.md", "docs/GUIDE.html")
        self.write("tool.py", "import sys\nprint(int(sys.argv[1]) * 2)\n")
        path = self.target / ".devframework/project.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        for expect, code in (("42", 0), ("43", 1)):
            config["smoke"] = [{"name": "doubles", "run": ["{python}", "tool.py", "21"], "expect_contains": expect}]
            path.write_text(json.dumps(config), encoding="utf-8")
            run = self.run_check("finish")
            self.assertEqual(run.returncode, code, run.stdout + run.stderr)

        explore = self.base / "explore"
        explore.mkdir()
        subprocess.run(["git", "-C", str(explore), "init", "-q"], check=True, timeout=30)
        install.install(explore, name="Probe", kind="explore")
        self.fill("PROJECT.md", root=explore)
        run = self.run_check("finish", root=explore)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("behaviour is NOT proven", run.stdout)

    def test_a_local_devlog_is_not_product_documentation(self):
        self.init()
        self.configure()
        self.write("docs/devlog/2026-09-24_notes.md",
                   "TODO(project): quoted from a dialogue\n"
                   "[missing](missing.md)\n")
        self.write("docs/devlog/rework.md",
                   "<!-- under-construction: storage rework (until 2099-01-01) -->\n")
        report = doctor(self.target)
        noise = report["errors"] + report["setup"] + report["warnings"]
        self.assertFalse(any("docs/devlog" in item.replace("\\", "/") for item in noise), noise)
        self.assertTrue(report["ready"], noise)

        self.write("docs/NOTES.md", "# Notes\n\n[missing](missing.md)\n")
        report = doctor(self.target)
        self.assertTrue(any("docs/NOTES.md" in item.replace("\\", "/") for item in report["errors"]), report["errors"])
        self.assertFalse(any("docs/devlog" in item.replace("\\", "/") for item in report["errors"]))

        self.write("README.md", "# Fixture\n")
        import verify
        from verification import check_links
        link_errors = [item.replace("\\", "/") for item in verify.doc_link_errors(self.target, check_links)]
        self.assertTrue(any("docs/NOTES.md" in item for item in link_errors), link_errors)
        self.assertFalse(any("docs/devlog" in item for item in link_errors), link_errors)
