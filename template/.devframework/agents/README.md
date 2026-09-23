# Building an AI agent — guidelines

For a person building an AI agent: a chat bot, an assistant, a scheduled LLM job, a news desk.
Distilled from four agents built and run in production (a personal digital twin, a news desk,
an assistant on a laptop, a retired companion bot) and about 35 recorded failure classes.
Each rule below exists because its absence cost real days or money.

Copy-ready templates in this folder:
- [AGENT_CARD.md](AGENT_CARD.md) — the one living document of an agent (copy to `docs/AGENT_<name>.md`);
- [AGENT_EVAL.md](AGENT_EVAL.md) — the smallest evaluation set that catches a regression in answers;
- [AGENT_RETIREMENT.md](AGENT_RETIREMENT.md) — the checklist that makes a retired agent actually gone.

## 1. One card per agent, kept true

Write the [card](AGENT_CARD.md) before the first prompt and change it in the same commit as the
behaviour. It names the role and what the agent is **not**, its boundary, models per job, scheduled
jobs, failure modes and open questions. Do not spread an agent over phase notes: one document,
always current. When several agents exist, re-read all cards against reality now and then; one pass
over four agents found ten silent divergences (dead jobs, stale docs, duplicate personal data).

## 2. Boundary first

- A persona or companion agent runs where it cannot reach secrets or host files (a sandbox or container).
- A tool or skill is a **permission**, not documentation: giving a companion engineering tools erases the
  boundary it was designed to have. List the tools and skills each agent may use.
- Live personal data is read through a read-only replica, never the working database.
- Corpora, memory and persona files hold patterns, not direct identifiers (names, phones, addresses).

## 3. Models: pinned, routed, watched

- Pin the model and provider on every scheduled job. A job left on the profile default follows the
  default into an empty quota pool (thousands of idle retries a day) or onto a paid copy of the same model.
- Decide where a request goes when the primary fails, and check that route: a premium job must not
  silently spill onto a paid provider.
- A weak or fallback model gets **text in, text out** — never file, config or command tools. One fallback
  model given "enable everything" rewrote a config file whole and deleted a bot token.
- Before editing an agent's `.env` or config: timestamped backup, then a targeted change, never a rewrite.
- Watch credentials like a dependency: token death, quota exhaustion and every switch to a fallback
  notify the owner. Two jobs once died silently for three days on a rotated refresh token.
- Count cost as turns × invocations: one agent call with `max_turns: 4` is four model requests.

## 4. Scheduled work: a script outside, the model only when there is work

- The outer job is a plain script with a cheap check ("anything new?"); it exits before any model call
  when the answer is no. An hourly frontier-model run that prints "no pending" is pure waste.
- A job that must produce one output runs single-shot or with a small turn cap, not a 90-turn agent loop.
- Bound everything: retries, turns, subprocess time (inner timeout below the scheduler's kill), queue
  head failures. A poisoned message at the head of a queue must not block the rest forever.
- Missed runs are replayed in order, and a replay never collapses several days into one summary.

## 5. Code holds the facts, the model writes the text

- Facts, numbers, names, links and provenance are assembled by code; the model translates or condenses
  given text. A rewriting model swapped a judge's name and a president's title in a real digest.
- Items that must survive (a release, an alert) are checked **after** the model, not only selected before it.
- Never trust the model to emit closed JSON for a parsed ledger: take the first object, repair a truncated
  one, and keep the raw text when repair fails — a silently dropped ledger lost an owner message.
- Keep the source's country, date and author as provenance, not as facts about the event.

## 6. Stored is not delivered

- Every output channel is verified end to end: request → the real executor → the person who receives it.
- "Ask agent X" must literally invoke X; a label like `responder="x"` on a generated answer is not a consult.
- An async question-and-answer queue needs a consumer that brings answers back; written rows are not delivery.

## 7. Deployed means running

Copying files proves nothing about a long-lived process. A deploy is done when the owning process was
restarted and verified (PID, start time), the deployed code hash matches, and one smoke run went through
the **real scheduler**. Known traps: the runtime remaps `HOME`; scheduled scripts may not inherit the
agent's `.env`; an update can move jobs into the wrong profile; a sandbox does not see host paths;
a service has no interactive `PATH`.

## 8. What the agent learns goes through a person

Anything that changes the agent's persona, memory or long-term behaviour enters as a **draft** and
becomes active only after the owner approves it: new facts about the owner, a proposed persona diff,
a new trend or topic. Insights are hypotheses with a confidence, few at a time; "nothing found" is a
valid answer and must be said plainly.

## 9. Testing an agent

The project's `testing` setting applies (AGENTS.md §4).
- **lean:**
  - one smoke per promise of the agent — a reply path or a scheduled output — through the real entry point;
  - the model may be replaced by a stub for the plumbing;
  - before switching a job on: one live run with a spending cap;
  - the first outputs go to the owner for review.
- **advanced:**
  - everything in lean;
  - an [evaluation set](AGENT_EVAL.md) run before every prompt or model change;
  - a shadow mode (the new logic runs beside the old one and only logs) before replacing logic that users rely on;
  - delivery and replay checks.

## 10. Before building: spike, then the host's own features

- Try the idea on the real host first: permissions, operating system, scheduler, sandbox. A ten-round
  design once failed at the end on a Windows permission a one-hour spike would have shown.
- Limit review loops: three rounds without a green gate means the scope is wrong, not the review.
- Use what the agent host already offers (skill directories, schedulers, git) before building delivery,
  sync or migration machinery. The most expensive month in the source project was spent on infrastructure
  later replaced by `git` and one config line.

## 11. Known errors, addressable

Keep agent failure classes in `docs/KNOWN_ERRORS.md` with ids, so `navigate.py find` returns one entry
instead of a 60 KB file read before every task. When an agent or construction is retired, generalize
its lessons and delete the specifics.

## 12. Retirement is a procedure

A retired agent keeps costing until its jobs, gateway, channels, keys and data are gone and its lessons
are generalized. Use [the checklist](AGENT_RETIREMENT.md); one retirement was still "not finished" a week later.
