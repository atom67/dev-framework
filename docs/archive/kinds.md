# kinds — Development kinds: product / tool / explore (v1.3.0)

**Started:** 2026-09-23
**Status:** done 2026-09-23

## Scope agreed with the operator

What is in, and — just as important — what is explicitly out. Decisions the operator has
already made, quoted, so they are not silently re-litigated later.

- In: ...
- Out: ...

## Portions

One portion = one iteration the operator can accept or send back. Make it as large as
the documentation, code analysis and closing tests can honestly carry — not a week-long
stage, and not a handful of file-level chores.

### 1. <portion name>


**Acceptance:** what the operator will be shown when this portion is done — the check that
was performed and its result, in plain language. Not "open the file and look".

### 2. <portion name>


**Acceptance:** ...

## Deliberate limitations

Shortcuts taken on purpose, each with the ceiling it has and what an upgrade would cost.
Recording them here is what stops them being rediscovered as bugs.

- ...

## Handoff — update at every portion boundary and provider switch

### 2026-09-23 (written by navigate.py handoff)
- Branch/commit: main @ 592a59c; uncommitted: 1 file(s)
- Open items: 0 — programme finished
- doctor: READY (structure/configuration; tests not run — run `check.py finish`)
- Note: v1.3.0 released 2026-09-23 (592a59c, tag dev-framework--v1.3.0), CI green 4/4. Kinds product/tool/explore, run_smoke.py, GUIDE.html, promotion, init asks name→kind→scale→devlog. Next: owner's live test of a tool install; then hosts phase 0.


- Branch/base commit and task-owned uncommitted changes:
- Current portion and next concrete step (the live checklist is copied at the end of
  every operator reply; do not maintain a second list here):
- Agreed decisions and links to their source of truth:
- Commands/checks actually run, date, result/counts, environment and evidence:
- Checks not run, reason and remaining risk:
- Known errors or deliberate limits affecting continuation:
- Acceptance/commit/deploy authorization actually received (never infer it):

The next agent reconciles this with git and code; a stale handoff is not authority.

## Product decisions or external authorization still needed

Only choices the operator can make from the evidence presented, or authorization the
engineer cannot grant. Engineering smoke tests remain the engineer's responsibility;
if access is unavailable, record the unverified behaviour and risk in Handoff above.

- [x] verification.py: KINDS, product-only docs, required(kind), kind from manifest; doctor per kind; tool checks docs/GUIDE.html
- [x] install.py: --kind (default product; old manifests read as product); kind blocks in templates; promotion explore→tool→product on --update, never downward
- [x] templates: kind blocks in AGENTS.md, PROJECT.md, KNOWLEDGE_MAP, entry-point pattern; docs/GUIDE.html; run_smoke.py; project.json per kind
- [x] check.py: finish without a test command for explore (says nothing is proven); selftest per kind; navigate brief/contract show the kind
- [x] init questions one by one: name → kind → scale (product only) → devlog; commands/init.md, df-import skill, Hermes df_init
- [x] tests: one comprehensive test per kind + promotion + old manifest; README section; v1.3.0; gate once; push; CI green
