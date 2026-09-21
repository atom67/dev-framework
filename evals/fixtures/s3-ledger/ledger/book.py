"""Entries live in a CSV: date,amount,category,note. Amount negative = spend, positive = income."""
import csv
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Entry:
    day: date
    amount: float
    category: str
    note: str = ""


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [Entry(date.fromisoformat(r["date"]), float(r["amount"]), r["category"], r.get("note", ""))
                for r in csv.DictReader(f)]


def save(entries, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "amount", "category", "note"])
        for e in entries:
            w.writerow([e.day.isoformat(), f"{e.amount:.2f}", e.category, e.note])


def balance(entries, month):
    """Sum of amounts whose date falls in month 'YYYY-MM', grouped by category."""
    out = {}
    for e in entries:
        if e.day.isoformat()[:7] == month:
            out[e.category] = out.get(e.category, 0.0) + e.amount
    return out
