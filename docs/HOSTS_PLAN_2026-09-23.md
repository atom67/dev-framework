# Hosts plan: Codex, Cursor, OpenCode

Date: 2026-09-23. Status: **plan, nothing implemented**. Owner of decisions: the operator.
Checklist: [PLUGIN_CHECKLIST.md](PLUGIN_CHECKLIST.md) portion 4. Base: v1.2.2 (Hermes + Claude Code adapters shipped).

The rule stays the same for every host: **core** (`template/` + `scripts/install.py` + `.devframework/*.py`) →
**skills** (agentskills.io `SKILL.md`) → **thin adapter**. An adapter holds no logic. The version is one `VERSION`
shared by every manifest.

Host facts below were researched on 2026-09-23 from each host's official documentation (sources at the end).
Anything marked **UNVERIFIED** must be confirmed by a live run before the phase that depends on it.

## 1. What each host offers (facts)

| Capability | Claude Code (shipped) | Codex | Cursor | OpenCode |
|---|---|---|---|---|
| Plugin manifest | `.claude-plugin/plugin.json` | root `plugin.json`, Agent Plugins schema (agent-plugins.org); `.codex-plugin/plugin.json` fallback | `.cursor-plugin/plugin.json`, **or** root `plugin.json` in the Agent Plugins format | JS/TS module (`.opencode/plugins/` or npm package listed in `opencode.json`) |
| Marketplace / install | repo = marketplace; `claude plugin marketplace add owner/repo` | `.agents/plugins/marketplace.json`; `codex plugin marketplace add owner/repo`; `/plugins` | `.cursor-plugin/marketplace.json`; editor sidebar, or CLI `/plugin marketplace add <git-url>`; local `~/.cursor/plugins/local/<name>` | npm package in `"plugin": [...]`, or a file in `~/.config/opencode/plugins/` |
| Skills (`SKILL.md`) | plugin `skills/` | plugin `skills/`; `.agents/skills` (cwd → repo root), `~/.agents/skills` | plugin `skills/`; `.agents/skills`, `.cursor/skills`, `~/.agents/skills`, also `.claude/skills` | `.opencode/skills`, `.agents/skills`, `.claude/skills` (+ `~/.config/opencode/skills`); `name` must equal the folder name |
| Slash commands | plugin `commands/*.md` | **none in plugins**; custom prompts are *deprecated — "use skills"* | plugin `commands/*.md` (arguments syntax UNVERIFIED) | `.opencode/commands/*.md`, `$ARGUMENTS`, `$1…`, `` !`cmd` `` |
| Session-start context | `SessionStart` hook, stdout → context | `SessionStart` hook, **stdout → developer context**; plugin `hooks/hooks.json`; user must trust the hook once | `sessionStart` hook, JSON `{"additional_context": …}`; **Windows bug: sessionStart may produce no output** (forum, Feb 2026) | plugin: `experimental.chat.system.transform` or `session.prompt({noReply:true})` on `session.created` (both UNVERIFIED end-to-end) |
| AGENTS.md | via `CLAUDE.md` → `@AGENTS.md` | native; `AGENTS.override.md` wins; git root → cwd; cap 32 KiB | native, nested; `.cursor/rules/*.mdc`; `.cursorrules` legacy | native; `CLAUDE.md` fallback; `instructions` array |
| Sandbox vs our gates | none by default | `workspace-write` + `on-request`; **network off**, **`.git` read-only** | sandbox (macOS/Linux) blocks `.git/config`, limited network; Windows sandbox UNVERIFIED | bash **allowed** by default |
| Windows | native | native CLI + native sandbox | editor native; hooks run through PowerShell → call `python` directly | native, WSL recommended; shell may be Git Bash or cmd |
| Installed on the owner's PC (2026-09-23) | yes | `~/.codex` present, `codex` CLI not on PATH | Cursor 3.18.9 | no |

**Two findings that shape the plan:**

1. **Codex and Cursor both read the portable Agent Plugins manifest** (root `plugin.json`, `$schema`
   agent-plugins.org). One manifest can serve both, with host-specific blocks under `extensions`. Each of them also
   loads plugin `skills/` automatically. So Codex + Cursor is **one adapter, not two**.
2. **Slash commands do not travel; skills do.** Codex dropped commands in favour of skills. Cursor and OpenCode
   accept both, and Claude Code invokes skills with `/` as well. Moving `init / check / nav` into skills removes the
   only per-host content we would otherwise have to maintain in three formats.

## 2. Phase 0 — shared groundwork (before any new host)

Each item benefits the shipped Claude Code and Hermes adapters too.

