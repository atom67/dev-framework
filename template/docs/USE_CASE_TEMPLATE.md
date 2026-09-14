# Use-case copy blocks

Copy a block into [`USE_CASES.md`](USE_CASES.md). Delete this header in the copy.
Rules of composition live there (*How to read*, *Identifiers*); this file is only
the shape. See `AGENTS.md` section 3.

Do not invent IDs. A number is permanent. Never reuse `UC-###` or `SET-###`.

---

## SET row

Add to *Setup & settings*. `Enables` may only name written `#### UC-` headings.
Do not pad a range (`UC-150…155` when 155 was never written). `UC-150+` means
UC-150 exists, not an open list.

```md
| SET-0xx | <setting name> | <where configured> | required / optional | UC-0xx |
```

---

## Module

One value area. Interactive and automatic cases sit together when they serve the
same benefit. If the module grows past a handful of cases, it is probably two.
If several cases share a meaning that is not itself a path (a glossary, a status
word), put that meaning above the cases — do not turn it into a fake UC.

```md
### Module: <value area name>

**Value this module delivers:** one sentence — the benefit, not the mechanism.
**Architecture components involved:** link the relevant rows of `docs/ARCHITECTURE.md`.
```

---

## Case

One path to one benefit. Outcome is mandatory. `Test` is exactly one of
`covered` (link) / `gap` / `NFV` (reason). Preconditions name `SET-###` rows that
exist. Flow names the live store or API when more than one exists; do not paste a
safety slogan from another path onto this one.

```md
#### UC-0xx — <short case name>

- **Trigger:** Interactive | Automatic — <control, timer, service, or inbound event>.
- **Actor:** the user, or the named automatic component.
- **Preconditions:** SET-0xx; <prior state if any>.
- **Flow:** <steps a test can reproduce, including which store is read or written>.
- **Outcome (value / function achieved):** <the concrete benefit now true>.
- **Test:** covered (link) | gap | NFV (reason).
```

---

## NFV register row

Only if `Test` is `NFV`. This is a constraint to keep by hand, not a gap to close.

```md
| UC-0xx | <why a standard functional test cannot prove it> | <how it is actually checked> | <what must not regress> |
```

---

## Traceability row

One row per heading. A heading without a row, or a row without a heading, is a
catalogue lie. `gap` also goes in `docs/BACKLOG.md`.

```md
| UC-0xx | Interactive or Automatic | FR-0xx | <architecture component> | covered / gap / NFV |
```
