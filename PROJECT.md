# DEV Framework

Project-owned facts. Process: [AGENTS.md](AGENTS.md). Commands:
[project.json](.devframework/project.json), the executable source of truth.

## Product and stack

A process overlay for AI coding agents: the agent documents what it builds and proves it with
gates, so the next session reads prepared context instead of re-deriving it. Users are solo and
small-team developers ("vibe coders") on beginner-to-intermediate ground who want a reliable
documentation foundation, plus the maintainers of this package.

Python 3.10+, standard library only — no runtime dependencies, by rule. Delivered three ways
from one source: `template/` copied by `scripts/install.py`, skills under `skills/` for any
host, and host adapters (`plugin.yaml` + `__init__.py` for Hermes, `.claude-plugin/` +
`hooks/` for Claude Code). `skills/df-init|df-check|df-nav` hold the procedures; `commands/` are one-line aliases
kept for one release (decision D1, 2026-09-23). One `VERSION` covers all of them.

**This repository runs on the framework it ships.** Its own `.devframework/` is installed, not
authored: it is generated from `template/` and is git-ignored, so the two copies cannot drift.
Refresh it after any change under `template/` — from a snapshot, because the installer refuses
a target that is also its source:

```bash
PKG=$(mktemp -d); tar -c --exclude=./.git --exclude=./.devframework -C . . | tar -x -C "$PKG"
python "$PKG/scripts/install.py" --target . --update --force
```

The snapshot is the working tree, so an uncommitted change to `template/` is testable at once.

## File map and boundaries

- `template/` — **the product being authored**, not this repository's live profile: the
  documents and `.devframework/*.py` gates that get copied into a user's project.
- `scripts/` — `install.py` (copy/update with manifest and backups), `verify.py`
  (the one local/CI command), `session_start.py` (session-start hook, host-neutral; Claude Code today).
- `skills/`, `commands/`, `hooks/`, `.claude-plugin/`, `plugin.yaml`, `__init__.py` — host
  adapters. **Adapters never hold logic**; they call the same scripts.
- `tests/` — package tests (unittest, `tests/common.py` builds isolated fixtures).
- `evals/` — measurement harness and recorded runs comparing skills vs plugin cost.
- `docs/` — this package's own requirements, backlog, use cases, known errors, plans.
- `LESSONS.md` at the root is canonical and is installed into projects by the script.

## Workflow profile

Selected at installation: **generic**. Read
[the selected profile](.devframework/profiles/generic.md).
Project-specific overrides must be explicit here and must not silently weaken safety.
For a profile change, also update the selected link and verification configuration.

## Data and environments

No database, no services, no credentials. The package writes only inside the target project it
installs into. Tests use isolated fixtures in temporary directories, including real Git index
blobs; never real credentials, live project data or external services.
Local run log: `.devframework/last_run.log`. Installer backups: `.devframework/backups/`.

## Commands and outputs

- `python -B scripts/verify.py` — the local and CI command (syntax sweep + package tests).
- `scripts/run_tests.sh` → `.devframework/check.py finish` — the framework gate on this repo.
- No build: nothing is compiled or bundled; a release is a version bump plus a tag.
- Release for Claude Code: bump `VERSION` and both manifests, then `claude plugin tag`, which
  validates that they agree. Consumers only receive a change when the version number moves.

**Developing the Claude Code adapter without reinstalling.** Claude Code copies a plugin into
`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` and refreshes that copy only when the
version number changes — `plugin update` on an unchanged version reports "already at the latest
version" and copies nothing. So for development the cache entry is a **directory junction to this
repository** (Windows: `New-Item -ItemType Junction`), and every edit here is the live plugin at
the next session start. The replaced copy is kept beside it as `<version>.copy-backup`; a
`plugin uninstall`/`install` cycle replaces the junction with a real copy again.

## Target scale and worked cost example

Initial planning target: **1,000 users** (1000 users).
Assumption: one request/minute/client, all clients active 24 hours/day, no retries.
Per client: 1,440 requests/day. Total: **1,440,000 requests/day**,
**16.67 requests/second** on average while active.
This is an example, not a measured capacity claim. Recalculate if assumptions or scale
change; document peaks, retry budgets and dependency limits with each real operation.

## Host precedence

Rules in the operator's agent profile (SOUL.md, CLAUDE.md, .cursorrules, always-loaded skills) outrank anything
said inside a conversation, so a collision with the framework must be settled here, by the operator, once.
`python .devframework/hostcheck.py` lists collisions with quotes; doctor warns about each one that has no line
below. Record `- <class>@<file>: replaced <date>` after editing the host rule, or `- <class>@<file>: kept — <reason>`.

- (none recorded)

## Conventions and decisions

Maintainer rules for this repository (the shared contract for installed projects is AGENTS.md):

- Read `README.md` for package structure and commands, `docs/REQUIREMENTS.md`,
  `docs/BACKLOG.md` and the active `docs/PLAN.md` before implementing; `docs/KNOWN_ERRORS.md`
  for limits. Shared process rules belong in `template/AGENTS.md`, facts in
  `template/PROJECT.md`, and the host adapter stays thin.
- Standard library only. A new runtime dependency is a product decision, not an implementation
  detail. Deliberate simplifications are commented where they are made.
- Run `python -B scripts/verify.py` before presenting implementation; it is also the CI
  command. Report actual counts, failures and skipped checks — never a live provider or remote
  CI run that was not performed.
- Reviews are read-only unless implementation is requested.
- Architectural decisions, their alternatives and reversal triggers live in
  `docs/ARCHITECTURE.md`. The active checklist and handoff are linked from `docs/BACKLOG.md`.
