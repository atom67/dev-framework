# Requirements — {{PROJECT_NAME}}

**What this is:** every requirement the product has, numbered, with its current status.
**Who reads it:** anyone planning work, before touching the backlog.
**Update when:** an incoming request asks for a new feature, a behaviour change, or a
correction to an existing function. See `AGENTS.md` section 7.

## Identifiers

- `FR-###` — functional requirement: something the product does.
- `NFR-###` — non-functional requirement: how well, how fast, how safely it does it.

Numbers are permanent and unique. A number never means two different things. If a
requirement is superseded, strike it through and add a new one pointing back at it.
Reusing a number silently rewrites history for everyone who quoted it.

## Product principles

The handful of statements that settle arguments. Not features — the reasons features get
accepted or rejected.

1. ...

## Functional requirements

| ID | Requirement | Status |
|---|---|---|
| FR-001 | Example: an in-progress session survives a crash or reboot and resumes instead of being lost. | planned |

## Non-functional requirements

| ID | Requirement | Status |
|---|---|---|
| NFR-001 | Example: every repeating operation carries a written cost calculation at the declared scale target. See `AGENTS.md` section 5. | planned |

## Superseded

Requirements that turned out wrong. Keep them, struck through, with a note saying what
replaced them and why. A deleted requirement comes back as a fresh idea within a year.

- ~~FR-000~~ — replaced by FR-00N: ...
