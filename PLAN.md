# PLAN — build the DEV Framework package

One-time program of work: extract the reusable process layer from Main OS into an
installable package, so the next project does not repeat the refactor that produced it.

Archive this file to `docs/archive/` when every portion is accepted. It is the single
living document for this work; nothing else tracks it.

**Scope decided with the operator (2026-08-31):**

- Carry over: rules, document skeletons, knowledge base. English.
- Do NOT carry over: the Python check pipelines (`periodic_cost.py`, `secrets.py`,
  `doc_drift.py`, `finish.py`, `attribution/build.py`). The *protocol* they enforce is
  written down; the implementations stay in Main OS as the reference to port from later.
- Form: `template/` plus `install.ps1` that lays it into a target repository.
- Home: local repo `D:\DEV\DEV-Framework`, mirrored to a **private** GitHub repository.

## Portions

One portion = one thing the operator can accept or send back.

### 1. Repository skeleton — DONE
- [x] `git init`, `.gitignore`, this checklist.

### 2. The protocol — `template/AGENTS.md`
- [x] Session-start reading order.
- [x] Working agreement: branch discipline, build/run discipline, commit format.
- [x] Planning rules: big task becomes a checklist file before the first code edit.
- [x] Acceptance is presented to a product owner, not to a developer.
- [x] Verify before claiming; verify the verification with a planted defect.
- [x] Execution cost rule.
- [x] Secrets rule.
- [x] Documentation maintenance rules — stated **once**, here only.
- [x] Crash-resilience; file-size and modularity limits.

### 3. Project facts — `template/CLAUDE.md`
- [x] Thin file: pointer to AGENTS.md plus stack/layout/build placeholders.
- [x] Explicit prohibition on duplicating process rules into it.

### 4. Document skeletons — `template/docs/*`
- [x] REQUIREMENTS, ARCHITECTURE, BACKLOG, KNOWN_ERRORS, REGRESSION_TEST, PLAN, RELEASE.
- [x] Each carries its own purpose header, ID format, and one worked example.

### 5. Knowledge base — `LESSONS.md`
- [x] Every rule traced to the incident that produced it, with the real numbers.
- [x] What was deliberately not ported, and where to find it.

### 6. Installer — `install.ps1`
- [x] Copy into a target repo, substitute the project name, never clobber existing files.
- [x] One runnable check: `-SelfTest` that fails if that logic breaks.

### 7. Publish
- [ ] `README.md`: what this is, how to install, what is inside.
- [ ] Commit, create the private GitHub repository, push.
