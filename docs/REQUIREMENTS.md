# DEV Framework requirements

| ID | Requirement | Status |
|---|---|---|
| FR-001 | A new project carries its rules, facts, lessons and handoff without provider chat history. | implemented; native pilot blocked by access/policy, see evidence |
| FR-002 | Shared rules have one source; desktop/service specifics are selected explicitly. | verified, awaiting acceptance |
| FR-003 | Install and update are previewable, versioned and preserve project edits. | verified, awaiting acceptance |
| FR-004 | Doctor and finish distinguish scaffolding from a configured, verified project. | verified, awaiting acceptance |
| FR-005 | Commit checks read staged content and never print secret values. | verified heuristic; see limits |
| FR-006 | Reliability recipes include failure tests and data-flow monitoring criteria. | delivered recipes; consumer implementation required |
| FR-007 | Finish requires fresh counted test evidence and identifies the verified source snapshot; commit-check rejects index/worktree mismatch. | verified locally, awaiting acceptance |
| FR-008 | Secret checks cover common dotenv/YAML/C# literals without blocking harmless OAuth metadata; no secret values in diagnostics. | verified heuristic, documented limits |
| FR-009 | Reviewed Main OS lessons have an auditable transfer map, applicability, regression criteria and explicit exclusions. | 23 rows / eight recipes verified; not an exhaustive history audit |
| FR-010 | A disposable live fresh-session handoff validates recovery of decisions, evidence, next work and authority without prior chat. | fixture verified; native pilot BLOCKED, docs/evidence/HANDOFF_2026-08-31.md |
| FR-011 | A project receives a use-case catalogue, copy templates, composition rules and doctor checks for stable UC/SET IDs, Test fields and traceability. | implemented locally; consumer fill-in still required |
| FR-012 | Work that will not fit in one iteration has a living checklist; every operator reply ends with that list, completed items struck through, until it is empty. | implemented in protocol |
| FR-013 | Planning prefers larger iterations that rest on documentation, code analysis and closing tests; the overlay is slower and more predictable, not a licence for tiny untestable slices. | implemented in protocol |
| FR-015 | Optional Devlog: opt-in at install; one verbatim dialogue file per finalized dialogue named by date, client/model and affected codes, header with commits and ≤3-sentence summaries; public/unknown repositories keep it local and git-ignored. | implemented |
| FR-014 | Independent tasks that do not share an unfinished output run in parallel subagents when the host provides them; serializing them is a planning defect. | implemented in protocol |
| NFR-001 | Tooling uses Python 3.10+ standard library; PowerShell remains an optional entry point. | verified locally on Python 3.11.15 / PowerShell 7.6.4 |
| NFR-002 | Automated tests use isolated temporary repositories and no production credentials. | verified |
| NFR-003 | No installation, check or finish implicitly commits, pushes, deploys or restarts an app. | verified; configured commands must be reviewed |

The original documentation-only scope is preserved in docs/archive/PLAN.md. Version 0.2
adds the minimal automation explicitly approved after review; it does not port Main OS.
