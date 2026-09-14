# Compatible contract and schema evolution

## Problem and applicability

Use when clients, services, stored data or background jobs may run different versions.
Do not assume all consumers upgrade atomically or that backend-first always works.

## Invariant and protocol

Every supported version combination has a documented behaviour and no silent data loss.

1. Name the contract/schema version authority and inventory consumers, including offline
   clients and pending messages. Define supported combinations and rejection behaviour.
2. Expand compatibly: add fields/endpoints/storage without prematurely removing old ones.
   Validate required fields; serializer defaults must not silently mask missing data.
3. Migrate/backfill in bounded resumable units with stable IDs and checkpoints. Monitor
   progress and reconcile counts. Test old data and realistically sized data.
4. Move consumers, verify adoption and outcomes, then contract/remove legacy support only
   under an agreed policy. Unknown versions fail explicitly where interpreting them is unsafe.
5. Test rollback of code against the new schema; if destructive migration prevents it,
   name the backup/restore or roll-forward procedure and its data-loss window before release.
6. Test transaction/constraint behaviour through the actual connection factory. Declaring
   a foreign key does not prove every connection enforces it. Partial migration must not
   advance the schema version; use transactional or explicitly recoverable migration.

## Failure tests

- Old/new producers with old/new consumers, missing fields, nulls and unsupported versions.
- Crash/retry during migration/backfill; resume without duplicate effects or skipped records.
- Old queued messages replay after deploy; retain identity and meaning.
- Restore a backup and verify changed user behaviour, not just process health.
- Production-like volume verifies duration, locks and resource/cost ceilings.

## Observability

Consumer version distribution, parse/rejection counts, migration progress, failed batch
age, reconciliation mismatch and time since last successful application.

## Limits

Use the stack's migration tools; handwritten SQL is not inherently safer. Tests establish
the named compatibility matrix only, not compatibility with arbitrary future versions.
