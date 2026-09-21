Install DEV Framework **from scratch** as a Hermes plugin (nothing of it is installed yet):

1. `hermes plugins install atom67/dev-framework` then `hermes plugins enable dev-framework` (if the tools `df_init`,
   `df_check`, `df_nav` are not in your tool list after enabling, restart the session and continue).
2. Use the tools, not the package: `df_init` installs, `df_check` runs the gates, `df_nav` navigates. Read the bundled
   skill once with `skill_view("dev-framework:df-import")` (new project) or `skill_view("dev-framework:df-catch-up")`
   (existing code) and follow it. Do not clone the framework repository and do not read its README.
