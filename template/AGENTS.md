# Agent Operating Protocol — {{PROJECT_NAME}}

The working agreement between the operator and any AI coding agent on this repository.
Read at the start of every session, before planning, before code, before build or run.

**Division of files.** Process rules live here. Project facts — stack, layout, build
commands, data locations — live in `CLAUDE.md`. A rule is stated in exactly one place.
Duplicated rules drift, and a drifted rule is worse than a missing one: the missing one
sends you to the code, the drifted one confidently lies.

---

## 0. Start of session

1. This file.
2. `docs/KNOWN_ERRORS.md` — before "fixing" anything or explaining odd behaviour, check
   whether it is already recorded, with a workaround.
3. `docs/REQUIREMENTS.md` — numbered requirements and product principles.
4. `docs/BACKLOG.md` — the current queue, priorities, and already-agreed scope.
5. `docs/ARCHITECTURE.md` — if the task touches data schema, new services, or data flow.
6. `docs/REGRESSION_TEST.md` — if the task changes existing behaviour or bumps a version.

Then run `ls *.md docs/*.md` and confirm no new root-level guide has appeared that this
list does not mention. Guides nobody is told to read stop being true within weeks.

---

## 1. Build the smallest thing that works

Before writing code, stop at the first rung that holds:

1. Does this need to exist at all? Speculative need — skip it, say so in one line.
2. Does the standard library already do it? Use it.
3. Does a native platform feature cover it? Use it.
4. Does an already-installed dependency solve it? Use it.
5. Can it be one line? One line.
6. Only then: the minimum code that works.

Rules:

- No abstraction nobody asked for. No interface with one implementation, no factory for
  one product, no configuration for a value that never changes.
- No new dependency for what a few lines can do.
- Deletion beats addition. Boring beats clever — clever is what someone decodes at 3am.
- Challenge complex requests: "do you actually need X, or does Y cover it?"
- Between two equally short standard-library options, take the one that is correct on
  edge cases. Lazy means writing less code, not picking the flimsier algorithm.
- Mark deliberate simplifications with a `simplification:` comment. If the shortcut has a
  known ceiling — a global lock, an O(n^2) scan, a naive heuristic — the comment names the
  ceiling and the upgrade path.

**Never simplify away:** input validation at trust boundaries, error handling that
prevents data loss, security, accessibility basics, **execution cost**, or anything the
operator explicitly asked for.

Non-trivial logic leaves behind **one runnable check** — the smallest thing that fails if
the logic breaks. An assert-based self-check, or one small test file. No frameworks, no
fixtures. Trivial one-liners need no test.

---

## 2. Working agreement

- **Branch.** The project runs linearly on `main`. The agent does not create or switch
  branches without an explicit request. If a branch was created on request, the agent
  either carries it through to a merge into `main` or stops with a loud warning that a
  merge is still owed. A working feature must never be left silently in a side branch.
- **Before any build or run**, state the current branch and the exact path of the binary
  that is about to be overwritten or launched.
- **Living build.** The operator uses one specific build output. Do not produce parallel
  output directories, do not switch build configurations, and do not publish without an
  explicit request.
- **Build artifacts.** Always publish to the *same* fixed directory, never to a
  version-stamped one. Version-stamped publish directories are how dead copies accumulate
  into gigabytes without anyone noticing. Remove staging directories after a rollout,
  both locally and on any remote host.
- **After a successful build, relaunch the application.** The operator may forget to
  restart, will then test the previous binary, and will report a fixed bug as still open.
- **Version string.** When the version is bumped, update the string the operator actually
  sees — window title, CLI banner, about box. It is the only way for them to know which
  build they are testing.

### Commit format

```
<type>: <description>

<optional body>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`.

Never bypass hooks (`--no-verify`) or signing without an explicit request. If a hook
fails, fix the cause.

---

## 3. Planning

### A big task becomes a checklist file before the first code edit

If the work does not fit in one session — a multi-step plan, a refactor, a migration, a
programme of work — it **does not start** without a checklist in the repository.

- The checklist is created **before** the first code edit, as its own file in `docs/`,
  and is the single living document for that topic.
- Work is cut into **portions**. One portion = one verifiable thing the operator can
  accept or send back. Not "a stage that takes a week".
- Reconcile against the checklist **at the start and at the end of every portion**, not
  when it happens to come to mind.
- An item is marked done only after it is built and verified. "Code is written" is not
  done.
- Work discovered along the way becomes a checklist item **first**, and is done second.
  Silently widening scope is not allowed.
- When the programme is finished, the file moves to `docs/archive/` in full. It does not
  linger as a second living document.

### Scope

Implementation matches the scope agreed in `docs/BACKLOG.md`. Deviations are agreed with
the operator, not assumed. After implementation, update the status in the backlog. After
the operator accepts, trim the backlog to active items, the next agreed items, and the
three most recently finished features — nothing else.

---

## 4. Finishing and acceptance

### Definition of done

Before presenting anything: build every project affected by the change, run the test
suite unconditionally, and run every automated check the repository has. If something did
not pass, it cannot be presented — fix it first.

When shared code is touched, build **every** consumer of it, not just the one in front of
you. That is exactly where a breakage travels unnoticed.

Nothing is pushed to shared storage before the operator says it is accepted. Silently
pushing unaccepted work means accepting it on their behalf.

### Acceptance is presented to a product owner, not to a developer

The operator is a product owner. They do not read code, do not open files at a line
number, do not run scripts, and do not reproduce defects by hand. Asking them to is not
finishing the work — it is handing them its last part.

Acceptance **may not** contain: "open this file near line N", "try making a commit", "run
this script", "check the log".

Acceptance **must** contain:

