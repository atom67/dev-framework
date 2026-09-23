# Agent evaluation set — template

<!-- For advanced testing (AGENTS.md §4). Copy to tests/agent_eval/<agent>.jsonl plus this page as its README. -->

An evaluation set is a fixed list of questions with what a good answer **must** and **must not**
contain. Run it before every prompt, model or memory-pipeline change and compare with the last run.
Twenty honest cases beat two hundred generated ones.

One case per line (JSON Lines):

```json
{"id": "EV-001", "promise": "UC-001", "input": "<what the user says>", "must": ["<fact or phrase>"], "must_not": ["<invented fact, forbidden tone, leaked identifier>"], "notes": "<why this case exists>"}
```

Rules:
- Cases come from real conversations and real failures (a wrong name, an invented date, a missed alert),
  with personal data replaced by patterns.
- Every promise in the agent card has at least one case; every fixed failure gets one.
- `must` checks facts the code can verify; tone and style are judged by a person on a small sample.
- Record per run: date, model, prompt version, cases passed / failed, and the failed ids. A drop is
  investigated before the change ships.
- The set runs against a stub-free agent, with a spending cap, never against the owner's live channel.
