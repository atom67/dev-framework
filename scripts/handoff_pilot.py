"""Prepare a disposable, deterministic handoff test subject. Never invokes a provider."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
import install

GOOD = '''def remaining(pending, confirmed):
    """Remove confirmed stable IDs, preserve order. In-memory example, not durable I/O."""
    acknowledged = set(confirmed)
    return [item for item in pending if item not in acknowledged]
'''
BAD = "def remaining(pending, confirmed):\n    return []\n"
TESTS = '''import unittest
from outbox import remaining

class OutboxTests(unittest.TestCase):
    def test_new_record_survives(self):
        self.assertEqual(remaining(["alpha", "beta"], ["alpha"]), ["beta"])
    def test_no_ack_keeps_everything(self):
        self.assertEqual(remaining(["alpha"], []), ["alpha"])
    def test_confirmed_removed(self):
        self.assertEqual(remaining(["alpha"], ["alpha"]), [])
'''


def write(root: Path, name: str, text: str):
    path = install.child(root, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(root: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=45)


def prepare(base: Path) -> dict:
    root = install.child(base, "project")
    install.install(root, name="Parcel Ledger", profile="generic")
    result = run(root, "git", "-c", "init.defaultBranch=main", "init", "-q")
    if result.returncode:
        raise ValueError("Could not initialize isolated fixture Git")
    run(root, "git", "config", "core.autocrlf", "false")
    facts = (root / "PROJECT.md").read_text(encoding="utf-8")
    replacements = {
        "TODO(project): describe users, the problem, runtime/language versions and key dependencies.":
        "Synthetic offline parcel acknowledgement example. Python 3.10+ standard library, no network or real users.",
        "TODO(project): map the source areas, tests and consumers of shared code.":
        "outbox.py owns the pure remaining-ID rule; tests/test_outbox.py exercises three cases. No executable app.",
        "TODO(project): list settings/database/log locations and isolated test locations, or N/A.":
        "No persistent application database: in-memory demonstration. This disposable project is the only test location.",
        "TODO(project): configure build/test commands in .devframework/project.json; document":
        "Python unittest adapter is configured; no build output. No running app. Document",
        "TODO(project): language, naming and today's deliberate limitations. Link architectural":
        "English documents and snake_case Python. Deliberately no network or durable queue. Link architectural",
    }
    for old, new in replacements.items():
        facts = facts.replace(old, new)
    write(root, "PROJECT.md", facts)
    config_path = root / ".devframework/project.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["commands"] = {"build": None, "test": ["{python}", "-B", ".devframework/run_unittest.py"], "checks": []}
    config["build_not_applicable"] = "Interpreted pure-function pilot; no application executable"
    write(root, ".devframework/project.json", json.dumps(config, indent=2))
    write(root, "docs/ARCHITECTURE.md", """# Parcel Ledger architecture

Python pure remaining(pending, confirmed) rule; no storage/schema/network. Decision ADR-01:
preserve unacknowledged IDs and their input order; remove only confirmed IDs. Do not use
clear-all or sort pending records. Outbox delivery/crash durability is deliberately NOT
implemented by this pure-function example. Next work is the duplicate acknowledgement test.
""")
    write(root, "docs/REQUIREMENTS.md", """# Requirements
| ID | Requirement | Status |
|---|---|---|
| FR-001 | Preserve records not explicitly acknowledged, retaining order | implemented, awaiting acceptance |
| FR-002 | Repeated acknowledgement has no extra effect | next test agreed; not verified yet |
""")
    write(root, "docs/BACKLOG.md", "# Active work\n\nParcel acknowledgement hardening: [active plan](ACK_PLAN.md).\n")
    write(root, "docs/KNOWN_ERRORS.md", """# Known errors

KE-PILOT-01: clear-all discarded newly queued beta while only alpha was acknowledged.
Fixed in working outbox.py, not committed. Three regression cases; no durability/network
claim. Repeated acknowledgement is the next agreed test, not already verified.
""")
    write(root, "docs/ACK_PLAN.md", """# Parcel acknowledgement plan

## Scope
Pure function only; no queue database/network integration. ADR-01 lives in ARCHITECTURE.md.

## Portions
- [x] Replace clear-all with confirmed-ID subtraction, retaining input order.
- [x] Three automated cases: new record survives; no acknowledgement preserves all; confirmed removed.
- [ ] Add repeated-acknowledgement idempotency regression, rerun counted finish.
- [ ] Product acceptance; no acceptance/commit/push/deploy authorization yet.

## Handoff
Branch main, no commits; all pilot files uncommitted. Source file outbox.py contains the fix.
Executed evidence is produced during fixture preparation: old behaviour must fail two of
three tests; fixed behaviour must pass all three, zero skips. Provider must distinguish
this recorded prior evidence from a test it personally ran.
Next concrete step: add the repeated-acknowledgement regression, do not rewrite architecture.
Forbidden now: edits during the read-only handoff test, commits, push, deploy, app restart,
network integration and access outside this synthetic project. No product acceptance received.
""")
    write(root, "outbox.py", BAD)
    write(root, "tests/test_outbox.py", TESTS)
    argv = (sys.executable, "-B", ".devframework/check.py", "finish")
    red = run(root, *argv)
    if red.returncode != 1 or "FAILED (failures=2)" not in red.stderr:
        raise ValueError("Pilot historical defect did not fail as expected: " + red.stdout + red.stderr)
    write(root, "outbox.py", GOOD)
    green = run(root, *argv)
    if green.returncode or "3 total, 0 skipped" not in green.stdout:
        raise ValueError("Pilot corrected behaviour failed: " + green.stdout + green.stderr)
    write(base, "red.txt", red.stdout + red.stderr)
    write(base, "green.txt", green.stdout + green.stderr)
    prompt = """This is a read-only handoff compatibility test, not an implementation task.
Read only this repository's files and its applicable instructions. Do not edit files,
run tests/apps, access external tools/services, commit, push or deploy. No prior chat exists.
Identify the project, current branch/base state, implemented behaviour, durable decision,
recorded verification (distinguish it from checks you ran), known limitation, next agreed
step, and authorization limits. Cite the local source for each. Do not invent missing facts.
Explain which applicable framework recipe would guide the next step. Answer concisely.
"""
    write(base, "prompt.txt", prompt)
    from source_scope import identity, snapshot
    return {"base": str(base), "project": str(root), "prompt": str(base / "prompt.txt"),
            "source_sha256": identity(snapshot(root)), "red": "3 tests; 2 failures", "green": "3 passed; 0 skips"}


if __name__ == "__main__":
    base = Path(tempfile.mkdtemp(prefix="devframework-pilot-")).absolute()
    print(json.dumps(prepare(base), indent=2))
