# Maintaining DEV Framework

Read README.md for package structure/commands and docs/REQUIREMENTS.md, docs/BACKLOG.md
and the active docs/PLAN.md before implementation. Read docs/KNOWN_ERRORS.md for limits.
The template directory is the product being authored, not this repository's live profile.

- Preserve unrelated work. Use the current branch; do not create/switch branches silently.
- Reviews are read-only unless implementation is requested. Do not run or alter Main OS.
- Multi-step changes have a checklist before code edits; update its evidence and Handoff.
  Prefer larger iterations that close with tests. Copy the live checklist at the end of
  every operator reply, striking through completed items, until it is empty.
  Independent work runs in parallel subagents when the host provides them.
- Keep shared process rules in template/AGENTS.md, facts in template/PROJECT.md, and the
  provider adapter thin. LESSONS.md at the root is canonical and installed by the script.
- Test risky behaviour with isolated fixtures, negative cases and actual Git index blobs.
  No real credentials, live project data or external services as fixtures.
- Run `python -B scripts/verify.py` before presenting implementation. It is also the CI
  command; no application exe is built. Report actual counts, failures and skipped checks.
- Update relevant docs and regression evidence with changes. Never claim a live provider
  or remote CI test was run when only static configuration was checked.
- No commits, pushes, deploys or runtime restarts before explicit operator acceptance/
  authorization. Present results and product decisions, not debugging chores.
