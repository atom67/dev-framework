---
name: df-import
description: Install the DEV Framework into a repository (new or existing) with the df_init tool, fill the project facts from the code, and prove readiness with df_check. Use when the operator says "import the framework", "install DEV Framework", "set up the project docs", "внедри фреймворк", "поставь правила в проект".
version: 0.4.0
---

# df-import — put a repository under the DEV Framework

Outcome: the repository has the project context files, `PROJECT.md`, the `docs/` set (use-case catalogue,
known errors, backlog, requirements, architecture …) and the verification gates, and `df_check doctor`
says READY. The documents are true, not decoration: no `TODO(project)` left, facts taken from the code.

## Procedure (tools first, files second)

1. **Facts you need before writing anything**: project name (what the operator calls it), scale target
   (integer + unit, e.g. `100 users` — a product decision: ask if it was not given), profile
   (`generic` unless told otherwise). Never invent the scale.
2. `df_init(target, name, scale)` — one call: previews, installs, reports the files laid in. On an existing
   repository it refuses to overwrite a foreign context file; read the message and decide with the operator.
3. `df_nav(target, "contract")` once — it tells you exactly what doctor and finish will demand.
4. Fill, from the code (read it) and from the operator (ask):
   `PROJECT.md` (stack, file map, data, environments, commands) and `docs/ARCHITECTURE.md` — until no
   `TODO(project):` remains; `.devframework/project.json` — real build/test commands in argv form
   (`{python}` expands to the interpreter; `.devframework/run_unittest.py --start tests` is the built-in
   counted runner). Replace the example requirement and the example use cases with the agreed product;
   every user-visible capability is a `#### UC-### — title` with a `**Test:**` field and a traceability row.
5. `df_check(target, "doctor")` → fix what it lists → `df_check(target, "finish")` once tests exist.
   `finish` needs a Git repository; initialise one if the operator agreed.
6. Report in numbers: files created, cases written (covered / gap), doctor and finish results, what remains
   unconfirmed for the operator.

## Rules that survive shortcuts

- A statement in a document is either read out of the code or marked unconfirmed for the operator.
- Do not write a full catalogue from imagination on import; write what the product agreed to do.
- Tests use temporary fixtures, never a real profile, database, token or live service.
- Independent steps run in parallel subagents when the host provides them; work beyond one iteration gets one checklist (`df_nav checklist`) copied at the end of every reply. Reply shape, exact headings: `🛠️ Tech` then `💬 Message` ending with the explicit ask; if your profile wants its own plain-language footer, the Message is that footer (one block, not two).
- Your host profile decides tone; this skill decides only the project's gates.

Why every rule exists, the incidents behind them and the long form of this procedure:
`references/full.md` (read on first use of the framework, not on every project).
