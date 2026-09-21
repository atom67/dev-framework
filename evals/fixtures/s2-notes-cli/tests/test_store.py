import os
import tempfile
import unittest

from notes import store


class StoreTests(unittest.TestCase):
    def test_add_assigns_incrementing_ids_and_dedupes_tags(self):
        notes = store.add([], "first", ["b", "a", "a"])
        notes = store.add(notes, "second")
        self.assertEqual([n["id"] for n in notes], [1, 2])
        self.assertEqual(notes[0]["tags"], ["a", "b"])

    def test_delete_unknown_id_raises(self):
        with self.assertRaises(KeyError):
            store.delete([{"id": 1, "text": "x", "tags": [], "created": "2026-01-01"}], 2)

    def test_id_is_max_plus_one_so_deleting_the_last_note_frees_its_id(self):
        notes = store.add(store.add(store.add([], "a"), "b"), "c")
        self.assertEqual(store.add(store.delete(notes, 2), "d")[-1]["id"], 4)  # middle id not reused
        self.assertEqual(store.add(store.delete(notes, 3), "d")[-1]["id"], 3)  # last id is reused

    def test_save_then_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "n.json")
            notes = store.add([], "hello", ["x"])
            store.save(notes, path)
            self.assertEqual(store.load(path), notes)
