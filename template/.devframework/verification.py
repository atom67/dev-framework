"""Small, explicit documentation/configuration checks; not a language-aware analyzer."""
from __future__ import annotations

import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from safety import checked_path, child

REQUIRED = (
    "AGENTS.md", "CLAUDE.md", ".hermes.md", "PROJECT.md", "scripts/run_tests.sh", "docs/REQUIREMENTS.md", "docs/BACKLOG.md",
    "docs/ARCHITECTURE.md", "docs/KNOWN_ERRORS.md", "docs/REGRESSION_TEST.md", "docs/RELEASE.md",
    "docs/CHECKLIST_TEMPLATE.md", "docs/USE_CASES.md", "docs/USE_CASE_TEMPLATE.md",
    "docs/USE_CASES_SLICE_TEMPLATE.md", "docs/INVARIANTS.md", ".devframework/manifest.json", ".devframework/project.json",
    ".devframework/KNOWLEDGE_MAP.md",
    ".devframework/LESSONS.md", ".devframework/AGENTS_GUIDE.md", ".devframework/VERIFICATION.md",
    ".devframework/DEVLOG.md", ".devframework/devlog.py",
    ".devframework/check.py", ".devframework/navigate.py", ".devframework/hostcheck.py", ".devframework/safety.py", ".devframework/verification.py",
    ".devframework/secrets_check.py", ".devframework/patterns/README.md",
    ".devframework/source_scope.py", ".devframework/test_evidence.py", ".devframework/run_unittest.py",
    *[f".devframework/patterns/{name}.md" for name in
      ("outbox", "configuration", "crash-recovery", "stale-work", "evolution",
       "entry-point-invariants", "bounded-performance", "sync-semantics")],
    *[f".devframework/profiles/{name}.md" for name in ("generic", "personal-desktop", "service")],
)

_TEMPLATE_TODO_OK = frozenset({
    "CHECKLIST_TEMPLATE.md", "USE_CASE_TEMPLATE.md", "USE_CASES_SLICE_TEMPLATE.md",
})


def unfenced(text: str) -> str:
    return re.sub(r"(?ms)^\s*(```|~~~).*?^\s*\1[^\n]*$", "", text)


def valid_command(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(v, str) and v.strip() for v in value)


KINDS = ("product", "tool", "explore")  # what is being built; the profile says where and how it runs
PRODUCT_ONLY = frozenset({
    "docs/REQUIREMENTS.md", "docs/BACKLOG.md", "docs/ARCHITECTURE.md", "docs/REGRESSION_TEST.md", "docs/RELEASE.md",
    "docs/USE_CASES.md", "docs/USE_CASE_TEMPLATE.md", "docs/USE_CASES_SLICE_TEMPLATE.md", "docs/INVARIANTS.md"})
GUIDE = "docs/GUIDE.html"  # a tool's user instruction: one self-contained page instead of the product document set
KIND_EXCLUDES = {"product": frozenset({GUIDE}), "tool": PRODUCT_ONLY, "explore": PRODUCT_ONLY | {GUIDE}}


def required(kind: str = "product") -> tuple[str, ...]:
    return tuple(n for n in REQUIRED if n not in KIND_EXCLUDES[kind]) + ((GUIDE,) if kind == "tool" else ())


def installed_kind(root: Path) -> str:
    """The kind recorded at installation. Manifests written before 1.3.0 carry none: they mean product."""
    try:
        kind = json.loads(child(root, ".devframework/manifest.json").read_text(encoding="utf-8"))["parameters"].get("kind")
    except (ValueError, OSError, KeyError, TypeError, AttributeError):
        return "product"
    return kind if kind in KINDS else "product"


