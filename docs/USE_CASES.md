# Use cases — DEV Framework

**What this is:** how this process package delivers value — not an application runtime.
**Who reads it:** the operator (what installing it buys) and the maintainer (what to
guard). Composition rules for *consumer* catalogues are in
[template/docs/USE_CASES.md](../template/docs/USE_CASES.md); copy blocks in
[USE_CASE_TEMPLATE.md](../template/docs/USE_CASE_TEMPLATE.md).
**Update when:** a package path's trigger, flow or outcome changes.

**Sibling of [ARCHITECTURE.md](ARCHITECTURE.md).**

---

## Setup & settings

| ID | Setting | Where configured | Required / optional | Enables |
|---|---|---|---|---|
| SET-001 | Python 3.10+ on PATH | operator machine | required | UC-001, UC-002, UC-003, UC-004, UC-005, UC-006, UC-007 |
| SET-002 | Git | operator machine | required for finish/commit-check and package verify | UC-006, UC-007 |
| SET-003 | Target directory disjoint from this package | install `-Target` | required | UC-001, UC-002, UC-003, UC-004 |

---

## Modules

### Module: Install and recover

**Value:** a new or existing project receives the process without silent clobber or a half-applied update.
**Components:** `scripts/install.py`, `install.ps1`, `template/.devframework/safety.py`.

#### UC-001 — Preview an install or update

- **Trigger:** Interactive — `install.ps1 -DryRun` or `python scripts/install.py --dry-run`.
- **Actor:** operator or implementing agent.
- **Preconditions:** SET-001, SET-003.
- **Flow:** the plan is printed; no target directory or files are created.
- **Outcome:** the operator sees creates/preserves/conflicts before any write.
- **Test:** covered — `tests/test_install.py`, `tests/test_package.py` preview cases.

#### UC-002 — Seed a project

- **Trigger:** Interactive — install without `-Update`.
- **Actor:** installer.
- **Preconditions:** SET-001, SET-003.
- **Flow:** template files are rendered and written; project-owned docs are seeded once;
  Git is not initialized; no commit, push, build or app launch.
- **Outcome:** the target has AGENTS, PROJECT, docs (including the use-case catalogue and
  copy templates) and `.devframework` checks.
- **Test:** covered — install tests; doctor on a fresh scaffold.

#### UC-003 — Update without overwriting project documents

- **Trigger:** Interactive — install `-Update`.
- **Actor:** installer.
- **Preconditions:** SET-001, SET-003; an existing manifest.
- **Flow:** untouched framework files update; edited framework files conflict and stop the
  whole update; `docs/*`, PROJECT.md and project.json are preserved.
- **Outcome:** later template improvements do not silently rewrite the project's catalogue.
- **Test:** covered — `tests/test_install.py` preserve-project.

#### UC-004 — Recover an interrupted install

- **Trigger:** Interactive — install `-Recover`.
- **Actor:** installer.
- **Preconditions:** SET-001, SET-003; a pending journal.
- **Flow:** hashes in the journal are checked; matching backups restore; a later user edit
  blocks recovery rather than being overwritten.
- **Outcome:** a crash mid-write is recoverable without inventing file contents.
- **Test:** covered — interruption and later-edit refusal tests.

### Module: Verification

**Value:** scaffolding is not mistaken for a tested product, and a green result names what was actually checked.
**Components:** `check.py`, `verification.py`, `test_evidence.py`, `scripts/verify.py`.

#### UC-005 — Doctor: scaffold vs ready

- **Trigger:** Interactive — `python .devframework/check.py doctor`.
- **Actor:** doctor.
- **Preconditions:** SET-001.
- **Flow:** required files, links, requirement IDs and the use-case catalogue contract are
  checked; missing facts keep the project NOT READY.
- **Outcome:** a fresh install cannot be presented as a verified application.
- **Test:** covered — `tests/test_checks.py`.

#### UC-006 — Finish with counted tests

- **Trigger:** Interactive — `python .devframework/check.py finish` after implementation.
- **Actor:** finish runner.
- **Preconditions:** SET-001, SET-002; configured project.json commands.
- **Flow:** reviewed argv commands run; fresh counted evidence is required; source must not
  change during the run; a digest of the verified tree is printed.
- **Outcome:** "done" means tests ran on this snapshot, not that a future commit is clean.
- **Test:** covered — `tests/test_evidence_scope.py`.

#### UC-007 — Commit-check reads the index

- **Trigger:** Interactive — `python .devframework/check.py commit-check` before an
  authorized commit.
- **Actor:** commit-check.
- **Preconditions:** SET-001, SET-002.
- **Flow:** nonignored untracked files, index/worktree mismatch and hidden-change flags
  fail; secret scan reads index blobs and redacts values.
- **Outcome:** a staged defect cannot hide behind a clean working file.
- **Test:** covered — `tests/test_checks.py`, `tests/test_evidence_scope.py`.

### Module: Consumer value catalogue

**Value:** the next project records benefit paths the way Main OS had to learn to.
**Components:** `template/docs/USE_CASES.md`, `USE_CASE_TEMPLATE.md`,
`USE_CASES_SLICE_TEMPLATE.md`, doctor catalogue checks.

#### UC-008 — Write and check a value path

- **Trigger:** Interactive — a capability is added or a path's trigger/flow/outcome changes.
- **Actor:** implementing agent.
- **Preconditions:** SET-001.
- **Flow:** a case is copied from the case template into `docs/USE_CASES.md`; SET Enables
  and Preconditions name existing IDs; doctor expands ranges and requires a Test field and
  a traceability row.
- **Outcome:** unwritten IDs and untested-but-testable paths are visible, not implied.
- **Test:** covered — `test_use_case_*` in `tests/test_checks.py`.

---

## Not functionally verifiable

| Case | Why it is NFV | How it is actually checked | Development constraint to preserve |
|---|---|---|---|
| *(none in this catalogue)* | live provider handoff is FR-010, recorded as blocked in evidence, not numbered here as a shipping path | [pilot evidence](evidence/HANDOFF_2026-08-31.md) | do not report a blocked native session as a pass |

## Traceability

| Case | Trigger | Requirement | Architecture component | Test |
|---|---|---|---|---|
| UC-001 | Interactive | FR-003 | `scripts/install.py` | covered |
| UC-002 | Interactive | FR-001, FR-011 | `scripts/install.py` | covered |
| UC-003 | Interactive | FR-003 | `scripts/install.py` | covered |
| UC-004 | Interactive | FR-003 | `scripts/install.py` | covered |
| UC-005 | Interactive | FR-004, FR-011 | `verification.py` | covered |
| UC-006 | Interactive | FR-007 | `check.py` | covered |
| UC-007 | Interactive | FR-005, FR-007 | `check.py` | covered |
| UC-008 | Interactive | FR-011 | `template/docs/USE_CASES.md` | covered |
