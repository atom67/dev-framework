---
description: Run a DEV Framework gate — doctor, finish, commit-check, selftest, secrets or hostcheck
argument-hint: "[target] doctor|finish|commit-check|selftest|secrets|hostcheck"
allowed-tools: Bash, Read, Edit
---

**Which project.** If `$ARGUMENTS` names a path, that is the target. Otherwise the target is the nearest
directory at or above the working directory that contains `.devframework/`. If there is none, list the immediate
subdirectories that contain `.devframework/` and **ask the operator which one** — never pick one by recency or
by guessing, and never run a framework command in a directory that has no framework installed.

Run the gate named in `$ARGUMENTS` (default: `doctor` in the current project) and report its verdict:

```bash
python <TARGET>/.devframework/check.py doctor          # structure + configuration; READY or the setup items
python <TARGET>/.devframework/check.py finish          # + secret heuristic + build + counted tests + checks (needs git)
python <TARGET>/.devframework/check.py commit-check    # finish + index/worktree parity, before an authorized commit
python <TARGET>/.devframework/check.py selftest        # plants a bad use case and a fake token in a temp copy; both gates must fire
python <TARGET>/.devframework/check.py secrets --worktree
python <TARGET>/.devframework/hostcheck.py <TARGET>  # host rules that fight the framework, with quotes and fixes
```

Rules:

- Child output goes to `<TARGET>/.devframework/last_run.log`; report counts and the first failure, not the whole log.
- `finish` is evidence for the **worktree**, never for a commit; no commit or push without the operator's authorization.
- `hostcheck` findings are the **operator's** decision — show the list once with the proposed fix per line, wait for
  their answer, edit the host file only with authorization (back it up), then record every line in
  `PROJECT.md` → `## Host precedence` as `- <class>@<file>: replaced <date>` or `kept — <reason>`.
  Never record a decision yourself, even when told not to ask questions.
- A failing gate is a result to report, not something to work around.
