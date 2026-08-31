# Architecture — {{PROJECT_NAME}}

**What this is:** how the system is put together — components, data schema, data flows.
**Update when:** the data schema changes, tables or migrations are added, new services or
components appear, or data flows change. See `AGENTS.md` section 7.

**Current schema version: v1** — this number is the one documents are checked against.
If the code says something else, the code is right and this file is a bug.

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

Migrations are sequential and hand-written. Record every one, including the ones that
have already shipped — the history is legitimate here, and only the "current version"
statement above is checked for drift.

| Version | Change |
|---|---|
| v1 | initial schema |

## Data flows

For each flow that crosses a process, a device, or a network boundary: what triggers it,
what moves, in which direction, and how often. Frequency belongs here because it is what
the cost rule is checked against.

1. ...

## State that must survive a crash

Per `AGENTS.md` section 8, any state whose loss breaks the product is persisted. List
what is persisted and where, so the next feature can be checked against the same bar.

- ...
