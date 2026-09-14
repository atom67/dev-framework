---
name: catch-up
description: Reconstruct the DEV Framework documentation set from a codebase that was already built without it — requirements, architecture, use cases, known errors, backlog, regression plan, release procedure — plus the cost and secret audits, with everything unverifiable marked as unconfirmed rather than guessed. Use when the operator says "catch up the docs", "restore documentation", "we already have code, apply the framework", "backfill AGENTS docs", "восстанови документацию", "подтяни доки под фреймворк".
argument-hint: "<target-repo-path>"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Catch up the documentation on an existing codebase

The framework assumes documents that grew alongside the code. This skill is for the
ordinary case where they did not: the product works, the `docs/` skeletons are empty, and
everything they should contain exists only in the code and in the operator's head.

Reconstruct them from the code. Not from the README, not from an older design document,
not from what the code looks like it ought to do.

## The rule that governs everything here

**A reconstructed statement is either read out of the code, or marked unconfirmed.**

There is no third option, and inventing one is the single way this exercise does harm.
Three documents in the source project stated the storage schema version as 12 while the
real one was 43, and it stopped nobody for months. A drifted document is worse than a
missing one: the missing one sends you to the code, the drifted one confidently lies and
you believe it. You are about to write seven documents at once, which is the highest-risk
moment that failure has.

So: every document ends with an **Unconfirmed** section. Anything you inferred, could not
reach, or had to guess at goes there by name, addressed to the operator. A named gap gets
filled. A plausible guess never gets checked.

## 0. Preconditions

`AGENTS.md` and the `docs/` skeletons must already be in the target — run
`import-dev-framework` first if they are not. Read `AGENTS.md` and this repository's
`LESSONS.md` before starting; you are about to apply rules whose reasons matter.

Note the scale target in `PROJECT.md`. Section 4 of this skill depends on it.

## 1. This is a programme of work — make the checklist first

On anything larger than a few hundred files, reconstruction will not fit in one
iteration. Section 3 of `AGENTS.md` therefore applies to the reconstruction itself:
copy `docs/CHECKLIST_TEMPLATE.md` to `docs/CATCH_UP.md` **before the first edit**.
Prefer a few large iterations (inventory; reconstruct architecture, requirements and
use cases together; remaining docs; cost and secret audits) each closed with doctor
or the relevant audit plant, not one file per tiny portion. Independent reconstruction
or audit work that does not share an unfinished file **must** run in parallel subagents
when the host provides them. At the **end of every
reply to the operator**, copy that checklist and strike through what is done, until
every item is struck. When it is finished, move the file to `docs/archive/` in full.

Doing this to yourself first is also the honest test of whether the rule is workable.

## 2. Inventory

Establish the ground truth before writing a line:

- Languages, entry points, build and dependency manifests, and what the artefacts are.
- Module and directory layout, and which parts are actually loaded at runtime versus dead.
- Test suites: what exists, whether it passes today, and what it covers. Those names
  are what later become `Test: covered` on a use case. A suite that does not isolate
  from real data/services is not coverage; record it as unconfirmed.
- Git history: the shape of the work, and — valuable — every commit whose message says
  `fix`. Those are the known errors, already written down by the person who hit them.
- An issue tracker, if there is one.

Record how big the thing is in numbers. You will need them for the handover.

## 3. Reconstruct, in this order

Each document is filled to the skeleton's own format — ID schemes, tables, and headers are
already defined in the files; do not invent parallel ones.

**`docs/ARCHITECTURE.md`** — first, because the others reference it. Components and their
real responsibilities and dependencies, taken from the module graph rather than from
intent. The data schema, with the version **read from the migrations or the code**; if
there is no schema, delete the version claim and say there is none. Data flows that cross
a process, a device, or a network boundary, each with its frequency — frequency belongs
here because section 4 checks against it. Finally, what state is persisted against a
crash, which is usually where the first real gap appears.

