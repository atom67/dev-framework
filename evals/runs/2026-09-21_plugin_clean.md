# Run 2026-09-21 14:05 — variant **plugin** v0.4.0 + fixes (2cfaf9f), gpt-5.6-terra, profile `mastermind` cleaned first

Clean start: plugin dir, copied skills and config entries removed from the profile; Desktop restarted before and after
the install. Each session holds the install attempt (2–4 calls) plus the task after the restart.

| scenario | session | active s | api | tool calls | reasoning msgs | in tok | questions | reply shape |
|---|---|---|---|---|---|---|---|---|
| S1 | 20260921_140517_a891c9 | 528 | 29 | 55 | 27 | 155k | 0 | 0/2 with 💬 Message, 1 footer |
| S2 | 20260921_140616_97d8cf | 479 | 18 | 59 | 18 | 78k | 0 | 0/2 with 💬 Message, 1 footer |
| S3 | 20260921_140625_fbcfa3 | 608 | 29 | 61 | 28 | 152k | 3 (3/3 planted) | 3/5 with 💬 Message, 4 footers |

Quality: all three FINISH PASSED (4/6/6 tests), committed, `__pycache__` no longer tracked (seeded .gitignore worked),
code byte-identical in S2/S3, S3 asked exactly the three planted questions. No post-report ad-hoc scripts.
Calls are slightly above the 12:38 run (55/59/61 vs 43/53/49) and S1/S3 input tokens are higher (TDD skill 11k and
hermes-agent skill 14k pulled in by the SOUL); S2 improved (78k). Still 0.5–0.6× the skills baseline on calls.

## Reply-shape conflict — result: **both blocks**
The agent now writes `🛠️ Tech` / `💬 Message` in its working replies (S3: 3 of 5) **and still appends the SOUL
footer «🟢 Простыми словами»** (every final reply). Final eval reports carry no Message at all because the eval's own
REPORT template dictates a different block (an eval defect, fixed next).
Reading: a rule inside the system prompt (SOUL) is not overridden by text in a tool result or a skill; the model
satisfies both. The framework cannot win this from inside the conversation — it has to surface the collision to the
operator and change the SOUL line (their file) with their consent. That is portion 2 (`hostcheck`): detect the footer
rule, propose the one-line edit («🟢 Простыми словами» → framework Message), record the decision, re-check on
every doctor.
