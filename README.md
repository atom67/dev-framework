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
