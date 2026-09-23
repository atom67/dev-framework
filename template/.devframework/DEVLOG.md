# Devlog — optional rule

**What:** a verbatim record of the dialogue between the operator and the agent that led
to a finalized piece of work, stored as one Markdown file per dialogue. It is the "why"
behind a commit that the diff and the backlog cannot carry.

**When:** at finalization — after `check.py finish` / `commit-check` pass and before (or
together with) the push. Not for every reply: one file per finished dialogue.

**Enabled by:** `.devframework/project.json`

```json
"devlog": {"enabled": true, "dir": "docs/devlog", "commit": false}
```

The installer asks whether to enable it (`--devlog` / `--no-devlog` skip the question).
When disabled nothing is written and no reminder is printed.

## File

- Name: `<YYYY-MM-DD>_<client>-<MODEL>_<CODE>_<CODE>.md` — the dialogue date, the client
  and model that drove the development, and the codes it touched (`FR-###`, `UC-###`,
  `KE-…`, `NFR-###`, `SET-###`, `INV-###`), e.g.
  `2026-09-20_claudecode-OPUS5_FR-005_UC-004_UC-006.md`. If models were switched during
  the dialogue, name the **two models that carried the largest share** of it, joined by
  `+`: `2026-09-20_claudecode-OPUS5+hermes-gpt5.6terra_UC-007.md`. Several dialogues on one
  day = several files; the same agent and code set on the same day = append.
- Header info block: date, agent(s), codes, storage decision, then a table of the commits
  made in that dialogue — hash and a summary of **at most three sentences** each.
- Body: `## Dialogue (verbatim)` — the turns as they happened, `**User:**` /
  `**Assistant:**`, in order, unedited. Tool outputs may be summarized in `[brackets]`.
  Never secrets, tokens, credentials or private data of third parties.

Create the entry (header from git; the body is filled from the host's session log — an agent cannot recall its
own transcript). `--dialogue auto` (default) reads this project's Claude Code session log, `hermes[:<session id>]`
reads Hermes state.db, `<file.jsonl>` a given log, `none` leaves the body to paste. User and assistant text stays
verbatim, tool calls become one `[tools: …]` line, system reminders are dropped and secret-shaped lines redacted.
`--codes` is optional; without it the kind stands in (`TOOL`, `EXPLORE`, `PRODUCT`).

```text
python .devframework/check.py devlog --agent claudecode-OPUS5 --codes FR-005,UC-004 --from-git 2
python .devframework/check.py devlog --agent claudecode-OPUS5 --agent hermes-gpt5.6terra --codes UC-007 --commit 42687dd="Desktop pane added. Fed by cli.exec." --date 2026-09-20
```

`finish` and `commit-check` print a `DEVLOG:` reminder when the rule is enabled and no
entry exists for today. They never fail because of it.

## Public repositories — the important rule

A dialogue log is personal working material. **If the repository is public — or its
visibility cannot be determined — the devlog stays local:** the skeleton command adds
`/<dir>/` to the root `.gitignore` before writing, and the header records the decision.
Committing devlogs requires both `"commit": true` and a *private* repository (checked
through `gh repo view` when the remote is on GitHub; anything else counts as unknown).

## Why it exists

Backlog trims itself, commit messages are short, and known-error entries record the
mechanism, not the conversation that found it. A devlog keeps the operator's actual
words — corrections, scope decisions, rejected options — next to the commits they
produced, so a later session (or another person) can see what was agreed and why
without re-deriving it.
