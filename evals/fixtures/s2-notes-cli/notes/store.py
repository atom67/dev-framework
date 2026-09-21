"""JSON-file storage for notes. One file, whole list rewritten on every change."""
import json
import os
from datetime import date

DEFAULT_PATH = os.environ.get("NOTES_FILE", os.path.expanduser("~/.notes.json"))


def load(path=DEFAULT_PATH):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(notes, path=DEFAULT_PATH):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def add(notes, text, tags=()):
    """Append a note; id = max existing id + 1 (1-based)."""
    next_id = max((n["id"] for n in notes), default=0) + 1
    note = {"id": next_id, "text": text, "tags": sorted(set(tags)), "created": date.today().isoformat()}
    return notes + [note]


def delete(notes, note_id):
    """Return notes without the given id. Unknown id -> KeyError."""
    if not any(n["id"] == note_id for n in notes):
        raise KeyError(note_id)
    return [n for n in notes if n["id"] != note_id]
