# DEV Framework evaluation — follow-up session (variant: {{VARIANT}})

This is a **new session** on a project that already uses DEV Framework. You are being timed and every tool call is counted. Start by reading the project's own documents (they tell you how to work); do not re-derive the project from the code if the documents answer the question. Do not ask me anything that the documents or code answer.

## Task
Project: `{{WORK}}`. Add the feature below the way the project's process prescribes (use case → test → code → checks → commit):

- If the project is **wordfreq**: add `--min-length N` — ignore words shorter than N letters (default 1).
- If the project is **notes**: add the `edit ID TEXT` command listed in the roadmap — replaces the note's text, keeps id/tags/created; unknown id → message on stderr, exit 1.
- If the project is **ledger**: add `balance --all` — print every month present in the file, one block per month, oldest first.

Done: use case added with its `Test:` field, tests pass, `python .devframework/check.py doctor` and `finish` pass, committed.

## Step 2 — Final report (your last message: the filled block under a `🛠️ Tech` heading, then a `💬 Message` block in plain language ending with what the operator must do next)

```
## DEV Framework eval report — Scenario FOLLOWUP (variant: {{VARIANT}})
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
