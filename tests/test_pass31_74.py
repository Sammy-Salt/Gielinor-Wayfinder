#!/usr/bin/env python3
"""PASS31.74 gate: reorganised Progress page (summary, closest-to-target, sortable compact skill rows)."""
import subprocess
from pathlib import Path

S = Path(__file__).resolve().parents[1] / "site"
html = (S / "progress.html").read_text(encoding="utf-8")
js = (S / "js/pages/progress.js").read_text(encoding="utf-8")
css = (S / "css/pages/progress.css").read_text(encoding="utf-8")
assert subprocess.run(["node", "--check", str(S / "js/pages/progress.js")]).returncode == 0
for i in ("totalLevel", "totalXP", "questPoints", "targetsMet", "summaryText", "summaryFill", "nextUp", "sortSkills", "skills", "refreshSyncBtn", "resetTargetsBtn", "syncStatus"):
    assert f'id="{i}"' in html, i
for o in ("game", "lowest", "closest", "remaining"):
    assert f'value="{o}"' in html, o
for n in ("skill-stats.html?skill=", "wayfinder.progress.sort", "function sorted", "function remaining"):
    assert n in js, n
assert ".skill-row" in css and "Current level" not in js
print("PASS31.74 gate: Progress page reorganised, errors=0")
