# {{PROJECT_NAME}}

Project-owned facts. Process: [AGENTS.md](AGENTS.md). Commands:
[project.json](.devframework/project.json), the executable source of truth.

## Product and stack

TODO(project): describe users, the problem, runtime/language versions and key dependencies.

## File map and boundaries

TODO(project): map the source areas, tests and consumers of shared code.

## Workflow profile

Selected at installation: **{{PROFILE}}**. Read
[the selected profile](.devframework/profiles/{{PROFILE}}.md).
Project-specific overrides must be explicit here and must not silently weaken safety.
For a profile change, also update the selected link and verification configuration.

## Data and environments

TODO(project): list settings/database/log locations and isolated test locations, or N/A.
Record schema/version authority in docs/ARCHITECTURE.md, not a second copy of the number.
Never record credentials. Distinguish developer, test and production destinations.

## Commands and outputs

TODO(project): configure build/test commands in .devframework/project.json; document
output locations and any process locks. A build never authorizes relaunch or deployment.

## Target scale and worked cost example

Initial planning target: **{{SCALE_TARGET}}** ({{SCALE_COUNT}} {{SCALE_UNIT}}).
Assumption: one request/minute/client, all clients active 24 hours/day, no retries.
Per client: 1,440 requests/day. Total: **{{REQUESTS_DAY}} requests/day**,
**{{REQUESTS_SECOND}} requests/second** on average while active.
This is an example, not a measured capacity claim. Recalculate if assumptions or scale
change; document peaks, retry budgets and dependency limits with each real operation.

## Conventions and decisions

TODO(project): language, naming and today's deliberate limitations. Link architectural
decisions to their rationale, alternatives and reversal trigger in docs/ARCHITECTURE.md.
The active checklist and handoff are linked from docs/BACKLOG.md.
