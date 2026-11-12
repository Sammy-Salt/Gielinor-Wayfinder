#!/usr/bin/env python3
"""PASS31.66 gate: map search covers shops/NPCs/monsters, the Map Key only offers categories that have data, markers are smaller."""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "site"
js, css = (S / "js/pages/map.js").read_text(), (S / "css/pages/map.css").read_text()
assert subprocess.run(["node", "--check", str(S / "js/pages/map.js")]).returncode == 0
for needle in ('addSearchRecords(shops, "Shop")', 'addSearchRecords(npcs, "NPC")', 'addSearchRecords(monsterRecords, "Monster")', "function nearestRecord", "legendCount(category)", "if(!count) return;", "L.popup({ maxWidth:260", "iconSize:[22,22]"):
    assert needle in js, needle
assert "setMapToolsOpen(true)" not in js.split("function showLocation", 1)[1].split("Search: places", 1)[0]  # details no longer force the drawer open
assert ".map-popup" in css and ".map-marker span{font-size:14px" in css
for line in (ROOT / "audit/map-boundary.sha256").read_text().splitlines():
    h, rel = line.split("  ", 1)
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, rel
print("PASS31.66 map search and key gate: spawn search, data-backed key, popups, smaller markers, errors=0")
