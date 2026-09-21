# DEV Framework evaluation — Scenario S3: migrate documentation with gaps (variant: {{VARIANT}})

You are being timed and every tool call is counted. Work autonomously for everything that the code, tests and existing notes decide. **Where the intended behaviour for the end user cannot be determined from them, ask me** — one question per message, state the options you see and what the code does today, then wait for my answer before writing that use case. Do not guess, and do not silently record the current code behaviour as the intent. Do not ask about things the code or tests already answer.

## Step 0 — Install DEV Framework
<<INSTALL>>

## Step 1 — Task
The repository at `{{WORK}}/ledger/` was built without the framework and its documentation has gaps. Bring it under DEV Framework with the `{{SKILL_CATCHUP}}` skill (install the framework into the repo first; project name **ledger**, scale target **1 user (personal tool)**, profile **generic**, devlog **off**; initialise Git and commit at the end).

Rules: as in a normal catch-up — every statement is read from code/tests/notes or confirmed by me; nothing from `README.md` may be lost. Where my answer contradicts what the code does today, do **not** change the code in this run: record the intended behaviour in `docs/USE_CASES.md` and register the difference as a defect in `docs/KNOWN_ERRORS.md` / `docs/BACKLOG.md`. Existing tests must still pass. Finish with `python .devframework/check.py doctor` passing.

## Step 2 — Final report (your last message: the filled block under a `🛠️ Tech` heading, then a `💬 Message` block in plain language ending with what the operator must do next)

```
## DEV Framework eval report — Scenario S3 (variant: {{VARIANT}})
Install: <commands you ran; what failed and how you recovered>
Steps taken: <numbered, one line each>
Questions asked to the user: <N> — <list each question in one line>
Files created / modified: <list>
Tests: <command> — passed <n> / failed <n> / skipped <n>
doctor: PASS|FAIL — <remaining items>     finish: PASS|FAIL|NOT RUN — <why>
Self-estimate: tool calls ≈ <n>, model turns ≈ <n>, wall time ≈ <min> (the user verifies these from the session DB)
Where you lost time / what was unclear in the framework docs: <≤5 bullets>
Unconfirmed statements left for the operator: <list or "none">
Host conflicts found / decided: <n found, n recorded in PROJECT.md ## Host precedence, or "none">
```
