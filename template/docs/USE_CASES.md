# Use cases — {{PROJECT_NAME}}

**What this is:** a modular catalogue of how the product delivers value — every case
driven either by a user action or by an automatic tool — with the achieved benefit stated
at the end of each. Text only, no screenshots.
**Who reads it:** the product owner (what value exists and where), and the engineer (the
source list for functional tests).
**Update when:** a capability is added, or a case's trigger, flow, or outcome changes.
See `AGENTS.md` section 3. Copy-ready blocks: [`USE_CASE_TEMPLATE.md`](USE_CASE_TEMPLATE.md).
An edition or public cut of this catalogue: [`USE_CASES_SLICE_TEMPLATE.md`](USE_CASES_SLICE_TEMPLATE.md).

**Sibling of `ARCHITECTURE.md`.** The two live in parallel and must not duplicate each
other: `ARCHITECTURE.md` says how the system is built (components, schema, flows);
`USE_CASES.md` says what value it produces and how that value is exercised. Every case
names the architecture components it runs through, by reference, not by copy.

**Starting point for functional autotests.** Each case is written so it maps to one
functional test: a defined trigger, defined preconditions, an observable outcome. The
`Test` field carries one of three states (see *Identifiers*). A case that is merely
untested is a coverage gap; a case that *cannot* be tested by standard functional means is
a different thing entirely — it is recorded in the *Not functionally verifiable* register
below so that it is kept in mind during development even though no automated test guards
it.

---

## How to read this document

- **Modules** are value areas / capability domains. One module groups the cases that
  deliver one kind of benefit. A module usually contains both interactive and automatic
  cases — that is expected, and they sit together because they serve the same value.
- **A case** is one path to one benefit. It has a stable ID, a trigger type, the
  preconditions it needs, the steps, and the outcome it achieves.
- **Setup and settings are not inside cases.** They live in the separate *Setup &
  settings* block below and are referenced by ID (`SET-###`). A case names the setup it
  needs; it does not re-describe how to configure it. This keeps configuration in one
  place and the cases readable.
- **Human meaning is not a case.** If several paths share a glossary (what a calendar
  row *means*, what a status word means), write that glossary once in the module. Cases
  do not restate it.

## Identifiers

- `UC-###` — a use case. Permanent and unique; never reused for a different case.
- **Trigger** — how the value is initiated:
  - **Interactive** — a deliberate user action (open a screen, press a control, drop an
    item).
  - **Automatic** — no user present at the moment: a timer, a background service, a
    connector, a scheduled job, or an inbound external event.
- `SET-###` — a setup or settings item in the block below.
- **Test status** — every case carries exactly one:
  - **covered** — a link to the automated test that guards it.
  - **gap** — testable by standard functional means, but not yet covered. An open
    functional-coverage item; record it in `docs/BACKLOG.md`.
  - **NFV** (not functionally verifiable) — cannot be checked by a standard automated
    functional test. It still ships and still matters, so it is listed in the *Not
    functionally verifiable* register with the reason, and is verified by hand or held as
    a development constraint. `NFV` is a deliberate classification, never a synonym for
    "no test yet".
- Link out to `FR-###` in `docs/REQUIREMENTS.md` and to components in
  `docs/ARCHITECTURE.md`. Do not restate their text here.
- A SET row's **Enables** column and a case's **Preconditions** may only name IDs that
  exist as `#### UC-` headings or SET rows. Ellipsis ranges (`UC-150…155`) are expanded:
  every number in the range must have a case. Do not pad a range to a round number.
  `UC-150+` means UC-150 exists, not an open-ended list.
- When the product has more than one store or API, **Flow** names which one this case
  uses. Do not paste a safety slogan from another path (for example "read-only replica")
  onto a case that actually calls a server API.

---

## Setup & settings (separate block)

Everything a case may depend on, configured once or per environment, in one place. A case
references these by ID; it does not repeat them. Mark whether each is required before any
value is possible, or optional and enabling a subset of cases.

| ID | Setting | Where configured | Required / optional | Enables |
|---|---|---|---|---|
| SET-001 | Example: backend URL and access token | app settings screen | required for sync cases | UC-001 |
| SET-002 | Example: launch on system start | app settings / OS integration | optional | UC-002 |

Replace the examples with the real setup items. Anything a case lists under *Preconditions*
must have a row here.

---

## Modules

Copy the block below per module. Keep modules to a single value area; if a module grows
past a handful of cases, it is probably two.

### Module: <value area name>

**Value this module delivers:** one sentence — the benefit, not the mechanism.
**Architecture components involved:** link the relevant rows of `docs/ARCHITECTURE.md`.

#### UC-001 — <short case name>

- **Trigger:** Interactive | Automatic — and the specific initiator (which control, or
  which timer/service/event).
- **Actor:** the user, or the named automatic component.
- **Preconditions:** the `SET-###` items and any prior state required.
- **Flow:** the steps, in order, including which store or API is read or written when
  more than one exists. Enough for a test to reproduce, no more.
- **Outcome (value / function achieved):** the concrete benefit the user or the business
  now has. This line is mandatory and is the reason the case exists.
- **Test:** `covered` (link) | `gap` | `NFV` (reason). See *Identifiers*.

#### UC-002 — <short case name>

- **Trigger:**
- **Actor:**
- **Preconditions:**
- **Flow:**
- **Outcome (value / function achieved):**
- **Test:**

---

## Not functionally verifiable — keep in mind during development

Some value paths cannot be proven by a standard automated functional test, and pretending
otherwise produces a green suite that guards nothing. They are collected here on purpose:
a developer touching the surrounding code must treat each as a **constraint to preserve by
hand**, because no test will fail if it breaks.

An `NFV` case is not a gap to be closed later — it is a permanent property of that path.
Typical reasons, each with how it *is* checked instead:

| Reason it can't be a standard functional test | How to keep it correct |
|---|---|
| Killing the test process (a modal dialog, a hard process exit, an OS restart path) | manual regression step in `docs/REGRESSION_TEST.md` |
| Needs a real external service, device, or OS-level integration (network, drivers, hardware) | isolated fixture for the logic; manual check for the integration |
| Visual / timing / UX judgement (layout, colour contrast, animation, "feels responsive") | reviewer's eye + a screenshot in regression, not an assertion |
| Requires real behaviour over time (streaks, multi-day trends, long-running drift) | seed synthetic history in a fixture where possible; otherwise manual |
| Would damage real user data or state to trigger (destroys a live profile, mutates prod) | test the decision on a synthetic copy; never on the real target |

| Case | Why it is NFV | How it is actually checked | Development constraint to preserve |
|---|---|---|---|
| UC-0xx | e.g. modal crash dialog + hard exit kills the runner | manual regression case R-## | e.g. the exit path must stop timers before showing the dialog |

Keep this register short and honest. If a case can be automated, automate it and move it
out of here — an `NFV` entry that is really just laziness rots the whole distinction.

## Traceability

One row per case, so no value area is left unexercised and no requirement is left with no
way to demonstrate it. This table is what a reviewer scans to find gaps.

| Case | Trigger | Requirement | Architecture component | Test |
|---|---|---|---|---|
| UC-001 | Interactive | FR-0xx | ... | covered / gap / NFV |
| UC-002 | Automatic | FR-0yy | ... | covered / gap / NFV |

**Gap rule:** a `gap` case (testable, not yet covered) is an open functional-coverage item —
record it in `docs/BACKLOG.md`, do not leave it only here. An `NFV` case is not a gap: it
belongs in the *Not functionally verifiable* register above, as a constraint to keep in
mind, not a task to close.
