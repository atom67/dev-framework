# DEV Framework evaluation results

One row per run. Objective columns come from `python evals/measure.py --profile <profile> --last`;
quality columns from the agent's final report and a look at the resulting repo.

| date | scenario | variant | model | seconds (active) | api calls | tool calls | msgs w/ reasoning | reasoning tok | questions (expected) | tests pass | doctor | finish | old docs preserved | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-20 | S1 | skills | grok-4.6 | 754 | 35 | 78 | 35 | 13279 | 0 (0) | 10/10 | PASS | PASS | n/a | runs/2026-09-20_skills.md; shared profile, parallel |
| 2026-09-20 | S2 | skills | grok-4.6 | 715 | 38 | 96 | 38 | 13658 | 0 (0) | 6/6 | PASS | PASS | yes | fixture not pre-copied |
| 2026-09-20 | S3 | skills | grok-4.6 | 5434 (1269) | 55 | 150 | 55 | 21413 | 5 (see private key: 3/3 + 2 extra, all legit) | 6/6 | PASS | PASS | yes | code untouched except KE comments |
| | S1→followup | skills | | | | | | | (0) | | | | n/a | |
| | S2→followup | skills | | | | | | | (0) | | | | n/a | |
| 2026-09-21 | S1 | plugin v0.4.0 | gpt-5.6-terra | 1011 (471) | 22 | 43 | 19 | 2235 | 0 (0) +1 re-prompt | 5/5 | PASS | PASS | n/a | runs/2026-09-21_plugin.md; incl. install attempt |
| 2026-09-21 | S2 | plugin v0.4.0 | gpt-5.6-terra | 1075 (537) | 24 | 53 | 22 | 2298 | 0 (0) +1 re-prompt | 6/6 | PASS | PASS | yes | two doctor/finish hiccups (profile link, test evidence) |
| 2026-09-21 | S3 | plugin v0.4.0 | gpt-5.6-terra | 2239 (598) | 28 | 49 | 25 | 4046 | 3 (3/3 planted, 0 extra) +1 re-prompt | 6/6 | PASS | PASS | yes | code untouched |

Definition of "faster": plugin run ≤ 0.7 × skills run in seconds **and** tool calls, same quality columns.
Definition of "better thinking": follow-up session reaches its first code edit with fewer tool calls than the
first-session install step took (agent reads docs instead of re-deriving).
