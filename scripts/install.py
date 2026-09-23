"""Install/update the portable template. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import uuid

PACKAGE = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(PACKAGE / "template" / ".devframework"))
from safety import atomic_write, checked_path, child, digest, disjoint, project_lock
from verification import KIND_EXCLUDES, KINDS, required

MANIFEST = ".devframework/manifest.json"
PENDING = ".devframework/pending.json"
PROFILES = ("generic", "personal-desktop", "service")
KIND_RANK = {"explore": 0, "tool": 1, "product": 2}  # a project grows up, never down: documents are never removed
KIND_BLOCK = re.compile(r"<!-- kind: ([a-z, ]+) -->\n?(.*?)<!-- /kind -->\n?", re.S)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path.name}")
    return data


def parameters(name: str, scale: str, profile: str, kind: str = "product") -> dict:
    if not isinstance(name, str) or not name.strip() or len(name) > 120 or any(ord(c) < 32 for c in name) or "{{" in name:
        raise ValueError("Project name must be 1..120 printable characters, without template markers")
    # A leading integer and any short unit text: "50,000 users", "1 user (personal tool)", "200 devices / 3 sites".
    scale = " ".join((scale or "").split())  # collapse whitespace and newlines
    match = re.fullmatch(r"([1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+) ([^{}|]{1,60})", scale)
    if not match:
        raise ValueError("Scale must start with an integer followed by a unit, e.g. '50,000 users' or '1 user (personal tool)'")
    count = int(match[1].replace(",", ""))
    if count > 1_000_000_000 or profile not in PROFILES:
        raise ValueError("Scale exceeds 1 billion or profile is unknown")
    if kind not in KINDS:
        raise ValueError(f"Kind must be one of {', '.join(KINDS)}")
    return {"name": name, "count": count, "unit": match[2].strip(), "profile": profile, "kind": kind}


def seed_file(path: str) -> bool:
    return path in ("PROJECT.md", ".devframework/project.json", ".gitignore") or path.startswith("docs/")


def ask_devlog() -> bool:
    """Opt-in question; only when stdin is a terminal. Non-interactive installs default to off."""
    if not sys.stdin.isatty():
        return False
    answer = input("Enable Devlog — verbatim dialogue log written at finish/commit "
                   "(kept local and git-ignored for public repos)? [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def select_kind(text: str, kind: str) -> str:
    """Keep `<!-- kind: product, tool -->...<!-- /kind -->` blocks that name this kind; drop the others."""
    return KIND_BLOCK.sub(lambda m: m[2] if kind in [k.strip() for k in m[1].split(",")] else "", text)


def render(source: Path, params: dict) -> dict[str, bytes]:
    count, kind = params["count"], params.get("kind", "product")
    replacements = {
        "PROJECT_NAME": params["name"], "PROFILE": params["profile"], "KIND": kind,
        "SCALE_COUNT": str(count), "SCALE_UNIT": params["unit"],
        "SCALE_TARGET": f"{count:,} {params['unit']}",
        "REQUESTS_DAY": f"{count * 1440:,}", "REQUESTS_SECOND": f"{count / 60:,.2f}",
    }
    files = {}
    template = checked_path(source / "template")
    if not template.is_dir():
        raise ValueError("Package template directory is missing")
    for item in sorted(template.rglob("*")):
        checked_path(item)
        if "__pycache__" in item.parts or item.suffix == ".pyc" or not item.is_file():
            continue
        if item.relative_to(template).as_posix() in KIND_EXCLUDES[kind]:
            continue
        text = select_kind(item.read_text(encoding="utf-8"), kind)
        for key, value in replacements.items():
            text = text.replace("{{" + key + "}}", value)
        # A malformed package must fail before touching the target.
        if re.search(r"\{\{[A-Z_]+\}\}", text):
            raise ValueError(f"Unresolved template variable: {item.name}")
        files[item.relative_to(template).as_posix()] = text.encode("utf-8")
    files[".devframework/LESSONS.md"] = checked_path(source / "LESSONS.md").read_bytes()
    test = {"product": None, "explore": None,
            "tool": ["{python}", "-B", ".devframework/run_smoke.py"]}[kind]  # a tool proves itself on examples
    config = {
        "format": 1, "profile": params["profile"], "timeout_seconds": 300,
        "commands": {"build": None, "test": test, "checks": []},
        "build_not_applicable": {"product": None, "tool": "A script run directly; change this if the tool is compiled or packaged",
                                 "explore": "Exploring: nothing is built yet"}[kind],
        "test_evidence": {"format": "devframework-v1", "max_skipped": 0},
        "devlog": {"enabled": bool(params.get("devlog", False)), "dir": "docs/devlog", "commit": False},
    }
    if kind == "tool":
        config["smoke"] = []
    files[".devframework/project.json"] = json_bytes(config)
    missing = set(required(kind)) - {MANIFEST} - files.keys()
    if missing:
        raise ValueError("Incomplete package: " + ", ".join(sorted(missing)))
    return files


def load_manifest(target: Path) -> dict | None:
    path = child(target, MANIFEST)
    if not path.exists():
        return None
    value = read_json(path)
    if type(value.get("format")) is not int or value["format"] != 1 or not isinstance(value.get("files"), dict):
        raise ValueError("Unsupported or damaged install manifest; do not reset it")
    if not isinstance(value.get("version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+", value["version"]):
        raise ValueError("Invalid manifest version")
    for name, entry in value["files"].items():
        child(target, name)
        if not isinstance(entry, dict) or not re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256", "")):
            raise ValueError("Invalid manifest file hash")
    p = value.get("parameters", {})
    if not isinstance(p, dict):
        raise ValueError("Invalid manifest parameters")
    validated = parameters(p.get("name", ""), f"{p.get('count')} {p.get('unit')}", p.get("profile"), p.get("kind", "product"))
    if validated != {**p, "kind": p.get("kind", "product")}:  # manifests before 1.3.0 have no kind: product
        raise ValueError("Invalid manifest parameters")
    return value


def make_plan(target: Path, files: dict[str, bytes], previous: dict | None, force: bool) -> list[dict]:
    plan = []
    old_files = previous["files"] if previous else {}
    for name, incoming in files.items():
        path = child(target, name)
        if path.exists() and not path.is_file():
            raise ValueError(f"Expected file at {name}")
        current = path.read_bytes() if path.exists() else None
        old = old_files.get(name)
        if current is None:
            action = "create"
        elif seed_file(name):
            action = "preserve-project"
        elif digest(current, text=True) == digest(incoming, text=True):
            action = "unchanged"
        elif old and digest(current, text=True) == old["sha256"]:
            action = "update"
        else:
            action = "replace-with-backup" if force else "conflict"
        plan.append({"path": name, "action": action, "old": current, "new": incoming})
    # Never silently remove a file dropped by a newer package. Retain and report it.
    for name in sorted(old_files.keys() - files.keys()):
        plan.append({"path": name, "action": "retain-retired", "old": None, "new": None})
    return plan


def restore_pending(target: Path) -> None:
    pending_path = child(target, PENDING)
    if not pending_path.exists():
        raise ValueError("No interrupted installation to recover")
    marker = read_json(pending_path)
    relative = marker.get("backup", "")
    if not re.fullmatch(r"\.devframework/backups/[0-9TZ-]+-[0-9a-f]{32}", relative):
        raise ValueError("Invalid recovery backup location")
    backup = child(target, relative)
    journal = read_json(child(backup, "journal.json"))
    entries = journal.get("files")
    if journal.get("format") != 1 or not isinstance(entries, list) or not entries:
        raise ValueError("Invalid recovery journal")
    prepared = []
    names = set()
    for entry in entries:
        name = entry["path"]
        lowered = name.lower()
        if lowered in names or lowered in (PENDING, ".devframework/install.lock") or lowered.startswith(".devframework/backups/"):
            raise ValueError("Invalid recovery target")
        names.add(lowered)
        path = child(target, name)
        old_hash, new_hash = entry["old_sha256"], entry["new_sha256"]
        if not isinstance(new_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", new_hash):
            raise ValueError("Invalid recovery hash")
        if old_hash is not None and (not isinstance(old_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", old_hash)):
            raise ValueError("Invalid recovery hash")
        saved = child(backup, "files/" + name).read_bytes() if old_hash else None
        if old_hash and digest(saved) != old_hash:
            raise ValueError(f"Backup content changed: {name}")
        current = path.read_bytes() if path.exists() else None
        if (digest(current) if current is not None else None) not in (old_hash, new_hash):
            raise ValueError(f"Recovery would overwrite a later edit: {name}")
        prepared.append((path, saved))
    for path, saved in reversed(prepared):
        if saved is None:
            if path.exists():
                checked_path(path).unlink()
        else:
            atomic_write(path, saved)
    pending_path.unlink()


def apply_plan(target: Path, plan: list[dict], manifest: dict) -> str | None:
    changes = [p for p in plan if p["action"] in ("create", "update", "replace-with-backup")]
    current_manifest = child(target, MANIFEST)
    old_manifest = current_manifest.read_bytes() if current_manifest.exists() else None
    new_manifest = json_bytes(manifest)
    if old_manifest == new_manifest and not changes:
        return None
    changes.append({"path": MANIFEST, "old": old_manifest, "new": new_manifest})
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ") + "-" + uuid.uuid4().hex
    backup_name = ".devframework/backups/" + stamp
    backup = child(target, backup_name)
    # Each backup ignores its own contents, including recovery data, even during first init.
    atomic_write(child(backup, ".gitignore"), b"*\n")
    journal = []
    for item in changes:
        path = child(target, item["path"])
        current = path.read_bytes() if path.exists() else None
        if current != item["old"]:
            raise ValueError(f"File changed after preview: {item['path']}")
        if current is not None:
            atomic_write(child(backup, "files/" + item["path"]), current)
        journal.append({"path": item["path"], "old_sha256": digest(current) if current is not None else None,
                        "new_sha256": digest(item["new"])})
    atomic_write(child(backup, "journal.json"), json_bytes({"format": 1, "files": journal}))
    atomic_write(child(target, PENDING), json_bytes({"backup": backup_name}))
    try:
        for item in changes:
            path = child(target, item["path"])
            current = path.read_bytes() if path.exists() else None
            if current != item["old"]:
                raise ValueError(f"File changed during install: {item['path']}")
            atomic_write(path, item["new"])
            if item["path"].endswith(".sh") and os.name != "nt":
                os.chmod(path, 0o755)  # scripts/run_tests.sh must be runnable as `scripts/run_tests.sh`
    except BaseException:
        # If recovery itself fails, keep marker/backups and require explicit --recover.
        restore_pending(target)
        raise
    child(target, PENDING).unlink()
    return backup_name


def install(target: Path, *, source: Path = PACKAGE, name: str | None = None,
            scale: str | None = None, profile: str | None = None, kind: str | None = None, update: bool = False,
            force: bool = False, dry_run: bool = False, devlog: bool = False) -> dict:
    source, target = checked_path(source), checked_path(target)
    disjoint(source, target)
    if child(target, PENDING).exists():
        raise ValueError("Interrupted installation: review backups and run --recover first")
    previous = load_manifest(target)
    if update and previous is None:
        raise ValueError("No manifest; use init/adoption for a legacy project, not update")
    if previous and not update:
        raise ValueError("Already installed; use --update (or --dry-run --update)")
    old = {**previous["parameters"], "kind": previous["parameters"].get("kind", "product")} if previous else {}
    kind = kind or old.get("kind", "product")
    default_scale = "10000 users" if kind == "product" else "1 user"  # scale is a product decision; tools do not ask
    params = parameters(name or old.get("name", ""),
                        scale or (f"{old['count']} {old['unit']}" if previous else default_scale),
                        profile or old.get("profile", "generic"), kind)
    if previous:
        promoting = KIND_RANK[kind] - KIND_RANK[old["kind"]]
        if promoting < 0:
            raise ValueError(f"A project grows, never shrinks: {old['kind']} cannot become {kind} (documents are never removed)")
        if kind == "product" and promoting and not scale:
            raise ValueError("Promotion to product needs --scale: the target scale is the operator's product decision")
        fixed = ("name", "profile") if kind == "product" and promoting else ("name", "profile", "count", "unit")
        if any(params[k] != old[k] for k in fixed):
            raise ValueError("Update preserves installation parameters; edit project-owned facts separately")
    version = checked_path(source / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Package VERSION must be numeric major.minor.patch")
    if previous and tuple(map(int, version.split("."))) < tuple(map(int, previous["version"].split("."))):
        raise ValueError("Downgrade is not an update; restore reviewed backups instead")
    files = render(source, {**params, "devlog": devlog})
    plan = make_plan(target, files, previous, force)
    conflicts = [p["path"] for p in plan if p["action"] == "conflict"]
    manifest = {"format": 1, "version": version, "parameters": params, "files": {}}
    for item in plan:
        if item["action"] == "retain-retired":
            manifest["files"][item["path"]] = previous["files"][item["path"]]
        else:
            manifest["files"][item["path"]] = {
                "sha256": digest(item["new"], text=True),
                "ownership": "project" if seed_file(item["path"]) else "framework",
            }
    backup = None
    if not dry_run and not conflicts:
        with project_lock(target):
            if load_manifest(target) != previous or child(target, PENDING).exists():
                raise ValueError("Installation changed during planning; inspect and retry")
            backup = apply_plan(target, plan, manifest)
        if devlog and not previous:
            # Devlog is personal working material: for public/unknown repositories the
            # directory is git-ignored from the first minute (see .devframework/DEVLOG.md).
            import devlog as devlog_mod
            local_only, _ = devlog_mod.keep_local(target, {"enabled": True, "dir": "docs/devlog", "commit": False})
            if local_only:
                devlog_mod.ensure_gitignored(target, "docs/devlog")
    return {"version": version, "dry_run": dry_run, "conflicts": conflicts, "backup": backup,
            "files": [{"path": p["path"], "action": p["action"]} for p in plan]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--name")
    parser.add_argument("--scale", help="e.g. '50,000 users'; defaults to 10,000 on init")
    parser.add_argument("--profile", choices=PROFILES)
    parser.add_argument("--kind", choices=KINDS, help="what is being built: product (default), tool, explore; "
                        "with --update it promotes explore → tool → product and never removes documents")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--force", action="store_true", help="replace conflicted framework files WITH backup; never project documents")
    parser.add_argument("--dry-run", action="store_true", help="preview without creating or writing anything")
    parser.add_argument("--recover", action="store_true", help="roll back an interrupted transaction; never overwrite later edits")
    log = parser.add_mutually_exclusive_group()
    log.add_argument("--devlog", action="store_true", help="enable the optional Devlog rule without asking")
    log.add_argument("--no-devlog", action="store_true", help="disable the optional Devlog rule without asking")
    args = parser.parse_args()
    try:
        if args.recover:
            if args.dry_run or args.update or args.force or args.name or args.scale or args.profile or args.kind:
                raise ValueError("--recover cannot be combined with install/update options")
            target = checked_path(args.target)
            disjoint(checked_path(PACKAGE), target)
            if not child(target, PENDING).exists():
                raise ValueError("No interrupted installation to recover")
            with project_lock(target):
                restore_pending(target)
            print("Interrupted installation rolled back; backups retained.")
            return 0
        devlog_on = True if args.devlog else False if (args.no_devlog or args.update or args.dry_run) else ask_devlog()
        result = install(args.target, name=args.name, scale=args.scale, profile=args.profile, kind=args.kind, devlog=devlog_on,
                         update=args.update, force=args.force, dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result["conflicts"]:
            print("CONFLICT: nothing installed. Reconcile existing instructions or preview --force; replacements are backed up.")
            return 2
        print("PREVIEW ONLY" if args.dry_run else "Installed. Run doctor: scaffold is NOT a configured/verified project.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
