import unittest

from ledger.rules import categorize

RULES = [{"match": "coffee", "category": "food", "priority": 1},
         {"match": "starbucks", "category": "treats", "priority": 5}]


class RulesTests(unittest.TestCase):
    def test_substring_match_case_insensitive(self):
        self.assertEqual(categorize("Morning COFFEE", RULES), "food")

    def test_no_match_is_uncategorized(self):
        self.assertEqual(categorize("haircut", RULES), "uncategorized")

    # def test_two_matches_...(self): "starbucks coffee" -> ? first rule wins today, but priority says treats. TBD
