from __future__ import annotations

import json
import subprocess
import sys

from common import WorkspaceTest
from secrets_check import findings, scan_index
from source_scope import snapshot, scan_worktree
from test_evidence import validate


class EvidenceTests(WorkspaceTest):
    def test_report_rejects_zero_skipped_stale_malformed_and_failures(self):
        good = dict(format=1, run_id="current", total=3, failed=0, errors=0, skipped=0)
        variants = [dict(total=0), dict(skipped=3), dict(run_id="old"), dict(total=True),
                    dict(failed=1), dict(errors=1), dict(skipped=1), dict(total=-1),
                    dict(format=2), dict(skipped=8)]
        for fields in variants:
            with self.subTest(fields=fields):
                path = self.write("report.json", json.dumps(good | fields))
                with self.assertRaises(ValueError):
                    validate(path, "current", 0)
        path = self.write("report.json", json.dumps(good | dict(skipped=1)))
        self.assertEqual(validate(path, "current", 1)["total"], 3)
        for content in ("null", "{", "[]", '{"format": 1}'):
            path = self.write("report.json", content)
            with self.assertRaises(ValueError):
                validate(path, "current", 0)

    def test_missing_report_is_failure(self):
        with self.assertRaises(ValueError):
            validate(self.target / "absent.json", "current", 0)


class SnapshotFinishTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.init()
        self.config = self.configure()
        self.git_init()

    def configure_command(self, command):
        self.config["commands"]["test"] = command
        self.write(".devframework/project.json", json.dumps(self.config))

    def test_finish_before_first_stage_succeeds_but_does_not_certify_commit(self):
        run = self.checker("finish")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("1 total, 0 skipped", run.stdout)
        self.assertIn("SOURCE SHA256:", run.stdout)
        self.assertIn("WORKTREE ONLY", run.stdout)
        self.assertEqual(self.git("ls-files", "--stage", "-z"), b"")
        self.assertNotEqual(self.checker("commit-check").returncode, 0)

    def test_parallel_jobs_merge_evidence_and_surface_a_failing_module(self):
        """--jobs auto runs one process per module: totals must add up and one bad module must fail the gate."""
        case = "import unittest\nclass T(unittest.TestCase):\n def test_{n}(self): self.assertTrue({ok})\n"
        self.write("tests/test_alpha.py", case.format(n="alpha", ok="True"))
        self.write("tests/test_beta.py", case.format(n="beta", ok="True"))
        self.configure_command(["{python}", "-B", ".devframework/run_unittest.py", "--start", "tests", "--jobs", "auto"])
        run = self.checker("finish")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("3 total, 0 skipped", run.stdout)  # the seeded fixture test plus these two
        self.write("tests/test_beta.py", case.format(n="beta", ok="False"))
        run = self.checker("finish")
        self.assertEqual(run.returncode, 1)
        self.assertIn("test_beta.py", run.stdout + run.stderr)

    def test_legacy_zero_test_command_is_not_success(self):
        (self.target / "empty_tests").mkdir()
        self.configure_command(["{python}", "-B", "-m", "unittest", "discover", "-s", "empty_tests"])
        legacy = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "empty_tests"],
                                cwd=self.target, capture_output=True, timeout=30)
        # historical false-green control: 0 before Python 3.12; 3.12+ exits 5 ("no tests ran")
        self.assertIn(legacy.returncode, (0, 5))
        run = self.checker("finish")
        self.assertEqual(run.returncode, 1)
        self.assertIn("test evidence", run.stderr)

    def test_safe_adapter_rejects_empty_and_all_skipped_suites(self):
        (self.target / "empty_tests").mkdir()
        self.configure_command(["{python}", "-B", ".devframework/run_unittest.py", "--start", "empty_tests"])
        self.assertEqual(self.checker("finish").returncode, 1)
        self.configure_command(["{python}", "-B", ".devframework/run_unittest.py"])
        self.write("tests/test_fixture.py", "import unittest\n@unittest.skip('fixture')\nclass F(unittest.TestCase):\n def test_skip(self): pass\n")
        self.assertEqual(self.checker("finish").returncode, 1)

    def test_skip_budget_is_enforced_by_finish(self):
        self.write("tests/test_skip.py", "import unittest\nclass F(unittest.TestCase):\n @unittest.skip('fixture')\n def test_skip(self): pass\n")
        self.assertEqual(self.checker("finish").returncode, 1)
        self.config["test_evidence"]["max_skipped"] = 1
        self.write(".devframework/project.json", json.dumps(self.config))
        self.assertEqual(self.checker("finish").returncode, 0)

    def test_changed_source_during_build_fails(self):
        self.config["commands"]["build"] = ["{python}", "-c", "from pathlib import Path; Path('app.py').write_text('changed')"]
        self.write(".devframework/project.json", json.dumps(self.config))
        run = self.checker("finish")
        self.assertEqual(run.returncode, 1)
        self.assertIn("Source changed", run.stderr)

    def test_staged_bug_fixed_only_in_worktree_is_rejected_for_commit(self):
        self.write("app.py", "def reject(): return False\n")
        self.write("tests/test_fixture.py", "import unittest\nimport app\nclass F(unittest.TestCase):\n def test_guard(self): self.assertTrue(app.reject())\n")
        self.git("add", ".")
        self.assertEqual(self.checker("finish").returncode, 1)  # regression is actually detected
        self.write("app.py", "def reject(): return True\n")
        self.assertEqual(self.checker("finish").returncode, 0)
        run = self.checker("commit-check")
        self.assertEqual(run.returncode, 1)
        self.assertIn("Index differs", run.stderr)
        self.git("add", "app.py")
        self.assertEqual(self.checker("commit-check").returncode, 0)

    def test_assume_unchanged_cannot_hide_index_mismatch(self):
        self.write("app.py", "old\n")
        self.git("add", ".")
        self.git("update-index", "--assume-unchanged", "app.py")
        self.write("app.py", "changed\n")
        self.assertEqual(self.checker("commit-check").returncode, 1)

    def test_worktree_secret_is_checked_even_when_index_clean(self):
        self.git("add", ".")
        self.write(".env", "API_" + "TOKEN=synthetic-private-0123456789\n")
        self.assertEqual(scan_index(self.target)["findings"], [])
        run = self.checker("finish")
        self.assertEqual(run.returncode, 1)
        self.assertIn(".env:1", run.stdout)
        self.assertNotIn("synthetic-private-", run.stdout + run.stderr)

    def test_nested_directory_cannot_scan_parent_repository(self):
        nested = self.target / "nested"
        nested.mkdir()
        with self.assertRaisesRegex(ValueError, "root"):
            snapshot(nested)

    def test_ignored_output_excluded_but_tracked_ignored_file_included(self):
        self.write(".gitignore", "build/\n")
        self.write("build/output.bin", b"\x00\x01")
        self.assertNotIn("build/output.bin", snapshot(self.target))
        self.git("add", "-f", "build/output.bin")
        self.assertIn("build/output.bin", snapshot(self.target))


class SecretFormatTests(WorkspaceTest):
    def test_common_formats_and_safe_metadata(self):
        value = "synthetic-credential-012345"
        cases = [("API_TOKEN" + "=" + value, True), ("api_token" + ": " + value, True),
                 ('ApiToken' + ' = @' + json.dumps(value) + ';', True),
                 ('token_' + 'type = "Bearer"', False),
                 ('token_' + 'endpoint = "https://example.invalid/oauth/token"', False),
                 ('token_' + 'endpoint = "' + "ghp_" + "a" * 36 + '"', True),
                 ('api_' + 'token = ${API_TOKEN}', False),
                 ('password' + ': null', False), ('password' + ': abc', True)]
        for content, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(bool(findings(content)), expected)

    def test_format_detection_in_actual_git_blobs_and_worktree(self):
        self.git_init()
        for path, name, sep in ((".env", "API_" + "TOKEN", "="), ("config.yml", "api_" + "token", ": ")):
            self.write(path, name + sep + "synthetic-credential-value\n")
        self.git("add", ".")
        self.assertEqual(len(scan_index(self.target)["findings"]), 2)
        self.assertEqual(len(scan_worktree(snapshot(self.target))["findings"]), 2)
