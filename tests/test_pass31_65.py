#!/usr/bin/env python3
"""PASS31.65 gate: map page once-over — compact navigation, marker switches, lighter clusters; map data files unchanged."""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "site"
html, js, css = (S / "map.html").read_text(), (S / "js/pages/map.js").read_text(), (S / "css/pages/map.css").read_text()
assert html.count('id="layerSwitches"') == 1 and all(f'data-kind="{k}"' in html for k in ("Shop", "NPC", "Monster")) and 'href="reference.html"' in html
assert "kindVisible" in js and "wayfinder.map.kinds" in js and "CLUSTER_CELL_PX = 64" in js and "try {" in js
assert "rgba(59,111,182,.82)" in css and "#app-tools-host{display:none}" in css
assert subprocess.run(["node", "--check", str(S / "js/pages/map.js")]).returncode == 0
sitecss = (S / "site.css").read_text()
assert 'body:not([data-page="map"]) #site-nav' not in sitecss.split("PASS31.63 UI pass", 1)[1]  # nav rules now apply to the map too
# the three map code files were re-baselined on purpose; the big spawn/shop data files must still match their original hashes
lines = dict(reversed(l.split("  ", 1)) for l in (ROOT / "audit/map-boundary.sha256").read_text().splitlines())
for rel in ("site/data/map/npcs.js", "site/data/map/monsters.js", "site/data/map/shops.js"):
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == lines[rel], rel
print("PASS31.65 map once-over gate: switches, compact nav, lighter clusters, data files intact, errors=0")
