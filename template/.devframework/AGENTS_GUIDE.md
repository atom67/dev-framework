# Provider loading and handoff

The package carries instructions and knowledge in git, not a provider's private memory.
Keep AGENTS.md short enough to load; route task-specific reading rather than importing
every archive. Facts live in PROJECT.md; live work lives in the backlog-linked checklist.

## Entry points

- Codex reads AGENTS.md and applicable overrides along its discovery path. Global/scoped
  overrides and its instruction-size limit can affect the result.
- Cursor Agent supports root and nested AGENTS.md; a duplicate .cursor/rules copy is not
  needed for this simple package. This is not a guarantee for every Cursor feature.
- Claude Code imports AGENTS.md and PROJECT.md through the two lines in CLAUDE.md.
  Backticks/code fences around imports would make them literal instead of imports.

Verified against official documentation on 2026-08-31:
[Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[Cursor](https://cursor.com/docs/rules),
[Claude Code](https://code.claude.com/docs/en/memory#agents-md).
These are loading mechanisms, not guarantees that a model follows every instruction.

## Fresh-session compatibility test (performed by the engineer)

Use a disposable installed repository, not Main OS or the framework source directory.
Configure a tiny sample project and place an agreed decision and next step in its plan.
Start a fresh session without the original chat in each available provider and ask:

> Read the repository instructions. Do not change files or run the app. Identify the
> project, active task, accepted decisions, last verified result, next step, and what you
> are not authorized to do. Cite the local source for each.

Pass: facts match the repo, the agent finds the selected profile and local lessons, does
not depend on private memory, and makes no unsolicited writes/restarts/deployments.
Repeat from a scoped subdirectory if the project uses nested instructions. Inspect the
tool's loaded-source view when available; a model's own claim is not loading evidence.

For a reproducible small example, the framework source includes scripts/handoff_pilot.py.
It prepares a disposable project with a real red/green behaviour test and an unfinished
next step; it never invokes a provider automatically. Keep expected answers outside the
project and out of the prompt. Compare source digests before/after read-only probing.
Expired authentication, denied file access and unavailable CLI are BLOCKED/NOT RUN, never
success. Do not bypass policy, borrow credentials or alter the operator's working app.

Record provider/version, date, commit, configured overrides, observed result and missing
access in the active checklist. Do not mark an unavailable provider as tested. Package
tests verify adapter contents and links only, not a live model/account interaction.
