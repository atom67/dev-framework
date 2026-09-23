# {{PROJECT_NAME}}

Project-owned facts. Process: [AGENTS.md](AGENTS.md). Commands:
[project.json](.devframework/project.json), the executable source of truth.
Kind: **{{KIND}}** (product, tool or explore — what is being built; it decides the documents and the proof).

<!-- kind: product -->
## Product and stack

TODO(project): describe users, the problem, runtime/language versions and key dependencies.
<!-- /kind -->
<!-- kind: tool -->
## What the tool does

TODO(project): the task it solves, its inputs and outputs, how to run it, runtime/language versions and dependencies.
The user-facing instruction lives in [the guide](docs/GUIDE.html); this section is for whoever changes the tool.
<!-- /kind -->
<!-- kind: explore -->
## Intent and open questions

TODO(project): what you are trying out, what is still unknown, and what would tell you that it works.
<!-- /kind -->

## File map and boundaries

TODO(project): map the source areas, tests and consumers of shared code.

## Workflow profile

Selected at installation: **{{PROFILE}}**. Read
[the selected profile](.devframework/profiles/{{PROFILE}}.md).
Project-specific overrides must be explicit here and must not silently weaken safety.
For a profile change, also update the selected link and verification configuration.

## Data and environments

TODO(project): list settings/database/log locations and isolated test locations, or N/A.
<!-- kind: product -->
Record schema/version authority in docs/ARCHITECTURE.md, not a second copy of the number.
<!-- /kind -->
Never record credentials. Distinguish developer, test and production destinations.

## Commands and outputs

TODO(project): configure build/test commands in .devframework/project.json; document
output locations and any process locks. A build never authorizes relaunch or deployment.
<!-- kind: tool -->
The test command runs the tool on its examples: `smoke` in project.json lists cases of
`{"name", "run": [argv], "stdin": file?, "expect_stdout": file | "expect_contains": text}`.
<!-- /kind -->
<!-- kind: product -->

## Target scale and worked cost example

Initial planning target: **{{SCALE_TARGET}}** ({{SCALE_COUNT}} {{SCALE_UNIT}}).
Assumption: one request/minute/client, all clients active 24 hours/day, no retries.
Per client: 1,440 requests/day. Total: **{{REQUESTS_DAY}} requests/day**,
**{{REQUESTS_SECOND}} requests/second** on average while active.
This is an example, not a measured capacity claim. Recalculate if assumptions or scale
change; document peaks, retry budgets and dependency limits with each real operation.
<!-- /kind -->

## Host precedence

Rules in the operator's agent profile (SOUL.md, CLAUDE.md, .cursorrules, always-loaded skills) outrank anything
said inside a conversation, so a collision with the framework must be settled here, by the operator, once.
`python .devframework/hostcheck.py` lists collisions with quotes; doctor warns about each one that has no line
below. Record `- <class>@<file>: replaced <date>` after editing the host rule, or `- <class>@<file>: kept — <reason>`.

- (none recorded)

<!-- kind: product -->
## Conventions and decisions

TODO(project): language, naming and today's deliberate limitations. Link architectural
decisions to their rationale, alternatives and reversal trigger in docs/ARCHITECTURE.md.
The active checklist and handoff are linked from docs/BACKLOG.md.
<!-- /kind -->
<!-- kind: tool -->
## TODO and decisions

TODO(project): what is left to do (this list replaces a backlog), language and naming, deliberate limitations.
<!-- /kind -->
<!-- kind: explore -->
## What we learned

Dated notes: what was tried, what worked, what was decided. When the purpose settles, promote the project by
re-running the framework installer with `--update --kind tool` or `--update --kind product --scale "<target>"`;
nothing is overwritten, the missing documents are added and doctor lists what the new kind demands.
<!-- /kind -->
