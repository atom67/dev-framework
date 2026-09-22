---
description: Install the DEV Framework into a repository (documents + verification gates), then fill its project facts
argument-hint: <target-repo-path> [project name] [scale, e.g. "100 users"]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

Install the DEV Framework into the repository named in `$ARGUMENTS` (default: the current project).

1. Facts you need first: the product name as the operator calls it, and the **scale target** (integer + unit,
   e.g. `100 users`) — a product decision. Ask if it was not given; never invent it.
2. Preview, then install:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/install.py" --target <TARGET> --name "<NAME>" --scale "<SCALE>" --profile generic --no-devlog --dry-run
   python "${CLAUDE_PLUGIN_ROOT}/scripts/install.py" --target <TARGET> --name "<NAME>" --scale "<SCALE>" --profile generic --no-devlog
   ```

   It never overwrites existing project documents and refuses on a foreign `AGENTS.md`/`CLAUDE.md`.
   On an already-installed project use `--update` instead of the name/scale flags.
3. `python <TARGET>/.devframework/navigate.py contract` — exactly what doctor and finish will demand.
4. Fill from the code (read it) and from the operator (ask): `PROJECT.md` and `docs/ARCHITECTURE.md` until no
   `TODO(project):` remains; `.devframework/project.json` with a real test argv that writes counted evidence
   (`["{python}", "-B", ".devframework/run_unittest.py", "--start", "tests", "--jobs", "auto"]` for Python;
   `--jobs auto` runs one process per test module and is the difference between a 40-second gate and a
   7-minute one — drop it only if the modules share state outside their own fixtures); `docs/USE_CASES.md`
   with one `#### UC-### — title` per user-visible capability, each with a `**Test:**` field and a traceability row.
5. `/dev-framework:check <TARGET> hostcheck` — host rules that fight the framework. Show the operator the list
   **once**, one decision per line; their decision, never yours.
6. `/dev-framework:check <TARGET> doctor` → fix what it lists → `/dev-framework:check <TARGET> finish` once tests exist.
7. Report in numbers: files created, cases written (covered / gap), doctor and finish results, what is still unconfirmed.

Deeper procedure and the incidents behind the rules: skill `dev-framework:df-import`.
