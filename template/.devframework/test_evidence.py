"""Fresh, counted test evidence. Reports are trusted runner output, not coverage proof."""
from __future__ import annotations

import json
from pathlib import Path

from safety import checked_path


def validate(path: Path, run_id: str, max_skipped: int) -> dict:
    path = checked_path(path)
    if not path.is_file() or path.stat().st_size > 64 * 1024:
        raise ValueError("Missing/oversized test evidence")
    report = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(report, dict) or type(report.get("format")) is not int or report["format"] != 1:
        raise ValueError("Unsupported test evidence format")
    if report.get("run_id") != run_id:
        raise ValueError("Stale test evidence (run ID mismatch)")
    for name in ("total", "failed", "errors", "skipped"):
        if type(report.get(name)) is not int or report[name] < 0:
            raise ValueError("Test evidence counts must be nonnegative integers")
    if report["failed"] + report["errors"] + report["skipped"] > report["total"]:
        raise ValueError("Inconsistent test evidence counts")
    if report["total"] - report["skipped"] <= 0:
        raise ValueError("No tests executed (zero discovery or all skipped)")
    if report["failed"] or report["errors"] or report["skipped"] > max_skipped:
        raise ValueError("Test failures/errors or skip budget exceeded")
    return report
