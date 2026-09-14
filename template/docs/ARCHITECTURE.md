# Architecture — {{PROJECT_NAME}}

**What this is:** how the system is put together — components, data schema, data flows.
**Update when:** the data schema changes, tables or migrations are added, new services or
components appear, or data flows change. See `AGENTS.md` section 3.

**Sibling of `USE_CASES.md`.** This file says how the system is built; `USE_CASES.md` says
what value it delivers and how each path is exercised. Keep the two in step and do not
copy one into the other: when a component here gains a user-visible or automatic value
path, add the case there; when a case there names a component, it links back here.

**Schema authority:** TODO(project): name the code/migration source, or explicitly N/A.
Do not invent a current version or copy it into multiple documents. Where a current-version
claim is useful, name its source and add a stack-specific drift check. This package does
not parse arbitrary migration languages.

## Components

| Component | Responsibility | Depends on |
|---|---|---|
| ... | ... | ... |

## Data schema

State the version above, then the tables. For each table: what it is for, its columns,
and its indexes.

### `example_table` — what it holds

| Column | Type | Notes |
|---|---|---|
| `id` | integer | primary key |
| `created_at` | text | ISO-8601 UTC, e.g. `2026-01-31T14:05:00Z` |

### Migration history

Use the stack's migration mechanism. Record ordering, compatibility, backup and recovery
policy; generated migrations need review, not a blanket ban. History is legitimate and
must not be mistaken for a claim about the current schema version.

| Version | Change |
|---|---|
| Example only | describe a real migration when one exists |

## Data flows

For each important flow record the items below. Frequency informs cost, while delivery
and durability determine whether the flow is correct. Do not call an HTTP 200 a verified
business outcome when the record has not yet been applied.

- Owner and source of truth; trigger, direction, contract/version and frequency.
- Record/correlation ID; validation; commit and acknowledgement boundaries.
- Retry budget, deduplication, ordering, timeouts, cancellation and recovery after crash.
- Queue/storage limits and overload behaviour; no silent record deletion.
- Observable counts at persisted, sent, acknowledged and applied stages. Account for
  intentional rejection and in-flight work when reconciling; do not expect instant equality.
- Queue size, oldest pending age, last successful application, retries and failures.
- Alert threshold, time window, recovery action and responsible owner. Redact payloads
  and credentials; avoid unbounded user/record IDs as metric labels.

Apply the [reliability recipes](../.devframework/patterns/README.md) where relevant.

1. ...

## State that must survive a crash

Per `AGENTS.md` section 7, any state whose loss breaks the product is persisted. List
what is persisted and where, so the next feature can be checked against the same bar.

- ...

## Architectural decisions

For each durable choice: date, context, chosen option, rejected alternatives, consequences,
known ceiling and revisit trigger. Link the relevant requirement/incident/checklist instead
of repeating its full text. Historical decisions do not override the current contract.
