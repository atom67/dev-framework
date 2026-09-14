# Invariants across entry points

## Problem and applicability

A correct guard does not protect a path which bypasses it. Main OS's tray exit changed
from a cancellable close to unconditional shutdown; the password guard never changed.
Use for authorization, protected shutdown, deletion, billing and other behaviour whose
violation defeats the product, including non-UI entry points.

## Invariant and protocol

Every ordinary entry point enforces the domain rule before the protected effect.

1. Register the invariant, owner, guarded effect and applicable states in
   [the invariant register](../../docs/INVARIANTS.md). Enumerate buttons, tray/menu actions,
   hotkeys, API handlers, timers, startup/recovery and shared consumers that can reach it.
2. Enforce at the domain/effect boundary, not just a dialog or disabled button. A callback
   being invoked is not proof its cancellation result is respected by the caller.
3. Name intentionally different semantics explicitly. Do not merge normal and emergency
   exit just to remove duplicate lines. Debug bypasses require explicit authorization,
   a visible name and a distribution policy excluding them from forbidden contexts.
4. On denial/cancel verify no mutation/effect, and restore temporary flags so the next
   ordinary action behaves correctly. Authorization must remain valid until commit;
   for concurrent changes see [stale work](stale-work.md).
5. On shared guard/lifecycle changes inspect callers across consumers. Add a newly found
   path to the register before implementing its fix.

## Failure tests

- Parameterize actual entry adapters: permitted, denied, cancelled, repeated, restarted.
- Keep the guard correct but route one adapter around it: its integration test must fail.
- After denial, repeat the normal action; no leaked bypass/minimize flag.
- Verify emergency/debug paths separately, including absence in restricted artifacts.
- UI/process tests use disposable windows/child processes, never the operator's app.

## Observability

Denied/allowed effects by bounded entry-point/reason categories; operation ID in redacted
diagnostics, not metric labels. An unauthorized effect is failure even on a clean exit.

## Limits

A registry is not automatic discovery of every caller. Guard unit tests do not prove
adapter behaviour. A local UI lock is not an OS security boundary; explicitly define
whether hostile local administrators are in scope.
