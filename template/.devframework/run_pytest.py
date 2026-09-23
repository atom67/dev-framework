"""pytest adapter emitting the finish runner's counted evidence (plain `def test_...` functions welcome).

Runs `python -m pytest --junitxml=<temp>` with any extra arguments you pass (for example `-n auto` when
pytest-xdist is installed) and turns the JUnit XML totals into the same report run_unittest.py writes.
pytest itself must be installed in the interpreter that runs the gate; this file is standard library only.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree

sys.dont_write_bytecode = True


def junit_counts(path: Path) -> dict:
    """Totals over every <testsuite>; pytest writes <testsuites><testsuite .../></testsuites>."""
    root = ElementTree.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else root.iter("testsuite")
    counts = {"total": 0, "failed": 0, "errors": 0, "skipped": 0}
    for suite in suites:
        counts["total"] += int(suite.get("tests", 0))
        counts["failed"] += int(suite.get("failures", 0))
        counts["errors"] += int(suite.get("errors", 0))
        counts["skipped"] += int(suite.get("skipped", 0))
    return counts


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="devframework-pytest-") as raw:
        junit = Path(raw) / "junit.xml"
        run = subprocess.run([sys.executable, "-m", "pytest", "-q", f"--junitxml={junit}", *sys.argv[1:]])
        if not junit.is_file():
            print("FAILED: pytest wrote no report — is pytest installed in this interpreter? "
                  f"({sys.executable} -m pip install pytest, or use run_unittest.py)", file=sys.stderr)
            return 1
        counts = junit_counts(junit)
    report_path, run_id = os.environ.get("DEVFRAMEWORK_TEST_REPORT"), os.environ.get("DEVFRAMEWORK_RUN_ID")
    if report_path and run_id:
        Path(report_path).write_text(json.dumps({"format": 1, "run_id": run_id, **counts}), encoding="utf-8")
    if not counts["total"] or counts["total"] <= counts["skipped"]:
        print("FAILED: no tests executed", file=sys.stderr)
        return 1
    return run.returncode


if __name__ == "__main__":
    raise SystemExit(main())
