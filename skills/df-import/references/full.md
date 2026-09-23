# Import the DEV Framework into a repository

The package is a process layer, not a library. Installing it means the target repository
gains an operating protocol, a thin facts file, and the `docs/` skeletons including
requirements, architecture, use cases, backlog, known errors, regression, release and
copy templates — and that the agent working there starts obeying them.

Laying the files down is the easy part and takes one command. The part that decides
whether this survives is steps 4 and 5: a template that keeps its placeholders, or a
`PROJECT.md` full of `TODO(project):`, teaches everyone that these documents are decoration.

## 0. Read the reasons first

Read `LESSONS.md` in this repository before installing anything. Every rule in
`template/AGENTS.md` was bought with an incident, and the incidents carry the numbers.

This is not ceremony. A rule whose reason is unknown gets deleted within a year by someone
who finds it inconvenient — and they are not being careless, they genuinely cannot see
what it is holding up. You are about to be the first reader of these rules in the target
project. If you cannot say what a rule is protecting, you will not enforce it.

## 1. Survey the target

Before writing anything, establish (run independent survey questions in parallel
subagents when the host provides them):

- Is the target empty, or a repository with existing content and history?
- What is the language, build system, and entry point?
- Does it already have `CLAUDE.md`, `AGENTS.md`, `PROJECT.md`, `README.md`, or a `docs/`
  directory? **Never overwrite an existing `CLAUDE.md` or `AGENTS.md`.** Project facts
  that nobody else has live in those files (and after install, in `PROJECT.md`);
  clobbering them is data loss, and that is why the installer refuses without `-Force`.
- Does it already have tests? Note the runner and whether they are isolated from real
  data. Import does not write tests; it must not claim the product is verified. Catch-up
  maps existing tests onto use-case `Test:` fields.
- Is there a second copy of any process rules already in the repository — a `CONTRIBUTING`,
  a `.cursorrules`, a rules block inside `README.md`? Note them. They become duplicates
  the moment `AGENTS.md` lands, and duplicated rules drift (lesson 7).

## 2. Settle the two substitutions

`{{PROJECT_NAME}}` — the name the operator uses for the product, not the directory name.

`{{SCALE_TARGET}}` — the figure every `cost:` calculation in the project will be written
against. **Ask the operator.** It is a product decision, not a technical default, and the
template's `10,000 users` is a placeholder for a project that no longer exists. Getting it
wrong makes every cost calculation in the project wrong in the same direction.

Ask for the figure they actually mean at the horizon they care about — an internal tool
for one company and a public service differ by three orders of magnitude, and the whole
point of the rule is that the arithmetic is real.

## 3. Lay in the template

Preview first; it must create no target files:

Profiles: `generic` (default), `personal-desktop`, `service`. Ask the operator if the
target is a personal desktop app or a service; do not guess:

```text
python scripts/install.py --target <path> --name "<name>" --profile generic --scale "<figure>" --dry-run
```

Verify this package first with `python -B scripts/verify.py`.
Run install without `--force`. Existing files are then kept or conflict; read that report,
and merge by hand rather than re-running with `-Force`.

Do not copy `template/` by hand. The installer computes the scale arithmetic, writes
`PROJECT.md`, and seeds `docs/USE_CASES.md` plus the copy templates. A manual copy misses
that and leaves placeholders the doctor will reject.

## 4. Correct what the substitution cannot reach

The installer replaces placeholder tokens and **does** compute the worked totals in
`PROJECT.md` for the scale you passed. It still does not know the codebase. Fix these
before showing anything to the operator.

**Project facts.** Fill `TODO(project):` in `PROJECT.md` and `docs/ARCHITECTURE.md` from
the code, or write N/A. `CLAUDE.md` is only the adapter (`@AGENTS.md` / `@PROJECT.md`);
do not paste process rules or a second stack description there.

**The schema-version claim.** Read the real version out of the code or the migrations.
If there is no schema, delete any current-version claim and say so in one sentence.
A drifted version is worse than a missing one.

