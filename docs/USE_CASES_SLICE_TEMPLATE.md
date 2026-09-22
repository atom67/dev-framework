# Edition / public slice — copy to `docs/USE_CASES_<SLICE>.md`

Use this when a build, edition or public cut is a **subset** of the live catalogue.
Copy this file, delete this header, replace `<SLICE>`. See `AGENTS.md` section 3.

The live catalogue [`USE_CASES.md`](USE_CASES.md) keeps its `UC-###` numbers.
This file uses a **new** permanent prefix (`PUC-###`, or another that this product
owns). Do not renumber living cases to match the slice.

Each slice row **maps to one** `UC-###`. It does not copy Flow, architecture or
the Test evidence — those stay on the source case. `Test` here repeats the source
status so a reviewer of the slice does not have to open the full catalogue.

Do not invent slice rows for value that is out of this edition. If it is not in
the agreed cut, it is absent, not numbered as "later".

---

# Use cases — <edition name>

**What this is:** the value this edition actually ships.
**Who reads it:** the operator (what a user of this cut gets) and the engineer
(what not to mix in from the full product).
**Maps to:** [`USE_CASES.md`](USE_CASES.md). One `PUC-###` → one `UC-###`.

## Composition

- New IDs, never reused; never recycle a `UC-###` as a slice id.
- Trigger and Outcome are restated in the language of this edition.
- `Maps to` is mandatory. `Test` matches the source case (`covered` / `gap` / `NFV`).
- No Flow copy, no second architecture, no second SET block.

## Rows

```md
#### PUC-0xx — <short name in this edition's language>

- **Maps to:** UC-0xx
- **Trigger:** Interactive | Automatic
- **Outcome:** <the benefit this edition's user now has>.
- **Test:** covered | gap | NFV (as on UC-0xx)
```

## Traceability

| Slice | Maps to | Trigger | Test |
|---|---|---|---|
| PUC-0xx | UC-0xx | Interactive or Automatic | covered / gap / NFV |
