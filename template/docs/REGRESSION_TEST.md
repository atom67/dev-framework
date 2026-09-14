# Regression test plan — {{PROJECT_NAME}}

**What this is:** a risk/coverage index and the remaining manual engineering checks.
**Update when:** features are added or existing behaviour changes. See `AGENTS.md`
section 3.

## When to run

Run the configured automated suite after implementation. On a behaviour change, update
affected cases and exercise relevant boundaries. Before release, run the agreed release
coverage and record any unavailable check as a limitation, not a pass.

## What belongs here and what does not

Automate repeatable assertions using the existing test framework. Crash/restart and
permission failures can often be tested in isolated child processes or environments;
they are not inherently manual. Never corrupt the operator's actual settings to test.

Keep a short link to automated coverage rather than duplicate the test procedure here.
Manual cases cover remaining UX/environment behaviour and are performed by the engineer,
not handed back to the product owner as debugging chores.

## Case format

| # | Area | Steps | Expected result | Result |
|---|---|---|---|---|
| 1 | Example: recovery | In an isolated temporary profile, supply invalid settings and start a child process | Recovery is explicit; existing bytes survive; close/restart never becomes a silent first run | not run |

## Automated coverage index

| Risk / requirement | Test command or source | What is NOT covered |
|---|---|---|
| Example: outbox | link to actual test when implemented | do not label a pure-function test as crash/concurrent-I/O coverage |

## Cases

| # | Area | Steps | Expected result | Result |
|---|---|---|---|---|
| 1 | ... | ... | ... | |

## Findings

Anything that failed goes into `docs/KNOWN_ERRORS.md` with an ID before the version ships,
even if it is not being fixed in this version. An unrecorded known failure is how the same
bug gets rediscovered three times.
