from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "template" / ".devframework"))
import install
from safety import checked_path


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="devframework-test-")).absolute()
        self.target = self.base / "new project"
        self.addCleanup(self.cleanup_workspace)

    def cleanup_workspace(self):
        # Delete only this exact newly-created fixture root, never an environment root.
        expected_parent = Path(tempfile.gettempdir()).resolve()
        actual = checked_path(self.base).resolve()
        if actual.parent != expected_parent or not actual.name.startswith("devframework-test-"):
            raise RuntimeError("Unsafe test cleanup root")

        def writable(function, path, error):
            candidate = checked_path(Path(path))
            if not candidate.is_relative_to(actual):
                raise RuntimeError("Unsafe cleanup child")
            os.chmod(candidate, stat.S_IWRITE | stat.S_IREAD)
            function(candidate)

        shutil.rmtree(actual, onerror=writable)

    def write(self, relative, content, root=None):
        path = (root or self.target) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        return path

    def init(self, **kwargs):
        return install.install(self.target, name="Fixture project", **kwargs)

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.target), *args], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result.stdout

    def git_init(self):
        self.target.mkdir(parents=True, exist_ok=True)
        self.git("-c", "init.defaultBranch=main", "init", "-q")
        self.git("config", "core.autocrlf", "false")

    def checker(self, *args):
        return subprocess.run([sys.executable, "-B", str(self.target / ".devframework/check.py"), *args],
                              cwd=self.target, capture_output=True, text=True, timeout=30)

    def configure(self):
        for relative in ("PROJECT.md", "docs/ARCHITECTURE.md"):
            path = self.target / relative
            path.write_text(path.read_text(encoding="utf-8").replace("TODO(project):", "Fixture configured:"), encoding="utf-8")
        config = self.target / ".devframework/project.json"
        value = json.loads(config.read_text(encoding="utf-8"))
        value["commands"] = {"build": ["{python}", "-c", "print('fixture build')"],
                             "test": ["{python}", "-B", ".devframework/run_unittest.py"], "checks": []}
        value["test_evidence"] = {"format": "devframework-v1", "max_skipped": 0}
        self.write("tests/test_fixture.py", "import unittest\nclass Fixture(unittest.TestCase):\n    def test_true(self):\n        self.assertEqual(2 + 2, 4)\n")
        config.write_text(json.dumps(value), encoding="utf-8")
        return value

    def package_copy(self):
        source = self.base / "package"
        shutil.copytree(ROOT / "template", source / "template", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copyfile(ROOT / "LESSONS.md", source / "LESSONS.md")
        shutil.copyfile(ROOT / "VERSION", source / "VERSION")
        return source
