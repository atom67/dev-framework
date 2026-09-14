# Crash, shutdown and recovery

## Problem and applicability

Use when a failed operation could leave background work or persisted state inconsistent.
Adapt the presentation to desktop/service profiles; do not swallow invariant failures.

## Invariant and protocol

No new affected work or unsafe writes after the lifecycle enters failed/stopping state.
Persisted recovery data survives both abnormal termination and normal shutdown paths.

1. Give each worker/timer/subscription an owner and a registered lifecycle. Gate entry
   to operations and writes; reflection over UI fields is not lifecycle coverage.
2. On failure, transition lifecycle state once, block new work, preserve diagnostics,
   signal cancellation and wait for owned in-flight work up to a bounded deadline.
3. Workers check cancellation and commit authority; stopping a timer does not cancel
   its running callback. A modal dialog can keep dispatching queued UI events.
4. Do not invoke a normal "end session" action if it deletes the state needed for recovery.
5. Recover from committed durable checkpoints on restart. Validate them before resuming;
   replay must not repeat non-idempotent effects unknowingly.
6. If consistency cannot be preserved, terminate the affected process rather than keep
   mutating state. Service supervisors need explicit backoff/restart budgets.
7. Persist coupled transitions in one transaction. A block plus its remaining budget, or
   applied records plus cursor, cannot be independent successful writes. Test recovery after
   related timers expire too; a temporary restore guard can conceal stale durable state.

## Failure tests

- Each registered worker is stopped; add a new worker and ensure the contract still holds.
- Fault during persistence, UI event and timer callback; no later unsafe save occurs.
- Show an error dialog while events are queued; lifecycle gates still block mutation.
- Kill a child process at persistence boundaries and verify restart from old/new committed state.
- Force shutdown timeout and reentrant error reporting; no endless restart or recursive dialog.

## Observability

Lifecycle state, failed operation/correlation ID, last durable checkpoint, worker count
still draining and restart count per window. Log diagnostics before closing the logger.

## Limits

Graceful cleanup is not guaranteed on kill/power loss. Durable writes/checkpoints provide
recovery, not the shutdown handler. A service's health probe alone says nothing about
lost or stalled records; reconcile the relevant data flow.
