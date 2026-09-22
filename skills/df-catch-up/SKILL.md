---
name: df-catch-up
description: Reconstruct the DEV Framework document set for a codebase that already exists — requirements, architecture, use cases mapped to tests, known errors, backlog — from the code, the tests and the operator's existing notes, with every unverifiable statement marked unconfirmed instead of guessed. Use when the operator says "catch up the docs", "we already have code, apply the framework", "migrate the documentation", "восстанови документацию", "подтяни доки под фреймворк".
version: 0.4.0
---

# df-catch-up — documents for code that was written without them

**The rule that governs everything: a reconstructed statement is either read out of the code/tests,
taken from an existing note (cite it), or confirmed by the operator — otherwise it is listed as
unconfirmed.** A drifted document lies confidently; a missing one at least sends you to the code.

## Procedure

1. `df_init(target, name, scale)` if the framework is not installed yet (it never overwrites existing
   project documents; a foreign context file is reported, not replaced). Then `df_nav(target, "contract")`.
2. **Inventory before writing**: modules and entry points, every test and what it pins, every existing
   note (README, TODO, design notes, comments marked TODO/FIXME/???). Large repository → open one checklist
   first: `df_nav(target, "checklist", "new <slug> \"catch-up\"")`, one item per document.
3. **Use cases** (`docs/USE_CASES.md`): one `#### UC-### — title` per user-visible capability, with
   `**Test:** covered — <test id>` when a test pins it, `gap — <why>` when none does, `NFV — <reason>` when
   it cannot be functionally tested. Traceability row per case. Where intent is undecidable from code
   and notes (a flag with no body, a field nobody reads, a "???" comment): **ask the operator** —
   options plus what the code does today — and record the answer as intent; where code disagrees,
   register a `KE-` entry, do not change the code in this pass.
4. **Known errors, requirements, architecture, backlog**: fold the old notes in (nothing is lost; replace
   the old files with a one-line pointer), then `df_nav(target, "index")`.
5. **Host rules**: `df_check(target, "hostcheck")` lists profile rules that fight the framework (footer per reply,
   commit after every change, no tests, read-skill-first …) with a fix each. Show the operator the list once, get one
   decision per line, edit the host file with authorization (backup first), record decisions in `PROJECT.md` →
   `## Host precedence`. Unrecorded collisions stay doctor warnings — including rules added later. The decision is the operator's: never
   record `kept`/`replaced` yourself, even when told not to ask — this is the one question the framework requires.
6. **Audits**: `df_check(target, "selftest")` proves the doctor contract and the secret heuristic fire;
   run `df_check(target, "secrets")` for the worktree; read every repeating operation (timers, polls,
   retries) and write its `cost:` at the scale target — this one is a reading exercise, no tool simulates it.
7. `df_check(target, "doctor")` READY, existing tests still pass (`df_check(target, "finish")`), then the
   handover in numbers: documents and cases reconstructed (covered / gap / NFV), known errors registered,
   cost ceilings found, secrets scan result, and the **unconfirmed** list as questions in product terms.

## Rules

- Never silently record the current code behaviour as the intended behaviour.
- Do not change product code or test behaviour in a catch-up; comments that name a `KE-` id are fine.
- Independent steps run in parallel subagents when the host provides them; work beyond one iteration gets one checklist (`df_nav checklist`) copied at the end of every reply. Reply shape, exact headings: `🛠️ Tech` then `💬 Message` ending with the explicit ask; if your profile wants its own plain-language footer, the Message is that footer (one block, not two).
- Your host profile decides tone; this skill decides only what the documents may claim.

Incidents behind these rules and the long-form procedure (audits, plants, handover template):
`references/full.md`.
