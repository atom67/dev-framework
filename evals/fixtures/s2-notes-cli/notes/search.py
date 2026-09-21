"""Search: case-insensitive substring in text, optional tag filter (all tags must match)."""


def search(notes, query="", tags=()):
    q = query.lower()
    want = set(tags)
    return [n for n in notes if q in n["text"].lower() and want <= set(n["tags"])]
