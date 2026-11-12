#!/usr/bin/env python3
"""PASS31.59 gate: the Skill Calculator reads the 2009Scape-derived training data offline."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
js = (SITE / "js/pages/skill-stats.js").read_text()
html = (SITE / "skill-stats.html").read_text()
sw = (SITE / "sw.js").read_text()
assert 'id="methods"' in html and html.count('<nav id="site-nav"') == 1
files = ["gathering.json", "thieving.json", "agility.json", "hunter.json", "farming.json"]
for f in files:
    assert f'"{f}"' in js, f
    assert f'"./data/{f}"' in sw, f"{f} not precached"
    assert (SITE / "data" / f).is_file()
assert "escapeHTML" in js and "METHOD_FILES" in js
assert subprocess.run(["node", "--check", str(SITE / "js/pages/skill-stats.js")]).returncode == 0
doc = json.loads((SITE / "data/gathering.json").read_text())
assert set(doc["skills"]) == {"Woodcutting", "Mining", "Fishing", "Firemaking"}
print("PASS31.59 skill calculator methods gate: 8 skills wired, offline precache, errors=0")
