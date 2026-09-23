# <agent name> — agent card

<!-- Copy to docs/AGENT_<name>.md and fill every <...>. One card per agent; change it in the same
     commit as the behaviour. Guidelines: .devframework/agents/README.md -->

Living document. Last change: <YYYY-MM-DD>.

## 1. Role

What it does, for whom, in one paragraph: <...>

**Is not:** <the neighbouring roles it must not take over — e.g. "not the engineer, not the owner's twin">

## 2. Boundary

| Question | Answer |
|---|---|
| Where it runs | <host / container / laptop; always on or when switched on> |
| Secrets it can reach | <none / listed keys, profile-local> |
| Tools and skills allowed | <list; a tool is a permission> |
| Data it reads | <sources; live personal data only through a read-only copy> |
| Data it writes | <stores; persona and memory changes only as drafts> |
| Personal data rule | <patterns only / what is excluded> |

## 3. Models and keys

| Work | Model | Provider / key | When the primary fails |
|---|---|---|---|
| <conversation> | <model> | <provider> | <route; never a paid copy by accident> |
| <scheduled job> | <model, pinned> | <provider> | <route> |

Tool-using work runs only on the models above; fallback models get text in, text out.

## 4. Promises

What a user can rely on — each one has a smoke test (lean) or an evaluation (advanced).

| Id | Promise | Entry point | Test |
|---|---|---|---|
| <UC-001> | <e.g. answers a question about the calendar> | <chat / API> | <covered / gap / NFV> |
| <UC-002> | <e.g. morning digest by 08:00> | <scheduler> | <covered / gap / NFV> |

## 5. Scheduled jobs

| Job | Schedule | Cheap gate (exits before the model) | Model (pinned) | Delivery | Watcher | Replay of missed runs |
|---|---|---|---|---|---|---|
| <name> | <cron> | <"new items?"> | <model> | <channel + recipient> | <who is told on failure> | <yes / not needed: why> |

## 6. Watchers

| What | How it is checked | Who is told |
|---|---|---|
| Credential / token | <probe> | <owner channel> |
| Quota | <probe, threshold> | <owner channel> |
| Fallback in use | <signal> | <owner channel> |
| Delivery | <end-to-end check> | <owner channel> |

## 7. Deploy

Command: `<deploy command>`. Done when: the owning process restarted (PID, start time), deployed hash
matches, one smoke run through the real scheduler passed.

## 8. Failure modes

| Symptom | Cause | What to do |
|---|---|---|
| <log line or behaviour> | <cause> | <action> |

## 9. Runbook

```text
<status, logs, run a job now, restart>
```

## 10. Open questions

- <decisions deferred, known debt>
