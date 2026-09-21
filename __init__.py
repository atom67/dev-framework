"""Hermes plugin: DEV Framework as three tools plus two bundled skills.

The framework itself stays what it is (template/, scripts/install.py, .devframework/*.py — standard
library only). This file only removes what cost the agent tokens in the baseline runs: reading the
package to learn it, multi-step installs, verbose gate output, and Hermes' verify-on-stop not
recognising the finish gate as evidence.
"""
from __future__ import annotations

import logging
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
PACKAGE = Path(__file__).resolve().parent
MAX_LINES, MAX_CHARS = 40, 3500


def _path(raw: str) -> Path:
    """Accept D:/x, D:\\x and git-bash /d/x alike (the baseline lost turns to this on Windows)."""
    text = (raw or "").strip().strip('"').strip("'")
    if os.name == "nt":
        match = re.fullmatch(r"/([A-Za-z])/(.*)", text)
        if match:
            text = f"{match[1].upper()}:/{match[2]}"
    path = Path(text).expanduser()
    return path if path.is_absolute() else Path.cwd() / path


def _trim(text: str, lines: int = MAX_LINES, chars: int = MAX_CHARS) -> str:
    rows = text.strip().splitlines()
    if len(rows) > lines:
        rows = rows[: lines // 2] + [f"… ({len(rows) - lines} lines omitted)"] + rows[-lines // 2:]
    out = "\n".join(rows)
    return out if len(out) <= chars else out[: chars // 2] + "\n… (truncated)\n" + out[-chars // 2:]


def _run(argv: list[str], cwd: Path, timeout: int) -> tuple[int, str]:
    try:
        run = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=timeout, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"
    except OSError as error:
        return 127, f"could not start: {error}"
    return run.returncode, (run.stdout + ("\n" + run.stderr if run.stderr.strip() else "")).strip()


def _framework_dir(target: Path) -> Path | None:
    devframework = target / ".devframework"
    return devframework if (devframework / "check.py").is_file() else None


# ---------------------------------------------------------------- tools

def df_init(args: dict, **kwargs) -> str:
    target = _path(args.get("target", ""))
    name = (args.get("name") or target.name).strip()
    scale = (args.get("scale") or "").strip()
    if not scale and not args.get("update"):
        return "ERROR: scale is required (integer + unit, e.g. \"100 users\"); it is a product decision — ask the operator."
    profile = args.get("profile") or "generic"
    argv = [sys.executable, "-B", str(PACKAGE / "scripts" / "install.py"), "--target", str(target), "--name", name,
            "--scale", scale, "--profile", profile, "--devlog" if args.get("devlog") else "--no-devlog"]
    if args.get("update"):
        argv = [sys.executable, "-B", str(PACKAGE / "scripts" / "install.py"), "--target", str(target), "--update"]
    code, out = _run(argv, PACKAGE, 120)
    if code:
        return f"INIT FAILED (exit {code}):\n{_trim(out, 25)}"
    summary = [line for line in out.splitlines() if line.strip() and line[0] not in ' \t{}"'][-6:]  # skip the JSON plan
    return ("INIT OK: " + str(target) + "\n" + "\n".join(summary) +
            "\nNext: fill PROJECT.md and docs/ARCHITECTURE.md (no TODO(project) left), set the test command in "
            ".devframework/project.json, write docs/USE_CASES.md, then df_check doctor. Contract: df_nav contract.")


def df_check(args: dict, **kwargs) -> str:
    target = _path(args.get("target", ""))
    mode = (args.get("mode") or "doctor").strip()
    devframework = _framework_dir(target)
    if devframework is None:
        return f"ERROR: {target} has no .devframework/check.py — run df_init first."
    if mode not in ("doctor", "finish", "commit-check", "selftest", "secrets"):
        return "ERROR: mode must be doctor | finish | commit-check | selftest | secrets"
    extra = {"secrets": ["--worktree"], "doctor": ["--structural"] if args.get("structural") else []}.get(mode, [])
    if args.get("verbose") and mode in ("finish", "commit-check"):
        extra = ["--verbose"]
    code, out = _run([sys.executable, "-B", str(devframework / "check.py"), mode, *extra], target, 900)
    if mode in ("finish", "commit-check"):
        _record_evidence(target, code, out, kwargs)
    verdict = "PASS" if code == 0 else ("NOT READY" if code == 2 else "FAIL")
    return f"{mode} {verdict} (exit {code})\n{_trim(out)}"


def _record_evidence(target: Path, code: int, out: str, kwargs: dict) -> None:
    """Let Hermes' verify-on-stop guard see the finish gate as verification evidence (best effort)."""
    try:
        from agent.verification_evidence import record_terminal_result  # host module; absent outside Hermes

        record_terminal_result(command="scripts/run_tests.sh", cwd=str(target),
                               session_id=kwargs.get("session_id") or kwargs.get("task_id") or "default",
                               exit_code=code, output=out)
    except Exception as error:  # never fail the gate over bookkeeping
        logger.debug("verification evidence not recorded: %s", error)


def df_nav(args: dict, **kwargs) -> str:
    target = _path(args.get("target", ""))
    command = (args.get("command") or "brief").strip()
    devframework = _framework_dir(target)
    if devframework is None or not (devframework / "navigate.py").is_file():
        return f"ERROR: {target} has no .devframework/navigate.py — run df_init (or df_init with update=true on an older install)."
    if command not in ("brief", "find", "index", "contract", "checklist", "handoff"):
        return "ERROR: command must be brief | find | index | contract | checklist | handoff"
    extra = shlex.split(args.get("args") or "", posix=True)
    code, out = _run([sys.executable, "-B", str(devframework / "navigate.py"), command, *extra], target, 60)
    return _trim(out, 60, 6000) if code == 0 else f"{command} failed (exit {code}):\n{_trim(out, 20)}"


SCHEMAS = {
    "df_init": {
        "name": "df_init",
        "description": (
            "Install the DEV Framework into a repository in one call (preview + install + summary): project context "
            "files, PROJECT.md, docs/ (use cases, known errors, backlog, requirements, architecture …) and the "
            ".devframework gates. Never overwrites existing project documents; refuses on a foreign context file. "
            "Use for a new project or before df-catch-up on an existing one. Then fill PROJECT.md/ARCHITECTURE.md, "
            "project.json test command and docs/USE_CASES.md, and run df_check doctor."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Repository directory (absolute path; D:/x, D:\\x or /d/x)."},
                "name": {"type": "string", "description": "Product name as the operator calls it (defaults to the directory name)."},
                "scale": {"type": "string", "description": "Scale target: integer + unit, e.g. '100 users' or '1 user (personal tool)'. A product decision — ask if unknown."},
                "profile": {"type": "string", "enum": ["generic", "personal-desktop", "service"], "description": "Workflow profile (default generic)."},
                "devlog": {"type": "boolean", "description": "Enable the optional verbatim devlog rule (default false)."},
                "update": {"type": "boolean", "description": "Update an existing installation to this framework version instead of installing."},
            },
            "required": ["target"],
        },
    },
    "df_check": {
        "name": "df_check",
        "description": (
            "Run a DEV Framework gate in a repository and return its verdict with a short output. Modes: doctor "
            "(structure + configuration; READY / NOT READY with the setup items), finish (doctor + secret heuristic + "
            "build + counted tests + checks — the evidence that work is done; needs git), commit-check (finish + "
            "index/worktree parity, before an authorized commit), selftest (proves the gates fire on planted defects, "
            "in a temp copy), secrets (worktree secret heuristic). Child output is logged to .devframework/last_run.log; "
            "only counts and the first failure are returned. finish is also recorded as verification evidence for Hermes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Repository directory."},
                "mode": {"type": "string", "enum": ["doctor", "finish", "commit-check", "selftest", "secrets"], "description": "Which gate (default doctor)."},
                "structural": {"type": "boolean", "description": "doctor only: accept a fresh scaffold as structurally valid."},
                "verbose": {"type": "boolean", "description": "finish/commit-check: stream the full child output instead of logging it."},
            },
            "required": ["target", "mode"],
        },
    },
    "df_nav": {
        "name": "df_nav",
        "description": (
            "Navigate a DEV Framework project without reading whole documents. brief: one-screen session start "
            "(doctor state, git, use cases without tests, open known errors, active checklist + last handoff) — call it "
            "first in every session on a framework project. find <UC-|KE-|FR- id or keyword>: returns one block or a hit "
            "list. index: regenerate docs/INDEX.md. contract: what doctor/finish demand. checklist "
            "new|add|tick|show|archive <slug> [text|n]: multi-iteration plans in docs/<slug>.md. handoff <slug> "
            "--note '...': write the handoff block for the next session."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Repository directory."},
                "command": {"type": "string", "enum": ["brief", "find", "index", "contract", "checklist", "handoff"]},
                "args": {"type": "string", "description": "Arguments for find/checklist/handoff, shell-style, e.g. 'UC-007', 'new v1 \"strict flag\"', 'tick v1 2', 'v1 --note \"parser done\"'."},
            },
            "required": ["target", "command"],
        },
    },
}
HANDLERS = {"df_init": df_init, "df_check": df_check, "df_nav": df_nav}


