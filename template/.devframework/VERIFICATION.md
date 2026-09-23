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

Finish requires doctor readiness, scans tracked and nonignored untracked WORKING files for secrets,
then runs build/test/checks, stopping on the first failure. It works before first staging.
This is evidence about the working tree, not permission to commit.

Before an authorized commit use commit-check: finish plus a secret scan of the staged files.
The runner never stages, commits, pushes or launches an app.

### Test counts

The test command prints one line that finish reads:

```text
TESTS: total=12 failed=0 skipped=0
```

finish fails when that line is missing, when a test failed, when nothing ran (zero discovered or all
skipped) or when skips exceed `max_skipped`. run_unittest.py, run_pytest.py and run_smoke.py print it;
another stack needs a wrapper that prints it from its own results. A bare `python -m unittest` is NOT
enough even when it exits 0: zero discovered tests also exit 0.

Counts do not prove relevant coverage. Configured commands remain trusted; isolate tests from real data.

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
