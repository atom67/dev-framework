"""Month rollover: carry balances into the next month as synthetic entries dated the 1st."""
from datetime import date

from .book import Entry, balance


def next_month(month):
    y, m = map(int, month.split("-"))
    return f"{y + 1}-01" if m == 12 else f"{y}-{m + 1:02d}"


def rollover(entries, month):
    """Create carry-over entries for `month` -> next month. Returns the new entries only."""
    nm = next_month(month)
    first = date.fromisoformat(nm + "-01")
    carried = []
    for cat, amt in balance(entries, month).items():
        if amt < 0:
            carried.append(Entry(first, amt, cat, f"carry-over from {month}"))
        # positive balances: ??? — Dana said "envelopes reset" but Sam wanted savings to roll. left as is for now.
    return carried
