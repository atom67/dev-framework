# Synchronization semantics and state ownership

## Problem and applicability

Delivery success is not convergence. Stale snapshots can erase progress, the same metric
can mean different things on two clients, and source removal is not cancellation of all
its items. Use for multi-client, offline and imported-data flows.

## Invariant and protocol

Name each field's owner and meaning. Supported delivery orderings must not silently lose
acknowledged work or invent business events.

1. Separate authoritative content, user-local presentation and replicated business state.
   A remote refresh must not reset local read markers or pending edits accidentally.
   Agent-facing cases and maps must name the store they actually read. A safety replica
   of a live database is not a second API for facts that live on a server.
2. Define metric semantics at producers: start/end events, units, timezone. Share pure
   business rules or executable contract cases; similar client copies drift.
3. Persist each accepted action at its commit boundary, not only session completion.
   Local progress must not require another device online. Reconcile stale snapshots with
   pending work using version/operation identity.
4. If replay is chosen, specify stable IDs, deterministic order/tie-breaks, late arrival,
   deduplication, clock skew and conflict policy. Receipt order differs from event time.
   Event sourcing is optional, not a rule for every CRUD application.
5. Apply incoming records and advance the durable cursor atomically. Never advance past
   unapplied records. Define reset/replay and retention/compaction boundaries.
6. Distinguish explicit tombstones, filtered/partial/failed snapshots and source removal.
   Absence is not deletion unless completeness is guaranteed. Calendar unsubscription
   must not invent cancellation events for every meeting.
7. Keep complete source data unless retention/redaction is intentional. UI excerpts must
   not irreversibly truncate records at storage ingress.
8. Selection, right-click and rebinding are not automatically user intent. Separate explicit
   open/mark-read/reorder paths. Time-bounded state records timezone/day/generation so
   yesterday's restored budget cannot silently authorize today's actions.

## Failure tests

- Offline edit followed by stale snapshot: progress and pending work survive.
- Permute/repeat/late-deliver events with clock skew; converge under the defined policy.
- Crash between batch apply and cursor advance; no skipped or double-applied effects.
- Both clients measure the same interval and pass shared contract fixtures.
- Item deletion, source removal, fetch failure and partial page have distinct outcomes.
- Refresh preserves local read/edit state; long records survive storage round-trip.
- Keyboard/context menus/programmatic selection do not trigger unintended primary actions.

## Observability

Persisted/sent/acknowledged/applied counts, pending age, durable cursor, replay lag,
reconciliation mismatches, deletion reasons and conflicts. IDs belong in redacted traces,
not unbounded metric labels.

## Limits

Equal counts do not prove equal content; compare IDs/digests at defined checkpoints.
Replay order is a product decision, not proof clocks agree. Durable storage/transaction
tests and recipient idempotency remain necessary; see [outbox](outbox.md).
