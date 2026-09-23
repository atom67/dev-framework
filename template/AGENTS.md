# Agent Operating Protocol — {{PROJECT_NAME}}

This is the provider-neutral process contract. Project facts belong in [PROJECT.md](PROJECT.md),
not in provider adapters. Framework version and installed baselines are recorded in
`.devframework/manifest.json`. Instructions guide an agent; tests and permission controls
provide separate enforcement. Never treat a document as permission to exceed the request.
This project is a **{{KIND}}** (see PROJECT.md): the kind decides which documents exist and what proves the work.

## 0. Session start and handoff

Fast path: `python .devframework/navigate.py brief` prints the session brief (doctor state, git,
untested cases, open known errors, active checklist and last handoff) and `navigate.py find <ID|keyword>`
returns one block instead of a document. Read the documents below where the brief points.

1. Read this file and [PROJECT.md](PROJECT.md), including the selected profile.
2. Read [known errors](docs/KNOWN_ERRORS.md) relevant to the task before diagnosing it.
<!-- kind: product -->
3. Read [requirements](docs/REQUIREMENTS.md) and [backlog](docs/BACKLOG.md) before planning.
4. Follow the backlog link to the active checklist. Read its Handoff section: decisions,
   actual verification, uncommitted work, limitations and next step. Check git status.
<!-- /kind -->
<!-- kind: tool, explore -->
3. Read the TODO list (a tool) or the open questions (an exploration) in PROJECT.md before planning.
4. Open the active checklist in docs/, if there is one, and read its Handoff section: decisions,
   actual verification, uncommitted work, limitations and next step. Check git status.
<!-- /kind -->
   **Before the first edit make sure the code is current:** development is parallel — other
   people or agents may have committed since the handoff. Fetch, compare the branch with its
   upstream and with the handoff's commit (`navigate.py brief` prints behind/ahead); pull or
   rebase first, and re-read what changed in the files you are about to touch.
<!-- kind: product -->
5. For data or architecture work read [architecture](docs/ARCHITECTURE.md) and the relevant
   [pattern recipe](.devframework/patterns/README.md). For a value path (interactive or
   automatic) also read [use cases](docs/USE_CASES.md). For behaviour changes also read the
   [regression plan](docs/REGRESSION_TEST.md); for an authorized release read [release](docs/RELEASE.md).
<!-- /kind -->
<!-- kind: tool -->
5. Keep [the user guide](docs/GUIDE.html) true: a change to inputs, outputs, options or limits updates it
   in the same iteration, and so do the smoke examples in project.json.
<!-- /kind -->
<!-- kind: explore -->
5. Record what you tried and decided, dated, under "What we learned" in PROJECT.md. When the purpose
   settles, propose promoting the project to a tool or a product; the operator decides.
<!-- /kind -->
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

**Architecture healthcheck.** Before laying down the architecture of a feature, or before debugging one, run
`python .devframework/navigate.py health <areas>` for the areas it touches (db, tx, api, ui, bulk, job, cfg,
dep, ver, sec, llm; SCOPE always comes along) and name the rule ids that apply in the plan. Breaking one is
allowed only with the reason written next to it. Full table: [.devframework/ARCHITECTURE_HEALTHCHECK.md](.devframework/ARCHITECTURE_HEALTHCHECK.md).

If the work still does not fit in **one iteration**, write one checklist from
[the template](docs/CHECKLIST_TEMPLATE.md) **before the first code change**. Keep it
the single living plan. At the **end of every reply to the operator**, copy that
checklist and strike through (`~~done~~`) what is complete. Repeat until every item
is struck. Do not ask the operator to open the file; the copy in the reply is how they
see progress. The file remains the source of truth between sessions.
Maintain it with `python .devframework/navigate.py checklist new|add|tick|show|archive <slug>`
(`show` prints the live list to paste into the reply) and write the handoff at the end of a
session with `navigate.py handoff <slug> --note "..."`.

