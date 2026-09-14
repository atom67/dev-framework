# PLAN — DEV Framework 0.2

Started: 2026-08-31. Status: hardening verified locally; native provider pilot blocked by access/policy.
Not committed or published. The earlier 63-test result remains historical evidence, not
acceptance of the additional work below.

## Agreed scope

The operator approved the improvements from the 2026-08-31 review. Deliver a portable
process package, not an application runtime. Keep documentation in English.

- In: neutral project facts, provider entry points, handoff, opt-in project profiles;
  installed lessons and five reliability patterns; corrected testing/acceptance rules;
  numeric cost calculations; safe installation and upgrade with preview and backups;
  minimal stack-independent doctor, staged-secret check, configured finish and CI;
  positive and negative automated tests.
- Out: changing Main OS, application-specific build integrations, universal language
  parsers, production monitoring services, agent-account configuration, deployments,
  commits and pushes before operator acceptance. No fabricated cross-provider smoke test.
- Implementation choice: Python 3.10+ standard library for portable tooling, PowerShell
  wrapper for the existing Windows entry point. No application runtime dependencies.
- Migration: legacy unmanaged files are never silently overwritten. Conflicts stop the
  upgrade before writes; explicit overwrite requires a recoverable backup.

## Portions

### 1. Rules and context

- [x] Neutral PROJECT.md; AGENTS routing; Claude import; documented provider smoke test.
- [x] Personal-desktop and service profiles; review/build/run/deploy authority separated.
- [x] Risk-based tests, isolated fixtures, accurate acceptance and release procedures.
- [x] Handoff in the active checklist, no second backlog; no invented schema version.

Acceptance: document checks and entry-point tests; no copied provider-specific facts.

### 2. Installed knowledge

- [x] Install LESSONS.md from one canonical source.
- [x] Five pattern recipes: outbox, configuration, crash recovery, stale work, evolution.
- [x] Limits, failure cases, tests and observable data-flow outcomes in each recipe.
- [x] Correct reflection/generation overclaims; record missing outbox lesson.

Acceptance: a generated project has local links to every recipe, without Main OS access.

### 3. Tooling

- [x] Versioned manifest and numeric scale; preserve legacy ScaleTarget syntax safely.
- [x] Preview makes no writes; disjoint roots; reject symlink/junction path escapes.
- [x] Init/update distinguish managed content from project-owned documents.
- [x] Back up replacements, detect conflicts before writing, recover partial failures.
- [x] Serialize installer/recovery writers with an OS-released lock; reject stale previews.
- [x] Doctor: required files, placeholders, links, requirement IDs, explicit readiness.
- [x] Staged secrets: inspect index blobs, redact values, fail on inspection errors.
- [x] Finish: configured build/tests/checks, fail on missing commands, no push/deploy.
- [x] Local and CI run the same package tests; opt-in consumer CI/hook setup documented.

Acceptance: test empty/existing projects, 5k/10k/50k scale, upgrades, conflicts, backups,
path escapes, planted secrets and working-tree/index mismatch, doctor false-green cases,
and finish command failures. No real user data or external service writes.

### 4. Verification and handoff

- [x] Run the full suite and the PowerShell entry point; inspect diff and generated files.
- [x] Document actual results, limits, migration instructions and known errors.
- [x] Prepare acceptance evidence; changes remain uncommitted and unpushed.
- [ ] Operator acceptance (external decision; not engineering work).
- [ ] After authorization: commit/push and observe hosted CI. Not performed in this task.

## Handoff

- Baseline: main, d3d63d2. Started from a clean working tree.
- Current portion: portions 5-7 verified; portion 8 fixture verified, native handoff blocked.
- Verification: first full run, 53 tests passed in 92.480s on Windows, Python 3.11.15,
  PowerShell 7.6.4. Includes actual child-process crash and wrapper preview. No skips.
- Final verification: install.ps1 -SelfTest, 63 tests passed in 104.561s, zero failures,
  errors or skips. 10 Python files parsed. Includes actual wrapper install/update,
  hardlink/junction rejection, post-crash edit protection and staged/worktree mismatch.
