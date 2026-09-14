# Stale queued or in-flight work

## Problem and applicability

Use when work is decided under one session/configuration and executes after that state
changes. A late completion must not recreate a cancelled block, update the wrong user
or overwrite newer state.

## Invariant and protocol

Only work authorized by the current generation/ownership boundary can commit its result.

1. Capture a generation and stable operation ID when queuing work.
2. Increment/invalidate the generation under the same state ownership boundary when a
   session ends or its configuration becomes incompatible. Cancel outstanding tasks.
3. Perform slow work outside the lock, if safe. Before a local commit, check generation
   AND apply the result atomically under that boundary or a compare-and-swap transaction.
4. Check-before-execute alone has a race: invalidation can occur between check and effect.
   For remote effects, use server-validated fencing/version tokens or serialize ownership
   appropriately; idempotency handles duplicates but does not reject a stale first attempt.
5. If an irreversible effect already happened, cancellation cannot undo it. Reconcile or
   compensate according to a defined product contract; do not claim it never occurred.

## Failure tests

- Invalidate after enqueue, before execution: no stale commit.
- Invalidate while network work is in flight: completion cannot overwrite current state.
- Pause precisely between validation and commit; invalidation cannot slip through.
- Retry a duplicated operation; verify recipient idempotency separately from stale fencing.
- Restart with pending work; a reused in-memory generation must not authorize old records.

## Observability

Discarded-stale count, cancellation delay, pending age, rejected fencing tokens and
compensation outcomes. Include generation/operation IDs in bounded diagnostic traces.

## Limits

Generation counters need an explicit lifetime and reset policy. In-memory equality is
not a cross-process fencing scheme; distributed ownership requires durable coordination.
