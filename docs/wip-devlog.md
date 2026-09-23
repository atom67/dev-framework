# wip-devlog — Under construction marker + devlog from the session log (v1.4.0)

**Started:** 2026-09-23
**Status:** in progress

## Scope agreed with the operator

What is in, and — just as important — what is explicitly out. Decisions the operator has
already made, quoted, so they are not silently re-litigated later.

- In: ...
- Out: ...

## Portions

One portion = one iteration the operator can accept or send back. Make it as large as
the documentation, code analysis and closing tests can honestly carry — not a week-long
stage, and not a handful of file-level chores.

### 1. <portion name>


**Acceptance:** what the operator will be shown when this portion is done — the check that
was performed and its result, in plain language. Not "open the file and look".

### 2. <portion name>


**Acceptance:** ...

## Deliberate limitations

Shortcuts taken on purpose, each with the ceiling it has and what an upgrade would cost.
Recording them here is what stops them being rediscovered as bugs.

- ...

## Handoff — update at every portion boundary and provider switch

- Branch/base commit and task-owned uncommitted changes:
- Current portion and next concrete step (the live checklist is copied at the end of
  every operator reply; do not maintain a second list here):
- Agreed decisions and links to their source of truth:
- Commands/checks actually run, date, result/counts, environment and evidence:
- Checks not run, reason and remaining risk:
- Known errors or deliberate limits affecting continuation:
- Acceptance/commit/deploy authorization actually received (never infer it):

The next agent reconciles this with git and code; a stale handoff is not authority.

## Product decisions or external authorization still needed

Only choices the operator can make from the evidence presented, or authorization the
engineer cannot grant. Engineering smoke tests remain the engineer's responsibility;
if access is unavailable, record the unverified behaviour and risk in Handoff above.

- [x] doctor: <!-- under-construction: reason (until YYYY-MM-DD) --> in PROJECT.md or docs/ skips that document's checks, warns every run, expires on the date; never skips secrets, tests or file presence
- [x] brief lists documents under construction; AGENTS.md rule + contract line
- [x] transcript.py: dialogue from the Claude Code session JSONL (auto-located by cwd) or Hermes state.db; user/assistant text verbatim, tool calls summarized, system reminders stripped, secrets redacted, only the devlog's day
- [x] check.py devlog --dialogue auto|none|<file>|hermes[:id]; DEVLOG.md and AGENTS.md say the entry is filled from the log
- [ ] tests: marker (skip, expiry, framework files not markable); transcript from synthetic Claude JSONL and Hermes db; v1.4.0; gate once; push; CI
