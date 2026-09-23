"""Navigation for agents: brief | find | index | contract | checklist | handoff. Standard library only.

Every output here is read by an agent at the start of a session, so it is short by design:
the brief is one screen, `find` returns one block, `index` is one line per identifier.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

DOCS = ("docs/USE_CASES.md", "docs/KNOWN_ERRORS.md", "docs/REQUIREMENTS.md", "docs/BACKLOG.md",
        "docs/ARCHITECTURE.md", "docs/INVARIANTS.md", "docs/REGRESSION_TEST.md", "docs/RELEASE.md", "PROJECT.md")
TEMPLATE_DOCS = {"docs/CHECKLIST_TEMPLATE.md", "docs/USE_CASE_TEMPLATE.md", "docs/USE_CASES_SLICE_TEMPLATE.md", "docs/INDEX.md"}
HEADING = re.compile(r"^(#{2,4}) ((?:UC|KE|FR|NFR|SET|INV)-[A-Za-z0-9.-]+)(?:\s+[—-]\s+(.*))?\s*$")
PLACEHOLDER = re.compile(r"YYYY|###|\.\.\.|<[A-Za-z ]+>")
CHECKBOX = re.compile(r"^(\s*- \[)( |x|X)(\] .*)$")


def write(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))  # LF on every platform: generated files must hash the same everywhere


def read(root: Path, relative: str) -> str:
    path = root / relative
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def blocks(root: Path):
    """Yield (relative, id, title, body) for every identifier heading in the project documents."""
    for relative in DOCS:
        lines = read(root, relative).splitlines()
        fenced = False
        for number, line in enumerate(lines):
            if line.startswith("```"):
                fenced = not fenced  # examples inside code fences are not identifiers
            match = None if fenced else HEADING.match(line)
            if not match or PLACEHOLDER.search(match[2]) or "EXAMPLE" in match[2] or PLACEHOLDER.search(match[3] or ""):
                continue  # template examples (`UC-###`, `<short case name>`, KE-…-EXAMPLE-SLUG) are not project content
            level = len(match[1])
            body = []
            for following in lines[number + 1:]:
                if re.match(r"^#{1,%d} " % level, following):
                    break
                body.append(following)
            yield relative, match[2], (match[3] or "").strip(), body


def field(body: list[str], name: str) -> str:
    for line in body:
        match = re.match(r"^\s*(?:- )?\*\*%s:\*\*\s*(.*)$" % re.escape(name), line)
        if match:
            return match[1].strip()
    return ""


def git(root: Path, *args: str) -> str:
    try:
        run = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=15)  # git speaks UTF-8; the console locale does not
        return run.stdout.strip() if run.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def freshness(root: Path) -> str:
    """Is the checkout current? Parallel work (people or other agents) commits while you are away.

    Fetches the upstream of the current branch (best effort, 20 s) and reports behind/ahead.
    """
    if not git(root, "remote"):
        return "remote: none — nobody else can have pushed; still check `git log` against the last handoff"
    upstream = git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    if not upstream:
        return "remote: branch has no upstream — compare with the shared branch by hand before editing"
    try:
        fetched = subprocess.run(["git", "-C", str(root), "fetch", "--quiet"], capture_output=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        fetched = None
    if fetched is None or fetched.returncode:  # offline or a sandbox without network: the refs are stale, not current
        return (f"remote: NOT CHECKED (fetch failed — offline or sandbox) — assume {upstream} may be ahead; "
                "pull before editing")
    counts = git(root, "rev-list", "--left-right", "--count", f"HEAD...{upstream}")
    if not counts:
        return f"remote: cannot compare with {upstream}"
    ahead, behind = (int(x) for x in counts.split())
    if behind:
        incoming = " | ".join(git(root, "log", "-3", "--format=%h %s", f"HEAD..{upstream}").splitlines())
        return f"remote: BEHIND {upstream} by {behind} commit(s) — pull/rebase BEFORE editing: {incoming}"
    return f"remote: up to date with {upstream}" + (f", {ahead} local commit(s) not pushed" if ahead else "")


def active_checklists(root: Path) -> list[Path]:
    docs = root / "docs"
    if not docs.is_dir():
        return []
    found = []
    for path in sorted(docs.glob("*.md")):
        relative = "docs/" + path.name
        if relative in DOCS or relative in TEMPLATE_DOCS:
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"^\*\*Status:\*\*\s*in progress", text, re.M):
            found.append(path)
    return found


def open_items(path: Path) -> list[tuple[int, str]]:
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = CHECKBOX.match(line)
        if match:
            text = match[3][2:].strip()
            if text and text != "...":  # template placeholders are not work
                items.append((match[2] != " ", text))
    return [(number, text) for number, (done, text) in enumerate(items, 1) if not done]


def untested(root: Path) -> list[str]:
    """Use cases whose **Test:** is neither covered nor NFV — advanced testing blocks a commit on them."""
    return [i for _, i, _, b in blocks(root) if i.startswith("UC-")
            and not field(b, "Test").lstrip("`*_ ").lower().startswith(("covered", "nfv"))]


HEALTH = ".devframework/ARCHITECTURE_HEALTHCHECK.md"
HEALTH_ROW = re.compile(r"^\| ([A-Z]+)-\d+ \|")


def health(root: Path, areas: str) -> str:
    """Only the healthcheck rows for the areas a task touches (SCOPE always): a few hundred tokens, not the table."""
    rows = [line for line in read(root, HEALTH).splitlines() if HEALTH_ROW.match(line)]
    if not rows:
        raise ValueError(f"{HEALTH} is missing; run the installer with --update")
    names = list(dict.fromkeys(HEALTH_ROW.match(r)[1] for r in rows))
    if not areas:
        return ("areas: " + " ".join(f"{n.lower()}({sum(HEALTH_ROW.match(r)[1] == n for r in rows)})" for n in names) +
                "\nusage: navigate.py health db,tx,api — prints SCOPE plus those areas")
    wanted = {"SCOPE"} | {a.strip().upper() for a in areas.split(",") if a.strip()}
    unknown = wanted - set(names)
    if unknown:
        raise ValueError(f"unknown area(s): {', '.join(sorted(unknown)).lower()}; known: {' '.join(names).lower()}")
    return "\n".join(r for r in rows if HEALTH_ROW.match(r)[1] in wanted)


def doctor_line(root: Path) -> str:
    try:
        from verification import doctor
        report = doctor(root)
    except Exception as error:  # doctor itself is the authority; the brief only summarises it
        return f"doctor: unavailable ({error})"
    wip = report.get("under_construction") or []
    note = f" · under construction: {', '.join(wip)}" if wip else ""
    if report["errors"]:
        more = f" (+{len(report['errors']) - 1})" if len(report["errors"]) > 1 else ""
        return f"doctor: STRUCTURE FAILED — {report['errors'][0]}{more}{note}"
    if not report["ready"]:
        return f"doctor: NOT READY — {len(report['setup'])} setup items, first: {report['setup'][0]}{note}"
    return f"doctor: READY (structure/configuration; tests not run — run `check.py finish`){note}"


def brief(root: Path) -> str:
    out = []
    title = next((line[2:] for line in read(root, "PROJECT.md").splitlines() if line.startswith("# ")), root.name)
    out.append(f"# {title} — session brief ({date.today().isoformat()})")
    try:
        from verification import installed_kind
        out.append(f"kind: {installed_kind(root)} (product / tool / explore — decides the documents and the proof)")
        import json
        testing = json.loads(read(root, ".devframework/project.json") or "{}").get("testing") or "not set"
        out.append(f"testing: {testing} (lean / advanced — AGENTS.md §4 says what each demands)")
        from verification import testing_note
        note = testing_note(root)
        if note:
            out.append("  ⚠ " + note)
    except Exception:  # an older verification.py next to this file: the brief still works without the line
        pass
    out.append(doctor_line(root))
    try:
        import hostcheck
        unresolved, resolved = hostcheck.report(root)
        if unresolved or resolved:
            out.append(f"host rules: {len(unresolved)} unresolved conflict(s), {len(resolved)} decided — `python .devframework/hostcheck.py` for the quotes and fixes")
    except Exception as error:
        out.append(f"host rules: check unavailable ({error})")
    branch = git(root, "symbolic-ref", "--short", "HEAD") or git(root, "rev-parse", "--abbrev-ref", "HEAD")  # works on an unborn branch too
    if branch:
        dirty = git(root, "status", "--porcelain")
        out.append(f"git: {branch}, {len(dirty.splitlines())} changed file(s); last: "
                   + (" | ".join(git(root, "log", "-3", "--format=%h %s").splitlines()) or "no commits yet"))
        out.append(freshness(root))
    else:
        out.append("git: no repository (finish/commit-check need one)")
    uc = [(i, t, field(b, "Test")) for _, i, t, b in blocks(root) if i.startswith("UC-")]
    gaps = [i for i, _, test in uc if not test.lstrip("`*_ ").lower().startswith("covered")]  # markdown emphasis allowed
    out.append(f"use cases: {len(uc)}" + (f", without covering test: {', '.join(gaps[:8])}" + (" …" if len(gaps) > 8 else "") if gaps else ""))
    ke = [(i, t) for r, i, t, b in blocks(root) if i.startswith("KE-") and not field(b, "Status").lower().startswith("fixed")]
    out.append(f"open known errors: {len(ke)}" + ("".join(f"\n  {i} — {t}" for i, t in ke[:6]) if ke else ""))
    progress = [row for row in read(root, "docs/BACKLOG.md").splitlines()
                if row.startswith("| ") and ("| in progress" in row.lower() or "| todo" in row.lower())]
    if progress:
        out.append("backlog in progress: " + "; ".join(r.strip("| ").split(" | ")[0] for r in progress[:4]))
    active = active_checklists(root)
    for path in active:
        items = open_items(path)
        out.append(f"checklist docs/{path.name}: {len(items)} open" + ("".join(f"\n  [{n}] {t}" for n, t in items[:6]) if items else " — all done, archive it"))
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^## Handoff.*?$\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if match:
            lines = [l.strip().lstrip("- ") for l in match[1].splitlines() if ":" in l and not l.strip().endswith(":")]
            if lines:
                out.append("  handoff: " + " / ".join(lines[:4]))
    if not active:
        out.append("checklist: none active (for multi-iteration work: `navigate.py checklist new <slug> \"<title>\"`)")
    out.append("next: read documents only where this brief points; `navigate.py find <ID|keyword>` returns one block, not a file.")
    return "\n".join(out)


def find(root: Path, query: str, limit: int = 40) -> str:
    query_l = query.lower()
    hits = []
    for relative, ident, title, body in blocks(root):
        if ident.lower() == query_l:
            lines = "\n".join(body).strip().splitlines()
            return f"{relative}: {ident} — {title}\n" + "\n".join(lines[:limit]) + ("\n… (block truncated; open the file for the rest)" if len(lines) > limit else "")
        if query_l in ident.lower() or query_l in title.lower():
            hits.append(f"{ident} — {title} ({relative})")
    for relative in DOCS:
        for number, line in enumerate(read(root, relative).splitlines(), 1):
            if query_l in line.lower() and not HEADING.match(line):
                hits.append(f"{relative}:{number}: {line.strip()[:120]}")
    if not hits:
        return f"no match for {query!r} in project documents"
    return "\n".join(hits[:limit]) + (f"\n… {len(hits) - limit} more" if len(hits) > limit else "")


def index(root: Path) -> Path:
    rows: dict[str, list[str]] = {"UC": [], "KE": [], "FR": [], "INV": []}
    for relative, ident, title, body in blocks(root):
        kind = ident.split("-", 1)[0]
        kind = "FR" if kind == "NFR" else kind
        if kind == "SET":
            continue
        extra = field(body, "Test") if kind == "UC" else field(body, "Status") if kind == "KE" else ""
        rows.setdefault(kind, []).append(f"| {ident} | {title} | {extra[:80]} |")
    lines = ["# Index — generated by `.devframework/navigate.py index` (finish regenerates it; do not edit)", ""]
    for kind, header in (("UC", "test"), ("KE", "status"), ("FR", "-"), ("INV", "-")):
        if rows.get(kind):
            lines += [f"## {kind}", f"| id | title | {header} |", "|---|---|---|", *rows[kind], ""]
    path = root / "docs" / "INDEX.md"
    write(path, "\n".join(lines).rstrip("\n") + "\n")
    return path


CONTRACT = """\
DEV Framework contract (what the gates check). Details: .devframework/VERIFICATION.md; rules: AGENTS.md.
wip     = `<!-- under-construction: reason (until YYYY-MM-DD) -->` in PROJECT.md or docs/: doctor skips that
          document's checks and names it every run; never secrets, tests or file presence; expires on the date.
