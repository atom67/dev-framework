# ledger

Envelope budgeting from the terminal. Each month every category ("envelope") has a budget; spending
comes out of it. Entries are kept in `ledger.csv` (`date,amount,category,note`), negative = spend.

```
python -m ledger.cli add -- -4.50 "coffee at corner shop"        # category auto-detected from rules.json
python -m ledger.cli add -c housing -- -900 "rent march"
python -m ledger.cli balance 2026-03
python -m ledger.cli rollover 2026-03
```

`rules.json` maps note keywords to categories (see file). Unknown notes land in `uncategorized`.

Tests: `python -m unittest discover -s tests`

## notes from the last two syncs (unsorted)
- Dana: envelopes should behave like real envelopes.
- Sam: I want to see savings accumulate across months.
- --strict flag was added for the CI import script, ask Sam what it was supposed to do.
- priorities in rules.json were Dana's idea from the "uber eats" incident (it went to transport).
