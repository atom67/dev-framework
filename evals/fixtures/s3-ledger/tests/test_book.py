import os
import tempfile
import unittest
from datetime import date

from ledger.book import Entry, balance, load, save

E = [Entry(date(2026, 3, 2), -4.5, "food", "coffee"), Entry(date(2026, 3, 9), -900, "housing", "rent"),
     Entry(date(2026, 4, 1), 2000, "income", "salary")]


class BookTests(unittest.TestCase):
    def test_balance_groups_by_category_within_month(self):
        self.assertEqual(balance(E, "2026-03"), {"food": -4.5, "housing": -900})

    def test_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "l.csv")
            save(E, p)
            self.assertEqual(load(p), E)
