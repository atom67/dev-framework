# Known errors — {{PROJECT_NAME}}

**What this is:** every known bug, limitation, and piece of technical debt.
**Read it before** "fixing" anything or explaining odd behaviour — the thing may already
be recorded, with a workaround and a reason.
**Update when:** any bug or limitation is found, during development, testing, or review.
See `AGENTS.md` section 3.

## Entry format

Identifier: `KE-YYYY-MM-DD-SHORT-SLUG`. Stable, so code comments can quote it — that is
how the reason for a non-obvious defence survives the next refactor.

```
### KE-2026-01-31-EXAMPLE-SLUG — one-line summary

**Where:** path/to/file.ext:123
**Introduced / detected:** commit or unknown / date and evidence
**Impact:** what the user or the data actually loses. Not "it is wrong" — what breaks.
**Cause:** the mechanism, in one or two sentences.
**Status:** not fixed / fixed in <commit or version>
**Workaround:** what to do until it is fixed, or "none".
**Verification:** regression test, observed result and coverage limitations
```

Rules:

- A fixed entry is **marked** fixed, with the commit or version. It is not deleted:
  the same mistake gets made again, and the record is what makes it recognisable.
- State the affected scope precisely. A local fix is not proof every consumer is fixed.
  Separate confirmed defects, hypotheses and accepted risks; do not invent dates.
- If a defence in the code exists because of an entry here, the code comment names the ID.

## Open

### KE-YYYY-MM-DD-... — ...

**Where:**
**Introduced / detected:**
**Impact:**
**Cause:**
**Status:** not fixed
**Workaround:**
**Verification:**

## Fixed

### KE-YYYY-MM-DD-... — ...

**Status:** fixed in ...
