# Agent Operating Protocol — {{PROJECT_NAME}}

This is the provider-neutral process contract. Project facts belong in [PROJECT.md](PROJECT.md),
not in provider adapters. Framework version and installed baselines are recorded in
`.devframework/manifest.json`. Instructions guide an agent; tests and permission controls
provide separate enforcement. Never treat a document as permission to exceed the request.

## 0. Session start and handoff

Fast path: `python .devframework/navigate.py brief` prints the session brief (doctor state, git,
untested cases, open known errors, active checklist and last handoff) and `navigate.py find <ID|keyword>`
returns one block instead of a document. Read the documents below where the brief points.

1. Read this file and [PROJECT.md](PROJECT.md), including the selected profile.
2. Read [known errors](docs/KNOWN_ERRORS.md) relevant to the task before diagnosing it.
3. Read [requirements](docs/REQUIREMENTS.md) and [backlog](docs/BACKLOG.md) before planning.
4. Follow the backlog link to the active checklist. Read its Handoff section: decisions,
   actual verification, uncommitted work, limitations and next step. Check git status.
   **Before the first edit make sure the code is current:** development is parallel — other
   people or agents may have committed since the handoff. Fetch, compare the branch with its
   upstream and with the handoff's commit (`navigate.py brief` prints behind/ahead); pull or
   rebase first, and re-read what changed in the files you are about to touch.
5. For data or architecture work read [architecture](docs/ARCHITECTURE.md) and the relevant
   [pattern recipe](.devframework/patterns/README.md). For a value path (interactive or
   automatic) also read [use cases](docs/USE_CASES.md). For behaviour changes also read the
   [regression plan](docs/REGRESSION_TEST.md); for an authorized release read [release](docs/RELEASE.md).
6. On first use read [lessons](.devframework/LESSONS.md). Later follow relevant incident
   links and the [transfer map](.devframework/KNOWLEDGE_MAP.md). Check for scoped
   instructions without loading every archive.

Do not rely on a provider's private memory or prior chat. Persist agreed decisions in
the appropriate document and handoff evidence in the active checklist, not a second plan.
Missing or contradictory context: inspect code and report uncertainty; do not invent it.
Provider loading and an engineer-run fresh-session test: [agents](.devframework/AGENTS_GUIDE.md).

## 1. Authority and working agreement

- Review/explain/diagnose: read-only by default. Isolated diagnostic fixtures are allowed;
  changing source, live data, services or remote state needs implementation authorization.
- Implement: make the requested changes, preserve unrelated edits, verify affected paths.
  Before running commands inspect and state the branch, outputs and side effects.
- Do yourself everything a tool can do: create directories, copy fixtures, run commands, read
  logs, prepare test data. Ask the operator only where a human is genuinely required — input
  in an interface made for people (a desktop app, a browser session, a phone), an approval,
  a product decision, or a credential you must not handle. "Please create the folder and copy
  the files" is a defect in the reply, not a task for the operator.
- Build is not run; run is not deploy. Never stop or restart the user's working app,
  upload, publish or change production solely because a build succeeded.
- Use the existing branch unless the operator or selected project workflow requests a
  branch. Do not switch, merge, reset or rewrite history silently.
- No commit or push before acceptance unless explicitly authorized. Never bypass hooks
  or signing to obtain a green result. Stage only task-owned changes when authorized.
- Select desktop/service specifics in PROJECT.md. A profile cannot broaden permissions.
- Clean only validated task-owned staging paths. Keep a documented rollback set of release
  artifacts with a retention limit; versioned releases are not inherently waste.

Commit format: `<type>: <description>`; types feat, fix, refactor, docs, test, chore, perf, ci.

## 2. Simplicity and testability

Use the standard library, platform or existing dependency when it meets correctness,
security and maintenance needs. Avoid speculative layers; do not ban an interface or a
test framework just because there is one production implementation. A boundary around
files, network, clocks or processes can be necessary to test failure safely.

Prefer cohesive modules and readable functions. File/function length is a review signal,
not a universal line-count gate; generated code is different from handwritten logic.
Keep business rules out of UI glue. Read callers and shared consumers when changing a contract.

