# DEV Framework as a product — plugin, hosts, evals

**Started:** 2026-09-21
**Status:** in progress

## Scope agreed with the operator

- In: DEV Framework for beginner/intermediate vibe-coders so agents document work and read the documents
  instead of re-deriving context; measured by tool calls / seconds / reasoning per session and by quality
  (use case ↔ module ↔ test). Hermes first, then Claude Code, Cursor, Codex.
- Decided 2026-09-21: three layers in one repository — **core** (template + scripts, any host, stdlib) →
  **skills** (agentskills.io SKILL.md, every host) → **adapters** (Hermes plugin.yaml/__init__.py, Claude Code
  plugin manifest + hooks; Cursor/Codex need none). A feature lands in core first, the skill points at it,
  the adapter only wraps. One VERSION.
- Decided 2026-09-21: `hostcheck` in doctor comes **after** the plugin eval, so effects are not mixed.
- Decided 2026-09-21: the reply shape Tech / Message (ending with the explicit ask) is a framework rule;
  parallel subagents and the checklist copied at the end of every reply stay mandatory in every host
  context file (AGENTS.md, .hermes.md, skills).
- Out (for now): MCP server over the tools — only if Claude Code evals show the agent needs explicit tools;
  lite profile and GUIDE split — operator decision pending (TOKEN_BUDGET §D).

## Portions

### 1. Plugin v0.4.0 measured against the skills baseline

- [x] Plugin built: df_init / df_check / df_nav, bundled skills df-import / df-catch-up, navigate.py, quiet
      finish, selftest, .hermes.md, scripts/run_tests.sh; 100 tests green (2026-09-21)
- [x] Tech / Message reply rule, parallel subagents and per-reply checklist copy present in AGENTS.md,
      .hermes.md and both skills (audited 2026-09-21)
- [x] Commit v0.4.0 (ff0386d, 2026-09-21)
- [x] Plugin evals S1–S3 in profile `mastermind` (2026-09-21, gpt-5.6-terra): calls 0.33–0.55×, input tokens
      0.30–0.47×, active seconds 0.47–0.75× of the skills baseline; quality equal or better (S3: 3/3 planted
      questions, no extras). Report `evals/runs/2026-09-21_plugin.md`
- [x] Verified: no post-report ad-hoc scripts, no hub detour, foreign skills reported (`known-errors` 46k via SOUL)
- [x] Fixed what the runs showed (2026-09-21): doctor names the exact profile-link path; the test-command SETUP
      message names the counted runner argv and warns that bare unittest/pytest fails finish; seeded root `.gitignore`
- [x] Clean re-run 2026-09-21 14:05 (`evals/runs/2026-09-21_plugin_clean.md`): quality equal, .gitignore fix confirmed;
      reply-shape conflict result = **both blocks** (Message appears, SOUL footer stays) → cannot be won from inside
      the conversation; handed to portion 2
- [ ] Eval REPORT template gets the 🛠️ Tech / 💬 Message shape itself (eval defect found in the clean run)
- [ ] FOLLOWUP evals (new session on S1/S2 results) for skills and plugin — the "agent reads instead of
      re-deriving" metric

**Acceptance:** a table skills vs plugin per scenario (seconds, calls, reasoning, questions, quality columns)
and the verdict against the ≤ 0.7× target, in plain language.

### 2. Host conflicts caught by doctor (`hostcheck`)

- [x] `.devframework/hostcheck.py` (f8e3e65): host context (HERMES_HOME SOUL.md, ~/.claude/CLAUDE.md + rules,
      ~/.codex/AGENTS.md, .cursorrules / .cursor/rules), detect conflict classes with file:line quotes:
      per-reply blocks on both sides · "read skill X before any task" · test/commit rules against the gate ·
      bans on files the framework maintains · duplicate rule sources
- [x] `## Host precedence` register in PROJECT.md template; doctor WARNING for a detected conflict with no
      recorded decision; re-checked on every doctor/finish (SOUL edited later → surfaces again)
- [x] df-import / df-catch-up: step "hostcheck, one list to the operator, edit with authorization, record decisions"
- [x] Tests (4): planted SOUL + referenced skill → 6 conflicts; recorded decisions → none; rule added later → surfaces
- [x] S2 plugin eval 2026-09-22 with a hardened profile (test block in SOUL: read-skill-first, commit-after-every-change,
      no-tests; conflict skill `ship-fast`: docs ban, ad-hoc verify, auto-push) — 8 conflicts expected; operator gives one
      decision — result in `evals/runs/2026-09-22_hostcheck.md`: reply shape won (0 footers), all four harmful rules
      ignored in practice, 8 conflicts surfaced; defect (agent recorded decisions itself) fixed in 8ab31c1
- [x] Phase B 2026-09-22: a rule added to SOUL **after** installation surfaced in `brief` as "1 unresolved", the agent
      stopped with one clarify question, then rewrote SOUL / ship-fast / known-errors to be framework-aware (backups),
      recorded 9 `replaced` decisions and reran hostcheck CLEAN; the feature itself went RED→GREEN, finish 9/9, `7c266f0`
- [ ] Restore the owner's profile: remove the test block from SOUL, delete `ship-fast`, keep or revert the reworded rules

**Acceptance:** doctor output on the owner's real profile listing the actual collisions (known-errors skill,
🟢 footer, RED-first) with their recorded decisions.

### 3. Second host: Claude Code adapter

