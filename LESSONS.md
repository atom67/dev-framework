# Lessons

These are incident-derived lessons, not proof that every source-project implementation
is universally correct. The installer copies this canonical file to
`.devframework/LESSONS.md`; projects do not need access to Main OS to read it.
Rules live in the project-root AGENTS.md; recipe links are in .devframework/patterns/README.md.

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
"current version" statement needs a stack-specific mechanical check. See AGENTS.md section 3.

**Second-order lesson.** The first version of that check also flagged the legitimate
migration history — `v14`, `v15`, and so on in the architecture document — producing
**22 false alarms in one run**. Twenty-two false alarms kill trust in a check faster than
its absence does. Check only the assertions that claim to be current.

---

## 3. 2.5 GB of dead build output

Publishing to version-stamped directories (`publish/server-0.6.1`, `temp/server-0.5.4`,
versioned `.zip` and `.apk` copies) accumulated about **2.5 GB** of dead copies before
anyone looked.

**Transferable rule:** bounded retention and validated cleanup of task-owned staging.
The source project chose a fixed publish directory; a service may instead need immutable
versioned artifacts and a known-good rollback set. See AGENTS.md section 1 and the profile.

Note the shape of the fix: the cleanup was automated on push, and the automation was
written so it **never blocks the push**. Housekeeping that can fail a developer's push
gets disabled within a week.

---

## 4. The check that read the working tree instead of the index

A check scanned files on disk. Commits contain the **index**. Stage a defective version,
then fix the working file without re-staging: the check sees a fix, while the commit still
contains the defect. Conversely, an unstaged defect must not be mistaken for staged content.

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

**Rule produced in this package:** process rules live in AGENTS.md only, project facts in
PROJECT.md, and executable verification commands in .devframework/project.json. CLAUDE.md
imports the shared documents. Provider-private memory is not a portable source of truth.

---

## 8. A read error turned into a factory reset

Loading the settings file went wrong, and the recovery path quietly produced factory
defaults — erasing the stop password, the API tokens, and the monitored-application list.
Three mechanisms conspired:

- the corrupt file was quarantined **before** the operator had chosen anything, so the
  original path disappeared; the next launch could mistake that absence for first run,
  even though the bytes still existed under the quarantine name;
- a parser returning `null` was treated as success and swallowed into a fresh object;
- a missing file was indistinguishable from a first run, so a profile that had existed for
  months could be reset by a single failed read.

**Rules produced:** bounded retries for transient failures; no automatic reset after a
failed load of an existing profile; factory defaults only on a **confirmed** first run;
resetting is a separate explicit operator action; block every automatic save until valid
configuration is loaded. See AGENTS.md section 7 and the configuration recipe.

---

## 9. The crash handler that kept working

The global handler showed an error window and then **continued running** — with the logger
already closed, on state nobody had verified. Adding a notification would not have fixed
it; the defect was the continuation.

Three further traps found while fixing it, worth knowing in advance:

- a modal dialog still pumps the event queue, so timers keep firing behind the crash
  window;
- the "stop everything" routine originally listed timers by name and covered **3 of about
  25**. Reflection was a local mitigation, not a general lifecycle design: it cannot by
  itself cancel in-flight work or timers owned by other services. Register owned workers,
  gate new work/writes, cancel and await quiescence with a bounded deadline;
- one of the stop routines deleted persisted state as part of stopping, so crashing would
  have destroyed exactly the data that crash-resilience exists to protect.

**Rule produced:** an unexpected invariant failure stops affected work and unsafe writes.
A desktop may offer restart/close; a service needs readiness, draining and a bounded
supervisor policy. See AGENTS.md section 7 and the crash-recovery recipe.

---

## 10. Work decided under a lock, executed outside it

Moving slow work out of a lock is correct, and it opens a window: the decision was made
under the old state, the execution happens under the new one. Ending a session cleared all
state and removed the blocks — and the already-queued work then recreated a block that had
just been cancelled.

**Pattern worth carrying:** when work is queued under a lock and performed outside it,
capture a generation counter with the queued item and drop the item if the generation
changed. Validate the generation and commit the state change atomically under the same
ownership boundary; otherwise the state can change between the check and the write.
Cancellation does not undo an external effect already sent. The stale-work recipe names
fencing/idempotency and the remaining race tests; a counter alone is not a guarantee.

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

## 12. Clearing an outbox lost newly queued records

Main OS took a queue snapshot, sent it, and on success saved an empty queue. A user record
added during the request disappeared. Two copies of the rule had independently diverged.
Source evidence: Main OS docs/ARCHITECTURE.md, "Правило очередей отправки на телефоне",
and KE-2026-08-27-OUTBOX in docs/KNOWN_ERRORS.md (recorded 2026-08-27).

