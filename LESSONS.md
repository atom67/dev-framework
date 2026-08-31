# Lessons

Every rule in `template/AGENTS.md` was bought with an incident. This file is the receipt.

A rule without its reason gets deleted by the next person who finds it inconvenient — and
they are not being careless, they genuinely cannot see what it is holding up. Keep the
numbers. "Polling was expensive" persuades nobody; "17,000 requests a day from one phone
for 63 days" ends the discussion.

Source project: Main OS (private; .NET 8 desktop, ASP.NET Core server, MAUI Android),
roughly five months of work through 2026-08.

---

## 1. The five-second poll — where the cost rule came from

Message polling ran every five seconds. It lived **63 days** and produced **17,000
requests per day from a single phone**. The line of code looked harmless: five seconds,
so what.

Nobody had ever written the number down. That is the whole failure — not the interval, the
absence of arithmetic.

**Rule produced:** every repeating operation is saved together with a `cost:` comment
naming the load at a declared scale target. See `AGENTS.md` section 5.

**Unexpected payoff.** Costing the 26 existing repeating sites surfaced three ceilings
nobody had seen: a third-party integration whose own rate limits are exceeded at the
target scale; server handlers written for one user that do not survive being put in one
loop for everyone; and a message-wait design needing one held connection per client. All
three moved into planning instead of being discovered at launch.

---

## 2. Storage schema v12 in the documents, v43 in the code

Three documents stated the storage schema version as 12. The real one was 43. It stopped
nobody, for months.

A document that has drifted is worse than a missing one: the missing one sends you to the
code, the drifted one confidently lies and you believe it.

**Rule produced:** documentation maintenance is a listed obligation per document, and the
"current version" statement is checked mechanically. See `AGENTS.md` section 7.

**Second-order lesson.** The first version of that check also flagged the legitimate
migration history — `v14`, `v15`, and so on in the architecture document — producing
**22 false alarms in one run**. Twenty-two false alarms kill trust in a check faster than
its absence does. Check only the assertions that claim to be current.

---

## 3. 2.5 GB of dead build output

Publishing to version-stamped directories (`publish/server-0.6.1`, `temp/server-0.5.4`,
versioned `.zip` and `.apk` copies) accumulated about **2.5 GB** of dead copies before
anyone looked.

**Rule produced:** always publish to the same fixed directory; remove staging after a
rollout, locally and remotely. See `AGENTS.md` section 2.

Note the shape of the fix: the cleanup was automated on push, and the automation was
written so it **never blocks the push**. Housekeeping that can fail a developer's push
gets disabled within a week.

---

## 4. The check that read the working tree instead of the index

A check scanned files on disk. Commits contain the **index**. So: stage a fix, then revert
it in the working tree without re-staging — the check reads disk, sees "fixed", stays
quiet, and the unfixed version goes into the commit.

The same bug then appeared independently in two more checks written later.

**Rule produced:** a check that guards a commit reads `git show :<path>`, not the file
system. Recorded as a known error with an ID, so the next check gets it right by reading
the entry instead of rediscovering it.

---

## 5. The check that had never fired

A check that has never failed is not a check. It is a decoration, and it manufactures
confidence, which is worse than having nothing.

Two real defects were found by deliberately planting the thing the check was meant to
catch:

- A secret-detection pattern required the keyword at the **start** of the identifier, so
  `_devPassword` and `ApiToken` passed straight through.
- An "is this value benign" pattern had an empty first alternative, which matches
  everything — so the check was silent on every input, permanently.

Both were caught by a planted password. Neither would have been caught by reading the code.

**Rule produced:** verify the verification. Plant the defect, confirm the check fails with
the exact expected value, restore, confirm green. See `AGENTS.md` section 4.

---

## 6. The backlog that reached 167 KB

The operational queue accumulated everything ever finished until it hit **167 KB**, at
which point nobody read it and it stopped steering anything.

**Rule produced:** after acceptance, trim to active items, the next agreed items, and the
three most recently finished features. Keep it under 80 KB. See `AGENTS.md` section 3.

---

## 7. The same rule in two files, already diverging

The source project carried its operating rules in both `AGENTS.md` (35 KB) and `CLAUDE.md`
(21 KB). The documentation-maintenance section existed in both — and had **already
diverged**: each listed a document the other did not.