- [x] **Done v1.5.0. Fix: brief reports "up to date" after a failed fetch.** `navigate.freshness()` ignores the return code of
      `git fetch`. In a sandbox without network (Codex default) or offline, the fetch fails quietly and the brief
      compares against **stale** remote refs. Check the return code and report
      `remote: not checked (fetch failed — offline or sandbox)`. One regression test: an unreachable remote.
- [x] **Done v1.5.0 (D1-A: commands are one-line aliases). Commands → skills.** Add `skills/df-init`, `skills/df-check`, `skills/df-nav` carrying the text of
      `commands/*.md` (project resolution, "ask, never guess"). Keep `commands/` as thin aliases for Claude Code and
      Cursor, or delete them — **operator decision D1**.
- [x] **Done v1.5.0 as a rename; `--format` waits for the Phase 2 Cursor spike (its JSON shape and project-dir input are unverified). One session-start script for every host.** Rename `scripts/claude_session_start.py` → `scripts/session_start.py`
      with `--format text|cursor-json`. It locates the plugin through `__file__` (no host variable needed) and keeps
      the v1.2.1 guarantee that no code from the opened repository runs. Test: both formats, silent outside a project.
- [x] **Done v1.5.0 (+ a root AGENTS.override.md is reported as a structural conflict). hostcheck knows the new hosts' rule files.** Add `AGENTS.override.md` (Codex, repo and `~/.codex`), which
      *wins* over `AGENTS.md`; `~/.config/opencode/AGENTS.md`; `.cursor/rules/*.mdc` with `alwaysApply: true`;
      `.agents/skills` referenced by host files. Test with a planted override.
- [x] **Cancelled 2026-09-23 by the operator (D2): no `dist/` branch** — 0.55 MB package, ~0.2 MB of it not
      needed by users; a build step and CI job would cost more than they save. **Plugin payload.** Every host copies the package into its cache (Claude Code copies all 1.1 MB, including
      `evals/` and `docs/`). Decide on a publish boundary: a `dist/` branch, or manifest path fields where the host
      supports them — **operator decision D2**.

**Acceptance:** CI green; Claude Code behaves exactly as in v1.2.2 (brief, three commands or skills, hook
silent outside a project); the gate stays under one minute.

## 3. Phase 1 — Codex (first new host)

Why first: the closest match to what we ship. It has native plugins, skills and a SessionStart hook whose stdout
becomes context. It runs natively on Windows, and the owner already has `~/.codex`.

- [ ] Root `plugin.json` (Agent Plugins schema): `name`, `version` (from `VERSION`), `description`, `skills`, and the
      hook path under `extensions.com.openai`. `.agents/plugins/marketplace.json` makes the repo its own marketplace,
      as it already is for Claude Code.
- [ ] Codex hook file: SessionStart with matcher `startup|resume`, running `python <plugin>/scripts/session_start.py`,
      plus `commandWindows`. **UNVERIFIED:** whether Codex accepts Claude Code's `hooks/hooks.json` as-is and which
      variable holds the plugin root. Settle both in the first spike.
- [ ] Sandbox guidance in README and in the `df-check` skill. By default `finish` can run tests but cannot
      `git fetch` (no network) and cannot write `.git`. The brief degrades honestly (Phase 0 fix), and
      `commit-check` is read-only on `.git`, so it should pass (**UNVERIFIED**). For a live freshness check the
      operator can allow network with `[sandbox_workspace_write] network_access = true`, and the brief says so.
- [ ] Manifest-consistency test: `plugin.json` version = `VERSION` = the other manifests (extend
      `tests/test_claude_plugin.py` → `tests/test_manifests.py`).
- [ ] From-scratch install test with prompts A/B, adapted from `INSTALL_CLAUDE_CODE.md`. It needs the Codex CLI or
      app on the owner's machine.

**Acceptance:** fresh install from GitHub; the brief appears in a new session inside a framework project and the
hook is silent outside one; `init → doctor → finish` works on a sample project under the default sandbox; the
installing agent's pre-install review finds nothing we have not documented.

## 4. Phase 2 — Cursor (same manifest, second consumer)

- [ ] Reuse the Phase 1 root `plugin.json`; add Cursor fields only if the spike shows they are needed.
      **UNVERIFIED:** whether Cursor reads `.claude-plugin/`. Do not rely on it.
- [ ] Cursor hook file (`version: 1`, event `sessionStart`) → `session_start.py --format cursor-json`. The manifest
      field `hooks` points at it, so it never collides with the Claude/Codex hook file.
- [ ] **Windows fallback for the known sessionStart bug:** an `alwaysApply: true` rule in the plugin's `rules/`
      that says "run `/df-nav brief` first when `.devframework/` exists". It is a single line, so the brief is still
      reached when the hook stays silent.