<!-- kind: product -->
A new or changed value path is a case in [use cases](docs/USE_CASES.md), copied from
[the case template](docs/USE_CASE_TEMPLATE.md). A shipped subset of the catalogue uses
[the slice template](docs/USE_CASES_SLICE_TEMPLATE.md); it maps to live `UC-###` IDs and
does not renumber them.
<!-- /kind -->
<!-- kind: tool -->
A tool's behaviour is defined by its smoke examples (`smoke` in project.json: input → expected
output). A change in behaviour changes an example first, then the code, then the guide.
<!-- /kind -->
**Under construction.** A document in long rework — waiting for code, tests or a decision — may carry one
line `<!-- under-construction: <reason> (until YYYY-MM-DD) -->`. Doctor then skips that document's checks
(placeholders, links, catalogue rules), names it on every run and in the brief, and applies the checks again
after the date. Only PROJECT.md and docs/ can be marked; secrets, tests and the presence of required files are
never skipped. Remove the line in the iteration that finishes the work; a marker is not a place to park debt.

Reconcile the checklist before and after each iteration. Discovered work enters it
before implementation; a material scope change needs agreement. An item is done only
after it is built and verified. Keep the checklist active while awaiting acceptance;
archive it after completion/acceptance.

| Source of truth | Maintain when |
|---|---|
| PROJECT.md | stack, file map, selected profile, storage paths or conventions change |
| .devframework/project.json | executable verification commands change; no secrets here |
<!-- kind: product -->
| docs/REQUIREMENTS.md | agreed product behaviour or quality requirement changes; stable FR/NFR IDs |
| docs/BACKLOG.md | scope/status changes; retain active, agreed next and 3 recently accepted items |
<!-- /kind -->
| docs/KNOWN_ERRORS.md | a defect/limit is found during implementation; record dates, impact and evidence |
<!-- kind: product -->
| docs/ARCHITECTURE.md | components, contracts, schema or data flows change |
| docs/USE_CASES.md | a value path (interactive or automatic) is added, or a case's trigger, flow or outcome changes; stable UC IDs. SET Enables and Preconditions cite only existing IDs (ranges expand). Flow names the live store when more than one exists; do not merge a replica/safety slogan into an API path |
| docs/REGRESSION_TEST.md | risk scenarios or automated/manual coverage change |
| docs/INVARIANTS.md | a product guard, entry point or intentional exception changes |
| docs/RELEASE.md | authorized release, rollback or retention procedure changes |
<!-- /kind -->
<!-- kind: tool -->
| docs/GUIDE.html | the tool's inputs, outputs, options, examples or limits change |
<!-- /kind -->

In a read-only review, report new defects instead of silently editing the knowledge base.
Project-specific decisions stay in project docs; reusable lessons can be proposed upstream
without sending source code, credentials or private incident data automatically.

## 4. Verification and acceptance

**Testing depth** is `testing` in `.devframework/project.json`, chosen by the operator:
- **Lean testing** — recommended for explorations, tools and software with a small number of users. One
  scenario test per user-visible promise, run through the real entry point (CLI, API, UI adapter) on
  isolated fixtures. No tests of internals and no matrix of edge cases until a defect shows one is needed
  (then its regression test). Before trusting a new test, break the behaviour once in a scratch copy and
  see the test fail. The whole suite runs in under a minute.
- **Advanced testing** — recommended from tens of thousands of users, for complex projects with a
  production environment and a high cost of error. Unit tests for logic with branches, integration tests
  for storage, network and process boundaries, end-to-end tests for every critical user path; negative
  and boundary cases at every trust boundary; interruption, concurrency and crash recovery in child
  processes where relevant; every use case `covered` or `NFV` (commit-check refuses a `gap`); a current
  regression plan (`docs/REGRESSION_TEST.md`); verification in an isolated staging environment before production.

Both: use the project's test framework; never a real profile, production database, actual token or live
integration as a fixture. Moving to advanced is the operator's call when users, production or the cost of
an error grow; say so when you see it.

