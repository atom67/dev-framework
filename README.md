# DEV Framework

The process layer extracted from a five-month project, packaged so the next project does
not have to rediscover it.

This is **not** a code framework. There is no library here, no dependency to add, no
runtime. It is the set of rules, document skeletons, and hard-won reasons that made the
source project stop losing work — plus one script that lays them into a repository.

## What is inside

| Path | What it is |
|---|---|
| `template/AGENTS.md` | the operating protocol: session-start reading, planning, definition of done, acceptance, execution cost, secrets, documentation maintenance, architecture principles |
| `template/CLAUDE.md` | project facts only — stack, structure, data locations, build commands. Deliberately thin, with an explicit ban on restating the rules |
| `template/docs/` | skeletons for requirements, architecture, backlog, known errors, regression plan, release checklist, and a checklist template for programmes of work |
| `LESSONS.md` | **read this one.** Every rule traced to the incident that produced it, with the real numbers |
| `install.ps1` | lays the template into a target repository |
| `skills/` | two skills for the AI agent doing the work — see below |

## Install

```powershell
.\install.ps1 -Target D:\DEV\NewProject -ProjectName "New Project"
```

Optional:

- `-ScaleTarget "50,000 users"` — the figure the cost rule is written against. Default is
  `10,000 users`.
- `-Force` — replace files that already exist. Without it, existing files are kept and
  reported, because clobbering a project's own `CLAUDE.md` is data loss.

Works on an empty directory and on a repository that already has content.

Verify the installer itself:

```powershell
.\install.ps1 -SelfTest
```

## After installing

1. Fill in `CLAUDE.md` — stack, structure, data locations, build commands.
2. Set the current schema version in `docs/ARCHITECTURE.md` if the project has one.
3. Confirm the scale target in `AGENTS.md` section 5 is the figure you actually mean.
4. Read `LESSONS.md` once. Rules whose reasons are unknown get deleted within a year.

## Skills for the agent

`install.ps1` copies files. It cannot ask what the scale target should be, read a stack out
of a manifest, or notice that the schema version in the template is a claim about code it
has never seen. Those steps decide whether the documents stay true, and they are the work
of whoever — or whatever — is at the keyboard.

`skills/` holds that part, written for an AI coding agent and usable by a person reading it
as a procedure. Both take the target repository as their argument and are run from this
repository, so `template/` stays exactly what gets laid into a project and nothing more.

| Skill | When |
|---|---|
| `import-dev-framework` | installing the package into a repository: settle the scale target with the operator, lay in the template, correct what substitution cannot reach, fill `CLAUDE.md` from the code, verify no placeholder survived |
| `catch-up` | the code already exists and the documents do not: reconstruct requirements, architecture, known errors, backlog, regression plan, and release procedure from the codebase, then run the cost and secret audits |

`catch-up` governs itself by the rule it enforces — on a large repository it opens a
checklist in `docs/` before its first edit and archives it at the end. Its one hard rule is
that a reconstructed statement is either read out of the code or listed as unconfirmed for
the operator. Six documents written at once is the highest-risk moment lesson 2 has, and a
plausible guess is never checked again.

Neither skill fixes what it finds. A ceiling found while costing, or a secret found in the
index, goes into the documents and to the operator as a decision — not into a quiet
refactor inside a documentation task.

## What was deliberately left out

The source project enforces several of these rules with about 1,200 lines of Python and
two git hooks — cost calculation, secret scanning, document drift, a one-command finish,
per-commit model attribution. Those are **not** included: the next project's stack is not
settled, and a check written for the wrong language is worse than no check.

The last section of `LESSONS.md` lists them, what each does, how portable each is, and the
three properties worth keeping whatever the language.

## Maintaining this package

When a project using it learns something the hard way, the lesson comes back here — the
incident with its numbers in `LESSONS.md`, the rule it produced in `template/AGENTS.md`.
A package that only ever flows outward goes stale in one project cycle.
