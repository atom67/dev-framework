# Quickstart

Read this after the [demo](../README.md#run-the-demo). Both routes below are real. Start with the one that matches the directory you have.

Python 3.10+ and Git. No pip install. Preview before you write.

## New project

```text
python scripts/install.py --target /path/to/new-project --name "New Project" --profile generic --scale "1 user" --kind product --dry-run
```

`--kind` is `product`, `tool`, or `explore`. `--scale` is a positive count plus a unit, for example `50 users`. The installer asks about Devlog unless you pass `--devlog` or `--no-devlog`. On a public repository, leave Devlog off or keep it local.

Remove `--dry-run` only after the preview lists the files you expect. Then:

```text
python .devframework/check.py doctor
```

A new scaffold prints `STRUCTURE OK; PROJECT NOT READY`. Fill the files it names. `DOCTOR READY` means the documents and commands are present. It does not mean tests ran.

```text
python .devframework/check.py finish
```

`finish` is the check that runs the configured tests, or the tool's examples. It does not commit, push, or deploy.

## Existing project

Use the same preview, with the existing directory as `--target`.

If that directory already has `AGENTS.md` or `CLAUDE.md`, the install stops before writing. Read the conflict. Do not pass `--force` to make the check green. `--force` replaces a conflicted framework file and keeps a backup. It does not overwrite project-owned documents.

After a clean install, run `doctor`. Expect `NOT READY` until the existing facts are in `PROJECT.md` and the test command is the real one.

An update from a newer checkout of this package:

```text
python scripts/install.py --target /path/to/project --update --dry-run
```

Untouched framework files update. Edited framework files conflict, and then nothing in that update is written until the conflict is resolved. Project-owned documents are not overwritten.

## Hermes

```text
hermes plugins install trenthalden/dev-framework
hermes plugins enable dev-framework
```

Restart the desktop app after enable. Plugins are loaded at process start. The tools are `df_init`, `df_check`, and `df_nav`.

## Claude Code

```text
/plugin marketplace add trenthalden/dev-framework
/plugin install dev-framework@dev-framework
```

Use `/dev-framework:df-init`, `/dev-framework:df-check`, and `/dev-framework:df-nav`. The older names without `df-` are aliases for one release.

The session-start hook is silent unless the working directory is a framework project. Inside one, it runs the plugin's copy of the brief, not code from the opened repository, and it fetches that project's own upstream. If the fetch fails, the brief says the upstream was not checked.

## What to read next

| Reader | Document |
|---|---|
| A person installing or updating | this file |
| An agent working in a project | `AGENTS.md` in that project |
| Installer, hosts, and evaluation records | [MAINTAINER.md](../MAINTAINER.md) |
| What the checks do not prove | `.devframework/VERIFICATION.md` after install |