- a check *you* performed, with the result quoted — numbers, not "it works";
- what is visible in the application during ordinary use, where that applies;
- the product decisions they can make from a plain-language account: frequencies,
  delays, limits, trade-offs.

If something can only be verified from inside the code, you verify it and present the
result. The operator makes the decision; they do not perform the check.

### Verify before claiming

Do not report anything you have not checked. And check the check: temporarily plant the
defect the check is supposed to catch, confirm it fails with the exact expected value,
restore it, confirm it passes again. A check that has never fired is not a check; it is a
decoration that manufactures false confidence.

Report outcomes faithfully. If tests fail, say so and quote the output. If a step was
skipped, say which and why. If part of the scope turns out to be blocked, finish
everything else in full and state explicitly what was left out and why.

---

## 5. Execution cost

Any **repeating** work — a timer, a background service, a loop with a pause, a poll — is
saved only together with a calculation of what it costs. The calculation is written as a
comment starting with `cost:` next to the site, and it must name the load at
**{{SCALE_TARGET}}**. Not "the server will cope", but how many requests per day and per
second.

```
// cost: 1 request per minute, 1 440 per day per device;
//       at {{SCALE_TARGET}} that is 14.4M requests per day, 167 per second.
```

Minimal code and minimal cost are different things, and the first is routinely passed off
as the second. Polling every five seconds is shorter to write than a held request, and a
thousand times more expensive to run. Laziness is measured in lines, not in requests,
wakeups, and calls into other people's services. Where the work repeats: calculate first,
write the code second.

The calculation is also reconnaissance. Costing the existing sites is how you find the
ceilings nobody could see — third-party rate limits, handlers written for a single user,
one open connection per client — before launch instead of during it.

---

## 6. Secrets

- Never put a plaintext token, key, or password into settings files, config files, README
  examples, test artifacts, logs, or the backlog.
- MVP / prototype / beta status is not a justification. There is no such exemption.
- Secrets go into platform-protected storage. If a new feature needs a secret, protected
  storage is added **first** and the integration second.
- A secret that reaches a tracked file is in history forever — removing it means
  rewriting history. It is far cheaper not to let it in.
- If a secret was ever written in plaintext, treat it as compromised: move it to
  protected storage, rotate it, and record the incident in `docs/KNOWN_ERRORS.md`.

Two different exposures need two different checks: **sources** (only files git actually
tracks) and **build output** (a secret can be absent from the sources and still sit
inside a shipped binary). When checking build output, check the whole output *directory* —
in release mode the payload is compressed, and scanning one file proves nothing.

---

## 7. Documentation maintenance

Stated once, here. `CLAUDE.md` must not restate it.

| Document | Update when | Write what |
|---|---|---|
| `docs/KNOWN_ERRORS.md` | any bug or limitation is found — while developing, testing, or reviewing | description, file/line, impact, fix or the status "not fixed". On fix, mark it fixed with the commit or version |
| `docs/ARCHITECTURE.md` | the data schema changes, tables or migrations are added, new services or components appear, data flows change | new tables, fields, indexes, component diagrams, dependencies |
| `docs/REQUIREMENTS.md` | any incoming request for a new feature, a behaviour change, or a correction to an existing function | a new numbered requirement, its description, and implementation status |
| `docs/REGRESSION_TEST.md` | features are added or existing behaviour changes | new cases for new features; updated cases where behaviour changed. Run the full pass on every version bump |
| `docs/BACKLOG.md` | a task is taken up, finished, or appears | the implementation scope, what did and did not make the version, and what remains |
| `docs/RELEASE.md` | the release or deployment procedure changes | the corrected step; keep the checklist runnable start to finish |

**A document that has drifted from the code is worse than a missing one.** This is not
theory: three documents once carried a storage schema version of 12 while the real one was
43, and it stopped nobody.

---

## 8. Architecture principles

### Crash-resilience — required for every feature

Any state whose loss breaks the user experience or the business logic **must** be
persisted:

- When designing a feature, work through the abnormal-termination scenario: crash,
  reboot, killed process.
- Timers, locks, progress — persisted at the moment the state changes, not on exit.
- On start, look for unfinished states and restore them.

### Unexpected failures stop the work; they do not continue it

- An **expected** failure — network down, server did not answer, file temporarily locked —
  is handled inside the specific operation, with bounded retries.
- An **unexpected** failure that reached the global handler: stop further operations, save
  diagnostics, and offer the operator "Restart" or "Close". Do not carry on in an unknown
  state, and do not write unverified in-memory state over good data on the way out. No
  infinite automatic restart loop.
- A read error must never turn into a silent reset. Factory defaults are acceptable
  automatically only on a confirmed first run — never after a failure to load an existing
  profile. Resetting to defaults is a separate, explicit operator action, because it
  erases passwords, tokens, and configuration.
- Until valid configuration is loaded, block every automatic save of it, including the
  save on window close.

### Modularity

- No source file over 800 lines; 200–400 is the normal range. A file approaching the limit
  gets logic extracted into a service or split by domain.
- Functions under 50 lines. No nesting deeper than four levels — use early returns.
- Business logic lives in services, not in UI code-behind. UI files bind and dispatch.
- A new feature that adds more than ~50 lines of UI glue gets its own file, named for the
  feature. Do not append to an existing file "because it is nearby".
- When developing, read only the file you need. Keep the file map in `CLAUDE.md` current
  so that stays possible.

---

## 9. Known-error identifiers

Entries in `docs/KNOWN_ERRORS.md` use a stable ID so code comments can point at them:

```
KE-YYYY-MM-DD-SHORT-SLUG
```

A comment explaining a non-obvious defence quotes the ID. That is how the reason survives
the next refactor — the alternative is that someone removes the defence because the code
looks redundant.