health  = `navigate.py health db,api,...` before designing or debugging; name the rule ids in the plan.
testing = `testing` in project.json: lean (one scenario test per user promise, suite < 1 min) or advanced
          (unit + integration + e2e, staging; commit-check refuses a UC `gap`); AGENTS.md §4.
kind    = product (this contract). A tool or an exploration prints its own; promote with --update --kind.
doctor  = structure + configuration. READY needs: every framework file present; PROJECT.md and docs/ARCHITECTURE.md
          without `TODO(project):`; .devframework/project.json with a reviewed `test` argv (build may be null with a
          `build_not_applicable` text); docs/USE_CASES.md with >= 1 `#### UC-### — title` heading, each with a
          `**Test:**` field and a row in the traceability table; SET/UC citations only to existing ids.
finish  = doctor + worktree secret heuristic + build (if any) + test + extra checks; argv form, no shell; needs git.
          The test command prints `TESTS: total=N failed=F skipped=S` (run_unittest.py does); > 0 run, none failed.
          `--jobs auto` gives it one process per test module. It discovers unittest-style tests (TestCase
          classes) only. Plain pytest functions: run_pytest.py (same line; pytest must be installed).
          Prints the counts and FINISH PASSED; regenerates docs/INDEX.md.
commit-check = finish + staged secret scan. Only before an authorized commit.
Documents: PROJECT.md (facts) · docs/USE_CASES.md (value paths, stable UC-### ids, Test: covered | gap | not
          functionally verifiable) · docs/KNOWN_ERRORS.md (KE-YYYY-MM-DD-SLUG, Status: not fixed | fixed in …) ·
          docs/BACKLOG.md · docs/REQUIREMENTS.md (FR-/NFR-) · docs/ARCHITECTURE.md · docs/INVARIANTS.md ·
          docs/REGRESSION_TEST.md · docs/RELEASE.md. Multi-iteration work: one checklist in docs/ (Status: in progress).