# ---------------------------------------------------------------- CLI: hermes devframework <init|check|nav>

def _cli_setup(parser) -> None:
    sub = parser.add_subparsers(dest="df_command", required=True)
    init = sub.add_parser("init", help="install the framework into a repository")
    init.add_argument("target"); init.add_argument("--name"); init.add_argument("--scale")
    init.add_argument("--profile", default="generic"); init.add_argument("--devlog", action="store_true")
    init.add_argument("--update", action="store_true")
    check = sub.add_parser("check", help="doctor | finish | commit-check | selftest | secrets")
    check.add_argument("target"); check.add_argument("mode", nargs="?", default="doctor"); check.add_argument("--verbose", action="store_true")
    nav = sub.add_parser("nav", help="brief | find | index | contract | checklist | handoff")
    nav.add_argument("target"); nav.add_argument("command"); nav.add_argument("rest", nargs="*")


def _cli_handler(args) -> int:
    if args.df_command == "init":
        print(df_init({"target": args.target, "name": args.name, "scale": args.scale, "profile": args.profile,
                       "devlog": args.devlog, "update": args.update}))
    elif args.df_command == "check":
        print(df_check({"target": args.target, "mode": args.mode, "verbose": args.verbose}))
    else:
        print(df_nav({"target": args.target, "command": args.command, "args": " ".join(shlex.quote(r) for r in args.rest)}))
    return 0


def register(ctx) -> None:
    for name, schema in SCHEMAS.items():
        ctx.register_tool(name=name, toolset="dev_framework", schema=schema, handler=HANDLERS[name],
                          description=schema["description"][:120], emoji="📐")
    for skill in ("df-import", "df-catch-up"):
        path = PACKAGE / "skills" / skill / "SKILL.md"
        if path.is_file():
            try:
                ctx.register_skill(name=skill, path=path, description=f"DEV Framework: {skill}")
            except Exception as error:  # older hosts without plugin skills still get the tools
                logger.debug("skill %s not registered: %s", skill, error)
    try:
        ctx.register_cli_command(name="devframework", help="DEV Framework: init | check | nav",
                                 setup_fn=_cli_setup, handler_fn=_cli_handler,
                                 description="Install, gate and navigate a DEV Framework project from the shell.")
    except Exception as error:
        logger.debug("cli command not registered: %s", error)
