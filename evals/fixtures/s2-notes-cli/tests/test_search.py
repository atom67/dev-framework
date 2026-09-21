import unittest

from notes.search import search

NOTES = [
    {"id": 1, "text": "Buy milk", "tags": ["home"], "created": "2026-01-01"},
    {"id": 2, "text": "Milk the deadline", "tags": ["work", "urgent"], "created": "2026-01-02"},
]


class SearchTests(unittest.TestCase):
    def test_substring_is_case_insensitive(self):
        self.assertEqual([n["id"] for n in search(NOTES, "MILK")], [1, 2])

    def test_all_requested_tags_must_match(self):
        self.assertEqual([n["id"] for n in search(NOTES, tags=["work", "urgent"])], [2])
        self.assertEqual(search(NOTES, tags=["work", "home"]), [])