Nobody decided to diverge. Two copies simply cannot be edited together forever.

**Rule produced in this package:** process rules live in `AGENTS.md` only. `CLAUDE.md`
holds project facts plus an explicit prohibition on restating the rules. This is the one
place where the package deliberately does **not** copy the source project.

---

## 8. A read error turned into a factory reset

Loading the settings file went wrong, and the recovery path quietly produced factory
defaults — erasing the stop password, the API tokens, and the monitored-application list.
Three mechanisms conspired:

- the corrupt file was quarantined **before** the operator had chosen anything, so
  "restore the original" no longer existed by the time it was offered;
- a parser returning `null` was treated as success and swallowed into a fresh object;
- a missing file was indistinguishable from a first run, so a profile that had existed for
  months could be reset by a single failed read.

**Rules produced:** bounded retries for transient failures; no automatic reset after a
failed load of an existing profile; factory defaults only on a **confirmed** first run;
resetting is a separate explicit operator action; block every automatic save until valid
configuration is loaded. See `AGENTS.md` section 8.

---

## 9. The crash handler that kept working

The global handler showed an error window and then **continued running** — with the logger
already closed, on state nobody had verified. Adding a notification would not have fixed
it; the defect was the continuation.

Three further traps found while fixing it, worth knowing in advance:

- a modal dialog still pumps the event queue, so timers keep firing behind the crash
  window;
- the "stop everything" routine originally listed timers by name and covered **3 of about
  25** — a hand-maintained list of things to stop is guaranteed to drift, so sweep them
  reflectively instead;
- one of the stop routines deleted persisted state as part of stopping, so crashing would
  have destroyed exactly the data that crash-resilience exists to protect.

**Rule produced:** an unexpected failure stops the work and offers restart or close. It
does not continue, does not write unverified memory over good data, and does not loop
restarting. See `AGENTS.md` section 8.

---

## 10. Work decided under a lock, executed outside it

Moving slow work out of a lock is correct, and it opens a window: the decision was made
under the old state, the execution happens under the new one. Ending a session cleared all
state and removed the blocks — and the already-queued work then recreated a block that had
just been cancelled.

**Pattern worth carrying:** when work is queued under a lock and performed outside it,
capture a generation counter with the queued item and drop the item if the generation
changed. Cheap, and it makes the whole class of bug impossible rather than unlikely.

---

## 11. Acceptance handed back to the operator

Acceptance repeatedly arrived as "open this file near line 240", "try making a commit",
"check the log". The operator is a product owner. They do not read code.

Handing them the verification is not finishing the work — it is handing them its last
part, and it is the part they are least equipped to do.

**Rule produced:** acceptance contains a check *you* ran with its result quoted in
numbers, what is visible in normal use, and the product decisions they can actually make.
See `AGENTS.md` section 4.

---

## Deliberately not carried over: the automated checks

The source project enforces several of these rules with 1,237 lines of Python plus two git
hooks. Those were **not** ported — the operator's decision, since the next project's stack
is not settled, and a check written for the wrong language is worse than no check.

The protocol they enforce is written down in `AGENTS.md`. When automation is wanted, port
from the reference rather than reinventing: these were debugged against real defects.

| Reference | Lines | What it does | Portability |
|---|---|---|---|
| `scripts/checks/secrets.py` + its test | 301 | secrets in tracked sources and in build output | high — regexes plus an extension list |
| `scripts/attribution/build.py` | 317 | per-commit model attribution from agent transcripts and commit trailers | high — two paths to change |
| `scripts/checks/finish.py` | 242 | one command: build affected projects, run tests, run checks, stop before pushing | medium — the project list is a constant |
| `scripts/checks/doc_drift.py` | 207 | current-version claims in documents against the code | low — knows the source project's files |
| `scripts/checks/periodic_cost.py` | 170 | repeating work with no `cost:` calculation | low — patterns are language-specific |
| `.githooks/pre-commit`, `pre-push` | 2 files | runs the checks; cleans build output on push, never blocking it | high |

Three things about them are worth reusing whatever the language:

1. Read the **index**, not the working tree (lesson 4).
2. Ship a test that plants the defect the check exists to catch (lesson 5).
3. Never block on housekeeping; only block on correctness (lesson 3).
