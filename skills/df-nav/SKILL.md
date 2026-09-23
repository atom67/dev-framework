---
name: df-nav
description: Navigate a DEV Framework project — session brief, one block by id, index, checklist, handoff. Use at the start of every session in a framework project and when the operator asks where things stand, for one block by id, or to open, tick or hand off a checklist ("brief", "где мы", "чек-лист").
argument-hint: "brief | find <ID|keyword> | index | contract | checklist new|add|tick|show|archive <slug> | handoff <slug>"
allowed-tools: Bash, Read
---

**Which project.** If the operator's arguments (`$ARGUMENTS`) names a path, that is the target. Otherwise the target is the nearest
directory at or above the working directory that contains `.devframework/`, without crossing a git root. If there is none, list the immediate
subdirectories that contain `.devframework/` and **ask the operator which one** — never pick one by recency or
by guessing, and never run a framework command in a directory that has no framework installed.

Run the navigation command in the operator's arguments (`$ARGUMENTS`) (default `brief`) and work from its output instead of opening documents:

```bash
python <TARGET>/.devframework/navigate.py brief                 # doctor state, host rules, git (behind/ahead), untested cases, open known errors, active checklist + handoff
python <TARGET>/.devframework/navigate.py find UC-007           # one block, not a file; also works with a keyword
python <TARGET>/.devframework/navigate.py index                 # regenerate docs/INDEX.md
python <TARGET>/.devframework/navigate.py contract              # what doctor and finish demand
python <TARGET>/.devframework/navigate.py checklist new v1 "title"
python <TARGET>/.devframework/navigate.py checklist add v1 "item"
python <TARGET>/.devframework/navigate.py checklist tick v1 2
python <TARGET>/.devframework/navigate.py checklist show
python <TARGET>/.devframework/navigate.py handoff v1 --note "what the next session must know"
```

Rules:

- `brief` first in every session on a framework project; open a document only where the brief points.
- If the brief says **BEHIND** the upstream, pull or rebase before the first edit and re-read the files you will touch.
- Work that does not fit one iteration gets one checklist before the first code change; copy the live list
  (`checklist show`) at the end of every reply and write the handoff before the session ends.
