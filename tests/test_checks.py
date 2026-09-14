from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from common import ROOT, WorkspaceTest
import check
from secrets_check import findings, scan_index
from verification import doctor


class DoctorTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.init()

    def test_scaffold_valid_but_not_ready(self):
        report = doctor(self.target)
        self.assertEqual(report["errors"], [])
        self.assertFalse(report["ready"])
        self.assertTrue(report["setup"])
        self.assertEqual(self.checker("doctor").returncode, 2)
        structural = self.checker("doctor", "--structural")
        self.assertEqual(structural.returncode, 0, structural.stdout + structural.stderr)
        self.assertIn("PROJECT NOT READY", structural.stdout)

    def test_configured_fixture_ready_does_not_claim_tests_ran(self):
        self.configure()
        report = doctor(self.target)
        self.assertTrue(report["ready"], report)
        self.assertIn("tests have not run", self.checker("doctor").stdout)

    def test_missing_knowledge_is_error(self):
        (self.target / ".devframework/LESSONS.md").unlink()
        self.assertTrue(any("LESSONS" in e for e in doctor(self.target)["errors"]))

    def test_bad_links_and_placeholders_detected(self):
        path = self.target / "docs/ARCHITECTURE.md"
        self.write("docs/ARCHITECTURE.md", path.read_text(encoding="utf-8") + "\n[missing](missing.md)\n{{UNSET}}\n")
        errors = doctor(self.target)["errors"]
        self.assertTrue(any("broken/escaping" in e for e in errors))
        self.assertTrue(any("placeholder" in e for e in errors))

    def test_duplicate_definitions_but_not_references(self):
        path = self.target / "docs/REQUIREMENTS.md"
        before = path.read_text(encoding="utf-8")
        self.write("docs/REQUIREMENTS.md", before + "\nSee FR-001 and NFR-001.\n")
        self.assertFalse(any("Duplicate" in e for e in doctor(self.target)["errors"]))
        self.write("docs/REQUIREMENTS.md", before + "\n| FR-001 | duplicate | planned |\n")
        self.assertTrue(any("Duplicate" in e for e in doctor(self.target)["errors"]))

    def test_use_case_enables_range_must_have_headings(self):
        path = self.target / "docs/USE_CASES.md"
        before = path.read_text(encoding="utf-8")
        self.write("docs/USE_CASES.md", before.replace("| UC-001 |", "| UC-001…UC-009 |", 1))
        errors = doctor(self.target)["errors"]
        self.assertTrue(any("SET Enables" in e for e in errors), errors)

    def test_use_case_precondition_set_must_exist(self):
        path = self.target / "docs/USE_CASES.md"
        before = path.read_text(encoding="utf-8")
        self.write("docs/USE_CASES.md", before.replace(
            "- **Preconditions:** the `SET-###` items and any prior state required.",
            "- **Preconditions:** SET-999.",
            1))
        errors = doctor(self.target)["errors"]
        self.assertTrue(any("Preconditions name settings" in e for e in errors), errors)

    def test_use_case_missing_test_field(self):
        path = self.target / "docs/USE_CASES.md"
        before = path.read_text(encoding="utf-8")
        self.write("docs/USE_CASES.md", before.replace(
            "- **Test:** `covered` (link) | `gap` | `NFV` (reason). See *Identifiers*.",
            "- **Coverage:** gap.",
            1))
        errors = doctor(self.target)["errors"]
        self.assertTrue(any("Test field" in e for e in errors), errors)

    def test_use_case_missing_traceability_row(self):
        path = self.target / "docs/USE_CASES.md"
        before = path.read_text(encoding="utf-8")
        self.write("docs/USE_CASES.md", before.replace(
            "| UC-002 | Automatic | FR-0yy | ... | covered / gap / NFV |\n",
            "",
            1))
        errors = doctor(self.target)["errors"]
        self.assertTrue(any("traceability table" in e for e in errors), errors)

    def test_use_case_duplicate_heading(self):
        path = self.target / "docs/USE_CASES.md"
        before = path.read_text(encoding="utf-8")
        self.write("docs/USE_CASES.md", before + "\n#### UC-001 — duplicate\n\n- **Test:** gap\n")
        errors = doctor(self.target)["errors"]
        self.assertTrue(any("Duplicate use-case headings" in e for e in errors), errors)

    def test_use_case_templates_are_seeded(self):
        self.assertTrue((self.target / "docs/USE_CASE_TEMPLATE.md").is_file())
        self.assertTrue((self.target / "docs/USE_CASES_SLICE_TEMPLATE.md").is_file())
        self.assertTrue((self.target / "docs/USE_CASES.md").is_file())

    def test_archives_and_fenced_link_examples_not_flagged(self):
        self.write("docs/archive/old.md", "[gone](gone.md) {{OLD}}")
        path = self.target / "docs/REQUIREMENTS.md"
        self.write("docs/REQUIREMENTS.md", path.read_text(encoding="utf-8") + "\n```md\n[example](not-real.md)\n```\n")
        self.assertEqual(doctor(self.target)["errors"], [])

    def test_provider_import_inside_fence_is_not_an_import(self):
        self.write("CLAUDE.md", "```text\n@AGENTS.md\n@PROJECT.md\n```\n")
        self.assertTrue(any("must import" in e for e in doctor(self.target)["errors"]))

    def test_mismatched_profile_detected(self):
        config = self.configure()
        config["profile"] = "service"
        self.write(".devframework/project.json", json.dumps(config))
        self.assertTrue(any("profile link" in e for e in doctor(self.target)["errors"]))

    def test_shell_string_command_not_accepted(self):
        config = self.configure()
        config["commands"]["test"] = "python -m unittest"
        self.write(".devframework/project.json", json.dumps(config))
        self.assertTrue(any("argument array" in e for e in doctor(self.target)["errors"]))

    def test_null_config_and_bad_timeout_fail_closed(self):
        self.write(".devframework/project.json", "null")
        self.assertTrue(doctor(self.target)["errors"])
        self.assertNotEqual(self.checker("finish").returncode, 0)

    def test_pending_transaction_is_not_ready(self):
        self.write(".devframework/pending.json", "{}")
        self.assertTrue(any("Interrupted" in e for e in doctor(self.target)["errors"]))

    def test_incomplete_manifest_not_ready(self):
        self.configure()
        self.write(".devframework/manifest.json", '{"format": 1, "version": "0.2.0", "files": {}}')
        self.assertFalse(doctor(self.target)["ready"])
        self.assertTrue(any("baseline" in e for e in doctor(self.target)["errors"]))

    def test_invalid_timeout_and_missing_test_are_not_ready(self):
        config = self.configure()
        config["timeout_seconds"] = -1
        config["commands"]["test"] = None
        self.write(".devframework/project.json", json.dumps(config))
        report = doctor(self.target)
        self.assertFalse(report["ready"])
        self.assertTrue(any("timeout" in e for e in report["errors"]))
        self.assertTrue(any("test" in e for e in report["setup"]))


class SecretsTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.git_init()

    @staticmethod
    def credential():
        return 'api_token' + ' = ' + json.dumps('synthetic-private-value-123456') + '\n'

    def test_looks_at_index_not_fixed_worktree(self):
        self.write("config.txt", self.credential())
        self.git("add", "config.txt")
        self.write("config.txt", "no credentials here\n")
        report = scan_index(self.target)
        self.assertEqual(len(report["findings"]), 1)
        self.assertNotIn("synthetic-private-value", json.dumps(report))

    def test_unstaged_secret_does_not_masquerade_as_staged(self):
        self.write("config.txt", "clean\n")
        self.git("add", "config.txt")
        self.write("config.txt", self.credential())
        self.assertEqual(scan_index(self.target)["findings"], [])

    def test_placeholder_and_empty_index_handling(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            scan_index(self.target)
        self.write("sample.txt", 'api_' + 'token = "REPLACE_ME"\n')
        self.git("add", "sample.txt")
        self.assertEqual(scan_index(self.target)["findings"], [])

    def test_camelcase_and_nonprefix_identifiers_caught(self):
        for name in ("_devPassword", "ApiToken", "service_api_key"):
            with self.subTest(name=name):
                self.assertEqual(len(findings(name + ' = "synthetic-credential"')), 1)

    def test_short_password_is_not_exempt(self):
        self.assertEqual(len(findings("password" + ' = "abc"')), 1)

    def test_private_key_and_token_shapes(self):
        self.assertTrue(findings("-----BEGIN " + "PRIVATE KEY-----"))
        self.assertTrue(findings("ghp_" + "a" * 36))

    def test_docs_not_exempt_and_utf16_supported(self):
        self.write("docs/example.md", self.credential().encode("utf-16"))
        self.git("add", "docs/example.md")
        self.assertEqual(len(scan_index(self.target)["findings"]), 1)

    def test_binary_scope_is_explicit(self):
        self.write("source.txt", "clean")
        self.write("image.bin", b"\x00\xff\x01")
        self.git("add", ".")
        result = scan_index(self.target)
        self.assertEqual(result["nontext_files"], ["image.bin"])
        self.assertEqual(result["text_files"], 1)

    def test_scan_size_limit_is_failure_not_success(self):
        self.write("large.txt", "abcdefgh")
        self.git("add", ".")
        with patch("secrets_check.MAX_BLOB", 4), self.assertRaisesRegex(ValueError, "limit"):
            scan_index(self.target)

    def test_secret_cli_redacts_value(self):
        self.init()
        self.write("config.txt", self.credential())
        self.git("add", "config.txt")
        run = self.checker("secrets", "--staged")
        self.assertEqual(run.returncode, 1)
        self.assertIn("value redacted", run.stdout)
        self.assertNotIn("synthetic-private-value", run.stdout + run.stderr)

    def test_staged_package_has_no_heuristic_findings(self):
        self.init()
        self.git("add", ".")
        self.assertEqual(scan_index(self.target)["findings"], [])


class FinishTests(WorkspaceTest):
    def setUp(self):
        super().setUp()
        self.init()
        self.git_init()

    def test_unconfigured_finish_does_not_execute(self):
        run = self.checker("finish")
        self.assertEqual(run.returncode, 2)
        self.assertNotIn("RUN test", run.stdout)

    def test_finish_runs_configured_commands_without_mutating_git(self):
        self.configure()
        self.git("add", ".")
        before = self.git("ls-files", "--stage", "-z")
        run = self.checker("finish")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("FINISH PASSED: 2", run.stdout)
        self.assertEqual(self.git("ls-files", "--stage", "-z"), before)
        self.assertFalse((self.target / ".git/refs/heads/main").exists())

    def test_failing_build_prevents_test(self):
        config = self.configure()
        config["commands"]["build"] = ["{python}", "-c", "raise SystemExit(7)"]
        self.write(".devframework/project.json", json.dumps(config))
        self.git("add", ".")
        run = self.checker("finish")
        self.assertEqual(run.returncode, 1)
        self.assertIn("FAILED build: exit 7", run.stdout)
        self.assertNotIn("RUN test", run.stdout)

    def test_test_and_extra_check_failures_propagate(self):
        for failing in ("test", "checks"):
            with self.subTest(failing=failing):
                config = self.configure()
                command = ["{python}", "-c", "raise SystemExit(9)"]
                config["commands"][failing] = command if failing == "test" else [command]
                self.write(".devframework/project.json", json.dumps(config))
                self.git("add", ".")
                run = self.checker("finish")
                self.assertEqual(run.returncode, 1)
                self.assertNotIn("FINISH PASSED", run.stdout)

    def test_explicit_no_build_still_requires_test(self):
        config = self.configure()
        config["commands"]["build"] = None
        config["build_not_applicable"] = "Fixture has no build step"
        self.write(".devframework/project.json", json.dumps(config))
        self.git("add", ".")
        self.assertEqual(self.checker("finish").returncode, 0)

    def test_timeout_is_failure(self):
        self.configure()
        self.git("add", ".")
        # Deterministic timeout injection, no sleeping or detached background process.
        real_run = subprocess.run

        def timeout_command(argv, **kwargs):
            if argv[0] == sys.executable:
                raise subprocess.TimeoutExpired(argv, 1)
            return real_run(argv, **kwargs)

        output = io.StringIO()
        with patch("check.subprocess.run", side_effect=timeout_command), contextlib.redirect_stdout(output):
            self.assertEqual(check.finish(self.target), 1)
        self.assertIn("timeout", output.getvalue())
