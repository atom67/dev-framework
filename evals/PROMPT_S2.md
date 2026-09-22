# DEV Framework evaluation — Scenario S2: migrate scattered-but-complete documentation (variant: {{VARIANT}})

You are being timed and every tool call is counted. Work autonomously: do not ask for permission to run the steps below. Everything you need is in the files; a question to me should not be necessary (if you do ask, it is counted) — with one exception: host-rule conflicts reported by the framework are the operator's decision, ask about them in one message.

## Step 0 — Install DEV Framework
<<INSTALL>>

## Step 1 — Task
The repository at `{{WORK}}/notes-cli/` was built without the framework. Its documentation is complete but scattered across `README.md`, `NOTES_dev.txt`, `docs/ideas.md`, `TODO.md` and `tests/README.md`. Bring it under DEV Framework with the `{{SKILL_CATCHUP}}` skill (install the framework into the repo first; project name **notes**, scale target **1 user (personal tool)**, profile **generic**, devlog **off**; initialise Git and commit at the end).

Rules: every statement in the new documents is either read from the code/tests or taken from the existing notes — cite which; anything else goes to the "unconfirmed" list, not into the documents. **Nothing from the old files may be lost**: fold their content into the framework documents, then delete or replace the old files with a one-line pointer. Map every existing test to a `Test:` field in `docs/USE_CASES.md`; list capabilities that have no test as such. Do **not** change the behaviour of the code; the existing tests must still pass. Finish with `python .devframework/check.py doctor` passing.

## Step 2 — Final report (your last message: the filled block under a `🛠️ Tech` heading, then a `💬 Message` block in plain language ending with what the operator must do next)

```
## DEV Framework eval report — Scenario S2 (variant: {{VARIANT}})
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
