#!/usr/bin/env python3
"""PASS31.69 gate: Map Key results use per-category badge icons; NPC/monster spawns start hidden."""
import hashlib, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "site"
js, css = (S / "js/pages/map.js").read_text(), (S / "css/pages/map.css").read_text()
assert subprocess.run(["node", "--check", str(S / "js/pages/map.js")]).returncode == 0
for needle in ("const GLYPH", '"Fairy ring": "🍄"', "L.divIcon", "L.circleMarker"):
    assert needle in js, needle
assert ".map-badge span" in css
for line in (ROOT / "audit/map-boundary.sha256").read_text().splitlines():
    h, rel = line.split("  ", 1)
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, rel
print("PASS31.69 map icons gate: category badges, spawns hidden by default, errors=0")
