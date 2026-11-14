#!/usr/bin/env python3
"""PASS31.81 gate: map spawn data loads on demand, CI installs Pillow."""
import json, subprocess
from pathlib import Path
R = Path(__file__).resolve().parents[1]; S = R / "site"
html = (S / "map.html").read_text(encoding="utf-8"); js = (S / "js/pages/map.js").read_text(encoding="utf-8")
assert "monsters.js" not in html and "npcs.js" not in html
for n in ("function ensureSpawns", 'box.addEventListener("focus", ensureSpawns', "await ensureSpawns()", "data/map/monsters.js", "data/map/npcs.js"):
    assert n in js, n
assert subprocess.run(["node", "--check", str(S / "js/pages/map.js")]).returncode == 0
assert "pytest pillow" in (R / ".github/workflows/ci.yml").read_text()
print("PASS31.81 gate: lazy spawn data, CI has Pillow, errors=0")
