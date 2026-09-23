"""Portable doctor, staged-source heuristic and explicitly configured finish command."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
from safety import checked_path
from secrets_check import scan_index
from verification import doctor, load_config
from source_scope import scan_worktree, snapshot
import devlog as devlog_mod
import navigate


def show_doctor(report: dict, structural: bool) -> int:
    for group in ("errors", "setup", "warnings"):
        for message in report[group]:
            print(f"{group.upper()}: {message}")
    if report["errors"]:
        print("STRUCTURE FAILED")
        return 1
    if not report["ready"]:
        print("STRUCTURE OK; PROJECT NOT READY (configuration required)")
        return 0 if structural else 2
    print("DOCTOR READY: structure/configuration only; build/tests have not run")
    return 0


def show_secrets(root: Path, report: dict | None = None) -> int:
    staged = report is None
    report = scan_index(root) if staged else report
    for match in report["findings"]:
        print(f"SECRET SUSPECT: {match['path']}:{match['line']} ({match['kind']}; value redacted)")
    for path in report["nontext_files"]:
        print(f"NOT TEXT-SCANNED: {path}")
    print(f"{'Staged' if staged else 'Worktree'} heuristic: {report['text_files']} text files, {report['bytes']} bytes, "
          f"{len(report['findings'])} suspects. Artifacts/history are NOT checked.")
    return 1 if report["findings"] else 0


LOG = ".devframework/last_run.log"
# The one line a test command prints for finish; run_unittest.py, run_pytest.py and run_smoke.py do.
TESTS = re.compile(r"^TESTS: total=(\d+) failed=(\d+) skipped=(\d+)\s*$", re.M)


def run_step(root: Path, label: str, command: list, timeout: int, verbose: bool) -> tuple[int, str]:
    """Run one configured command (argv, no shell). Output goes to the log; the agent reads counts and the tail."""
    argv = [sys.executable if arg == "{python}" else arg for arg in command]
    print(f"RUN {label}", flush=True)
    run = subprocess.run(argv, cwd=root, timeout=timeout, shell=False, capture_output=True,
                         env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    output = (run.stdout + run.stderr).decode("utf-8", errors="replace")
    with open(root / LOG, "a", encoding="utf-8") as log:
        log.write(f"== {label}: {' '.join(argv)}\n{output}\n")
    if verbose:
        print(output)
    return run.returncode, output


def finish(root: Path, *, commit: bool = False, verbose: bool = False) -> int:
    """doctor + secret heuristic + the configured commands; the test command must report counts (> 0, no failures)."""
    navigate.index(root)
    (root / LOG).write_bytes(b"")
    report = doctor(root)
    result = show_doctor(report, False)
    if result:
        return result
    if show_secrets(root, scan_worktree(snapshot(root))) or (commit and show_secrets(root)):
        return 1
    config, _, _ = load_config(root, report.get("kind", "product"))
    if commit and config.get("testing") == "advanced":
        gaps = navigate.untested(root)
        if gaps:  # advanced testing: no use case reaches a commit untested (AGENTS.md §4)
            print(f"COMMIT BLOCKED (advanced testing): use cases without a covering test: {', '.join(gaps)} — "
                  "cover each, or mark it NFV with the reason")
            return 1
    commands = config["commands"]
    steps = [("build", commands["build"])] if commands.get("build") is not None else []
    if not steps:
        print("BUILD NOT APPLICABLE: documented in project.json")
    if commands.get("test") is not None:
        steps.append(("test", commands["test"]))
    else:  # only an exploration may reach here: load_config demands a test command from every other kind
        print("NO TEST COMMAND (explore): structure and secrets checked; behaviour is NOT proven")
    steps += [(f"check-{number}", cmd) for number, cmd in enumerate(commands["checks"], 1)]
    if any("{python}" in command for _, command in steps):
        print(f"{{python}} = {sys.executable} (Python {sys.version.split()[0]})")
    tests = None
    for label, command in steps:
        try:
            code, output = run_step(root, label, command, config["timeout_seconds"], verbose)
        except subprocess.TimeoutExpired:
            print(f"FAILED {label}: timeout; inspect any child processes before retrying")
            return 1
        problem = f"exit {code}" if code else None
        if label == "test" and not problem:
            found = TESTS.findall(output)
            if not found:
                problem = "no `TESTS: total=N failed=F skipped=S` line (the test command must report its counts)"
            else:
                total, failed, skipped = map(int, found[-1])
                tests = f"{total} tests, {skipped} skipped"
                if failed or total - skipped <= 0 or skipped > config["test_evidence"]["max_skipped"]:
                    problem = f"{failed} failed, {total - skipped} executed, {skipped} skipped (max {config['test_evidence']['max_skipped']})"
        if problem:
            print(f"FAILED {label}: {problem}")
            if not verbose:
                print("\n".join(output.strip().splitlines()[-20:]) + f"\n(full output: {LOG})", file=sys.stderr)
            return 1
        print(f"PASSED {label}", flush=True)
    print(f"{'COMMIT CHECK' if commit else 'FINISH'} PASSED: {len(steps)} commands" + (f"; {tests}" if tests else "") +
          (". Staged secrets clean." if commit else ". Worktree checked.") + " No commit, push, deploy or restart was added.")
    reminder = devlog_mod.missing_today(root)
    if reminder:
        print(reminder)
    return 0


def devlog_entry(root: Path, args) -> int:
    from datetime import date
    day = date.fromisoformat(args.date) if args.date else date.today()
    commits = devlog_mod.recent_commits(root, args.from_git) if args.from_git else []
    for spec in args.commit or []:
        sha, _, summary = spec.partition("=")
        if not sha or not summary:
            raise ValueError("--commit expects <sha>=<summary of at most three sentences>")
        commits.append((sha.strip(), summary.strip()))
    from verification import installed_kind
    codes = args.codes.split(",") if args.codes else [installed_kind(root).upper()]  # a tool has no FR/UC ids
    import transcript
    dialogue, source = transcript.dialogue(root, args.dialogue, day)
    path = devlog_mod.new_entry(root, day, args.agent, codes, commits, dialogue, source)
    local_only, reason = devlog_mod.keep_local(root)
    filled = f"dialogue filled from the {source}; read it once" if dialogue else \
        f"{source}; paste the dialogue under '## Dialogue (verbatim)'"
    print(f"DEVLOG CREATED: {path.relative_to(root).as_posix()} ({reason}); {filled}")
    return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    sub = parser.add_subparsers(dest="command", required=True)
    doc = sub.add_parser("doctor")
    doc.add_argument("--structural", action="store_true", help="accept a scaffold, clearly marked NOT READY")
    secret = sub.add_parser("secrets")
    scope = secret.add_mutually_exclusive_group(required=True)
    scope.add_argument("--staged", action="store_true")
    scope.add_argument("--worktree", action="store_true")
    for name in ("finish", "commit-check"):
        sub.add_parser(name).add_argument("--verbose", action="store_true", help="also print child output (it is always logged)")
    log = sub.add_parser("devlog", help="create a devlog skeleton (optional rule, see DEVLOG.md)")
    log.add_argument("--agent", action="append", required=True, metavar="CLIENT-MODEL",
                     help="who drove the dialogue, e.g. claudecode-OPUS5; repeat once for the second model when models switched")
    log.add_argument("--dialogue", default="auto", help="auto (this project's Claude Code session log) | none | <session.jsonl> | hermes[:<session id>]")
    log.add_argument("--codes", help="comma-separated FR/UC/KE codes the dialogue touched; default: the kind (TOOL, EXPLORE)")
    log.add_argument("--date", help="dialogue date YYYY-MM-DD (default today)")
    log.add_argument("--from-git", type=int, default=0, metavar="N", help="take the last N commits from git log")
    log.add_argument("--commit", action="append", metavar="SHA=SUMMARY", help="explicit commit row (repeatable)")
    args = parser.parse_args()
    try:
        root = checked_path(args.root)
        if args.command == "doctor":
            return show_doctor(doctor(root), args.structural)
        if args.command == "secrets":
            return show_secrets(root, None if args.staged else scan_worktree(snapshot(root)))
        if args.command == "devlog":
            return devlog_entry(root, args)
        return finish(root, commit=args.command == "commit-check", verbose=args.verbose)
    except ValueError as error:
        # Our report/count failures are descriptive; arbitrary parser values stay redacted.
        if type(error) is ValueError:
            print(f"CHECK FAILED: {error}", file=sys.stderr)
        else:
            print("CHECK FAILED: invalid input", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        # Avoid dumping config or Git stderr, either of which can contain secrets.
        where = f" on {error.filename}" if isinstance(error, OSError) and error.filename else ""  # a path, not content
        print(f"CHECK FAILED ({type(error).__name__}{where}): inspection/execution could not complete", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