Record intentional shortcuts with `simplification:`, applicability, ceiling and upgrade
trigger. Never trade away data integrity, security, accessibility or execution cost.

## 3. Planning and documentation

This package is a heavy overlay of documentation, analysis and tests. It is meant to
raise the quality of development, of reading a change, and of understanding existing
code. Work is slower and the outcome is more predictable. Plan for that: prefer
**larger iterations** that rest on the catalogue, architecture and known errors, close
with isolated tests, and are independently acceptable. Do not slice a well-understood
path into many engineering chores; the overlay already pays for a bigger step.

Independent work that can run at the same time **must** run in parallel subagents when
the host provides them. Do not serialize reads, searches, reviews or implementations
that do not share an unfinished output. Give each subagent a closed task, the same
authority limits as this protocol, and no commit/push/deploy. The parent merges
results, checks contradictions, and remains accountable to the operator. Sequential
execution of independent work is a planning defect, not caution.

If the work still does not fit in **one iteration**, write one checklist from
[the template](docs/CHECKLIST_TEMPLATE.md) **before the first code change**. Keep it
the single living plan. At the **end of every reply to the operator**, copy that
checklist and strike through (`~~done~~`) what is complete. Repeat until every item
is struck. Do not ask the operator to open the file; the copy in the reply is how they
see progress. The file remains the source of truth between sessions.
Maintain it with `python .devframework/navigate.py checklist new|add|tick|show|archive <slug>`
(`show` prints the live list to paste into the reply) and write the handoff at the end of a
session with `navigate.py handoff <slug> --note "..."`.

A new or changed value path is a case in [use cases](docs/USE_CASES.md), copied from
[the case template](docs/USE_CASE_TEMPLATE.md). A shipped subset of the catalogue uses
[the slice template](docs/USE_CASES_SLICE_TEMPLATE.md); it maps to live `UC-###` IDs and
does not renumber them.
Reconcile the checklist before and after each iteration. Discovered work enters it
before implementation; a material scope change needs agreement. An item is done only
after it is built and verified. Keep the checklist active while awaiting acceptance;
archive it after completion/acceptance.

| Source of truth | Maintain when |
|---|---|
| PROJECT.md | stack, file map, selected profile, storage paths or conventions change |
| .devframework/project.json | executable verification commands change; no secrets here |
| docs/REQUIREMENTS.md | agreed product behaviour or quality requirement changes; stable FR/NFR IDs |
| docs/BACKLOG.md | scope/status changes; retain active, agreed next and 3 recently accepted items |
| docs/KNOWN_ERRORS.md | a defect/limit is found during implementation; record dates, impact and evidence |
| docs/ARCHITECTURE.md | components, contracts, schema or data flows change |
| docs/USE_CASES.md | a value path (interactive or automatic) is added, or a case's trigger, flow or outcome changes; stable UC IDs. SET Enables and Preconditions cite only existing IDs (ranges expand). Flow names the live store when more than one exists; do not merge a replica/safety slogan into an API path |
| docs/REGRESSION_TEST.md | risk scenarios or automated/manual coverage change |
| docs/INVARIANTS.md | a product guard, entry point or intentional exception changes |
| docs/RELEASE.md | authorized release, rollback or retention procedure changes |

In a read-only review, report new defects instead of silently editing the knowledge base.
Project-specific decisions stay in project docs; reusable lessons can be proposed upstream
without sending source code, credentials or private incident data automatically.

## 4. Verification and acceptance

Use the project's test framework and isolated fixtures. Cover risk, not an arbitrary
number of tests: normal behaviour, boundaries, invalid input, interruption and concurrency
where relevant. Test persistence with temporary stores and crash recovery in child processes.
Never use a real profile, production database, actual token or live integration as a fixture.

For a regression, demonstrate the relevant test fails on a synthetic defect/old behaviour
and passes on the correction. Do this in fixtures or an isolated checkout, not a live app.
A pure-function test is not evidence for concurrent I/O or crash durability.