**Transferable rule:** remove only confirmed IDs from current durable pending work, in an
atomic local operation. Preserve new and unacknowledged entries; retry with stable IDs
and an idempotent receiver. Share the rule, not two similar copies.

**Coverage limit:** the source's list-subtraction self-check is not proof of concurrent
I/O or crash safety. Test acknowledgement loss, concurrent enqueue and interruption around
commit separately. See the outbox recipe; it specifies the stronger target contract.

## 13. The guard was correct; the exit path bypassed it

A one-call refactor changed cancellable tray close to unconditional shutdown. The password
guard stayed correct. The incident report records **123 days** before discovery; a unit
test of the guard alone would not detect the caller ignoring its result.
Source: KE-2026-08-16-SESSION-LOCK and incident-report.html (transfer map S01/S03).

**Rule:** inventory protected effects and all entry points; test denial through actual
adapters. Keep emergency/debug semantics explicitly distinct. See entry-point-invariants
and docs/INVARIANTS.md in an installed project.

## 14. Fast inner timings, slow screen

A layout change disabled virtualization; hundreds of avatars decoded on the UI thread.
Follow-up fixes optimized SQL/binding while the displayed result still took seconds.
Collection notifications and per-folder aggregates added separate growth costs.
Source: Messenger performance guide in KNOWN_ERRORS.md (transfer map S03).

**Rule:** measure until rendered, at representative data volume with cold/warm caches.
Bound rows/images, query counts, refresh cascades and lock-held work. Particular WPF panels
or SQLite pragmas are not universal requirements. See bounded-performance.

## 15. Successfully delivered, semantically wrong

Clients measured different reaction-time intervals; stale snapshots erased progress;
removing a calendar source risked fabricating cancellations. Transport success could not
expose these errors. Source selections: transfer map K-014 through K-018.

**Rule:** name ownership, metric meaning, deletion semantics and conflict/order policy.
Persist accepted actions promptly; apply records/cursor atomically. Test offline/reordered
convergence, not only HTTP status or counts. See sync-semantics.

## 16. A padded ID range is a confident lie

A use-case catalogue listed SET-018 as enabling UC-150…155 and UC-170…173. The written
cases stopped at 154 and 172. The uniqueness check passed: every heading was unique and
every heading had a tracing-table row. The missing numbers existed only in the range.

The same catalogue described calendar/tasks as going "over /api/*, reading the read-only
replica". Both halves were true of *some* tool. Together they sent an agent looking for
Todoist in a database clone that does not contain it.

**Rule produced:** SET Enables and Preconditions are expanded and must name IDs that exist.
Do not pad ranges to look round. When more than one store exists, Flow names which one;
do not merge a safety slogan from another path into an API case. Doctor checks the IDs.
Which-store wording remains a review item (sync-semantics). See AGENTS.md section 3.

---

## Source checks and what version 0.2 actually carries

The source project enforces several of these rules with 1,237 lines of Python plus two git
hooks. Those implementations were not ported in the initial scope. Version 0.2 adds a
small stack-independent doctor, staged-secret heuristic and configurable finish runner,
with their own negative tests. It does not claim parity with source-specific checks.

The following paths and historical sizes identify reference material inside Main OS,
not files promised in this package. Re-evaluate applicability and test known defects
before reusing them; past debugging is not a universal correctness guarantee.

| Reference | Lines | What it does | Portability |
|---|---|---|---|
| `scripts/checks/secrets.py` + its test | 301 | secrets in tracked sources and in build output | high — regexes plus an extension list |
| `scripts/attribution/build.py` | 317 | per-commit model attribution from agent transcripts and commit trailers | provider-specific transcript formats; unknown attribution must stay unknown |
| `scripts/checks/finish.py` | 242 | one command: build affected projects, run tests, run checks, stop before pushing | medium — the project list is a constant |
| `scripts/checks/doc_drift.py` | 207 | current-version claims in documents against the code | low — knows the source project's files |
| `scripts/checks/periodic_cost.py` | 170 | repeating work with no `cost:` calculation | low — patterns are language-specific |
| `.githooks/pre-commit`, `pre-push` | 2 files | runs the checks; cleans build output on push, never blocking it | high |

Three things about them are worth reusing whatever the language:

1. Read the **index**, not the working tree (lesson 4).
2. Ship a test that plants the defect the check exists to catch (lesson 5).
3. Never block on housekeeping; only block on correctness (lesson 3).
