# Configuration loading and recovery

## Problem and applicability

Use for persisted settings/profiles whose loss changes protection or behaviour. An I/O
error, malformed JSON and an intentionally new profile are different states.

## Invariant and protocol

Failed loading never enables implicit defaults or overwrites the last known bytes.

1. Distinguish confirmed first run from an established profile using durable identity or
   install/profile metadata, not file absence alone. Do not misclassify a missing mount.
2. Retry only plausibly transient I/O errors with a bounded budget; permission errors,
   unsupported versions and validation failures require an appropriate explicit outcome.
3. Parse AND validate shape, required fields and schema. A valid JSON `null` is not a profile.
4. Keep automatic saves disabled until valid configuration is loaded or the operator
   explicitly authorizes reset/recovery. This includes shutdown and background saves.
5. Preserve originals/backups and record recovery state so closing/restarting cannot
   bypass recovery. Do not move the only file and then interpret its absence as first run.
6. Save via same-filesystem atomic replacement with a validated backup and the platform's
   durability policy. Coordinate concurrent writers; atomic rename alone prevents neither
   stale overwrites nor power-loss issues on every filesystem.
7. Required endpoint/environment configuration fails explicitly when absent. A plausible
   default address can disguise misconfiguration as a network outage. Test precedence and
   absence without access to the operator's real profile.

## Failure tests

- Temporary sharing failure then success preserves the profile unchanged.
- Persistent denial never causes reset or a save-on-close.
- Malformed input, JSON null, wrong types and future schema all enter explicit recovery.
- Missing established profile differs from confirmed first run.
- Close/restart in recovery remains in recovery; reset requires explicit authorization.
- Interrupt saving before/after replacement; recover a valid old or new profile.

## Observability

Load result category, bounded retry count, last successful load/save, recovery-required
state and backup identity. Never log secret fields or entire settings contents.

## Limits

Retries do not repair corruption. DPAPI/key-store failures can make intact encrypted
data unreadable; preserve it and diagnose identity/key access instead of overwriting it.
