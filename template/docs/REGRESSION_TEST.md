# Regression test plan — {{PROJECT_NAME}}

**What this is:** the manual pass run before every version bump, covering behaviour that
automated tests cannot reach.
**Update when:** features are added or existing behaviour changes. See `AGENTS.md`
section 7.

## When to run

A full pass on every version bump. A targeted pass on the affected areas after any change
to existing behaviour.

## What belongs here and what does not

Here: anything needing a human at the screen — modal dialogs, crash and restart paths,
first-run and recovery flows, permissions prompts, anything that would kill the test
process if automated.

Not here: anything an automated test can assert. If a case can be automated, automate it
and delete the case. This file is the residue, not the main event.

## Case format

| # | Area | Steps | Expected result | Result |
|---|---|---|---|---|
| 1 | Example: recovery | Corrupt the settings file, start the app | Recovery screen appears; no factory reset happens; "Close" then restart still shows recovery, not defaults | |

## Cases

| # | Area | Steps | Expected result | Result |
|---|---|---|---|---|
| 1 | ... | ... | ... | |

## Findings

Anything that failed goes into `docs/KNOWN_ERRORS.md` with an ID before the version ships,
even if it is not being fixed in this version. An unrecorded known failure is how the same
bug gets rediscovered three times.