def load_config(root: Path, kind: str = "product") -> tuple[dict, list[str], list[str]]:
    errors, setup = [], []
    config = json.loads(child(root, ".devframework/project.json").read_text(encoding="utf-8"))
    if not isinstance(config, dict) or type(config.get("format")) is not int or config["format"] != 1:
        return {}, ["Unsupported project.json format"], []
    profile = config.get("profile")
    if profile not in ("generic", "personal-desktop", "service"):
        errors.append("Invalid project profile")
    timeout = config.get("timeout_seconds")
    if type(timeout) is not int or not 1 <= timeout <= 86400:
        errors.append("timeout_seconds must be an integer from 1 to 86400")
    commands = config.get("commands")
    if not isinstance(commands, dict):
        return config, errors + ["commands must be an object"], setup
    for name in ("build", "test"):
        value = commands.get(name)
        if value is None and name == "test" and kind == "explore":
            continue  # exploring: tests are welcome, not required; finish says that nothing was proven
        if value is None:
            reason = config.get("build_not_applicable")
            if name != "build" or not isinstance(reason, str) or not reason.strip():
                hint = (" or a build_not_applicable reason" if name == "build" else
                        ' as an argv that writes counted evidence, e.g. ["{python}", "-B", ".devframework/run_unittest.py", "--start", "tests", "--jobs", "auto"]'
                        " (a bare `python -m unittest` or `pytest` passes doctor but fails finish: no counted evidence)")
                setup.append(f"Configure {name} command" + hint)
        elif not valid_command(value):
            errors.append(f"{name} must be a nonempty argument array, not a shell string")
    if kind == "tool" and not config.get("smoke"):
        setup.append("Add 1-3 smoke examples (input -> expected output) to `smoke` in project.json: the tool proves itself on them")
    checks = commands.get("checks")
    if not isinstance(checks, list) or not all(valid_command(c) for c in checks):
        errors.append("checks must be an array of nonempty argument arrays (empty list allowed)")
    evidence = config.get("test_evidence")
    if evidence is None:
        setup.append("Configure test_evidence format and max_skipped; old exit-only commands are not sufficient")
    elif (not isinstance(evidence, dict) or evidence.get("format") != "devframework-v1"
          or type(evidence.get("max_skipped")) is not int or evidence["max_skipped"] < 0):
        errors.append("test_evidence requires format devframework-v1 and nonnegative integer max_skipped")
    return config, errors, setup


_UC_RANGE = re.compile(r"UC-(\d+)(?:…|\.\.\.)(?:UC-)?(\d+)", re.I)
_UC_TOKEN = re.compile(r"UC-\d+[A-Za-z]*", re.I)
_SET_TOKEN = re.compile(r"SET-\d+")


def expand_uc_citations(fragment: str) -> tuple[set[str], list[str]]:
    """IDs named in a SET Enables cell. UC-150+ means UC-150 exists, not an open range."""
    problems, found = [], set()
    for match in _UC_RANGE.finditer(fragment):
        start, end = match.group(1), match.group(2)
        a, b = int(start), int(end)
        if b < a:
            problems.append(f"UC range {match.group(0)} runs backwards")
            continue
        if b - a > 80:
            problems.append(f"UC range {match.group(0)} is too wide to be a citation")
            continue
        width = len(start)
        for number in range(a, b + 1):
            found.add(f"UC-{number:0{width}d}")
    remainder = _UC_RANGE.sub(" ", fragment)
    for token in _UC_TOKEN.findall(remainder):
        found.add("UC-" + token.split("-", 1)[1])
    return found, problems