**`docs/REQUIREMENTS.md`** — functional requirements are what the product demonstrably
does, one `FR-###` per user-visible behaviour, status `done` only where you verified it.
Non-functional requirements are the constraints already implemented: timeouts, retry
bounds, size limits, permission models, accessibility affordances. Numbers are permanent
from the moment you assign them, so number conservatively and leave gaps rather than
renumbering later.

Requirements are the document most likely to be contaminated by intent. If the code does
X and the README promises Y, the requirement is X — and Y goes to the operator as a
question, because you have just found either a bug or a stale README.

**`docs/USE_CASES.md`** — after architecture and requirements, because a case names
components and `FR-###` by reference. Replace the example SET/UC rows; copy further
cases from `docs/USE_CASE_TEMPLATE.md`. Every user-visible or automatic benefit path
gets a stable `UC-###`, a trigger (Interactive or Automatic), SET preconditions, a
Flow that names the live store when more than one exists, an Outcome, and exactly one
`Test` status:
- `covered` — only if inventory found a real isolated test (or a named manual
  regression case) that guards this path. Link it. A green suite that never touches
  the path is not coverage.
- `gap` — testable by ordinary functional means, but not yet covered. Also record it
  in `docs/BACKLOG.md`. This skill does not write the missing test.
- `NFV` — cannot be a standard automated functional test; row in the NFV register
  with the reason and how it is actually checked. Never a synonym for "no test yet".

Do not pad SET Enables ranges. An edition/public cut uses
`docs/USE_CASES_SLICE_TEMPLATE.md` and does not renumber living cases. After the
catalogue and the other docs in this section are written, run
`python .devframework/check.py doctor` in the target: duplicate IDs, a heading
without `Test`, a heading missing from the traceability table, or a SET citation to
an unwritten case must be fixed before handover. Doctor still does not judge whether
Flow named the correct store — that stays a review item.

**`docs/KNOWN_ERRORS.md`** — the richest seam in an existing codebase, and the one nobody
ever writes down. Sources: `TODO`, `FIXME`, `HACK`, `XXX` comments; skipped, disabled, or
`xfail` tests; commented-out code with a nervous comment above it; workarounds with an
apology attached; bug-fix commit messages describing something still present elsewhere;
open issues. Give each a `KE-YYYY-MM-DD-SLUG` ID dated today — today is when it became
known to the project, whatever its age.

Two rules from the skeleton bind here. A claim must be true of the **whole** codebase; a
universal statement that holds in one place is worse than no entry, because it stops
people looking. And where the code contains a non-obvious defence you can trace to an
entry, add the ID to the code comment — that is how the reason survives the next refactor
by someone who thinks the line looks redundant.

**`docs/BACKLOG.md`** — what is in flight and what is agreed next. Apply the trimming rule
from the first day: active items, next agreed items, three most recently finished. Do not
import the git history into it. The file this replaces reached 167 KB in the source
project, at which point nobody read it and it stopped steering anything.

**`docs/REGRESSION_TEST.md`** — only what needs a human at the screen: crash and restart
paths, first-run and recovery flows, permission prompts, modal dialogs, anything that
would kill the test process if automated. If a case can be automated, automate it instead
and do not add the case. This file is the residue.

**`docs/RELEASE.md`** — read the real build, publish, and deployment scripts and any CI
configuration, and write the procedure that is actually performed, including the order
between components. If the truth is "one person does it by hand and remembers the steps",
write that down as the procedure and mark it unconfirmed. A wrong release checklist is
worse than an absent one.

**`PROJECT.md` / `CLAUDE.md`** — reconcile facts against everything above. `CLAUDE.md`
is the adapter and must not grow a second copy of the rules. `PROJECT.md` is the file
most likely to still carry `TODO(project):` from import.

## 4. The cost audit — the part that pays for the exercise

Find every repeating operation: timers, schedulers, cron entries, polls, retry loops,
loops containing a sleep, watchers, keepalives, background services. For each one compute
the load at the project's scale target and write it as a `cost:` comment at the site, in
the comment syntax of that language.