- Additional checks: git diff --check passes; working-tree text heuristic found 0 suspects;
  maintainer Markdown local-link check found 0 errors. Generated fixture roots cleaned.
- Second-review full run: 79 tests passed in 64.717s, zero failures/errors/skips;
  16 Python files parsed, package worktree scan 60 text files / 211333 bytes / 0 suspects.
  Final wrapper run after documentation updates: install.ps1 -SelfTest, 79 tests passed
  in 56.643s, zero failures/errors/skips; 61 text files / 219711 bytes / 0 suspects.
  This result was recorded afterwards; no implementation changed after that run.
- Live attempts: Codex 0.151.0-alpha.7.1 loaded AGENTS but file reads were denied by policy;
  Claude 2.1.177 returned expired OAuth 401, before a model turn. Neither is a handoff pass.
  Fixture old behaviour: 2 failures / 3 tests; fixed: 3 passed, zero skips. Its source
  digest was unchanged by provider attempts. [Evidence](evidence/HANDOFF_2026-08-31.md).
- Not run: a successful native cross-provider handoff, Cursor model session, hosted CI or local Linux execution.
  The workflow is configured for Windows/Linux and Python 3.10/3.13, not claimed executed.
- Next: restore provider access without weakening policy, rerun the native pilot, then
  present complete evidence for acceptance. No automatic commit/push.
  Main OS was not modified; no production app was built, stopped or relaunched.
- External input: Claude reauthentication requested; a permitted native Codex read path
  is also needed. These are access prerequisites, not user-assigned engineering tests.

## Second-review scope — authorized 2026-08-31

Independent reproduction: finish accepted zero discovered tests and a staged defect fixed
only in the working tree. The secret heuristic missed unquoted dotenv/YAML and C# verbatim
literals, and flagged harmless OAuth metadata. Source comparison found missing entry-point
invariants and performance lessons. No Main OS mutations or automatic commits/pushes.

### 5. Verifiable finish, worktree vs commit

- [x] Require fresh machine-readable test results, positive executed count, zero failures,
  and an explicit skip budget; provide a zero-test-safe unittest adapter.
- [x] Finish verifies tracked + nonignored untracked working files, names a content digest,
  rejects changes during checking; commit-check additionally requires index/worktree parity.
- [x] Keep staged-only scanning separate; no Git mutations or implicit staging.
- [x] Reproduce zero tests, stale/missing/malformed reports, all-skipped, source changes,
  index mismatch and pre-acceptance new-project workflow in isolated fixtures.

### 6. Secret checks

- [x] Cover quoted/unquoted dotenv/YAML and C# verbatim literals; reject harmless metadata
  only when its value independently matches a credential shape; no blanket file exemptions.
- [x] Redaction, positive/negative format cases and actual index/worktree integration tests.
- [x] Apply worktree source scanning to this package's own verification as well as consumers.

### 7. Knowledge completeness

- [x] Inventory the reviewed source corpus with stable source IDs/fingerprints, lesson →
  rule/recipe → regression/observable outcome, and explicit exclusions/unreviewed material.
- [x] Add entry-point invariant and bounded performance recipes, plus sync semantics where
  the source comparison identifies a separate failure class. Avoid universal WPF bans.
- [x] Validate installed map links/IDs and add an invariant register to project documents.

### 8. Real handoff pilot and final verification

- [x] Build a disposable tiny project with an actual tested behaviour change, durable
  decision, known defect and pending next step; preserve a reproducible pilot fixture.
- [ ] Run fresh provider sessions with no prior chat against only synthetic project data;
  compare recovered decisions, evidence, pending work and authority against expected facts.
  Sessions are test subjects, not delegated implementation. No real-project access requested.
- [x] Record provider/version, outputs and limitations; unavailable access is not a pass.
- [x] Full local suite and wrapper; update requirements, backlog, known errors and handoff.

Acceptance: demonstrated failures turn into failing gates; useful positive cases pass;
source coverage is bounded and auditable; live pilot evidence is distinguished from static
tests. Hosted CI remains pending authorized push, not silently marked executed.
