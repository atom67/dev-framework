# CHECKLIST TEMPLATE

Copy this file to `docs/<TOPIC>.md` **before the first code edit** of any programme of
work that does not fit in one session. Delete this header block in the copy.

While the programme runs, the copy is the single living document for that topic. When it
is finished, move it to `docs/archive/` in full — a finished plan left in `docs/` becomes
a second source of truth and starts contradicting the first.

Rules that govern this file are in `AGENTS.md` section 3. The short version: portions, not
stages; reconcile at the start and end of every portion; an item is done only after it is
built and verified; new work becomes an item before it becomes code.

---

# <TOPIC> — <one line saying what this programme achieves>

**Started:** YYYY-MM-DD
**Status:** in progress

## Scope agreed with the operator

What is in, and — just as important — what is explicitly out. Decisions the operator has
already made, quoted, so they are not silently re-litigated later.

- In: ...
- Out: ...

## Portions

One portion = one thing the operator can accept or send back.

### 1. <portion name>

- [ ] ...
- [ ] ...

**Acceptance:** what the operator will be shown when this portion is done — the check that
was performed and its result, in plain language. Not "open the file and look".

### 2. <portion name>

- [ ] ...

**Acceptance:** ...

## Deliberate limitations

Shortcuts taken on purpose, each with the ceiling it has and what an upgrade would cost.
Recording them here is what stops them being rediscovered as bugs.

- ...

## Handoff — update at every portion boundary and provider switch

- Branch/base commit and task-owned uncommitted changes:
- Current portion and next concrete step (reference the checklist, do not duplicate it):
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

- [ ] ...