Do the arithmetic explicitly — per-device rate, per day, times the target, per second:

```
# cost: 1 request per minute, 1 440 per day per device;
#       at <scale target> that is <N> per day, <N> per second.
```

The five-second poll that produced this rule lived **63 days** and cost **17 000 requests
per day from a single phone**. The line looked harmless. Nobody had ever written the
number down — that is the whole failure, not the interval.

Expect this pass to find ceilings, because it did in the source project: costing 26
existing sites surfaced a third-party integration whose own rate limits are exceeded at
the target scale, server handlers written for one user that do not survive being put in a
loop for everyone, and a design needing one held connection per client. **A ceiling is a
finding, not a licence to refactor.** It goes into `REQUIREMENTS.md` and `BACKLOG.md` and
in front of the operator. Silently rewriting the polling architecture during a
documentation task is exactly the scope creep section 3 forbids.

## 5. The secret audit

Two different exposures, two different checks.

**Sources** — only files git actually tracks, and read the **index**, not the working
tree: `git show :<path>`. A check that reads the disk can be defeated by staging a fix and
then reverting it unstaged; the check sees "fixed", stays quiet, and the unfixed version
goes into the commit. That bug appeared three times independently in the source project.

**Build output** — a secret can be absent from the sources and still sit inside a shipped
binary. Check the whole output *directory*: in release mode the payload is compressed and
scanning one file proves nothing.

Anything found is treated as compromised — moved to protected storage, rotated, and
recorded in `KNOWN_ERRORS.md` with an ID. Rotation is the operator's action; say so
plainly and do not attempt it. MVP or prototype status is not an exemption; there is no
such exemption.

## 6. Verify the verification

Both audits in this skill are checks, and a check that has never fired is not a check —
it is a decoration that manufactures confidence, which is worse than having nothing.

Before reporting either result, plant the thing it is supposed to catch and confirm it
fails with the exact expected value; then restore and confirm it passes. Plant a fake
credential in a tracked file for the secret pass. Plant an uncommented timer for the cost
pass. For the catalogue contract, plant a SET Enables range that names an unwritten
`UC-###` and confirm `python .devframework/check.py doctor` fails on that citation;
then restore.

This is not theoretical. Planting a password in the source project found two real defects
in checks that had been running green for months: a pattern that required the keyword at
the *start* of the identifier, so `_devPassword` and `ApiToken` walked straight through,
and a pattern with an empty first alternative, which matches everything and had therefore
been silent on every input since the day it was written. Neither would have been found by
reading the code.

## 7. Hand it over

To a product owner, in numbers, with no instruction to open a file or run a script:

- How many components, requirements, use cases, and known errors were reconstructed,
  and from what. For use cases: how many `covered` / `gap` / `NFV`, and that doctor
  accepted the catalogue contract (or what it rejected).
- The cost audit: how many repeating sites were found, and the total load at the scale
  target. Name every ceiling in plain language — which limit, whose limit, at what point
  it is reached, and what the options are. These are product decisions and they are the
  most valuable thing this exercise produces.
- The secret audit: what was scanned, what was found, and — if anything was — that
  rotation is needed and is theirs to authorise. State that you planted a defect to
  confirm each check actually fires, and what it caught.
- The **Unconfirmed** list from every document, as questions they can answer, phrased in
  product terms rather than as code archaeology.
- Anything you deliberately did not do, and why.

Then archive `docs/CATCH_UP.md` into `docs/archive/`. A finished plan left in `docs/`
becomes a second source of truth and starts contradicting the first.

## What this skill does not do

It does not fix what it finds. It does not refactor, it does not rotate secrets, it does
not change a polling interval, and it does not close a known error. Reconstruction that
quietly repairs things produces documents nobody can trust and a diff nobody can review.
Findings go into the documents and to the operator; fixes are separate, agreed work.
