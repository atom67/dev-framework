# Product invariant register

An invariant is a product property that must remain true across ordinary entry points,
failures and supported restarts. Read the [recipe](../.devframework/patterns/entry-point-invariants.md).
Populate applicable rows during design; examples are not implemented coverage.

| ID | Requirement / invariant | Owner and effect boundary | Entry points / consumers | Denial, crash and bypass test | Evidence / limits |
|---|---|---|---|---|---|
| EXAMPLE-INV | A protected action needs authorization | name domain service | list UI, API, timer, recovery paths | keep guard correct, bypass one adapter; test must fail | example only, not run |

Use stable INV-NNN IDs for real rows. Link tests instead of copying source. For exceptions
record scope, product approval and a distinguishing path name. New adapters/shared rules
trigger a review. Discovery of entry points is stack-specific, not provided by this package.
