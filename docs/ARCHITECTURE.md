# DEV Framework architecture

No application database or schema. Package version authority: VERSION. Manifest/config
format is 1; it is independent of the application schema. Python 3.10+ standard library.

## Components

- install.ps1: optional argument-forwarding wrapper. No policy changes or shell-built commands.
- scripts/install.py: render template, calculate scale, plan changes, lock, backup, apply/recover.
- template/.devframework/safety.py: shared path/reparse checks, OS lock and atomic file writes.
- template/.devframework/verification.py: doctor structure/readiness and command validation.
- template/.devframework/secrets_check.py: shared literal checks and frozen-index blob scan.
- template/.devframework/source_scope.py: tracked/nonignored source snapshot, digest and index parity.
- template/.devframework/test_evidence.py: fresh run ID and counted-result validation.
- template/.devframework/run_unittest.py: zero-test-safe adapter for the evidence contract.
- template/.devframework/check.py: worktree finish and commit-check; no implicit deployment.
- scripts/verify.py and tests/: package syntax checks, isolated positive/negative tests.
- scripts/handoff_pilot.py: disposable tested example and durable handoff, no provider invocation.
- template/.devframework/KNOWLEDGE_MAP.md: reviewed source selections, fingerprints, 23
  transferred failure classes and exclusions; eight linked recipes, no duplicate rule text.

## Ownership and update flow

Framework files are managed by normalized text SHA-256 baselines in the install manifest.
PROJECT.md, docs/* and project.json are project-owned seeds: they are never overwritten.
LESSONS.md has one source at package root and is installed under .devframework/.

Rendering uses numeric scale; a dry run performs no writes. All conflicts are collected
before applying anything. Actual apply acquires an OS lock, verifies the manifest has not
changed and checks file bytes again before replacement. Per-file replacement uses same-
directory temporary files, fsync and atomic replace. Original bytes and raw hashes are
stored in a unique ignored backup with a journal; pending.json blocks use while incomplete.
Manifest is written last. A caught failure rolls back; hard termination needs --recover.
Recovery validates every path/hash before restoring and refuses post-crash user edits.
Successful backups are retained for reviewed restoration, not automatically pruned.

The lock does not coordinate arbitrary editors or malicious filesystem changes. The
transaction provides recoverability, not atomically visible multi-file updates. Local
process-crash tests are not power-cut/filesystem durability certification.

## Verification boundary

Doctor's structural mode accepts a scaffold but prints NOT READY. Default requires facts
and real command configuration. No generic claim about schema/API/code semantic drift.
Finish checks working-source text and readiness, runs reviewed argv commands with timeouts,
requires fresh counted test evidence, and rejects changed source snapshots after commands.
It prints a source digest and explicitly does not certify a future commit. Commit-check
also requires index/worktree parity, no nonignored untracked files, no hidden-change flags
and a stable scanned index. Neither writes the index. New projects can finish before staging.
Ignored dependencies/host configuration and malicious edit-and-restore races are outside
the snapshot boundary; record pinned runtime/dependencies and use isolated verification.
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