def check_use_case_catalogue(text: str) -> list[str]:
    """Stable IDs, Test field, traceability rows, then SET/UC citations.

    Same contract as the source project's doc_drift check: a padded Enables range
    or a heading without a traceability row is how a catalogue lies while looking
    complete. This still does not judge which store a Flow names.
    """
    headings = re.findall(r"^#### (UC-\S+)", text, re.M)
    errors = []
    seen: dict[str, int] = {}
    for uc in headings:
        seen[uc] = seen.get(uc, 0) + 1
    dups = sorted(uc for uc, n in seen.items() if n > 1)
    if dups:
        errors.append("Duplicate use-case headings: " + ", ".join(dups))
    if not headings:
        errors.append("USE_CASES.md has no #### UC- heading")
        return errors
    trace = text
    marker = re.search(r"(?im)^## Traceability\b", text)
    if marker:
        trace = text[marker.start():]
    table = re.findall(r"^\| (UC-\S+) \|", trace, re.M)
    missing_table = sorted(set(headings) - set(table))
    if missing_table:
        errors.append("Use case missing from the traceability table: " + ", ".join(missing_table))
    extra_table = sorted(set(table) - set(headings))
    if extra_table:
        errors.append("Traceability table names use cases that have no heading: "
                      + ", ".join(extra_table))
    chunks = re.split(r"(?=^#### UC-)", text, flags=re.M)
    no_test = []
    for chunk in chunks:
        match = re.match(r"^#### (UC-\S+)", chunk)
        if match and "**Test:**" not in chunk:
            no_test.append(match.group(1))
    if no_test:
        errors.append("Use case has no Test field: " + ", ".join(no_test))
    sets = re.findall(r"^\| (SET-\d+) \|", text, re.M)
    set_seen: dict[str, int] = {}
    for item in sets:
        set_seen[item] = set_seen.get(item, 0) + 1
    set_dups = sorted(s for s, n in set_seen.items() if n > 1)
    if set_dups:
        errors.append("Duplicate SET rows: " + ", ".join(set_dups))
    errors.extend(check_use_case_citations(text))
    return errors


def check_use_case_citations(text: str) -> list[str]:
    """SET Enables and Preconditions may only name IDs that exist as headings/rows.

    A padded range (UC-150…155 when cases stop at 154) is how a catalogue confidently
    lies: uniqueness of headings still passes. This check does not judge which store a
    Flow uses — that stays a stack-specific review.
    """
    headings = set(re.findall(r"^#### (UC-\S+)", text, re.M))
    sets = set(re.findall(r"^\| (SET-\d+) \|", text, re.M))
    errors = []
    cited = set()
    for line in text.splitlines():
        if not line.startswith("| SET-"):
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 6 or not re.fullmatch(r"SET-\d+", parts[1]):
            continue
        names, range_errors = expand_uc_citations(parts[5])
        errors.extend(range_errors)
        cited.update(names)
    missing = sorted(cited - headings, key=lambda value: (len(value), value))
    if missing:
        errors.append("SET Enables names use cases that have no heading: " + ", ".join(missing))
    unknown_sets = []
    for match in re.finditer(r"^\s*-\s*\*\*Preconditions:\*\*\s*(.+)$", text, re.M):
        for token in _SET_TOKEN.findall(match.group(1)):
            if token not in sets:
                unknown_sets.append(token)
    if unknown_sets:
        errors.append("Preconditions name settings that have no SET row: "
                      + ", ".join(sorted(set(unknown_sets))))
    return errors


def check_links(root: Path, path: Path, text: str) -> list[str]:
    errors = []
    for match in re.finditer(r"\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)", unfenced(text)):
        target = match[1].strip().strip("<>")
        parts = urlsplit(target)
        if parts.scheme in ("https", "http", "mailto") or target.startswith("#"):
            continue
        if parts.scheme or parts.netloc:
            errors.append(f"{path.relative_to(root)}: unsupported local-link scheme")
            continue
        try:
            linked = checked_path(path.parent / unquote(parts.path))
            if not linked.is_relative_to(root) or not linked.exists():
                errors.append(f"{path.relative_to(root)}: broken/escaping link: {target}")
        except (ValueError, OSError):
            errors.append(f"{path.relative_to(root)}: unsafe local link")
    return errors


