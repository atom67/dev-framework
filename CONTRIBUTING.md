# Contributing

Issues and pull requests are welcome. There is no response-time commitment, and no pull request
is guaranteed to be accepted.

Before a pull request:

1. Run `python -B scripts/verify.py` from a clean checkout of this repository.
2. Update the docs or use cases that the change affects.
3. Do not add secrets, private logs, or a Devlog export.

The local check is not a hosted CI result. CI runs the same command on Windows and Ubuntu.
A green local run does not publish a release. Maintainer notes: [MAINTAINER.md](MAINTAINER.md).
