# Transfer map — Main OS to new projects

Reviewed: 2026-08-31. This is the coverage ledger, not another rulebook. Canonical rules
and recipes are linked and installed locally; Main OS is not needed to use them.
Transferred means a design/failure-test contract, not consumer implementation or proof
the source implementation was universally correct.

## Source boundary and fingerprints

Source checkout HEAD: `796d7f099e6eb6d479ac2c3982be884c45f002a3`. Hashes identify working
files, not a claim they equal HEAD. Paths below are source-relative references, not broken
links to missing generated-project files. Historical counts/dates are provenance.

| Source ID | File | Reviewed selections | SHA256 of source file |
|---|---|---|---|
| S01 | temp/incident-report.html | Polling and tray-exit incidents, shared causes | d504bec8bd7fa9c719ad88aa0366414eca86a695bdf32ce058daed86e9ad39dd |
| S02 | temp/process-overhaul.html | Cost/secret/doc gates, invariant register, negative controls, finish, data-flow counters | 972f826f1b060ca9fbd536c2dac5ea2a95b169671e6108e38a5b8589d2d99a5a |
| S03 | docs/KNOWN_ERRORS.md | Named KE entries below; UI implementation and Messenger performance guides | 5f0f069b9efd6567e2ab1c4a24065add9cd09082c05ca0623ad6d3be673d4f98 |
| S04 | docs/JAPANESE_SYNC_REFACTOR.md | Problem, target architecture, order/conflicts and acceptance scenarios | 47e72442cf91013091acf1828ac9ee214534d3b9e545c13ee2f3b9fdb10b4104 |
| S05 | AGENTS.md | Supplied planning, documentation, authority, cost, secret, crash and modularity conventions | 5901280c92be144dde0ce6f8a1f21d5544cf8f8c315f9a1a42d8c593fe52a42b |

## Transferred failure classes

Checks are consumer acceptance criteria unless explicitly named package tests. They guide
implementation, not runtime coverage claims from Markdown.

| ID | Source and incident / lesson | Rule or recipe | Required regression / observation |
|---|---|---|---|
| K-001 | S01, S02, S05: five-second poll | [Cost protocol](../AGENTS.md) | Arithmetic at scale, retries/peaks/connections; compare traffic |
| K-002 | S01, S03 KE-2026-08-16-SESSION-LOCK | [Entry points](patterns/entry-point-invariants.md) | Keep guard correct, bypass an adapter; denied effect must fail the test |
| K-003 | S03 KE-2026-08-31-SETTINGS-RESET-WITHOUT-CONSENT | [Configuration](patterns/configuration.md) | Transient read/null/missing profile; restart never implies reset |
| K-004 | S03 KE-2026-08-31-EMERGENCY-MODE | [Crash lifecycle](patterns/crash-recovery.md) | Worker gates/modal callbacks; durable recovery survives |
| K-005 | S03 KE-2026-08-31-STALE-COOLDOWN | [Stale work](patterns/stale-work.md) | Invalidate around dispatch; generation check and commit atomically |
| K-006 | S03 KE-2026-08-31-BLOCK-RUNTIME-NOT-ATOMIC | [Crash lifecycle](patterns/crash-recovery.md) | Coupled writes; recovery after related timer expiry |
| K-007 | S03 KE-2026-08-31-MONITORED-EXE-RACE, SCAN-CLOSEALL-UNDER-LOCK | [Performance](patterns/bounded-performance.md) | Owned input snapshot; slow work outside lock; concurrent edits |
| K-008 | S03 KE-2026-08-27-OUTBOX | [Outbox](patterns/outbox.md) | Concurrent enqueue, partial/lost acknowledgement, restart/idempotency |
| K-009 | S03 KE-2026-08-29-DB-TX, KE-2026-08-29-FK | [Evolution](patterns/evolution.md) | Interrupted migration; constraints through fresh connections |
| K-010 | S03 KE-2026-08-29-WORKOUT-SETSAT | [Evolution](patterns/evolution.md) | Real consumer serializers round-trip required timestamps |
| K-011 | S03 KE-2026-08-27-MCP-CONFIG | [Configuration](patterns/configuration.md) | Missing endpoint fails explicitly, no wrong fallback |
| K-012 | S03 Messenger layout/image/collection guides | [Performance](patterns/bounded-performance.md) | Growing rows/images; realized elements, notifications, bounded caches |
| K-013 | S03 Messenger SQL/measurement guides | [Performance](patterns/bounded-performance.md) | Query counts/plans, cold/warm click-to-render percentiles |
| K-014 | S03 UI implementation guide | [Sync semantics](patterns/sync-semantics.md) | Local read state preserved; rebinding is not user intent |
| K-015 | S03 KE-2026-08-10-CAL-DEL, CAL-TOMB | [Sync semantics](patterns/sync-semantics.md) | Source removal/item deletion/partial snapshot/fetch failure differ |
| K-016 | S04; S03 KE-2026-07-11-JP-A through E | [Sync semantics](patterns/sync-semantics.md) | Shared metric meaning, per-action persistence, offline convergence |
| K-017 | S04 order/conflicts; S03 KE-2026-08-30-APP-LIMIT-STALE-DAY | [Sync semantics](patterns/sync-semantics.md) | Timezone/day boundaries, replay and atomic apply/cursor |
| K-018 | S03 KE-2026-08-15-MSG-TRUNC | [Sync semantics](patterns/sync-semantics.md) | Long record round-trip; UI excerpt never truncates storage |
| K-019 | S02; S03 KE-2026-08-30-SECRETS-WORKING-TREE | [Verification](VERIFICATION.md) | Package tests: index/worktree mismatch, changed source, literal formats |
| K-020 | S02, S05: planted defects/finish | [Verification](VERIFICATION.md) | Package tests: zero/skipped/missing/stale evidence and command failure |
| K-021 | S02, S05: doc drift/backlog/handoff | [Protocol](../AGENTS.md) | Package link/ID checks; stack-specific drift checks; live handoff pilot |
<!-- kind: product -->
| K-022 | S03 KE-2026-08-26-CLEAN-OBJ; S05 artifacts | [Release](../docs/RELEASE.md) | No arbitrary intermediate pruning; final installable artifact, bounded retention |
<!-- /kind -->
| K-023 | S05: desktop vs service policy | [Profiles](profiles/generic.md) | Explicit workflow/outputs/authority; build is not deployment |
| K-024 | S02, S05: catalogue ID ranges / dual-store slogan | [Protocol](../AGENTS.md), [Sync](patterns/sync-semantics.md) | Package doctor: SET Enables/Preconditions vs headings; Flow store naming is review, not this check |

## Deliberate exclusions and unreviewed material

- Exact WPF panels/aliases, SQLite pragma constants, Android commands, personal paths and
  account identifiers are not universal defaults. Transfer the invariant and require an
  applicable stack profile with its own measured/verified implementation.
- Model-attribution collectors, Main OS feature catalog and language-specific gate source
  are not ported. Transcript adapters cannot reliably infer unknown authorship.
- Private logs, credentials, user records and provider-private memory are not copied.
- Other documents, unnamed known-error entries and the full historical Git corpus have
  NOT been exhaustively audited. Do not describe this as "all Main OS proven covered".
  Discoveries first receive a source selection/K-NNN row, then a recipe and negative test.
- The source refactor plan has historical phase/status claims. Transfer its contract, not
  a claim that a server deploy/live smoke actually passed.

Before a new project: select applicable K rows, name owners in architecture/invariants,
link real tests/telemetry, and record deferred/rejected rows with reasons. Package tests
verify map structure/local destinations only; maintainers review semantic coverage.
