# Known errors — {{PROJECT_NAME}}

**What this is:** every known bug, limitation, and piece of technical debt.
**Read it before** "fixing" anything or explaining odd behaviour — the thing may already
be recorded, with a workaround and a reason.
**Update when:** any bug or limitation is found, during development, testing, or review.
See `AGENTS.md` section 7.

## Entry format

Identifier: `KE-YYYY-MM-DD-SHORT-SLUG`. Stable, so code comments can quote it — that is
how the reason for a non-obvious defence survives the next refactor.

```
### KE-2026-01-31-EXAMPLE-SLUG — one-line summary

**Where:** path/to/file.ext:123
**Impact:** what the user or the data actually loses. Not "it is wrong" — what breaks.
**Cause:** the mechanism, in one or two sentences.
**Status:** not fixed / fixed in <commit or version>
**Workaround:** what to do until it is fixed, or "none".
```

Rules:

- A fixed entry is **marked** fixed, with the commit or version. It is not deleted:
  the same mistake gets made again, and the record is what makes it recognisable.
- A claim in this file must be true of the whole codebase. A universal statement that
  holds in only one place is worse than no entry — it stops people looking.
- If a defence in the code exists because of an entry here, the code comment names the ID.

## Open

### KE-YYYY-MM-DD-... — ...

**Where:**
**Impact:**
**Cause:**
**Status:** not fixed
**Workaround:**

## Fixed

### KE-YYYY-MM-DD-... — ...

**Status:** fixed in ...
