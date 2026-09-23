# DEV Framework architecture

No application database or schema. Package version authority: VERSION. Manifest/config
format is 1; it is independent of the application schema. Python 3.10+ standard library.

## Components

- scripts/install.py: render template, calculate scale, plan changes, back up, apply.
- template/.devframework/safety.py: shared path/reparse checks and atomic file writes.
- template/.devframework/verification.py: doctor structure/readiness and command validation.
- template/.devframework/secrets_check.py: shared literal checks and frozen-index blob scan.
- template/.devframework/source_scope.py: tracked/nonignored source snapshot for the secret heuristic.
- template/.devframework/run_unittest.py: unittest runner that prints the TESTS line finish reads.
- template/.devframework/check.py: worktree finish and commit-check; no implicit deployment.
- scripts/verify.py and tests/: package syntax checks, isolated positive/negative tests.
- template/.devframework/KNOWLEDGE_MAP.md: reviewed source selections, fingerprints, 23
  transferred failure classes and exclusions; eight linked recipes, no duplicate rule text.

## Ownership and update flow

Framework files are managed by normalized text SHA-256 baselines in the install manifest.
PROJECT.md, docs/* and project.json are project-owned seeds: they are never overwritten.
LESSONS.md has one source at package root and is installed under .devframework/.

Rendering uses numeric scale; a dry run performs no writes. All conflicts are collected before
anything is written. Every replaced file is copied to a unique ignored backup, each file is replaced
atomically (same-directory temporary file, fsync, replace), and the manifest is written last, so an
interrupted run is repeated rather than recovered. Backups are kept for reviewed restoration.

## Verification boundary

Doctor's structural mode accepts a scaffold but prints NOT READY. Default requires facts
and real command configuration. No generic claim about schema/API/code semantic drift.
Finish checks readiness and scans working files for secrets, then runs reviewed argv commands with
timeouts. The test command must print `TESTS: total=N failed=F skipped=S`; finish fails on a missing
line, a failure, zero executed tests or too many skips. Commit-check adds the staged-blob secret scan.
Neither writes the index. New projects can finish before staging.
Configured commands are executable trust; this runner is not a sandbox/process-tree manager.
The staged scan excludes no tests/docs, redacts matched values, reports non-text omissions,
and never claims artifact/history coverage. One cat-file batch process serves all index blobs.
The test command gets a unique temporary report path and UUID via environment. JSON reports
must match that invocation, contain valid counts, execute at least one test and respect
the configured skip budget. No arbitrary log parsing or inferred coverage percentage.

The package verifies its own working-source secrets and active documentation links in
addition to consumer fixture tests. Live provider probes are separate from automated tests;
their outcomes and environment failures are in [pilot evidence](evidence/HANDOFF_2026-08-31.md).

## Decisions

- 2026-08-31: Python standard library for cross-stack tooling; PowerShell remains a wrapper.
  No application framework/dependency was selected. Revisit only on an actual portability need.
- 2026-08-31: conservative conflict detection over automatic three-way merging. This avoids
  silently reconciling behavioural rules. Semantic merge remains an explicit reviewed edit.
- 2026-08-31: installed local knowledge over remote runtime imports; offline/provider switches
  must not depend on another private repository or a vendor's memory store.
