"""Zero-test-safe unittest adapter, emitting the finish runner's counted evidence."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

sys.dont_write_bytecode = True

SLOW_SECONDS = 60  # a gate that takes longer than this is worth one hint about --jobs


def test_modules(start: str, pattern: str) -> list[Path]:
    """Files unittest discovery would load, in a deterministic order."""
    return sorted(p for p in Path(start).rglob(pattern) if p.name != "__init__.py")


def run_one(module: Path, start: str, jobs_dir: Path, run_id: str) -> tuple[Path, int, str, dict]:
    report = jobs_dir / (module.stem + ".json")
    env = {**os.environ, "DEVFRAMEWORK_TEST_REPORT": str(report), "DEVFRAMEWORK_RUN_ID": run_id}
    started = time.monotonic()
    child = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()),
                            "--start", start, "--pattern", module.name, "--jobs", "1"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    counts = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else {}
    counts["seconds"] = round(time.monotonic() - started, 1)
    return module, child.returncode, (child.stdout or "") + (child.stderr or ""), counts


def run_parallel(modules: list[Path], start: str, jobs: int) -> tuple[int, dict]:
    """One process per test module. Modules must not share mutable state outside their own fixtures."""
    totals = {"total": 0, "failed": 0, "errors": 0, "skipped": 0}
    failed_modules, run_id = [], uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix="devframework-jobs-") as raw:
        jobs_dir = Path(raw)
        with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
            futures = [pool.submit(run_one, m, start, jobs_dir, run_id) for m in modules]
            results = sorted((f.result() for f in futures), key=lambda r: str(r[0]))
    for module, code, output, counts in results:
        for key in totals:
            totals[key] += int(counts.get(key, 0))
        print(f"{module.name}: {counts.get('total', 0)} tests, {counts.get('failed', 0) + counts.get('errors', 0)}"
              f" failed, {counts.get('skipped', 0)} skipped ({counts.get('seconds', 0)}s)", flush=True)
        if code != 0:
            failed_modules.append(module.name)
            print(output, file=sys.stderr)
    if failed_modules:
        print("FAILED modules: " + ", ".join(failed_modules), file=sys.stderr)
    return (1 if failed_modules else 0), totals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="tests")
    parser.add_argument("--pattern", default="test*.py")
    parser.add_argument("--jobs", default="1",
                        help="'auto' or an integer: run each test module in its own process. "
                             "Only for suites whose modules share no state outside their own fixtures.")
    args = parser.parse_args()
    # Script execution otherwise exposes only .devframework, not project imports.
    sys.path.insert(0, str(Path.cwd()))
    started = time.monotonic()

    modules = test_modules(args.start, args.pattern) if args.jobs != "1" else []
    if len(modules) > 1:
        jobs = min(os.cpu_count() or 1, len(modules)) if args.jobs == "auto" else max(1, int(args.jobs))
        code, counts = run_parallel(modules, args.start, jobs)
        total, skipped = counts["total"], counts["skipped"]
        print(f"{total} tests in {len(modules)} modules, {counts['failed'] + counts['errors']} failed, "
              f"{skipped} skipped, {round(time.monotonic() - started, 1)}s on {jobs} jobs", flush=True)
    else:
        suite = unittest.defaultTestLoader.discover(args.start, pattern=args.pattern)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        total = result.testsRun
        skipped = len(result.skipped) + len(result.expectedFailures)
        counts = {"total": total, "failed": len(result.failures) + len(result.unexpectedSuccesses),
                  "errors": len(result.errors), "skipped": skipped}
        code = 0 if result.wasSuccessful() else 1
        elapsed = time.monotonic() - started
        if elapsed > SLOW_SECONDS and len(test_modules(args.start, args.pattern)) > 1:
            print(f"{round(elapsed)}s sequentially: add --jobs auto if the modules are independent",
                  file=sys.stderr)

    report_path = os.environ.get("DEVFRAMEWORK_TEST_REPORT")
    run_id = os.environ.get("DEVFRAMEWORK_RUN_ID")
    if report_path and run_id:
        Path(report_path).write_text(json.dumps({"format": 1, "run_id": run_id, **counts}), encoding="utf-8")
    if not total or total <= skipped:
        print("FAILED: no tests executed", file=sys.stderr)
        return 1
    return code


if __name__ == "__main__":
    raise SystemExit(main())
