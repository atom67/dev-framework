# Outbox and acknowledgement

## Problem and applicability

Use when local records must reach another process/service without disappearing during
network failure, concurrent creation or restart. Source: Main OS KE-2026-08-27-OUTBOX.

## Invariant and protocol

Every accepted local record is durable and remains pending until its stable ID is
durably acknowledged. Duplicate transport must not duplicate the business effect.

1. In one local transaction, persist the business change and its outbox record with a
   stable ID. If there is no shared transaction, document the reconciliation strategy.
2. Claim a bounded batch using explicit worker ownership/lease semantics. Do not hold a
   database transaction open during an HTTP request.
3. The receiver validates and deduplicates IDs in the same transaction as its effect;
   acknowledge only committed IDs. Partial success names exactly those IDs.
4. Atomically remove/mark acknowledged IDs from the CURRENT outbox. Never replace the
   queue with an empty list or subtract from an obsolete snapshot outside a transaction.
5. Retry unknown outcomes with the same IDs and bounded backoff/jitter. Preserve rejected
   records with a diagnosable reason and a reviewed dead-letter/recovery path.

## Failure tests

- Enqueue B while A is in flight; acknowledge A: B remains durable and pending.
- A and B sent, only A acknowledged: B remains. Duplicate acknowledgement is harmless.
- Receiver commits A but response is lost: retry yields one effect, not two.
- Kill sender before/after local acknowledgement commit; restart loses no accepted record.
- Two workers claim concurrently; test actual store/lease behaviour, not just list subtraction.
- Fill the queue to its limit: the specified backpressure is visible, no silent eviction.

## Observability

Pending count, oldest pending age, retry/dead-letter counts, last confirmed application
time and reconciliation of accepted/acknowledged/applied records. Use record IDs in
redacted diagnostics, not as unbounded metric labels. Assign alert window/owner in architecture.

## Limits

At-least-once transport is not exactly-once delivery. External non-transactional effects
need recipient idempotency or reconciliation. A generation counter and a pure-function
queue test do not prove durable concurrency correctness.
