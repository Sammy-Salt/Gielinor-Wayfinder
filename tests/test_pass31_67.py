#!/usr/bin/env python3
"""PASS31.67 gate: 2009Scape-sourced map points (fairy rings, stars, dig spots, banks ...) are generated, wired into the Map Key, and unmapped data stays untouched."""
import hashlib, json, re, subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "site"
raw = (S / "data/map/points.js").read_text()
meta = json.loads(re.search(r"OSRS_MAP_POINTS_META\s*=\s*(\{.*?\});", raw, re.S).group(1))
pts = json.loads(re.search(r"OSRS_MAP_POINTS\s*=\s*(\[.*\]);", raw, re.S).group(1))
counts = Counter(p["legend"] for p in pts)
assert dict(counts) == {"Fairy ring": 35, "Fishing spot": 18, "Shooting star": 42, "Teleport destination": 24, "Dungeon": 10, "Bank": 30, "Slayer Master": 6, "Clue dig spot": 82}, counts
assert len(pts) == 247 and len({p["id"] for p in pts}) == 247
for p in pts:
    assert 1000 < p["x"] < 4000 and 2000 < p["y"] < 12000 and p["plane"] in (0, 1, 2, 3) and p["name"], p
assert meta, "provenance metadata missing"
html, js = (S / "map.html").read_text(), (S / "js/pages/map.js").read_text()
assert "data/map/points.js" in html and html.index("shops.js") < html.index("points.js")
assert subprocess.run(["node", "--check", str(S / "js/pages/map.js")]).returncode == 0
for needle in ("OSRS_MAP_POINTS", "categories", '"Fairy ring"', '"Clue dig spot"', '"Shooting star"'):
    assert needle in js, needle
assert (ROOT / "data-pipeline/generate_map_points.py").exists()
for line in (ROOT / "audit/map-boundary.sha256").read_text().splitlines():
    h, rel = line.split("  ", 1)
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, rel
print("PASS31.67 map points gate: 247 points in 8 Map Key categories, errors=0")
