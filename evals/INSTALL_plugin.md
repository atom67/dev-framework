Install DEV Framework **from scratch** as a Hermes plugin. Nothing of it is installed yet, and this is Hermes
Desktop: a normal user cannot run the CLI, so **you** install it from the chat, exactly as a user would ask you to.

1. Look at your tool list. If the tools `df_init`, `df_check`, `df_nav` are **already there**, skip to Step 1.
2. Otherwise run in the terminal:
   `hermes plugins install file://D:/DEV/DEV-Framework` then `hermes plugins enable dev-framework`
   (a public user would write `hermes plugins install atom67/dev-framework`). Plugins are discovered when the Hermes
   process starts, so you cannot use the new tools in this session. Reply with exactly one line —
   `PLUGIN INSTALLED — quit and reopen Hermes Desktop, start a new session and send this prompt again` — and stop.
   Do nothing else.
3. In the new session the tools are present: use them, not the package. `df_init` installs the framework into a
   repository, `df_check` runs the gates, `df_nav` navigates. Read the bundled skill once with
   `skill_view("dev-framework:df-import")` (new project) or `skill_view("dev-framework:df-catch-up")` (existing
   code) and follow it. Do not clone the framework repository and do not read its README.