After implementation run `python .devframework/check.py finish`. Configure its build,
test and extra-check commands and counted evidence for this stack. Build all consumers of
shared code. Missing checks mean NOT READY, not success. Report failures and blocked work
honestly; do not claim completion or expand authority to make a check pass.

Finish identifies the verified working-source digest, not a future commit. Before an
authorized commit run `python .devframework/check.py commit-check`; it rejects nonignored
untracked files, index/worktree differences and hidden-change flags. Stage only when
authorized. Later edits invalidate evidence; never bypass checks for convenience.

Register critical behaviour in [invariants](docs/INVARIANTS.md). Test actual entry adapters,
not just the guard. Growing data paths need representative-volume checks and visible
latency boundaries; see [performance](.devframework/patterns/bounded-performance.md).

Present checks performed and numerical results, visible UX outcomes and product decisions.
The operator accepts priorities and trade-offs, not debugging chores.

**Reply shape.** Every reply to the operator has two parts. **Tech**: what was done or planned,
with the technical detail (files, commands, counts). **Message**: the same, restated in plain
product language, ending with the explicit ask — what the operator must do now (accept, answer,
decide). The Message must stand on its own; never end a reply by pointing back into it. When a
checklist is live, its copy goes at the end of the Message.
Anything the operator must paste, run or open is delivered ready to use: the exact text in a
code block (copy-ready) and/or a clickable link to the file — never a bare path or a file name
the operator has to go and find on disk. Manual engineering
verification remains the implementer's job; inaccessible checks are explicit limitations.
Acceptance, commit and deployment are separate events.

**Devlog (optional).** When `devlog.enabled` is true in `.devframework/project.json`, every
finalized dialogue gets a verbatim log file before the push: `python .devframework/check.py
devlog --agent <client-MODEL> --codes <FR/UC codes> --from-git N`, then paste the dialogue. For public or
unknown-visibility repositories the log stays local and git-ignored. Rules and format:
[.devframework/DEVLOG.md](.devframework/DEVLOG.md).

## 5. Execution cost

Every repeating operation needs a nearby `cost:` explanation: interval, active duration,
concurrency, retries, daily volume and average/peak rate at the project's target scale.
Distinguish requests, open connections, bytes, CPU and wakeups; compare third-party limits.
Numeric scale and the worked example live in [PROJECT.md](PROJECT.md); do not duplicate totals.

For N clients polling every T seconds for H hours/day:
`requests/day = N * H * 3600 / T`; active average rate is `N / T` before retries.
Check these assumptions against measured traffic. A comment marker alone proves no maths.
Prefer push, caching, bounded backoff and jitter where appropriate, not by dogma.

## 6. Secrets and checks

No real plaintext credentials in source, docs, fixtures, logs or build configuration.
Use platform-protected storage or the deployment secret facility. Examples use obvious
placeholders, never working keys. Redact diagnostics. Rotate exposed credentials through
an authorized process and record the incident without reproducing the value.

`python .devframework/check.py secrets --staged` inspects index blobs, not working files.
It is a conservative heuristic, not an exhaustive security audit; see
[verification limits](.devframework/VERIFICATION.md). Do not blanket-exclude tests/docs.
Use a format-aware artifact scanner before distribution. Compressed, encrypted, unreadable
or unsupported output is NOT CHECKED; scanning a directory is not proof its payload is safe.

## 7. Reliability

Persist state whose loss violates product behaviour at a defined commit boundary, not
only on exit. State the durability and recovery contract. Do not overwrite good storage
with unverified memory after a failure.

Expected failures are handled at their operation boundary with bounded retries for
transient errors and idempotency where effects can repeat. Unexpected invariant failures
stop affected work and writes; diagnostics and recovery follow the selected profile.
Do not turn read failures into first-run defaults or make restarting an infinite loop.

Use the [recipes](.devframework/patterns/README.md) for outbox delivery, configuration,
crash recovery, stale work, evolution, entry-point guards, performance and sync semantics.
Record a stable known-error ID near
non-obvious defences so a later refactor can recover their reason.