- [ ] Run-mode note: the sandbox blocks `.git/config` and limits network, so `git fetch` behaves as in Codex.
      Allowlist mode can allow `python .devframework/check.py`.
- [ ] From-scratch install test in Cursor 3.18.9 (already installed): editor sidebar install, then the local path
      `~/.cursor/plugins/local/dev-framework` for development.

**Acceptance:** as in Phase 1, with the Windows result stated either way: "hook works" or "fallback rule used".

## 5. Phase 3 — OpenCode

- [ ] Skills: nothing to build. OpenCode reads `.agents/skills` and `.claude/skills`. Check that each skill's
      frontmatter `name` equals its folder name, which OpenCode enforces.
- [ ] Brief: a ~20-line `devframework.js` plugin. On `session.created` it runs `session_start.py` with Bun `$` and
      injects the output. Try `experimental.chat.system.transform` first and the `noReply` prompt second. Both are
      **UNVERIFIED** and one is marked experimental, so pin the tested OpenCode version in README.
- [ ] Distribution — **operator decision D3:** an npm package (needs an npm account; users add one line to
      `opencode.json`), or `install.py --host opencode` writing `.opencode/plugins/devframework.js` into the project
      (no account, per project).
- [ ] Commands: only if D1 keeps commands. `.opencode/commands/df-*.md` with `$ARGUMENTS`.
- [ ] Permissions: bash defaults to allow, so the gates run without prompts. Document how to restrict
      `python .devframework/*` if the operator wants to.
- [ ] From-scratch test: OpenCode is not installed yet. Install it with `scoop`/`npm` as part of the test.

**Acceptance:** as in Phase 1. The brief appears in a new session, and the test records the OpenCode version.

## 6. Measurement

For each host, smoke S1 by hand first, counting calls and seconds from the session. Where a structured log exists,
port `evals/measure.py`: Codex keeps session JSONL under `~/.codex/sessions` (**UNVERIFIED** format), OpenCode keeps
local storage, and Cursor has no known export. Record baselines in `evals/RESULTS.md` next to Hermes and Claude Code.

## 7. Operator decisions

**Decided 2026-09-23 by the operator: D1 = A, D2 = A, D3 = A, D4 = Codex → Cursor → OpenCode (all as recommended).**
**D2 reversed the same day: no `dist/` branch** (simplification pass; the payload is small).

| # | Decision | Recommendation |
|---|---|---|
| D1 | `commands/` after the move to skills: keep as aliases, or delete | keep for one release as aliases, then delete; skills are the one format every host reads |
| D2 | Plugin payload boundary | a generated `dist/` branch that manifests point at; `main` stays the development tree |
| D3 | OpenCode distribution | start with the project-local file (no account); publish to npm once OpenCode users ask for it |
| D4 | Order of hosts | Codex → Cursor → OpenCode (fidelity × owner's installed tools) |

## 8. Risks

- **Hook trust prompts** (Codex asks the user to trust plugin hooks) and pre-install reviews read as friction. The
  answer is the README section "What the plugin runs", written per host, not persuasion inside the plugin.
- **Cursor on Windows**: the sessionStart bug can hide the brief. The fallback rule covers it, but it is weaker than
  a hook.
- **OpenCode `experimental.*` hooks** may change between releases. Pin the version and keep the plugin to ~20 lines.
- **Sandboxed gates**: offline `git fetch` must never be reported as "up to date" (Phase 0 fix).
- **Three hosts moving fast** (every host changed its layout within 2026). Every phase starts with a spike against
  the live host; this table is dated and gets re-checked.

## Sources (fetched 2026-09-23)

- Codex: learn.chatgpt.com/docs — `plugins`, `build-skills`, `custom-prompts`, `hooks`,
  `agent-configuration/agents-md`, `extend/mcp`, `agent-approvals-security`, `windows/windows-sandbox`;
  developers.openai.com/plugins/build/plugins
- Cursor: cursor.com/docs — `plugins`, `reference/plugins`, `skills`, `rules`, `hooks`,
  `reference/third-party-hooks`, `mcp`, `agent/security/run-modes`, `cli/overview`, `cli/changelog`;
  forum thread "sessionStart plugin hook produces no output on Windows" (Cursor 2.5.22); github.com/cursor/plugin-template
- OpenCode: opencode.ai/docs — `plugins`, `sdk`, `skills`, `commands`, `rules`, `agents`, `mcp-servers`,
  `permissions`, `windows-wsl`; repo now github.com/anomalyco/opencode (v1.18.32, 2026-09-21)
