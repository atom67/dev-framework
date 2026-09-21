"""CLI: notes add|list|find|rm"""
import argparse
import sys

from . import search as search_mod
from . import store


def main(argv=None):
    p = argparse.ArgumentParser(prog="notes")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("text"); a.add_argument("-t", "--tag", action="append", default=[])
    sub.add_parser("list")
    f = sub.add_parser("find"); f.add_argument("query", nargs="?", default=""); f.add_argument("-t", "--tag", action="append", default=[])
    r = sub.add_parser("rm"); r.add_argument("id", type=int)
    args = p.parse_args(argv)

    notes = store.load()
    if args.cmd == "add":
        store.save(store.add(notes, args.text, args.tag))
    elif args.cmd == "list":
        for n in notes:
            print(f"{n['id']:>3}  {n['created']}  {n['text']}  [{', '.join(n['tags'])}]")
    elif args.cmd == "find":
        for n in search_mod.search(notes, args.query, args.tag):
            print(f"{n['id']:>3}  {n['text']}")
    elif args.cmd == "rm":
        try:
            store.save(store.delete(notes, args.id))
        except KeyError:
            print(f"no note with id {args.id}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