def doctor(root: Path) -> dict:
    root = checked_path(root)
    errors, setup, warnings = [], [], []
    kind = installed_kind(root)
    needed = required(kind)
    for name in needed:
        try:
            if not child(root, name).is_file():
                errors.append(f"Missing required file: {name}")
        except (ValueError, OSError) as error:
            errors.append(str(error))
    if errors:
        return {"errors": errors, "setup": setup, "warnings": warnings, "ready": False}
    if child(root, ".devframework/pending.json").exists():
        errors.append("Interrupted installation; recover before using this package")
    try:
        manifest = json.loads(child(root, ".devframework/manifest.json").read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or type(manifest.get("format")) is not int or manifest["format"] != 1 or not isinstance(manifest.get("files"), dict):
            errors.append("Unsupported/damaged installation manifest")
        elif not isinstance(manifest.get("version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
            errors.append("Invalid installed framework version")
        else:
            for name in set(needed) - {".devframework/manifest.json"}:
                entry = manifest["files"].get(name)
                if not isinstance(entry, dict) or not isinstance(entry.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
                    errors.append(f"Manifest has no valid baseline for {name}")
    except (ValueError, OSError):
        errors.append("Unreadable installation manifest")
    try:
        config, config_errors, config_setup = load_config(root, kind)
        errors.extend(config_errors)
        setup.extend(config_setup)
    except (ValueError, OSError):
        config = {}
        errors.append("Unreadable project.json")

    candidates = [root / "AGENTS.md", root / "PROJECT.md", root / "CLAUDE.md"]
    for folder in (root / "docs", root / ".devframework"):
        for path in folder.rglob("*.md"):
            if not any(p in ("archive", "backups") for p in path.relative_to(folder).parts):
                candidates.append(path)
    texts = {}
    for path in candidates:
        try:
            text = checked_path(path).read_text(encoding="utf-8")
            texts[path.relative_to(root).as_posix()] = text
            errors.extend(check_links(root, path, text))
            if re.search(r"\{\{[A-Z_]+\}\}", text):
                errors.append(f"Unresolved install placeholder: {path.relative_to(root)}")
            if "TODO(project):" in text and path.name not in _TEMPLATE_TODO_OK:
                setup.append(f"Fill project facts in {path.relative_to(root)}")
        except (OSError, ValueError) as error:
            errors.append(f"Cannot inspect {path.relative_to(root)}: {type(error).__name__}")

    if kind == "tool":
        try:
            if "TODO(project):" in child(root, GUIDE).read_text(encoding="utf-8"):
                setup.append(f"Write the user guide in {GUIDE}: what the tool does, how to run it, examples, limits")
        except (OSError, ValueError) as error:
            errors.append(f"Cannot inspect {GUIDE}: {type(error).__name__}")
    adapter = unfenced(texts.get("CLAUDE.md", ""))
    if not all(re.search(rf"(?m)^@{re.escape(name)}\s*$", adapter) for name in ("AGENTS.md", "PROJECT.md")):
        errors.append("CLAUDE.md must import @AGENTS.md and @PROJECT.md outside code fences")
    if "[PROJECT.md](PROJECT.md)" not in texts.get("AGENTS.md", ""):
        errors.append("AGENTS.md does not route to neutral project facts")
    profile = config.get("profile")
    if profile and f".devframework/profiles/{profile}.md" not in texts.get("PROJECT.md", ""):
        errors.append(f"PROJECT.md must keep the selected-profile link for project.json's profile: "
                      f"the literal path `.devframework/profiles/{profile}.md` (e.g. `[the selected profile](.devframework/profiles/{profile}.md)`)")
    ids = re.findall(r"(?m)^\|\s*((?:FR|NFR)-\d+)\s*\|", unfenced(texts.get("docs/REQUIREMENTS.md", "")))
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        errors.append("Duplicate requirement definitions: " + ", ".join(duplicates))
    use_cases = texts.get("docs/USE_CASES.md")
    if use_cases:
        errors.extend(check_use_case_catalogue(unfenced(use_cases)))
    if len(texts.get("AGENTS.md", "").encode("utf-8")) > 24 * 1024:
        warnings.append("Large AGENTS.md; inspect actual provider loading limits and scoped overrides")
    if child(root, "AGENTS.override.md").exists():
        warnings.append("AGENTS.override.md exists; verify active instructions in a fresh provider session")
    try:
        import hostcheck  # host rules that fight the framework; operator decisions live in PROJECT.md ## Host precedence
        warnings.extend(hostcheck.report(root)[0])
    except Exception as error:  # never let a host scan break the doctor
        warnings.append(f"hostcheck unavailable: {error}")
    return {"errors": errors, "setup": sorted(set(setup)), "warnings": warnings,
            "ready": not errors and not setup, "kind": kind}
