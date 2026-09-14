# Regression coverage — DEV Framework 0.2

Command: `python -B scripts/verify.py` (also `install.ps1 -SelfTest`).
All fixtures are temporary projects, with no real tokens, user databases or remote writes.

| Risk | Automated evidence | Boundary not claimed |
|---|---|---|
| Label-only scale substitution | test_scale_math_three_sizes: 5k/10k/50k, numeric expected totals | production traffic/load capacity |
| Knowledge disappears at provider switch | local lessons/patterns, each profile, adapter import/link tests | actual model sessions/accounts |
| Overwrite existing project | legacy conflict, forced backup, project-owned preservation, no-op update | semantic merge of custom instructions |
| Redirect writes outside target | overlap, traversal/case, Windows junction or POSIX symlink, hardlink tests | hostile concurrent path swapping |
| Interrupted update damages data | injected write failure, real child os._exit, journal/hash recovery, later-edit refusal | power-cut/filesystem durability |
| Concurrent installer or stale plan | OS lock rejection and newer-manifest race test | coordination with arbitrary editors |
| Doctor false green | missing knowledge/config, placeholders, links, duplicate IDs, padded SET→UC ranges, missing Test/traceability rows, fenced imports, incomplete manifest | arbitrary code/schema semantic drift; which-store claims in Flow |
| Secret in index but not worktree | staged/worktree mismatch both ways, camelcase, UTF-16, redacted CLI, size limit | exhaustive credential detection, history/artifacts |
| Finish hides failure | missing commands, nonzero build/test/check, explicit N/A build, injected timeout | detached descendant cleanup; real app test quality |
| Exit 0 but no tests ran | missing/stale/malformed/count-invalid evidence, zero/all-skipped suites, skip budget | relevant coverage and honest custom runner implementation |
| Tested tree differs from commit | parity mismatch, assume-unchanged, no implicit staging, changed source during build | ignored inputs and malicious edit/revert races |
| Common secret syntax missed | dotenv/YAML/C# cases, safe OAuth metadata, actual Git blobs, unstaged secrets | raw/multiline/encoded/unknown credentials |
| Transfer map gives false completeness | 24 unique IDs, five source fingerprints, local destinations; explicit exclusions | semantic completeness of all Main OS history |
| Handoff fixture has invented evidence | actual old-code 2/3 failures then fixed 3/3 pass; no commits, snapshot digest | live provider behaviour, tested separately |
| Windows entry point broken | PowerShell preview and actual install/update; full SelfTest entry point | legacy PowerShell policy configuration |

Final run details are in docs/PLAN.md so the result has one living source of truth.
GitHub workflow is configured for Windows/Linux and Python 3.10/3.13; hosted results
cannot be claimed until an accepted commit is pushed and CI actually executes.

## Engineer-run checks beyond this suite

- Fresh-session provider compatibility as described in template/.devframework/AGENTS_GUIDE.md.
  Actual attempts and access blockers: [pilot evidence](evidence/HANDOFF_2026-08-31.md).
  A blocked model invocation is not a passed handoff test.
- Stack-specific commands, app regressions and runtime data-flow monitoring must be
  implemented in each consumer. Installing recipes is not running those application tests.
