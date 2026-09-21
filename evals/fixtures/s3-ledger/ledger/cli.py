"""CLI: ledger add|balance|rollover"""
import argparse
import sys
from datetime import date

from . import rules as rules_mod
from .book import Entry, balance, load, save
from .rollover import rollover


def main(argv=None):
    p = argparse.ArgumentParser(prog="ledger")
    p.add_argument("--file", default="ledger.csv")
    p.add_argument("--rules", default="rules.json")
    p.add_argument("--strict", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("amount", type=float); a.add_argument("note"); a.add_argument("-c", "--category")
    b = sub.add_parser("balance"); b.add_argument("month")
    r = sub.add_parser("rollover"); r.add_argument("month")
    args = p.parse_args(argv)

    entries = load(args.file) if _exists(args.file) else []
    if args.cmd == "add":
        rules = rules_mod.load_rules(args.rules) if _exists(args.rules) else []
        cat = args.category or rules_mod.categorize(args.note, rules)
        if args.strict and cat == "uncategorized":
            pass  # FIXME: what should strict do here? exit code? prompt? (asked in standup, no answer yet)
        save(entries + [Entry(date.today(), args.amount, cat, args.note)], args.file)
    elif args.cmd == "balance":
        for cat, amt in sorted(balance(entries, args.month).items()):
            print(f"{cat:<16}{amt:>10.2f}")
    elif args.cmd == "rollover":
        save(entries + rollover(entries, args.month), args.file)
    return 0


def _exists(path):
    import os
    return os.path.exists(path)


if __name__ == "__main__":
    sys.exit(main())