- [x] `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` (repo is its own marketplace, source `./`),
      `commands/{init,check,nav}.md`, `hooks/hooks.json` → `scripts/claude_session_start.py` (injects `navigate.py brief`
      when the cwd or a parent holds `.devframework/`, silent otherwise); the existing `skills/df-*` are discovered as-is.
      `claude plugin validate .` passes; 4 tests in `tests/test_claude_plugin.py`
- [ ] Evals S1–S3 in Claude Code (same fixtures, same prompts, measure from the Claude session log)
- [x] README host matrix: Hermes / Claude Code / any agent with a shell

**Acceptance:** S2 passes in Claude Code with the same quality columns; brief appears without a call.

### 4. Cursor and Codex via skills only

- [ ] Confirm both load `skills/df-*/SKILL.md` unchanged (agentskills.io); note any frontmatter differences
- [ ] Smoke S1 in each (no measurement harness yet — record calls by hand)

**Acceptance:** one paragraph per host in README saying what was verified.

### 5. Public release

- [ ] Operator decisions: lite profile (4 documents) for novices; GUIDE split (agent-facing vs human-facing)
- [ ] Sanitizer/PII pass (evals fixtures, docs, memory references) — nothing personal in the public tree
- [ ] Push to GitHub; plugin-catalog entry PR in NousResearch/hermes-agent (`plugin-catalog/dev-framework.yaml`,
      40-hex SHA pin, capabilities from `hermes plugins doctor` on upstream main); Discord
      `#plugins-skills-and-skins` post with the eval numbers
- [ ] Fresh-profile eval runs as the second protocol column

**Acceptance:** catalog entry merged or reviewed; README numbers match RESULTS.md.

### 6. Custom skill: developing in the Hermes environment

- [ ] Write `skills/hermes-dev/SKILL.md` (host-specific, for the framework author and Hermes plugin developers)
      collecting every finding from this programme: plugin loader contract (`plugin.yaml` + `__init__.py`,
      `register(ctx)`, tool schema shape, `register_skill` namespacing, plugins discovered at **process** start —
      Desktop needs a restart, `hermes plugins install file://…`), skills-guard blocking any skill that mentions
      the context files, verify-on-stop and how `scripts/run_tests.sh` + `record_terminal_result` satisfy it,
      context-file precedence (`.hermes.md` > AGENTS.md, cwd-only, promptware scan), SOUL rule stacking and
      the reply-shape conflict, `state.db` schema for measurement, git-bash vs Windows paths, Desktop has no
      agent-plugin UI (install from chat), `hermes profile create --clone-from`, quotas shared across profiles
- [ ] Verify each statement against the current Hermes checkout (version-stamped); mark anything unverified
- [ ] Reference it from README (host matrix) and from `evals/README.md`

**Acceptance:** a new session given only this skill can install, evaluate and debug the plugin without re-deriving
any of the above.

## Deliberate limitations

- Interference is measured by skill_view bytes and by reading the dialogue; no automatic "conflict happened"
  detector in the evals yet — hostcheck (portion 2) is the first step.
- `measure.py` reads Hermes state.db only; other hosts need their own log readers.
- The cost audit is not simulated by selftest (reading exercise by design).

## Handoff — update at every portion boundary and provider switch

### 2026-09-22 (written by navigate.py handoff)
- Branch/commit: main @ 9d11ad4; uncommitted: 17 file(s)
- Open items: 17; next: [8] Eval REPORT template gets the 🛠️ Tech / 💬 Message shape itself (eval defect found in the clean run)
- doctor: READY (structure/configuration; tests not run — run `check.py finish`)
- Note: Self-hosting landed: the repository now runs on its own framework (generated .devframework is git-ignored, refresh command in PROJECT.md). doctor READY, finish PASSED 110 tests/2 skipped. Claude Code cache is a junction to this repo, so edits are live without reinstall. Uncommitted: AGENTS.md/CLAUDE.md replaced by the framework contract (old maintainer rules moved into PROJECT.md), .gitignore, PROJECT.md, new docs seeds, scripts/run_tests.sh, UTF-8 git decoding fix in template navigate/devlog + its regression test. Nothing committed or pushed.


- Branch/base commit and task-owned uncommitted changes: `main`; plugin v0.4.0 work uncommitted until the
  authorized commit in portion 1.
- Current portion and next concrete step: portion 1 — commit, then the operator runs the three plugin prompts.
- Agreed decisions and links to their source of truth: this file (Scope); `docs/TOKEN_BUDGET_2026-09-20.md`.
- Commands/checks actually run, date, result/counts: `python scripts/verify.py` 2026-09-21 — 100 tests OK,
  0 secret suspects; plugin loaded in a temp HERMES_HOME, three tools dispatched through the registry.
- Checks not run, reason and remaining risk: plugin evals (need the commit); `df_check finish` evidence
  recording inside a live Hermes session (unit-level only).
- Known errors or deliberate limits affecting continuation: skills hub install blocked by skills-guard —
  the plugin is the distribution form.
- Acceptance/commit/deploy authorization actually received: commit authorized 2026-09-21 (chat); no push.

## Product decisions or external authorization still needed

- [ ] Lite profile as the default for novices (cuts 5 of 9 documents)
- [ ] GUIDE split of the templates
- [ ] Public repository name and the moment of the first push
- [ ] Release discipline for Claude Code: bump VERSION + both manifests, then `claude plugin tag` (consumers only see a change when the version moves)
