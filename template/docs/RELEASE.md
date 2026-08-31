# Release checklist — {{PROJECT_NAME}}

**What this is:** the runnable procedure for shipping. Copy the relevant section into the
working plan and tick items off as they are done.
**Update when:** the procedure changes. See `AGENTS.md` section 7.

An agent does not start publishing, uploading, or restarting anything until the checklist
is written down and the intended order is explicit.

## Version sources

Name the single file that owns each component's version. Versions are independent — bump
only what the release actually changes.

| Component | Version lives in |
|---|---|
| ... | ... |

## Order

1. Backend first, when contracts or endpoints changed.
2. Clients next, when they depend on the new backend.
3. Anything independent last.
4. Run the regression pass and update `docs/REGRESSION_TEST.md` when behaviour changed.

## 1. Plan and version

- [ ] State the current branch and whether there are unrelated local changes.
- [ ] Write down the intended release order.
- [ ] Read the current versions from the source files named above.
- [ ] Confirm the new version is higher than what is currently deployed.
- [ ] Confirm the docs and regression entries for the changed behaviour already exist.

## 2. Commit

- [ ] Build every affected project locally.
- [ ] Run the full test suite.
- [ ] Commit only files belonging to the task; leave unrelated files alone and say so.
- [ ] Push, then verify local `HEAD` equals the remote head.

## 3. Deploy

- [ ] Record the current health of the target before touching it.
- [ ] Publish to the **fixed** output directory, never a version-stamped one.
- [ ] Deploy, wait for restart, verify the reported version equals the source version.
- [ ] Verify at least one endpoint or behaviour the release actually changed, not just
      a health probe.
- [ ] If health does not recover, follow the recovery procedure below before anything else.
- [ ] Remove staging directories, locally and remotely.

## 4. Recovery

The exact commands to restore the previous known-good build, per target. Written before
they are needed — an outage is not the moment to work them out.

```
...
```

## 5. Final verification

- [ ] Re-check health.
- [ ] Re-check the feature-specific behaviour the release was for.
- [ ] State plainly any check that could not be completed, and why.
