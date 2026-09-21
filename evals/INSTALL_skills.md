Install DEV Framework **from scratch** as Hermes skills (nothing of it is installed yet):

1. `git clone --depth 1 https://github.com/atom67/dev-framework {{WORK}}/dev-framework`
2. Install its two skills into this Hermes profile, then confirm they are listed:
   `hermes skills install atom67/dev-framework/skills/import-dev-framework --yes`
   `hermes skills install atom67/dev-framework/skills/catch-up --yes`
   `hermes skills list`
   If hub install fails, copy `{{WORK}}/dev-framework/skills/<name>/` to `<HERMES_HOME>/skills/dev-framework/<name>/` instead.
3. Read `{{WORK}}/dev-framework/README.md` and the SKILL.md of the skill this scenario names, then follow that skill. The installer is `python {{WORK}}/dev-framework/scripts/install.py` — run it non-interactively (`--name`, `--profile generic`, `--scale`, `--no-devlog`; preview with `--dry-run` first).
