#!/usr/bin/env python3
"""PASS31.63 gate: UI pass keeps the map untouched and scopes the compact navigation away from it."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
css = (ROOT / "site/site.css").read_text()
block = css.split("PASS31.63 UI pass", 1)[1]
assert block.count('body:not([data-page="map"])') >= 8 and "flex-wrap:nowrap;overflow-x:auto" in block
assert "repeat(auto-fit,minmax(92px,1fr))" in css
assert ".stats,.actions{grid-template-columns:1fr}" not in (ROOT / "site/css/pages/index.css").read_text()
for line in (ROOT / "audit/map-boundary.sha256").read_text().splitlines():
    h, rel = line.split("  ", 1)
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, rel
print("PASS31.63 UI gate: nav scoped away from map, map boundary intact, errors=0")
