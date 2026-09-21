#!/usr/bin/env python3
"""Assemble one paste-ready prompt: python evals/make_prompt.py S2 skills --work D:/dftest/s2 [--out prompt.txt]"""
import argparse
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
ap = argparse.ArgumentParser()
ap.add_argument("scenario", choices=["S1", "S2", "S3", "FOLLOWUP"])
ap.add_argument("variant", choices=["skills", "plugin"])
ap.add_argument("--work", required=True, help="absolute path of the run's working directory (fixture copied here)")
ap.add_argument("--out")
a = ap.parse_args()
text = (HERE / f"PROMPT_{a.scenario}.md").read_text(encoding="utf-8")
text = text.replace("<<INSTALL>>", (HERE / f"INSTALL_{a.variant}.md").read_text(encoding="utf-8").strip())
text = text.replace("{{WORK}}", a.work.replace("\\", "/")).replace("{{VARIANT}}", a.variant)
skills = {"skills": ("import-dev-framework", "catch-up"), "plugin": ("dev-framework:df-import", "dev-framework:df-catch-up")}[a.variant]
text = text.replace("{{SKILL_IMPORT}}", skills[0]).replace("{{SKILL_CATCHUP}}", skills[1])
assert "<<" not in text and "{{" not in text, "unresolved placeholder"
if a.out:
    pathlib.Path(a.out).write_text(text, encoding="utf-8")
else:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy code page
    print(text)
