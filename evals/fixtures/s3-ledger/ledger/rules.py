"""Auto-categorisation from rules.json: [{"match": "coffee", "category": "food", "priority": 1}, ...]"""
import json


def load_rules(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def categorize(note, rules):
    """Return the category of the first rule whose match is a substring of note, else 'uncategorized'."""
    text = note.lower()
    for r in rules:  # TODO priority? (see rules.json — values are there but nobody uses them yet)
        if r["match"].lower() in text:
            return r["category"]
    return "uncategorized"
