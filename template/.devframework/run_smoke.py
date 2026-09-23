"""Smoke runner for a tool: the tool is its own test, its examples are the evidence.

Reads `smoke` from .devframework/project.json — a list of cases:
  {"name": "converts 100C", "run": ["{python}", "temp.py", "100"],
   "stdin": "examples/in.txt",            (optional: file fed to standard input)
   "expect_stdout": "examples/out.txt",   (optional: output must equal this file, line endings ignored)
   "expect_contains": "212",              (optional: output must contain this text)
   "expect_exit": 0}                      (optional, default 0)
Runs each case, prints PASS/FAIL with the first difference, and prints the TESTS line finish reads.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
CASE_TIMEOUT = 120  # seconds per example; the gate's own timeout still bounds the whole run


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").strip().split("\n"))


def run_case(case: dict) -> str | None:
    """None when the case passes, otherwise the reason."""
    argv = [sys.executable if arg == "{python}" else str(arg) for arg in case["run"]]
    stdin = Path(case["stdin"]).read_bytes() if case.get("stdin") else None
    done = subprocess.run(argv, input=stdin, capture_output=True, timeout=CASE_TIMEOUT)
    out = done.stdout.decode("utf-8", errors="replace")
    if done.returncode != case.get("expect_exit", 0):
        tail = done.stderr.decode("utf-8", errors="replace").strip().splitlines()[-3:]
        return f"exit {done.returncode}, expected {case.get('expect_exit', 0)}" + (f": {' | '.join(tail)}" if tail else "")
    if case.get("expect_contains") is not None and case["expect_contains"] not in out:
        return f"output does not contain {case['expect_contains']!r}"
    if case.get("expect_stdout"):
        got = normalize(out).split("\n")
        want = normalize(Path(case["expect_stdout"]).read_text(encoding="utf-8")).split("\n")
        for number, (a, b) in enumerate(zip(got, want), 1):
            if a != b:
                return f"line {number}: got {a!r}, expected {b!r}"
        if len(got) != len(want):
            return f"{len(got)} output lines, expected {len(want)}"
    return None


def main() -> int:
    config = json.loads(Path(".devframework/project.json").read_text(encoding="utf-8"))
    cases = config.get("smoke") or []
    failed = errors = 0
    for case in cases:
        name = case.get("name") or " ".join(map(str, case.get("run", [])))
        try:
            if not isinstance(case.get("run"), list) or not case["run"]:
                raise ValueError("`run` must be a nonempty argument list")
            reason = run_case(case)
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            errors += 1
            print(f"ERROR {name}: {error}", flush=True)
            continue
        if reason:
            failed += 1
            print(f"FAIL  {name}: {reason}", flush=True)
        else:
            print(f"PASS  {name}", flush=True)
    counts = {"total": len(cases), "failed": failed, "errors": errors, "skipped": 0}
    print(f"TESTS: total={counts['total']} failed={counts['failed'] + counts['errors']} skipped={counts['skipped']}")
    if not cases:
        print("FAILED: no smoke examples — add at least one to `smoke` in .devframework/project.json", file=sys.stderr)
        return 1
    return 1 if failed or errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