**Example use cases.** `docs/USE_CASES.md` arrives with composition rules and example
`UC-001` / `UC-002` / `SET-001` rows, plus `docs/USE_CASE_TEMPLATE.md` and
`docs/USE_CASES_SLICE_TEMPLATE.md`. Confirm those three files exist. Do not invent a
full catalogue during import. If the target already has a substantial codebase, run
**`catch-up` next** — that is where cases are reconstructed and tests are mapped onto
the `Test:` field.

**Comment syntax in examples.** A `cost:` example copied into code must use that
language's comment marker. A reader copies the example verbatim.

Then confirm nothing was missed:

```bash
grep -rn '{{' <target> --include='*.md'
```

That must come back empty.

## 5. Fill PROJECT.md from the code, not from imagination

`PROJECT.md` arrives with `TODO(project):` markers. Fill it by reading the repository:

- **Project overview** — one paragraph: what it is, who uses it, what problem it solves.
- **Tech stack** — runtime and language version as actually pinned, UI framework, storage,
  the libraries a newcomer meets in the first hour. Read them from the manifest and lock
  files, not from memory.
- **Project structure** — the file map, one line per file or directory. This is what makes
  "read only the file you need" possible, so it has to be real and it has to stay current.
- **Data storage** — the real paths of settings, databases, caches, and logs, plus the
  current schema version if there is one.
- **Build and run** — the exact commands, including what must be stopped first and what to
  relaunch afterwards.
- **Conventions** — naming, comment language, framework quirks, workarounds a newcomer
  would trip over. Conventions only.
- **Notes for development** — sharp edges that are true today: things deliberately not
  done, known couplings, places needing elevated rights, manual migrations.

Two prohibitions. Do not restate process rules here — they live in `AGENTS.md` and stating
them twice guarantees they diverge. Do not leave a `TODO(project):` standing: an unfilled
section reads as "this document is not maintained", which becomes true shortly afterwards.
Configure real build/test argument arrays in `.devframework/project.json` only when you
have isolated tests; leaving them unconfigured is correct. Doctor will then report
NOT READY. That is not a licence to point tests at a live database to make it green.

If a fact cannot be established from the code, write what you did establish and mark the
gap explicitly as unknown. A named gap gets filled; a plausible guess never gets checked.

## 6. Verify before claiming

- `python -B scripts/verify.py` passes in **this** package.
- In the **target**: `docs/USE_CASES.md`, `docs/USE_CASE_TEMPLATE.md` and
  `docs/USE_CASES_SLICE_TEMPLATE.md` exist.
- `python .devframework/check.py doctor --structural` in the target is green on the
  scaffold (required files, links, catalogue ID contract). Default doctor is
  NOT READY until facts and test commands are filled — that is expected.
- No `{{` remains in any markdown file in the target.
- The printed totals in `PROJECT.md` match the scale arithmetic for the chosen figure —
  do the multiplication yourself.
- The schema version in `docs/ARCHITECTURE.md` matches what the code says, or the claim
  is gone.
- No previously existing file was overwritten. Diff against the pre-install state.
- Do not run `finish` as proof the product works. Finish needs configured, isolated tests
  and counted evidence; a fresh import has not earned that.

## 7. Hand it over

Acceptance goes to a product owner. It does not contain "open `AGENTS.md` and read
section 5".

Report: which files were added and which were kept untouched; the scale target now in
force and one sentence on what it will change day to day; any second copy of process rules
found in step 1 and the recommendation to delete it; anything in `PROJECT.md` you could not
determine and need them to answer; that the use-case file is still the example scaffold
unless catch-up ran.

Then say what happens next, because the rules only start working when they are read:

- Every session from now on begins with `AGENTS.md`.
- The `docs/` set arrives as skeletons and fills up as work passes through it. Example
  use cases are placeholders; real paths and their `Test:` status come with catch-up or
  with later features. Do not schedule a day to write them all for their own sake.
- If the target already has a substantial codebase, run **`catch-up`** next. It
  reconstructs the catalogue from the code, maps existing tests onto cases, and
  performs the cost and secret audits.
