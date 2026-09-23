---
description: Install the DEV Framework into a repository (documents + verification gates), then fill its project facts
argument-hint: <target-repo-path> [project name] [scale, e.g. "100 users"]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

Install the DEV Framework into the repository named in `$ARGUMENTS` (default: the current project).

1. Ask the operator, **one question per message**, only what was not given (do not announce a total: how many
   apply depends on the kind):
   1. the name, as the operator calls it;
   2. the **kind** — what is being built. Recommend one from what you see; the operator decides:
      - `product`: software with users that will grow — the full document set, tests with counted evidence;
      - `tool`: a script or utility for one job — PROJECT.md, a user guide in `docs/GUIDE.html`, and proof by
        running the tool on examples (`smoke` in project.json) instead of a regression suite; no backlog;
      - `explore`: not yet known what it becomes — the minimum, tests optional; promote it later without losing
        anything (`--update --kind tool|product`);
   3. only for a product: the **scale target** (integer + unit, e.g. `100 users`) — a product decision, never invent it;
   4. **devlog**: keep a verbatim log of every finished dialogue? Default no; in a public repository it stays local
      and git-ignored. Pass the answer as `--devlog` or `--no-devlog` — never decide it for the operator.
2. Preview, then install (`--scale` only for a product):

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/install.py" --target <TARGET> --name "<NAME>" --kind <KIND> [--scale "<SCALE>"] --profile generic --devlog|--no-devlog --dry-run
   python "${CLAUDE_PLUGIN_ROOT}/scripts/install.py" --target <TARGET> --name "<NAME>" --kind <KIND> [--scale "<SCALE>"] --profile generic --devlog|--no-devlog
   ```

   It never overwrites existing project documents and refuses on a foreign `AGENTS.md`/`CLAUDE.md`.
   On an already-installed project use `--update` instead of the name/scale flags. **Promotion** (the operator's
   call): `--update --kind tool`, or `--update --kind product --scale "<SCALE>"` — adds the missing documents,
   overwrites nothing, never goes back down.
3. `python <TARGET>/.devframework/navigate.py contract` — exactly what doctor and finish will demand.
4. Fill from the code (read it) and from the operator (ask) until doctor lists nothing. **A tool:** `PROJECT.md`,
   `docs/GUIDE.html` (the user's instruction: run, examples, errors, limits) and 1-3 `smoke` examples in
   `.devframework/project.json` — `{"name", "run": ["{python}", "tool.py", "arg"], "expect_contains": "..."}` or
   `"expect_stdout": "<file>"`; then skip to step 5. **An exploration:** the intent and open questions in `PROJECT.md`;
   then step 5. **A product:** `PROJECT.md` and `docs/ARCHITECTURE.md` until no
   `TODO(project):` remains; `.devframework/project.json` with a real test argv that writes counted evidence
   (`["{python}", "-B", ".devframework/run_unittest.py", "--start", "tests", "--jobs", "auto"]` for Python;
   `--jobs auto` runs one process per test module and is the difference between a 40-second gate and a
   7-minute one — drop it only if the modules share state outside their own fixtures); `docs/USE_CASES.md`
   with one `#### UC-### — title` per user-visible capability, each with a `**Test:**` field and a traceability row.
   `run_unittest.py` finds unittest-style tests (TestCase classes) only. For plain pytest functions use
   `["{python}", "-B", ".devframework/run_pytest.py"]` (pytest must be installed; extra args go to pytest, e.g. `-n auto`).
   **Product facts the code cannot show** — who the users are, what problem it solves — come from the operator:
   ask, or write them as `UNCONFIRMED: <your inference>`. Never present an inference from code as a fact.
5. `/dev-framework:check <TARGET> hostcheck` — host rules that fight the framework. Show the operator the list
   **once**, one decision per line; their decision, never yours.
6. `/dev-framework:check <TARGET> doctor` → fix what it lists → `/dev-framework:check <TARGET> finish` once tests exist.
7. Report in numbers: files created, cases written (covered / gap), doctor and finish results, what is still unconfirmed.

Deeper procedure and the incidents behind the rules: skill `dev-framework:df-import`.
