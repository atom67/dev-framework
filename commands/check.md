---
description: Run a DEV Framework gate — doctor, finish, commit-check, selftest, secrets or hostcheck
argument-hint: "[target] doctor|finish|commit-check|selftest|secrets|hostcheck"
allowed-tools: Bash, Read, Edit
---

Run the gate named in `$ARGUMENTS` (default: `doctor` in the current project) and report its verdict:

```bash
python .devframework/check.py doctor          # structure + configuration; READY or the setup items
python .devframework/check.py finish          # + secret heuristic + build + counted tests + checks (needs git)
python .devframework/check.py commit-check    # finish + index/worktree parity, before an authorized commit
python .devframework/check.py selftest        # plants a bad use case and a fake token in a temp copy; both gates must fire
python .devframework/check.py secrets --worktree
python .devframework/hostcheck.py .           # host rules that fight the framework, with quotes and fixes
```

Rules:

- Child output goes to `.devframework/last_run.log`; report counts and the first failure, not the whole log.
- `finish` is evidence for the **worktree**, never for a commit; no commit or push without the operator's authorization.
- `hostcheck` findings are the **operator's** decision — show the list once with the proposed fix per line, wait for
  their answer, edit the host file only with authorization (back it up), then record every line in
  `PROJECT.md` → `## Host precedence` as `- <class>@<file>: replaced <date>` or `kept — <reason>`.
  Never record a decision yourself, even when told not to ask questions.
- A failing gate is a result to report, not something to work around.
