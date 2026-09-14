---
name: import-dev-framework
description: Install the DEV Framework into a repository — lay in AGENTS.md, CLAUDE.md and the docs/ set, substitute the project name and scale target, fill CLAUDE.md from facts read out of the code, and verify nothing was left as a placeholder. Use when the operator says "import the framework", "install DEV Framework", "set up AGENTS.md", "adopt these rules in this project", "внедри фреймворк", "поставь правила в проект".
argument-hint: "<target-repo-path> [project name]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Import the DEV Framework into a repository

The package is a process layer, not a library. Installing it means the target repository
gains an operating protocol, a thin facts file, and six document skeletons — and that the
agent working there starts obeying them.

Laying the files down is the easy part and takes one command. The part that decides
whether this survives is steps 4 and 5: a template that keeps its placeholders, or a
`CLAUDE.md` full of `…`, teaches everyone that these documents are decoration.

## 0. Read the reasons first

Read `LESSONS.md` in this repository before installing anything. Every rule in
`template/AGENTS.md` was bought with an incident, and the incidents carry the numbers.

This is not ceremony. A rule whose reason is unknown gets deleted within a year by someone
who finds it inconvenient — and they are not being careless, they genuinely cannot see
what it is holding up. You are about to be the first reader of these rules in the target
project. If you cannot say what a rule is protecting, you will not enforce it.

## 1. Survey the target

Before writing anything, establish:

- Is the target empty, or a repository with existing content and history?
- What is the language, build system, and entry point?
- Does it already have `CLAUDE.md`, `AGENTS.md`, `README.md`, or a `docs/` directory?
  **Never overwrite an existing `CLAUDE.md`.** It holds project facts that nobody else
  has; clobbering it is data loss, and that is why the installer refuses without `-Force`.
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

On Windows, or anywhere PowerShell is available:

```powershell
.\install.ps1 -Target <path> -ProjectName "<name>" -ScaleTarget "<figure>"
```

Verify the installer itself first with `.\install.ps1 -SelfTest`. Run it without `-Force`.
Existing files are then kept and reported; read that report, and merge by hand rather than
re-running with `-Force`.

Where PowerShell is not available, do the same thing directly: copy everything under
`template/` into the target, preserving relative paths, replacing `{{PROJECT_NAME}}` and
`{{SCALE_TARGET}}` in the file contents, skipping any destination file that already
exists, and writing UTF-8 **without a BOM** — a BOM shows up as a stray character in every
tool that reads markdown as plain text.

## 4. Correct what the substitution cannot reach

The installer replaces placeholder tokens. It does not do arithmetic and it does not know
your codebase, so three things are left wrong on purpose-built templates. Fix all three
before showing anything to the operator.

**The worked cost example.** `AGENTS.md` section 5 carries an example calculation whose
numbers were computed for the template's default figure. After substitution the sentence
reads as though it were computed for *your* scale target, and it was not. Recompute it:
per-device rate → per-day → multiplied by the real target → per second. An example that
contradicts the rule it illustrates is the first thing a reader will copy.

**The schema-version claim.** `docs/ARCHITECTURE.md` asserts `Current schema version: v1`.
That is an assertion about the code, and the framework's own rule is that a document
which has drifted is worse than a missing one — the missing one sends you to the code, the
drifted one confidently lies and you believe it. Read the real version out of the code or
the migrations and write it down. If the project has no schema at all, delete the claim
and say so in one sentence; do not leave `v1` standing.

**Comment syntax in examples.** The `cost:` example is written with `//`. In a Python,
Ruby, or shell project it should be `#`. A reader copies the example verbatim.

Then confirm nothing was missed:

```bash
grep -rn '{{' <target> --include='*.md'
```

That must come back empty.

## 5. Fill CLAUDE.md from the code, not from imagination

`CLAUDE.md` arrives as a skeleton of `…` placeholders. Fill it by reading the repository:

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
them twice guarantees they diverge. Do not leave a `…` standing: an unfilled section
reads as "this document is not maintained", which becomes true shortly afterwards.

If a fact cannot be established from the code, write what you did establish and mark the
gap explicitly as unknown. A named gap gets filled; a plausible guess never gets checked.

## 6. Verify before claiming

- `install.ps1 -SelfTest` passes.
- Every file the installer reported as written exists.
- No `{{` remains in any markdown file in the target.
- The recomputed cost example is arithmetically right at the chosen scale target — do the
  multiplication yourself and confirm the printed numbers.
- The schema version in `docs/ARCHITECTURE.md` matches what the code says, or the claim
  is gone.
- No previously existing file was overwritten. Diff against the pre-install state.

## 7. Hand it over

Acceptance goes to a product owner. It does not contain "open `AGENTS.md` and read
section 5".

Report: which files were added and which were kept untouched; the scale target now in
force and one sentence on what it will change day to day; any second copy of process rules
found in step 1 and the recommendation to delete it; anything in `CLAUDE.md` you could not
determine and need them to answer.

Then say what happens next, because the rules only start working when they are read:

- Every session from now on begins with `AGENTS.md`.
- The `docs/` set arrives as skeletons and fills up as work passes through it. Do not
  schedule a day to write them all — documents written in one sitting for their own sake
  are the ones that drift first.
- If the target already has a substantial codebase, the skeletons can be reconstructed
  from what is already built: run **`catch-up`** next. It also performs the cost and
  secret audits that this framework exists to make routine.
