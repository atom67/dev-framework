# Architecture healthcheck

Before laying down the architecture of a feature, or before debugging one: print only the areas the task
touches — `python .devframework/navigate.py health db,tx,api` (SCOPE rows always come along) — and name
the rule ids that apply in the plan or checklist. Breaking a rule is allowed when the plan says why.
Sources: about 356 recorded defects in seven projects, 24 documented production incidents caused by AI
agents, and the established engineering canon. Areas: SCOPE DB TX API UI BULK JOB CFG DEP VER SEC LLM.

| ID | Rule | Prevents |
|---|---|---|
| SCOPE-1 | Build only what the task names; every new layer, dependency or option needs a present requirement. | over-engineering |
| SCOPE-2 | Stdlib, host feature or an installed dependency before new code; new infrastructure only when they demonstrably fail. | weeks on custom machinery |
| SCOPE-3 | Spike the riskiest platform assumption (permissions, OS, scheduler, sandbox) before designing around it. | late blocker after many rounds |
| SCOPE-4 | One source of truth per fact; everything else derives from it or links to it. | two copies drift apart |
| SCOPE-5 | Smallest diff that works; refactor commits separate from behaviour commits. | unreviewable, unrevertable change |
| SCOPE-6 | Three failed fix or review rounds: stop and re-scope instead of a fourth round. | endless loops |
| SCOPE-7 | For every fix, name the neighbouring defect it can create (lock → slow work under lock → stale queue) and check it. | the fix breeds the next bug |
| SCOPE-8 | Cost repeated work before shipping it: calls/day × payload × turns at the target scale. | silent cost and load |
| DB-1 | Parameterized queries only; never build SQL (or shell, HTML) from strings. | injection |
| DB-2 | Writes that must agree happen in one transaction, or have an explicit compensating step. | half-written state |
| DB-3 | Change the rows or fields that changed; never read-modify-rewrite a whole list or blob. | last writer wins, lost edits |
| DB-4 | Constraints (unique, foreign key, not null, check) live in the database, not only in code. | duplicates, orphans |
| DB-5 | A failed read is an error: never treat it as "empty" or "first run" and write defaults over the data. | data wiped by defaults |
| DB-6 | One writer per store, or explicit locking; a second instance is detected at startup. | concurrent corruption |
| DB-7 | Schema change = expand → migrate → contract; old and new code both work during the switch. | breaking migration |
| DB-8 | Every growing table, log or cache has a retention or purge rule. | disk full, slow queries |
| DB-9 | Index the queries you run; check the plan of any query that grows with the data. | slow at scale |
| DB-10 | Tools and agents read live or personal data through a read-only replica or role. | live database damaged |
| TX-1 | State change + side effect (send, charge, publish): record the intent in the transaction, deliver after (outbox). | sent but not saved, or the reverse |
| TX-2 | Every retried operation is idempotent: an idempotency key or dedupe by a stable id. | duplicates on retry |
| TX-3 | A queue cursor advances only after confirmed processing, not from what was read. | skipped or lost items |
| TX-4 | Re-check the condition when executing; a decision made before a wait or a lock is stale. | acting on old state |
| TX-5 | State that must survive a restart (queue, progress, flags) is persisted, never only in memory. | lost work on restart |
| TX-6 | Stop, cleanup and recovery paths release resources; they never delete or overwrite user data. | destructive shutdown |
| API-1 | Every remote call has a timeout; every job has a wall-clock limit below the scheduler's kill. | hangs, zombie jobs |
| API-2 | Retry only idempotent calls: bounded, exponential backoff with jitter; stop on auth errors, 4xx and 429. | retry storms |
| API-3 | A failing item never blocks the queue: after N failures, dead-letter it and move on. | poisoned head of queue |
| API-4 | Parse input at the boundary into a strict type and trust it inside; reject, do not coerce. | lossy or invalid data |
| API-5 | Prove an external API's or device's behaviour with a probe or its docs before depending on it; record the evidence. | wrong assumptions |
| API-6 | Configured ≠ working: check that the credential or capability actually works before promising work. | silent failure |
| API-7 | Fail loud: no silent fallback to a default model, path, config or data source. | wrong result that looks right |
| API-8 | "Stored" or "200 OK" is not "delivered": verify the full round trip to the recipient. | messages that never arrive |
| API-9 | A published contract stays backward compatible or is versioned; unseen consumers exist. | breaking clients |
| UI-1 | The UI never blocks on I/O: long work runs in the background with visible progress and cancel. | frozen app |
| UI-2 | Background work gets copies, not shared mutable UI state; results come back through one dispatcher. | races, crashes |
| UI-3 | A destructive action names its object in the confirmation and has undo or a backup. | irreversible mistakes |
| UI-4 | Measure what the user perceives (click → visible result), not inner timings. | fast code, slow app |
| UI-5 | Verify the framework's cancel, close and event semantics before relying on them. | wrong action on Esc or close |
| UI-6 | Empty, loading, error and no-permission states are designed, not left to chance. | broken screens |
| BULK-1 | Stream or page large collections; never load unbounded data into memory or into a prompt. | memory and token blowups |
| BULK-2 | Per-item work never rescans the whole set: batch lookups, use maps and indexes. | O(n²) slowdown |
| BULK-3 | Every limit is explicit and reported when hit; no silent truncation or cap. | data silently missing |
| BULK-4 | Try a data path at ten times today's volume before calling it done. | collapse at growth |
| BULK-5 | Deduplicate by stable identity, not by position or display text. | duplicates or merged items |
| JOB-1 | A periodic job starts with a cheap deterministic "is there work?" check; the expensive step runs only when there is. | idle cost burn |
| JOB-2 | Missed runs are detected and replayed in order; a watcher tells a person about failures. | silent gaps |
| JOB-3 | The scheduler's environment is not your shell: explicit paths, env, working directory and user. | works by hand, fails on schedule |
| JOB-4 | Every job exposes its last successful run to the owner. | dead job unnoticed for days |
| CFG-1 | Secrets live outside code and logs, are scanned before commit and never reach the model. | leaked credentials |
| CFG-2 | Missing required configuration fails fast at startup with a clear message. | half-working service |
| CFG-3 | Config edits are surgical, after a timestamped backup; never rewrite a config file whole. | config wiped |
| CFG-4 | Least privilege per task: scoped, short-lived credentials; none for production in a development or agent environment. | agent deletes production |
| CFG-5 | Explicit UTF-8 on every read, write and subprocess; store UTC, compute day boundaries in the user's zone. | mojibake, off-by-one days |
| DEP-1 | Deployed means running: restart the owning process, verify PID or start time, code hash and one smoke through the real entry. | old code still serving |
| DEP-2 | Test the installed artifact (permissions, layout, dependencies), not only the source tree. | works in repo, broken when shipped |
| DEP-3 | Every deploy has a rollback path that has been tried once. | no way back |
| DEP-4 | Publish checksums and versions only after the final build; ship nothing while a mandatory review is pending. | shipped unreviewed or mismatched |
| VER-1 | Every change has a runnable pass/fail check; its result, not the author's claim, is the evidence. | false "done" |
| VER-2 | Test through the real entry path (UI adapter, CLI, API, scheduler), not only the inner guard. | unit-green, wiring-red |
| VER-3 | A new check is seen failing once on a planted defect before it is trusted. | detectors that never fire |
| VER-4 | Tests are not edited to make code pass; a test change is reviewed on its own. | tampered tests |
| VER-5 | Reproduce a bug as a failing test before fixing it. | fixes that fix nothing |
| VER-6 | Errors surface where they happen, with context; none are swallowed. | late or silent failure |
| VER-7 | Documentation claims are checked against the code in the same change. | docs that lie |
| SEC-1 | Validate every path component against the root (`..`, symlinks, junctions), not only the root. | path escape |
| SEC-2 | One enforcement point: every entry (UI, API, CLI, tray, cron) passes the same guard. | guard bypassed by another door |
| SEC-3 | No single agent or token holds untrusted input, private data and an outbound channel together. | prompt-injection exfiltration |
| SEC-4 | Check every new dependency in its registry and approve it; never add a package by guess. | hallucinated or malicious package |
| SEC-5 | Irreversible operations (delete, drop, destroy, force, reset, production migration) need human approval of the resolved target; backups live outside the blast radius. | destroyed data |
| LLM-1 | Code assembles facts, ids and links; the model writes text from them. | fabricated facts |
| LLM-2 | Model output that code consumes goes through a schema; repair it or keep it raw, never drop it silently. | lost or corrupt records |
| LLM-3 | Cost = invocations × turns × tokens: cap turns and spend per run. | runaway bills |
| LLM-4 | Pin the model and provider per job; a fallback model gets no tools. | weak model with write access |
| LLM-5 | Classify meaning with the model or a reviewed list plus negative examples, not ad-hoc keyword regex. | false matches |
| LLM-6 | Tell the model what to do; a forbidden phrase quoted in the prompt gets copied. | prompt triggers what it forbids |
| LLM-7 | Items that must survive are checked after the model, not only selected before it. | silently dropped key items |
