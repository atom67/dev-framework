import unittest
from datetime import date

from ledger.book import Entry
from ledger.rollover import next_month, rollover


class RolloverTests(unittest.TestCase):
    def test_next_month_wraps_year(self):
        self.assertEqual(next_month("2026-12"), "2027-01")

    def test_rollover_carries_negative(self):
        e = [Entry(date(2026, 3, 5), -50, "food", ""), Entry(date(2026, 3, 6), 30, "food", "")]
        out = rollover(e, "2026-03")
        self.assertEqual(out, [Entry(date(2026, 4, 1), -20, "food", "carry-over from 2026-03")])