For a regression, demonstrate the relevant test fails on a synthetic defect/old behaviour
and passes on the correction. Do this in fixtures or an isolated checkout, not a live app.
A pure-function test is not evidence for concurrent I/O or crash durability.

After implementation run `python .devframework/check.py finish`. Configure its build,
test and extra-check commands for this stack; the test command reports its counts. Build all consumers of
shared code. Missing checks mean NOT READY, not success. Report failures and blocked work
honestly; do not claim completion or expand authority to make a check pass.
<!-- kind: tool -->
For a tool the test command is `run_smoke.py`: it runs the tool on the `smoke` examples in project.json and
compares the output. The tool is its own test; the examples are its evidence, so keep at least one.
<!-- /kind -->
<!-- kind: explore -->
While exploring, finish does not require tests: it checks structure and secrets and says plainly that
behaviour is unproven. Add a test command as soon as something is worth keeping.
<!-- /kind -->

Finish is evidence about the working tree, not a future commit. Before an authorized commit run
`python .devframework/check.py commit-check`; it adds a secret scan of the staged files. Stage only when
authorized. Later edits invalidate the result; never bypass checks for convenience.

<!-- kind: product -->
Register critical behaviour in [invariants](docs/INVARIANTS.md). Test actual entry adapters,
not just the guard.
<!-- /kind -->
Growing data paths need representative-volume checks and visible
latency boundaries; see [performance](.devframework/patterns/bounded-performance.md).

Present checks performed and numerical results, visible UX outcomes and product decisions.
The operator accepts priorities and trade-offs, not debugging chores.

**Reply shape.** Every reply to the operator has two parts, with these exact headings.
**🛠️ Tech**: what was done or planned, with the technical detail (files, commands, counts).
**💬 Message**: the same, restated in plain product language, ending with the explicit ask — what
the operator must do now (accept, answer, decide). The Message must stand on its own; never end
a reply by pointing back into it. When a checklist is live, its copy goes at the end of the Message.
If the host profile prescribes its own plain-language block or footer for replies, the Message
**is** that block: write one Message, not both. This shape wins over profile reply formats;
the profile keeps tone, language and persona.
Anything the operator must paste, run or open is delivered ready to use: the exact text in a
code block (copy-ready) and/or a link that actually opens in the operator's client — clients open
only files inside the session's working directory, so copy the file there first or give the text —
never a bare path or a file name the operator has to go and find on disk. Manual engineering
verification remains the implementer's job; inaccessible checks are explicit limitations.
Acceptance, commit and deployment are separate events.

**Devlog (optional).** When `devlog.enabled` is true in `.devframework/project.json`, every
finalized dialogue gets a verbatim log file before the push: `python .devframework/check.py
devlog --agent <client-MODEL> [--codes <FR/UC codes>] --from-git N`. The dialogue is filled from the host's session
log (Claude Code by default; `--dialogue hermes[:<session>]` in Hermes); read it once. For public or
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

**Cost of the loop itself.** Time the operations you repeat, and report those numbers with the
result. Re-running a full verification for a change whose scope you already know is waste, not
rigour: during iteration run the affected test module (seconds), and run the full gate once before
reporting. A gate slower than a minute is a defect in the suite, not a fact of life. Measure per
module before trimming anything: independent modules belong in parallel processes
(`run_unittest.py --jobs auto`), and only what is still slow deserves a smaller fixture or fewer
duplicated paths. Judge the suite by risk covered per second spent — a test that repeats another
test's path, an extra check that re-runs the same suite, and a fixture that installs more than the
case needs are removable without losing evidence. If a session spends more time verifying than
changing, say so and fix the loop before continuing.

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
Building an AI agent (a bot, an assistant, a scheduled LLM job): read the
[agent guidelines](.devframework/agents/README.md) first and keep one agent card per agent.
Record a stable known-error ID near
non-obvious defences so a later refactor can recover their reason.
