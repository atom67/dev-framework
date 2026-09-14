# Verification contract and limits

Requires Python 3.10+ and Git. No external Python packages. Run from the project root:

```text
python .devframework/check.py doctor --structural
python .devframework/check.py doctor
python .devframework/check.py secrets --staged
python .devframework/check.py secrets --worktree
python .devframework/check.py finish
python .devframework/check.py commit-check
```

## Doctor

Structural mode returns 0 for a valid scaffold but prints PROJECT NOT READY while facts
or commands are unconfigured. Default mode returns 2 for that state, 1 for structural
errors, and 0 only when configuration checks pass. It never claims tests were run.

Checks: required package files, local Markdown links in root instructions/active docs/
framework knowledge, unresolved install variables, explicit TODO(project) markers,
duplicate FR/NFR table definitions in REQUIREMENTS.md, and the use-case catalogue in
USE_CASES.md (unique headings, Test field, traceability rows, SET Enables ranges and
Preconditions against headings/rows; not whether a Flow names the right store), Claude
imports and profile routing.
Archive history and backups are excluded. Fenced examples are excluded from link/ID checks.
Markdown link titles, reference-style links and anchor existence are not fully parsed.
Schema/version/API-command drift needs a stack-specific check in commands.checks.

## Project commands

Edit project.json. Each command is an argv array, NOT a shell string. `{python}` resolves
to the current interpreter; other placeholders, shell variables and tilde are not expanded.
Use a reviewed script for compound build steps. Include all consumers of shared code.

Example for a Python project (adapt paths to actual code):

```json
{
  "format": 1,
  "profile": "generic",
  "timeout_seconds": 300,
  "commands": {
    "build": null,
    "test": ["{python}", "-B", ".devframework/run_unittest.py", "--start", "tests"],
    "checks": []
  },
  "build_not_applicable": "Interpreted package; no distributable build step",
  "test_evidence": {"format": "devframework-v1", "max_skipped": 0}
}
```

Finish requires doctor readiness, scans tracked and nonignored untracked WORKING files,
then runs build/test/checks, stopping on failure. It works before first staging. Tracked
deletions are represented in the snapshot. After each command it rejects source changes;
generated outputs need deliberate Git ignores, not ignored application source. On success
it prints the SHA256 source identity and counted test results. This is WORKTREE evidence,
not permission to commit or proof of the future index. Record the digest in Handoff.

Before an authorized commit use commit-check. It additionally scans index blobs and
requires index/worktree parity before/after commands, with no nonignored untracked files.
It rejects assume-unchanged/skip-worktree flags that could hide edits. Git handles newline
attributes/executable bits. The runner never stages, commits, pushes or launches an app.
In CI a clean checkout permits the same commit-check command.

### Fresh counted test evidence

Each test invocation receives a new `DEVFRAMEWORK_RUN_ID` and a unique, initially absent
`DEVFRAMEWORK_TEST_REPORT` path outside the repository. The configured runner writes JSON:

```json
{"format": 1, "run_id": "<copy DEVFRAMEWORK_RUN_ID>", "total": 12, "failed": 0, "errors": 0, "skipped": 0}
```

The unittest adapter does this automatically and fails on zero/all-skipped tests even
standalone. Other stacks need a reviewed wrapper mapping their native JUnit/TRX/etc.
result into this contract. Missing/oversized/malformed/stale reports, invalid counts,
failures/errors, no executed tests or exceeded max_skipped fail. Expected failures count
as skips in the unittest adapter. A legacy `python -m unittest discover` command without
an evidence wrapper is deliberately NOT sufficient even when its exit status is 0.
On upgrade, project.json is preserved: add test_evidence and adapt the test command.

Counts do not prove relevant coverage or honest runner implementation. Configured commands
remain trusted. A snapshot covers named Git source files, not ignored dependencies, host
configuration or a malicious process that edits and restores files between observations.
Pin dependencies, isolate tests and preserve relevant environment details with evidence.

This is NOT a sandbox: inspect configured commands and their scripts before running them.
Commands may print application output; they must redact secrets themselves. A timeout
terminates the direct command, not necessarily detached descendants; use test tools with
owned child-process cleanup and inspect leftovers before retrying.

## Source-secret heuristic

The staged mode reads regular-file index blobs by object ID. Worktree mode reads a bounded
source snapshot. Both detect quoted assignments (including C# verbatim), bare dotenv/YAML
scalars at line start, common token shapes and private-key headers. Findings show path/line/type,
never the value. Obvious whole-value placeholders such as REPLACE_ME are accepted.
Tests/docs have no blanket exemption. UTF-8 and BOM-marked UTF-16 text are supported.
Exact token_type Bearer/MAC and plain token_endpoint/token_url URLs without credentials,
query or fragment are metadata, not passwords. Independently recognizable credential
shapes still fail. Arbitrary expressions, multiline/raw/encoded values and provider-specific
formats need a richer scanner; this is deliberately not a universal language parser.

An unreadable/unmerged/empty index, unsupported entry or exceeded size limit fails.
Limits: 10 MiB/blob and 100 MiB total. Non-text files are explicitly listed as NOT
TEXT-SCANNED. No heuristic matches does NOT certify no secrets: split/encoded values,
unknown credential formats, Git history, submodules and build artifacts need other checks.
Artifact verification must understand the packaging format and fail on uninspected payloads.

## Optional local hook and CI

The installer never changes Git configuration or existing hooks. With authorization,
integrate the staged command into the project's existing pre-commit hook, preserving its
other checks. On Windows, invoke the configured Python executable without a policy bypass.
Hooks are a convenience, not the only enforcement point.

CI should use a clean checkout, configured runtime/dependencies and `commit-check`
command. Add CI only after commands and isolation are reviewed; do not upload diagnostics
or artifacts containing credentials. A clean checkout's index represents its tracked commit.
The framework CI workflow targets Windows and Linux; an individual consumer still needs
its own application build and integration coverage. Record actual CI outcomes separately
from the existence of a workflow file.
