# DEV Framework evaluation — Scenario S1: new Python module from scratch (variant: {{VARIANT}})

You are being timed and every tool call is counted. Work autonomously: do not ask for permission to run the steps below, and do not ask questions whose answer is in this message or in the files. Ask only if something is genuinely undecidable.

## Step 0 — Install DEV Framework
<<INSTALL>>

## Step 1 — Task
Create a new project in `{{WORK}}/wordfreq/` using the `{{SKILL_IMPORT}}` skill. Facts you would otherwise ask for: project name **wordfreq**, scale target **100 users**, profile **generic**, devlog **off**, Python **3.10+**, **standard library only**, Git: initialise a repository and commit at the end.

Product: a command-line tool `python -m wordfreq FILE [FILE ...] [--top N] [--stopwords FILE]` that prints the N (default 10) most frequent words across the given text files as `word count`, one per line, most frequent first, ties broken alphabetically. Words are case-insensitive runs of letters and apostrophes (`don't` is one word). `--stopwords FILE` is a text file with one word per line to ignore. A missing input file must produce a clear error message and exit code 2, not a traceback.

Done means, in this order: the framework's project documents are filled from this description (no `TODO(project)` or template placeholders left); `docs/USE_CASES.md` lists every user-visible capability above with its `Test:` field pointing at a real test; unit tests exist and pass (isolated: temp files only); `python .devframework/check.py doctor` passes; `python .devframework/check.py finish` passes; work is committed.

## Step 2 — Final report (your last message: the filled block under a `🛠️ Tech` heading, then a `💬 Message` block in plain language ending with what the operator must do next)

```
## DEV Framework eval report — Scenario S1 (variant: {{VARIANT}})
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
