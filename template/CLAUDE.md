# {{PROJECT_NAME}}

> **Read `AGENTS.md` first.** It holds the operating protocol: session-start reading,
> planning rules, definition of done, acceptance, cost, secrets, and documentation
> maintenance. This file holds only facts about *this* project.
>
> **Do not copy process rules into this file.** They are stated once, in `AGENTS.md`.
> Two copies drift, and the reader has no way to tell which one is current.

## Project overview

<!-- One paragraph: what this is, who uses it, what problem it solves. -->

{{PROJECT_NAME}} — …

## Tech stack

<!-- Runtime, language version, UI framework, storage, key libraries. Keep it to what a
     newcomer needs before touching code. -->

- …

## Project structure

<!-- The file map. This is what makes "read only the file you need" possible, so it has to
     stay current. One line per file or directory, saying what lives there. -->

```
{{PROJECT_NAME}}/
├── AGENTS.md                    # operating protocol — read first
├── CLAUDE.md                    # <-- this file
├── docs/
│   ├── REQUIREMENTS.md          # numbered requirements, product principles
│   ├── ARCHITECTURE.md          # architecture, data schema, data flows
│   ├── BACKLOG.md               # the operational queue
│   ├── KNOWN_ERRORS.md          # known bugs, limitations, debt
│   ├── REGRESSION_TEST.md       # regression plan
│   ├── RELEASE.md               # release and deployment checklist
│   └── archive/                 # finished programmes of work
└── …
```

## Data storage

<!-- Where settings, databases, caches, and logs actually live on disk, with the real
     paths. State the current schema version here if there is one. -->

- Settings: …
- Database: … (schema v…)
- Logs: …

## Build and run

<!-- The exact commands. Include what must be stopped first, and what to relaunch after. -->

```bash
# Build
…

# Run
…
```

## Conventions specific to this project

<!-- Naming, namespaces, language of comments and docs, framework quirks, known
     workarounds a newcomer would otherwise trip over. Conventions only — no process
     rules. -->

- …

## Notes for development

<!-- Sharp edges that are true today: things deliberately not done, known couplings,
     places that need elevated rights, manual migrations. Delete an entry when it stops
     being true rather than leaving it to rot. -->

1. …
