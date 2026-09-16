from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from common import ROOT, WorkspaceTest, install
from safety import child, project_lock

# Read from the package, so a VERSION bump does not silently break these tests.
PACKAGE_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
NEWER_VERSION = ".".join(str(n + (i == 2)) for i, n in enumerate(map(int, PACKAGE_VERSION.split("."))))


class InstallerTests(WorkspaceTest):
    def test_install_carries_local_knowledge_and_neutral_facts(self):
        result = self.init()
        self.assertFalse(result["conflicts"])
        self.assertEqual((self.target / ".devframework/LESSONS.md").read_bytes(), (ROOT / "LESSONS.md").read_bytes())
        self.assertIn("@PROJECT.md", (self.target / "CLAUDE.md").read_text())
        self.assertTrue((self.target / ".devframework/patterns/outbox.md").is_file())
        self.assertEqual(install.load_manifest(self.target)["version"], PACKAGE_VERSION)

    def test_scale_math_three_sizes(self):
        for number, daily, second in [(5000, "7,200,000", "83.33"), (10000, "14,400,000", "166.67"),
                                      (50000, "72,000,000", "833.33")]:
            with self.subTest(number=number):
                target = self.base / str(number)
                install.install(target, name='Проект "試験"', scale=f"{number:,} devices")
                text = (target / "PROJECT.md").read_text(encoding="utf-8")
                self.assertIn(f"**{daily} requests/day**", text)
                self.assertIn(f"**{second} requests/second**", text)
                self.assertNotIn("{{", text)
                self.assertEqual(install.load_manifest(target)["parameters"]["name"], 'Проект "試験"')

    def test_invalid_parameters_fail_before_creation(self):
        for scale in ["0 users", "-2 users", "50,00 users", "ten users", "1.5 users", "1000000001 users"]:
            with self.subTest(scale=scale), self.assertRaises(ValueError):
                self.init(scale=scale)
            self.assertFalse(self.target.exists())
        with self.assertRaises(ValueError):
            install.install(self.target, name="bad\nname")

    def test_preview_does_not_create_even_target(self):
        result = self.init(dry_run=True)
        self.assertTrue(result["dry_run"])
        self.assertFalse(self.target.exists())

    def test_legacy_conflict_stops_before_any_write(self):
        self.write("AGENTS.md", "Existing rules")
        result = self.init()
        self.assertEqual(result["conflicts"], ["AGENTS.md"])
        self.assertEqual(sorted(p.name for p in self.target.iterdir()), ["AGENTS.md"])

    def test_force_preserves_project_docs_and_backs_up_rules(self):
        original = b"Existing rules\r\n"
        self.write("AGENTS.md", original)
        self.write("PROJECT.md", "User facts")
        self.write("docs/REQUIREMENTS.md", "User requirements")
        result = self.init(force=True)
        backup = self.target / result["backup"] / "files/AGENTS.md"
        self.assertEqual(backup.read_bytes(), original)
        self.assertEqual((self.target / "PROJECT.md").read_text(), "User facts")
        self.assertEqual((self.target / "docs/REQUIREMENTS.md").read_text(), "User requirements")
        self.git_init()
        self.assertTrue(self.git("check-ignore", str(backup)))

    def test_identical_update_is_noop(self):
        self.init()
        before = (self.target / install.MANIFEST).read_bytes()
        result = install.install(self.target, update=True)
        self.assertIsNone(result["backup"])
        self.assertEqual((self.target / install.MANIFEST).read_bytes(), before)

    def test_upgrade_updates_managed_but_preserves_project(self):
        source = self.package_copy()
        self.init(source=source)
        self.write("PROJECT.md", "Project adaptation")
        self.write("AGENTS.md", (self.target / "AGENTS.md").read_bytes().replace(b"\n", b"\r\n"))
        new_rule = source / "template/AGENTS.md"
        new_rule.write_text(new_rule.read_text(encoding="utf-8") + "\nNew rule.\n", encoding="utf-8")
        (source / "VERSION").write_text(NEWER_VERSION + "\n")
        result = install.install(self.target, source=source, update=True)
        self.assertFalse(result["conflicts"])
        self.assertIn("New rule.", (self.target / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual((self.target / "PROJECT.md").read_text(), "Project adaptation")

    def test_modified_managed_file_conflicts_and_preview_leaves_bytes(self):
        self.init()
        self.write("AGENTS.md", "Local rule")
        manifest = (self.target / install.MANIFEST).read_bytes()
        for preview in (True, False):
            result = install.install(self.target, update=True, dry_run=preview)
            self.assertIn("AGENTS.md", result["conflicts"])
            self.assertEqual((self.target / install.MANIFEST).read_bytes(), manifest)
            self.assertEqual((self.target / "AGENTS.md").read_text(), "Local rule")

    def test_missing_manifest_is_not_an_update(self):
        with self.assertRaisesRegex(ValueError, "No manifest"):
            install.install(self.target, update=True)
        self.assertFalse(self.target.exists())

    def test_reinitialization_and_parameter_changes_are_explicit(self):
        self.init()
        with self.assertRaisesRegex(ValueError, "Already installed"):
            self.init()
        with self.assertRaisesRegex(ValueError, "preserves installation parameters"):
            install.install(self.target, update=True, scale="50,000 users")

    def test_overlap_and_non_directory_targets_rejected(self):
        for target in (ROOT, ROOT / "temp" / "forbidden", ROOT.parent):
            with self.subTest(target=target), self.assertRaises(ValueError):
                install.install(target, name="unsafe")
        self.target.write_text("not a folder")
        with self.assertRaises(ValueError):
            self.init()
        self.assertEqual(self.target.read_text(), "not a folder")

    def test_manifest_traversal_rejected(self):
        self.init()
        manifest = install.load_manifest(self.target)
        manifest["files"]["../escape"] = {"sha256": "0" * 64}
        self.write(install.MANIFEST, json.dumps(manifest))
        with self.assertRaises(ValueError):
            install.install(self.target, update=True)
        self.assertFalse((self.base / "escape").exists())

    def test_junction_or_symlink_cannot_redirect_target_writes(self):
        outside = self.base / "outside"
        outside.mkdir()
        self.target.mkdir()
        link = self.target / "docs"
        if os.name == "nt":
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True)
            self.assertEqual(result.returncode, 0)
            self.addCleanup(lambda: os.rmdir(link))
        else:
            link.symlink_to(outside, target_is_directory=True)
            self.addCleanup(link.unlink)
        with self.assertRaisesRegex(ValueError, "Symlink/reparse"):
            self.init()
        self.assertEqual(list(outside.iterdir()), [])

    def test_second_writer_is_rejected(self):
        self.init()
        with project_lock(self.target), self.assertRaisesRegex(ValueError, "Another installer"):
            install.install(self.target, update=True)

    def test_caught_failure_rolls_back_all_changed_files(self):
        self.write("AGENTS.md", "Original")
        real_write = install.atomic_write
        failed = False

        def fail_once(path, data):
            nonlocal failed
            if path == self.target / "PROJECT.md" and not failed:
                failed = True
                raise OSError("synthetic write failure")
            return real_write(path, data)

        with patch.object(install, "atomic_write", side_effect=fail_once), self.assertRaises(OSError):
            self.init(force=True)
        self.assertTrue(failed)
        self.assertEqual((self.target / "AGENTS.md").read_text(), "Original")
        self.assertFalse((self.target / install.MANIFEST).exists())
        self.assertFalse((self.target / install.PENDING).exists())

    def crash_install(self):
        # A real child exits without finally/cleanup, leaving an interrupted transaction.
        code = """
import os, pathlib, sys
sys.path.insert(0, sys.argv[1])
import install
target = pathlib.Path(sys.argv[2])
real = install.atomic_write
def abrupt(path, data):
    if path == target / 'PROJECT.md':
        os._exit(73)
    real(path, data)
install.atomic_write = abrupt
install.install(target, name='Crash fixture', force=True)
"""
        result = subprocess.run([sys.executable, "-B", "-c", code, str(ROOT / "scripts"), str(self.target)], timeout=30)
        self.assertEqual(result.returncode, 73)

    def test_process_crash_can_recover_and_os_releases_lock(self):
        self.write("AGENTS.md", "Before crash")
        self.crash_install()
        self.assertTrue((self.target / install.PENDING).exists())
        with self.assertRaisesRegex(ValueError, "Interrupted"):
            self.init()
        with project_lock(self.target):
            install.restore_pending(self.target)
        self.assertEqual((self.target / "AGENTS.md").read_text(), "Before crash")
        self.assertFalse((self.target / install.PENDING).exists())

    def test_recovery_will_not_overwrite_post_crash_edit(self):
        self.write("AGENTS.md", "Original")
        self.crash_install()
        self.write("AGENTS.md", "Later edit")
        with project_lock(self.target), self.assertRaisesRegex(ValueError, "later edit"):
            install.restore_pending(self.target)
        self.assertEqual((self.target / "AGENTS.md").read_text(), "Later edit")
        self.assertTrue((self.target / install.PENDING).exists())

    def test_removed_package_file_is_retained_not_deleted(self):
        source = self.package_copy()
        self.write("template/obsolete.md", "Old knowledge", root=source)
        self.init(source=source)
        (source / "template/obsolete.md").unlink()
        result = install.install(self.target, source=source, update=True)
        self.assertIn({"path": "obsolete.md", "action": "retain-retired"}, result["files"])
        self.assertEqual((self.target / "obsolete.md").read_text(), "Old knowledge")

    def test_changed_backup_is_not_restored(self):
        self.write("AGENTS.md", "Original")
        self.crash_install()
        marker = install.read_json(self.target / install.PENDING)
        self.write(marker["backup"] + "/files/AGENTS.md", "Tampered backup")
        with self.assertRaisesRegex(ValueError, "Backup content changed"):
            install.restore_pending(self.target)

    def test_child_helper_rejects_reserved_metadata(self):
        for relative in ("../outside", ".git/config", ".GIT/config", "C:/outside", "/absolute", "bad\\path"):
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                child(self.base, relative)

    def test_hardlink_is_not_overwritten(self):
        self.target.mkdir()
        original = self.base / "original.md"
        original.write_text("Preserve this")
        os.link(original, self.target / "AGENTS.md")
        with self.assertRaisesRegex(ValueError, "Hard-linked"):
            self.init(force=True)
        self.assertEqual(original.read_text(), "Preserve this")
        (self.target / "AGENTS.md").unlink()

    def test_incomplete_package_fails_before_writes(self):
        source = self.package_copy()
        (source / "template/AGENTS.md").unlink()
        with self.assertRaisesRegex(ValueError, "Incomplete package"):
            self.init(source=source)
        self.assertFalse(self.target.exists())

    def test_bad_template_variable_fails_before_writes(self):
        source = self.package_copy()
        self.write("template/extra.md", "{{MISSING_VARIABLE}}", root=source)
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            self.init(source=source)
        self.assertFalse(self.target.exists())

    def test_downgrade_rejected(self):
        source = self.package_copy()
        self.init(source=source)
        (source / "VERSION").write_text("0.1.0\n")
        with self.assertRaisesRegex(ValueError, "Downgrade"):
            install.install(self.target, source=source, update=True)

    def test_retired_files_do_not_cause_repeat_backup(self):
        source = self.package_copy()
        for name in ("z.md", "a.md", "m.md"):
            self.write("template/" + name, "old", root=source)
        self.init(source=source)
        for name in ("z.md", "a.md", "m.md"):
            (source / "template" / name).unlink()
        install.install(self.target, source=source, update=True)
        self.assertIsNone(install.install(self.target, source=source, update=True)["backup"])

    def test_newer_manifest_during_planning_is_not_overwritten(self):
        self.init()
        real_plan = install.make_plan

        def race(*args):
            plan = real_plan(*args)
            manifest = install.load_manifest(self.target)
            manifest["version"] = NEWER_VERSION
            self.write(install.MANIFEST, json.dumps(manifest))
            return plan

        with patch.object(install, "make_plan", side_effect=race), self.assertRaisesRegex(ValueError, "changed during planning"):
            install.install(self.target, update=True)
        self.assertEqual(install.load_manifest(self.target)["version"], NEWER_VERSION)
