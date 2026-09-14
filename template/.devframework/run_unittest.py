"""Zero-test-safe unittest adapter, emitting the finish runner's counted evidence."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="tests")
    parser.add_argument("--pattern", default="test*.py")
    args = parser.parse_args()
    # Script execution otherwise exposes only .devframework, not project imports.
    sys.path.insert(0, str(Path.cwd()))
    suite = unittest.defaultTestLoader.discover(args.start, pattern=args.pattern)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report_path = os.environ.get("DEVFRAMEWORK_TEST_REPORT")
    run_id = os.environ.get("DEVFRAMEWORK_RUN_ID")
    if report_path and run_id:
        report = {"format": 1, "run_id": run_id, "total": result.testsRun,
                  "failed": len(result.failures) + len(result.unexpectedSuccesses),
                  "errors": len(result.errors), "skipped": len(result.skipped) + len(result.expectedFailures)}
        Path(report_path).write_text(json.dumps(report), encoding="utf-8")
    if not result.testsRun or result.testsRun <= len(result.skipped) + len(result.expectedFailures):
        print("FAILED: no tests executed", file=sys.stderr)
        return 1
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
