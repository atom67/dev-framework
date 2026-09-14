# Personal desktop profile

Opt-in defaults derived from Main OS, not requirements for every project.

- Linear main development can be selected in PROJECT.md. Do not switch an existing
  branch merely because this profile mentions main.
- Document the developer's living executable and build configuration. Avoid accidental
  parallel installations; isolated test outputs are allowed.
- If a running app locks the output, report it and obtain permission before stopping it.
  Relaunch only when the operator authorized that workflow, never after a review build.
- On an unexpected invariant failure, gate new operations and writes, record redacted
  diagnostics, and offer restart/close where the UI remains reliable. A modal dialog does
  not stop timers. Closing must not serialize invalid state over valid settings.
- Release artifacts can be versioned; keep the current and agreed rollback versions,
  clean only known task-owned staging, and preserve user data.
