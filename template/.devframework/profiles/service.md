# Service profile

- Configure the team's branch/PR policy in PROJECT.md; preserve protected branches.
- Build and tests target isolated environments. Never restart a live service implicitly.
- Use identifiable, immutable release artifacts and a bounded retention policy that
  includes a known-good rollback. A fixed staging directory is not a release identity.
- Stop accepting affected work on an invariant failure. Record diagnostics, fail readiness
  as appropriate, and drain/cancel through owned lifecycle boundaries. The supervisor's
  restart budget must avoid crash loops. Health/liveness is not data-delivery correctness.
- Do not retry non-idempotent effects blindly. Preserve durable work for replay.
- Deploy only after explicit authorization, compatibility checks and a tested rollback
  procedure. Validate a changed data flow as well as a health endpoint.
