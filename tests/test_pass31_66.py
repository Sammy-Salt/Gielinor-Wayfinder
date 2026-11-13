#!/usr/bin/env python3
"""PASS31.66 gate: map search covers shops/NPCs/monsters, the Map Key only offers categories that have data, markers are smaller."""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "site"
js, css = (S / "js/pages/map.js").read_text(), (S / "css/pages/map.css").read_text()
assert subprocess.run(["node", "--check", str(S / "js/pages/map.js")]).returncode == 0
for needle in ("spawnGroups", "function find(", "bindPopup", "categories.set("):
    assert needle in js, needle
assert ".leaflet-popup-content" in css and ".map-badge span" in css
for line in (ROOT / "audit/map-boundary.sha256").read_text().splitlines():
    h, rel = line.split("  ", 1)
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, rel
print("PASS31.66 map search and key gate: spawn search, data-backed key, popups, smaller markers, errors=0")