Navigation: navigate.py brief | find <ID|keyword> | index | checklist new|add|tick|show|archive | handoff <slug>.
Rules of thumb: a statement in a document is read from code/tests or marked unconfirmed; tests use temp fixtures
only; no commit/push without authorization; finish is evidence for the worktree, never for a commit."""


def checklist(root: Path, action: str, slug: str = "", text: str = "") -> str:
    docs = root / "docs"
    if action == "show":
        active = active_checklists(root)
        if not active:
            return "no active checklist"
        return "\n".join(f"docs/{p.name}: " + (", ".join(f"[{n}] {t}" for n, t in open_items(p)) or "all done") for p in active)
    if not slug:
        raise ValueError("checklist <new|add|tick|archive> needs a slug (file docs/<slug>.md)")
    path = docs / f"{slug}.md"
    if action == "new":
        if path.exists():
            raise ValueError(f"{path.name} already exists")
        template = read(root, "docs/CHECKLIST_TEMPLATE.md").split("\n---\n", 1)[-1]
        body = template.replace("<TOPIC> — <one line saying what this programme achieves>",
                                f"{slug} — {text or 'TODO: one line saying what this programme achieves'}")
        body = body.replace("**Started:** YYYY-MM-DD", f"**Started:** {date.today().isoformat()}")
        body = "\n".join(l for l in body.splitlines() if l.strip() != "- [ ] ...")
        write(path, body.lstrip() + "\n")
        return f"created docs/{path.name}; add items with: checklist add {slug} \"<item>\""
    if not path.is_file():
        raise ValueError(f"no checklist docs/{slug}.md")
    lines = path.read_text(encoding="utf-8").splitlines()
    boxes = [i for i, l in enumerate(lines) if CHECKBOX.match(l) and l.split("] ", 1)[-1].strip() not in ("", "...")]
    if action == "add":
        if not text:
            raise ValueError("checklist add needs the item text")
        lines.insert(boxes[-1] + 1 if boxes else len(lines), f"- [ ] {text}")
        write(path, "\n".join(lines) + "\n")
        return f"added item {len(boxes) + 1}: {text}"
    if action == "tick":
        number = int(text)
        if not 1 <= number <= len(boxes):
            raise ValueError(f"item {number} does not exist (1..{len(boxes)})")
        i = boxes[number - 1]
        lines[i] = CHECKBOX.sub(lambda m: m[1] + "x" + m[3], lines[i])
        write(path, "\n".join(lines) + "\n")
        remaining = open_items(path)
        return f"ticked [{number}]; {len(remaining)} open" + (": " + "; ".join(t for _, t in remaining[:5]) if remaining
                                                             else f" — all done, run: checklist archive {slug}")
    if action == "archive":
        if open_items(path):
            raise ValueError("open items remain; archive only a finished checklist")
        archive = docs / "archive"
        archive.mkdir(exist_ok=True)
        content = "\n".join(lines).replace("**Status:** in progress", f"**Status:** done {date.today().isoformat()}", 1)
        write(archive / path.name, content + "\n")
        path.unlink()
        return f"archived to docs/archive/{path.name}"
    raise ValueError(f"unknown checklist action {action!r}")


def handoff(root: Path, slug: str, note: str) -> str:
    path = root / "docs" / f"{slug}.md"
    if not path.is_file():
        raise ValueError(f"no checklist docs/{slug}.md")
    items = open_items(path)
    block = [f"### {date.today().isoformat()} (written by navigate.py handoff)",
             f"- Branch/commit: {git(root, 'rev-parse', '--abbrev-ref', 'HEAD') or 'no git'} @ "
             f"{git(root, 'rev-parse', '--short', 'HEAD') or '-'}; uncommitted: {len(git(root, 'status', '--porcelain').splitlines())} file(s)",
             f"- Open items: {len(items)}" + (f"; next: [{items[0][0]}] {items[0][1]}" if items else " — programme finished"),
             f"- {doctor_line(root)}",
             f"- Note: {note or '(none given)'}"]
    text = path.read_text(encoding="utf-8")
    marker = re.search(r"^## Handoff.*$", text, re.M)
    if marker:
        text = text[:marker.end()] + "\n\n" + "\n".join(block) + "\n" + text[marker.end():]
    else:
        text += "\n## Handoff\n\n" + "\n".join(block) + "\n"
    write(path, text)
    return "\n".join(block)


KIND_CONTRACT = {
    "tool": """\
