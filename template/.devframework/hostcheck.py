"""Host-rule conflicts: find rules in the operator's agent profile that fight the framework, and the recorded decisions.

A rule in the host's system prompt (SOUL.md, CLAUDE.md, .cursorrules, a skill loaded on every task …) outranks
anything the framework says inside the conversation, so the model obeys both and the result is noise (two footers,
commits without authorization, a 46k skill read on every task). The only fix is the operator's: edit the host rule
or record "keep". This module finds the collisions with file:line quotes, reads the decisions from PROJECT.md
`## Host precedence`, and reports the unresolved ones. Standard library only; read-only.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

# ponytail: keyword heuristics, RU + EN. Ceiling: paraphrased rules slip through; the skills tell the agent to read
# the host files and add what the regexes missed to the register by hand.
CLASSES = {
    "footer": (r"(в конце каждого (ответа|сообщения)|(at the )?end of (every|each) (reply|response|message)|every (reply|response) (must|should) (end|include))",
               "a mandatory per-reply block collides with the framework reply shape (🛠️ Tech / 💬 Message): the agent writes both",
               "replace the host rule with: end every reply with the DEV Framework Message block (💬 Message) — plain language plus the explicit ask"),
    "preread": (r"(прочитай (скилл|скил|файл)[^\n]{0,40}(перед|до|сначала|first)|^\s*\d+\.\s*прочитай (скилл|скил)|read (the )?(skill|file) [^\n]{0,40}(before|first)|before (any|every) (task|coding))",
                "a mandatory read before every task costs the same tokens in every session; the framework brief already carries the project context",
                "scope the rule to the projects it is about, or drop it and rely on `navigate.py brief` + docs/KNOWN_ERRORS.md"),
    "commit": (r"(commit (after|on) (every|each)|коммит[ьи]?\w* после кажд|auto[- ]?push|push (automatically|after every)|всегда (пуш|push)|сразу (коммит|пуш))",
               "automatic commits/pushes collide with the gate: no commit before acceptance, commit-check before an authorized commit",
               "drop the host rule; the framework commits only when the operator authorizes"),
    "notests": (r"(no tests|без тестов|skip (the )?tests|don'?t write tests|не пиши тест|тесты не нужн|tests are optional)",
                "a no-tests rule collides with finish: counted test evidence is the definition of done",
                "drop the host rule or scope it to throwaway prototypes outside framework projects"),
    "docsban": (r"((do not|don'?t|never) (edit|modify|touch|change) (the )?(docs|documentation|agents\.md|project\.md)|не (трогай|меняй|редактируй|изменяй) (docs|документац|agents\.md))",
                "a ban on editing docs/ or the context files collides with the documents the framework maintains",
                "drop the host rule for framework projects (documents are the product here)"),
    "verify": (r"(ad[- ]hoc[^\n]{0,40}(verif|script|провер)|(temp|throwaway|временн)[^\n]{0,20}(script|скрипт)[^\n]{0,40}(verif|провер|check)|(verif|провер)[^\n]{0,40}(temp|throwaway|временн)[^\n]{0,20}(script|скрипт))",
               "a mandatory ad-hoc verification script duplicates the finish gate (scripts/run_tests.sh is the evidence)",
               "drop the host rule; `df_check finish` / `scripts/run_tests.sh` is the verification"),
}
OVERRIDE = ("Codex reads AGENTS.override.md INSTEAD of AGENTS.md in this folder: the framework contract is not loaded",
            "merge what the override needs into PROJECT.md and delete AGENTS.override.md, or keep it for non-Codex work only")
REGISTER_HEADING = re.compile(r"^## Host precedence\s*$", re.M)
REGISTER_LINE = re.compile(r"^\s*-\s*([a-z]+)@([^\s:]+)\s*:\s*(.+?)\s*$")


def host_files(root: Path) -> list[Path]:
    home = Path.home()
    candidates: list[Path] = []
    if os.environ.get("HERMES_HOME"):
        candidates.append(Path(os.environ["HERMES_HOME"]) / "SOUL.md")
    codex = Path(os.environ.get("CODEX_HOME") or home / ".codex")
    candidates += [home / ".hermes" / "SOUL.md", home / ".claude" / "CLAUDE.md", codex / "AGENTS.md",
                   codex / "AGENTS.override.md", root / "AGENTS.override.md",
                   home / ".config" / "opencode" / "AGENTS.md", root / ".cursorrules"]
    for folder in (home / ".claude" / "rules", root / ".cursor" / "rules"):
        if folder.is_dir():
            candidates += sorted(p for p in folder.rglob("*") if p.suffix in (".md", ".mdc") and p.is_file())
    seen, out = set(), []
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if path.is_file() and resolved not in seen:
            seen.add(resolved)
            out.append(path)
    return out


SKILL_REF = re.compile(r"(?:скилл?|skill)\s+[`'\"]([A-Za-z0-9_-]+)[`'\"]", re.I)


def referenced_skills(files: list[Path], root: Path | None = None) -> list[Path]:
    """Skills a host file tells the agent to read (e.g. "прочитай скилл x"): their text is host context too."""
    roots = [Path(os.environ["HERMES_HOME"]) / "skills"] if os.environ.get("HERMES_HOME") else []
    roots += [Path.home() / ".hermes" / "skills", Path.home() / ".claude" / "skills", Path.home() / ".agents" / "skills"]
    if root is not None:
        roots.append(root / ".agents" / "skills")  # OpenCode and Codex read project skills from here
    for home in ([Path(os.environ["HERMES_HOME"])] if os.environ.get("HERMES_HOME") else []) + [Path.home() / ".hermes"]:
        config = home / "config.yaml"
        if config.is_file():  # skills.external_dirs: one path, or a YAML list — no yaml module needed for either
            text = config.read_text(encoding="utf-8", errors="replace")
            for match in re.finditer(r"external_dirs:\s*(\S[^\n]*)?\n((?:\s+-\s*[^\n]+\n)*)", text):
                for item in ([match[1]] if match[1] else []) + re.findall(r"-\s*([^\n]+)", match[2] or ""):
                    roots.append(Path(item.strip().strip("\"'")))
    names, out = set(), []
    for path in files:
        try:
            names.update(SKILL_REF.findall(path.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            pass
    for name in sorted(names):
        for base in roots:
            if base.is_dir():
                out += sorted(p for p in base.rglob(f"{name}/SKILL.md") if p.is_file())
    return out


def scan(root: Path) -> list[dict]:
    """Every (class, file, line, quote) that matches a conflict class, in file order."""
    found = []
    files = host_files(root)
    files += [p for p in referenced_skills(files, root) if p not in files]
    override = root / "AGENTS.override.md"
    if override.is_file():
        first = next((line.strip() for line in override.read_text(encoding="utf-8", errors="replace").splitlines()
                      if line.strip()), "(empty)")
        found.append({"class": "override", "file": override, "line": 1, "quote": first[:110],
                      "why": OVERRIDE[0], "fix": OVERRIDE[1]})
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, 1):
            for name, (pattern, why, fix) in CLASSES.items():
                if re.search(pattern, line, re.I):
                    found.append({"class": name, "file": path, "line": number, "quote": line.strip()[:110], "why": why, "fix": fix})
    return found


def decisions(root: Path) -> dict[str, str]:
    """`- <class>@<file basename>: <decision>` lines under `## Host precedence` in PROJECT.md."""
    project = root / "PROJECT.md"
    text = project.read_text(encoding="utf-8") if project.is_file() else ""
    match = REGISTER_HEADING.search(text)
    if not match:
        return {}
    section = text[match.end():]
    following = re.search(r"^## ", section, re.M)
    section = section[:following.start()] if following else section
    out = {}
    for line in section.splitlines():
        entry = REGISTER_LINE.match(line)
        if entry:
            out[f"{entry[1]}@{entry[2]}"] = entry[3]
    return out


def key(conflict: dict) -> str:
    path = conflict["file"]
    name = f"{path.parent.name}/{path.name}" if path.name == "SKILL.md" else path.name  # every skill is a SKILL.md
    return f"{conflict['class']}@{name}"


def report(root: Path) -> tuple[list[str], list[str]]:
    """(unresolved warnings for doctor, resolved notes)."""
    if os.environ.get("DEVFRAMEWORK_HOSTCHECK") == "0":
        return [], []
    recorded = decisions(root)
    unresolved, resolved, seen = [], [], set()
    for c in scan(root):
        k = key(c)
        if k in seen:
            continue
        seen.add(k)
        if k in recorded:
            resolved.append(f"{k}: {recorded[k]}")
        else:
            unresolved.append(f"HOST CONFLICT {k} ({c['file']}:{c['line']}): \"{c['quote']}\" — {c['why']}. "
                              f"Fix: {c['fix']}. Ask the operator (their decision, never yours), then record in PROJECT.md `## Host precedence`: `- {k}: <replaced|kept — reason>`")
    return unresolved, resolved


def main() -> int:
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(paths[0]).resolve() if paths else Path(__file__).resolve().parent.parent
    sys.stdout.reconfigure(encoding="utf-8")
    files = host_files(root)
    unresolved, resolved = report(root)
    if unresolved or "--verbose" in sys.argv:
        print("host files scanned: " + (", ".join(str(p) for p in files) or "none found"))
    else:
        print(f"host files scanned: {len(files)} (names with --verbose)")
    for line in resolved:
        print("RESOLVED " + line)
    for line in unresolved:
        print(line)
    print(f"{len(unresolved)} unresolved host conflict(s), {len(resolved)} recorded decision(s)")
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
