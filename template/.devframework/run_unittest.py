"""unittest runner for the finish gate: prints `TESTS: total=N failed=F skipped=S`, the line finish reads.

--jobs auto runs each test module in its own process (only for modules that share no state outside their fixtures).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
LINE = re.compile(r"^TESTS: total=(\d+) failed=(\d+) skipped=(\d+)\s*$", re.M)


def run_module(module: Path, start: str) -> tuple[str, int, int, int, str]:
    child = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--start", start,
                            "--pattern", module.name], capture_output=True, text=True, encoding="utf-8", errors="replace")
    output = child.stdout + child.stderr
    found = LINE.findall(output)
    total, failed, skipped = map(int, found[-1]) if found else (0, 1, 0)  # a module that crashed counts as failed
    return module.name, total, failed, skipped, output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="tests")
    parser.add_argument("--pattern", default="test*.py")
    parser.add_argument("--jobs", default="1", help="'auto' or an integer: one process per test module")
    args = parser.parse_args()
    sys.path.insert(0, str(Path.cwd()))  # script execution otherwise exposes only .devframework, not project imports
    modules = sorted(p for p in Path(args.start).rglob(args.pattern) if p.name != "__init__.py")
    if args.jobs != "1" and len(modules) > 1:
        jobs = (os.cpu_count() or 1) if args.jobs == "auto" else max(1, int(args.jobs))
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(jobs, len(modules))) as pool:
            results = list(pool.map(lambda m: run_module(m, args.start), modules))
        for name, total, failed, skipped, output in results:
            if failed:
                print(output, file=sys.stderr)
            print(f"{name}: {total} tests, {failed} failed, {skipped} skipped", flush=True)
        total, failed, skipped = (sum(r[i] for r in results) for i in (1, 2, 3))
    else:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(args.start, pattern=args.pattern))
        total = result.testsRun
        failed = len(result.failures) + len(result.errors) + len(result.unexpectedSuccesses)
        skipped = len(result.skipped) + len(result.expectedFailures)
    print(f"TESTS: total={total} failed={failed} skipped={skipped}", flush=True)
    return 1 if failed or total <= skipped else 0


if __name__ == "__main__":
    raise SystemExit(main())
