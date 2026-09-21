"""Portable doctor, staged-source heuristic and explicitly configured finish command."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
from safety import checked_path
from secrets_check import scan_index
from verification import doctor, load_config
from source_scope import identity, require_index_parity, scan_worktree, snapshot
from test_evidence import validate
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


def finish(root: Path, *, commit: bool = False, verbose: bool = False) -> int:
    navigate.index(root)  # regenerated before the snapshot so the digest covers a fresh docs/INDEX.md
    (root / LOG).write_bytes(b"")
    before = snapshot(root)
    report = doctor(root)
    result = show_doctor(report, False)
    if result:
        return result
    index = require_index_parity(root) if commit else None
    if show_secrets(root, scan_worktree(before)):
        return 1
    if commit and show_secrets(root):
        return 1
    config, _, _ = load_config(root)
    commands = config["commands"]
    steps = []
    if commands.get("build") is not None:
        steps.append(("build", commands["build"]))
    else:
        print("BUILD NOT APPLICABLE: documented in project.json")
    steps.append(("test", commands["test"]))
    steps.extend((f"check-{number}", cmd) for number, cmd in enumerate(commands["checks"], 1))
    counts = None
    for label, command in steps:
        # Only reviewed project commands are allowed. This runner is not a sandbox;
        # argv avoids implicit shell parsing, but a configured command can have effects.
        argv = [sys.executable if arg == "{python}" else arg for arg in command]
        print(f"RUN {label}", flush=True)
        try:
            with tempfile.TemporaryDirectory(prefix="devframework-evidence-") as temporary:
                evidence_path = Path(temporary) / "tests.json"
                run_id = uuid.uuid4().hex
                env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
                if label == "test":
                    env.update(DEVFRAMEWORK_TEST_REPORT=str(evidence_path), DEVFRAMEWORK_RUN_ID=run_id)
                # Quiet by default: child output goes to the log, the agent reads counts and the first failure.
                run = subprocess.run(argv, cwd=root, timeout=config["timeout_seconds"], shell=False, env=env,
                                     capture_output=not verbose)
                if not verbose:
                    with open(root / LOG, "ab") as log:
                        log.write(f"== {label}: {' '.join(argv)}\n".encode("utf-8") + run.stdout + run.stderr)
                if label == "test" and run.returncode == 0:
                    counts = validate(evidence_path, run_id, config["test_evidence"]["max_skipped"])
        except subprocess.TimeoutExpired:
            print(f"FAILED {label}: timeout; inspect any child processes before retrying")
            return 1
        if run.returncode:
            print(f"FAILED {label}: exit {run.returncode}")
            if not verbose:
                tail = (run.stdout + run.stderr).decode("utf-8", errors="replace").strip().splitlines()[-20:]
                print("\n".join(tail) + f"\n(full output: {LOG})", file=sys.stderr)
            return 1
        print(f"PASSED {label}", flush=True)
        if snapshot(root) != before:
            raise ValueError("Source changed during verification; rerun on a stable snapshot")
    if commit and require_index_parity(root) != index:
        raise ValueError("Index changed during verification")
    print(f"TEST EVIDENCE: {counts['total']} total, {counts['skipped']} skipped, 0 failures/errors")
    print(f"SOURCE SHA256: {identity(before)} (tracked + nonignored untracked; ignored inputs NOT covered)")
    print(f"{'COMMIT CHECK' if commit else 'FINISH'} PASSED: {len(steps)} configured commands. "
          f"{'Index/worktree parity verified.' if commit else 'WORKTREE ONLY; commit content NOT certified.'} "
          "No commit, push, deploy or restart was added.")
    reminder = devlog_mod.missing_today(root)
    if reminder:
        print(reminder)
    return 0


def selftest(root: Path) -> int:
    """Plant what each gate must catch, in a temporary copy of the source, and expect the failure.

    Covers the two mechanical gates (catalogue contract, secret heuristic). The cost audit is a reading
    exercise (see catch-up skill §5) and is not simulated here.
    """
    files = snapshot(root)
    results = []
    with tempfile.TemporaryDirectory(prefix="devframework-selftest-") as temporary:
        copy = Path(temporary) / "copy"
        for name, data in files.items():
            if data is not None:
                target = copy / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        for args in (("init", "-q"), ("add", "-A")):
            subprocess.run(["git", "-C", str(copy), *args], capture_output=True, timeout=60, check=True)
        baseline = len(doctor(copy)["errors"])
        catalogue = copy / "docs" / "USE_CASES.md"
        original = catalogue.read_bytes()
        catalogue.write_bytes(original + "\n#### UC-999 — planted case without a Test field\n- **Trigger:** planted by selftest\n".encode("utf-8"))
        caught = len(doctor(copy)["errors"]) > baseline
        catalogue.write_bytes(original)
        restored = len(doctor(copy)["errors"]) == baseline
        results.append(("doctor contract", caught and restored, "a UC without **Test:** was rejected, then accepted after restore"))
        planted = copy / "planted_by_selftest.txt"
        planted.write_text("token = ghp_" + "A" * 36 + "\n", encoding="utf-8")
        found = bool(scan_worktree(snapshot(copy))["findings"])
        planted.unlink()
        clean = not scan_worktree(snapshot(copy))["findings"] or bool(scan_worktree(files)["findings"])
        results.append(("secret heuristic", found and clean, "a planted token-shaped literal was reported, then gone after restore"))
    for name, ok, detail in results:
        print(f"SELFTEST {name}: {'PASS' if ok else 'FAIL'} — {detail if ok else 'the gate did not fire as expected'}")
    print("SELFTEST cost audit: NOT SIMULATED — read repeating operations by hand (catch-up skill §5)")
    return 0 if all(ok for _, ok, _ in results) else 1


def devlog_entry(root: Path, args) -> int:
    from datetime import date
    day = date.fromisoformat(args.date) if args.date else date.today()
    commits = devlog_mod.recent_commits(root, args.from_git) if args.from_git else []
    for spec in args.commit or []:
        sha, _, summary = spec.partition("=")
        if not sha or not summary:
            raise ValueError("--commit expects <sha>=<summary of at most three sentences>")
        commits.append((sha.strip(), summary.strip()))
    path = devlog_mod.new_entry(root, day, args.agent, args.codes.split(","), commits)
    local_only, reason = devlog_mod.keep_local(root)
    print(f"DEVLOG CREATED: {path.relative_to(root).as_posix()} ({reason}); paste the dialogue under '## Dialogue (verbatim)'")
    return 0


def main() -> int:
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
        sub.add_parser(name).add_argument("--verbose", action="store_true", help="stream child output instead of logging it")
    sub.add_parser("selftest", help="prove the doctor contract and the secret heuristic fire, in a temp copy")
    log = sub.add_parser("devlog", help="create a devlog skeleton (optional rule, see DEVLOG.md)")
    log.add_argument("--agent", action="append", required=True, metavar="CLIENT-MODEL",
                     help="who drove the dialogue, e.g. claudecode-OPUS5; repeat once for the second model when models switched")
    log.add_argument("--codes", required=True, help="comma-separated FR/UC/KE codes the dialogue touched")
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
        if args.command == "selftest":
            return selftest(root)
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
        print(f"CHECK FAILED ({type(error).__name__}): inspection/execution could not complete", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