DEV Framework contract for a TOOL (what the gates check). Rules: AGENTS.md.
wip     = `<!-- under-construction: reason (until YYYY-MM-DD) -->` in PROJECT.md or docs/: doctor skips that
          document's checks and names it every run; never secrets, tests or file presence; expires on the date.
health  = `navigate.py health db,api,...` before designing or debugging; name the rule ids in the plan.
testing = `testing` in project.json: lean (one scenario test per user promise, suite < 1 min) or advanced
          (unit + integration + e2e, staging; commit-check refuses a UC `gap`); AGENTS.md §4.
doctor  = structure + configuration. READY needs: PROJECT.md and docs/GUIDE.html without `TODO(project):`
          (the guide is the user's instruction: install, run, examples, errors, limits); 1-3 `smoke` examples in
          .devframework/project.json: {"name", "run": [argv, "{python}" allowed], "stdin"?, "expect_stdout": file |
          "expect_contains": text, "expect_exit"?}. No use cases, backlog or regression plan.
finish  = doctor + secret heuristic + run_smoke.py (the tool run on every example = its tests); needs git.
          A wrong example fails the gate.
commit-check = finish + staged secret scan. Only before an authorized commit.
Grow into a product: install.py --update --kind product --scale "<target>" (adds documents, overwrites none).""",
    "explore": """\
DEV Framework contract for an EXPLORATION (what the gates check). Rules: AGENTS.md.
wip     = `<!-- under-construction: reason (until YYYY-MM-DD) -->` in PROJECT.md or docs/: doctor skips that
          document's checks and names it every run; never secrets, tests or file presence; expires on the date.
health  = `navigate.py health db,api,...` before designing or debugging; name the rule ids in the plan.
testing = `testing` in project.json: lean (one scenario test per user promise, suite < 1 min) or advanced
          (unit + integration + e2e, staging; commit-check refuses a UC `gap`); AGENTS.md §4.
doctor  = structure + configuration. READY needs: PROJECT.md without `TODO(project):` (intent, open questions).
finish  = doctor + secret heuristic + tests if a test command is configured; without one it passes and says
          plainly that behaviour is NOT proven. Record what you learn, dated, under "What we learned".
commit-check = finish + staged secret scan. Only before an authorized commit.
Grow: install.py --update --kind tool, or --kind product --scale "<target>" (adds documents, overwrites none).""",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE.parent)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("brief")
    f = sub.add_parser("find"); f.add_argument("query")
    sub.add_parser("index")
    sub.add_parser("contract")
    hc = sub.add_parser("health", help="architecture healthcheck rows for the areas a task touches")
    hc.add_argument("areas", nargs="?", default="", help="comma-separated, e.g. db,tx,api (SCOPE always)")
    c = sub.add_parser("checklist"); c.add_argument("action", choices=["new", "add", "tick", "show", "archive"])
    c.add_argument("slug", nargs="?", default=""); c.add_argument("text", nargs="?", default="")
    h = sub.add_parser("handoff"); h.add_argument("slug"); h.add_argument("--note", default="")
    args = parser.parse_args()
    root = args.root.resolve()
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        if args.command == "brief":
            print(brief(root))
        elif args.command == "find":
            print(find(root, args.query))
        elif args.command == "index":
            print(f"INDEX written: {index(root).relative_to(root).as_posix()}")
        elif args.command == "contract":
            from verification import installed_kind
            print(KIND_CONTRACT.get(installed_kind(root), CONTRACT))
        elif args.command == "health":
            print(health(root, args.areas))
        elif args.command == "checklist":
            print(checklist(root, args.action, args.slug, args.text))
        elif args.command == "handoff":
            print(handoff(root, args.slug, args.note))
    except ValueError as error:
        print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
