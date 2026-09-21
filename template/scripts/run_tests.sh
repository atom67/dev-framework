#!/usr/bin/env bash
# Verify entry point in the form coding agents already detect (Hermes: project_facts.verifyCommands).
# It is the framework's finish gate, nothing else: doctor + secret heuristic + build + counted tests + checks.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
command -v "$PY" >/dev/null 2>&1 || PY=python
exec "$PY" -B .devframework/check.py finish "$@"
