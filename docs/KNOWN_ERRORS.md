# Known errors — DEV Framework

## KE-2026-08-31-FINISH-EVIDENCE — success without test or snapshot evidence

- Found in uncommitted v0.2 second review. check.py accepted unittest's successful zero-test
  exit and tested a fixed working copy while the staged source still contained a defect.
- Status: fixed in v0.2. Simplified 2026-09-23: the runner prints one `TESTS:` line and finish fails
  on zero executed tests (tests/test_gates.py); the snapshot digest and index parity were removed.

## KE-2026-08-31-SECRET-FORMATS — common literals missed, OAuth metadata flagged

- Found in uncommitted v0.2 second review. secrets_check.py missed unquoted dotenv/YAML
  and C# verbatim values, but flagged token_type and token_endpoint ordinary metadata.
- Status: fixed in uncommitted v0.2 hardening; SecretFormatTests covers the named formats
  and false positives with synthetic data; broader heuristic limitations remain below.

## KE-2026-08-31-TRANSFER-COVERAGE — important source lessons absent

- Existing lesson/recipe links worked but did not establish completeness. Original tray
  exit guard bypass and UI/SQL performance lessons had no explicit transferable recipes.
- Status: named gaps fixed in uncommitted v0.2 hardening; 24-row transfer map, eight recipes
  and invariant register. Map explicitly names source selections and unreviewed material;
  not a claim that all historical implementations are portable or correct.

## KE-2026-08-31-SCALE — custom scale retained 10k totals

- Introduced: c48cf74; detected: 2026-08-31 review.
- Where: template/AGENTS.md cost example, installer substitution.
- Impact: 50k deployment estimate understated requests fivefold; 5k overstated twofold.
- Cause: string substitution changed the label, not the calculated totals.
- Status: fixed in v0.2.0 working tree, not yet committed/accepted.
- Verification: test_scale_math_three_sizes verifies 5k/10k/50k expected totals.

## KE-2026-08-31-KNOWLEDGE — lessons absent from installed projects

- Introduced: c48cf74; detected: 2026-08-31 review.
- Impact: provider/project switch loses rationale; the Main OS outbox incident was omitted.
- Status: fixed in v0.2.0 working tree, not yet committed/accepted.
- Verification: installed lesson bytes equal the canonical source; outbox and all five
  local recipe links are tested in generated projects.

## KE-2026-08-31-UPGRADE — no non-destructive upgrade protocol

- Introduced: c48cf74; detected: 2026-08-31 review.
- Impact: skip leaves old rules; Force overwrites project adaptation without a backup.
- Status: fixed in v0.2.0 working tree, not yet committed/accepted.
- Verification: forced replacement retains exact original bytes; project-owned docs are
  preserved; conflicts/no-op updates, interruption, later-edit refusal and OS lock tested.

## KE-2026-09-03-USECASE-PADDED-RANGE — unique headings, phantom citations

- Found: agent map vs USE_CASES.md (calendar/tasks via API; replica has neither). SET-018
  cited UC-155 and UC-173, which were never written.
- Cause: catalogue generated in one pass; Enables used round ranges; Flow merged the
  replica safety slogan with `/api/*`. Doctor only checked heading uniqueness.
- Status: doctor requires USE_CASES.md and expands SET Enables and Preconditions against
  headings/rows; it also requires unique headings, a Test field and a traceability row.
  Flow which-store claims stay a review item. Source project `doc_drift.py` gets the same ID
  check.
- Verification: test_use_case_enables_range_must_have_headings,
  test_use_case_precondition_set_must_exist, test_use_case_missing_test_field,
  test_use_case_missing_traceability_row, test_use_case_duplicate_heading.

## Explicit v0.2 boundaries (not silently claimed as covered)

- Staged secret detection is a text heuristic. Non-text files are reported, history and
  built artifacts are not inspected. No claim of exhaustive absence of credentials.
- Doctor checks the stated document/config contract, including the use-case catalogue
  in required USE_CASES.md. It does not judge schema/API semantic drift or whether a
  Flow names the correct store.
- Finish runs reviewed project commands, not a sandbox. Timeout does not guarantee that
  detached descendants are stopped; test process ownership remains a project concern.
- Installer protects normal local edits and blocks unsafe paths. It does not defend
  against malicious concurrent filesystem replacement. A multi-file update is not atomic:
  an interrupted run is repeated; replaced files stay in .devframework/backups/.
- Native handoff pilot is blocked: Claude OAuth expired; Codex read commands denied by
  machine policy; Cursor agent unavailable in inspected CLI. See the evidence report.
  Hosted Linux/Windows CI remains unexecuted pending accepted commit/push.
