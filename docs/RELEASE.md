# Release checklist — DEV Framework

**What this is:** the runnable procedure for shipping. Copy the relevant section into the
working plan and tick items off as they are done.
**Update when:** the procedure changes. See `AGENTS.md` section 3.

This is a template, not deployment authorization. Publishing, uploading and restarting
need an accepted result and explicit authorization for the named environment and actions.

## Version sources

Name the single file that owns each component's version. Versions are independent — bump
only what the release actually changes.

| Component | Version lives in |
|---|---|
| Package | `VERSION` |
| Hermes plugin | `plugin.yaml` |
| Claude Code plugin | `.claude-plugin/plugin.json` |

These three must stay on the same number. This package has no deployed service. Recovery is
`git checkout` of the previous tag, then `python -B scripts/verify.py`. There is no runtime to restart.

## Order

1. Decide order from compatibility: old/new clients, old/new server and stored data.
2. Prefer expand, migrate, contract for breaking changes; remove the old path only after
   supported consumers have moved. Backend-first is not universally safe.
3. Verify behaviour and recovery in an isolated environment before deployment.
4. Name production verification and rollback triggers before the rollout starts.

## 1. Plan and version

- [ ] State the current branch and whether there are unrelated local changes.
- [ ] Write down the intended release order.
- [ ] Read the current versions from the source files named above.
- [ ] Confirm the new version is higher than what is currently deployed.
- [ ] Confirm the docs and regression entries for the changed behaviour already exist.

## 2. Commit

- [ ] Build every affected project locally.
- [ ] Run the full test suite.
- [ ] Present numerical results and limitations; record operator acceptance.
- [ ] Confirm authorization to commit/push. These are separate from deployment approval.
- [ ] Stage authorized task files, then run `python .devframework/check.py commit-check`.
      A changed snapshot invalidates earlier evidence; do not bypass mismatches.
- [ ] Commit only files belonging to the task; leave unrelated files alone and say so.
- [ ] Push, then verify local `HEAD` equals the remote head.

## 3. Deploy

- [ ] Record the current health of the target before touching it.
- [ ] Confirm the exact environment and deployment authorization.
- [ ] Identify the artifact by version/commit/digest and preserve the agreed known-good
      rollback set. Use fixed disposable staging or versioned artifacts with retention.
- [ ] Deploy, wait for restart, verify the reported version equals the source version.
- [ ] Smoke-test the final packaged artifact via ordinary installation/start, not only an
      IDE/debug run. Never prune arbitrary build-intermediate files; use the build tool's
      supported clean operation only on validated task-owned paths with authorization.
- [ ] Verify at least one endpoint or behaviour the release actually changed, not just
      a health probe.
- [ ] If health does not recover, follow the recovery procedure below before anything else.
- [ ] Remove only validated task-owned staging. Do not delete user data or rollback builds.

## 4. Recovery

This package has no service to restart. Recovery is a separate checkout of the previous tag,
not a command to run in a tree that already has uncommitted work:

```text
git clone --branch dev-framework--v1.6.0 https://github.com/trenthalden/dev-framework.git dev-framework-rollback
python -B dev-framework-rollback/scripts/verify.py
```

Use the tag you are leaving, not a tag guessed from this file, if a newer tag exists.
The person who published the tag decides whether to roll back. There is no automatic rollback.

## 5. Final verification

- [ ] Re-check health.
- [ ] Re-check the feature-specific behaviour the release was for.
- [ ] State plainly any check that could not be completed, and why.
