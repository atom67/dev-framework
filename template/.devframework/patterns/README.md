# Reliability patterns

These are language-neutral design/test recipes, not implementations or proof a generated
project is reliable. Select by risk and link chosen invariants to project requirements.
Record the actual implementation tests and untested boundaries in the regression index.

- [Outbox and acknowledgement](outbox.md): records survive concurrent enqueue and retry.
- [Configuration recovery](configuration.md): read errors never become silent resets.
- [Crash and shutdown](crash-recovery.md): lifecycle ownership, write gates and durable recovery.
- [Stale work](stale-work.md): cancellation, generation checks and external effects.
- [Compatible evolution](evolution.md): migrations and old/new consumer contracts.
- [Entry-point invariants](entry-point-invariants.md): guards through every ordinary caller.
- [Bounded performance](bounded-performance.md): growing data, query counts and visible latency.
- [Sync semantics](sync-semantics.md): ownership, replay, cursor atomicity and deletion meaning.

Each recipe includes applicability, failure tests, observable outcomes and limits. The
historical [lessons](../LESSONS.md) explain why these issues were selected. Project-specific
data-flow owners, thresholds and recovery procedures belong in docs/ARCHITECTURE.md.
Source coverage and deliberate exclusions: [transfer map](../KNOWLEDGE_MAP.md).
