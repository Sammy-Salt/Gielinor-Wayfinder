#!/usr/bin/env python3
"""PASS31.64 gate: the look-and-feel pass is scoped away from the map and keeps its accessibility floor."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
css = (ROOT / "site/site.css").read_text()
block = css.split("PASS31.64 look and feel", 1)[1]
assert block.count('body:not([data-page="map"])') >= 40
assert "--gold:#dcb65e" in block and "accent-color:var(--gold)" in block and "display:none}" in block
for banned in ("outline:none", "outline:0"):
    assert banned not in block, banned  # keyboard focus stays visible
for line in (ROOT / "audit/map-boundary.sha256").read_text().splitlines():
    h, rel = line.split("  ", 1)
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, rel
print("PASS31.64 look-and-feel gate: scoped away from map, focus rings kept, errors=0")
