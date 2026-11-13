#!/usr/bin/env python3
"""PASS31.77 gate: map rewritten as plain Leaflet on a simple CRS; one control bar; deep links kept; tile maths matches the shipped tiles."""
import subprocess
from pathlib import Path
S = Path(__file__).resolve().parents[1] / "site"
js = (S / "js/pages/map.js").read_text(encoding="utf-8")
html = (S / "map.html").read_text(encoding="utf-8")
assert subprocess.run(["node", "--check", str(S / "js/pages/map.js")]).returncode == 0
assert len(js.splitlines()) < 300, "map.js should stay small"
for n in ("L.CRS.Simple", "ORIGIN_X = 960", "ORIGIN_Y = 1216", "-c.y - 1", "maxNativeZoom", "deepLink", "const SURFACE", "function setArea", "underground view"):
    assert n in js, n
for old in ("osrsToLatLng", "mapToOSRS", "CLUSTER_CELL_PX", "map.getMaxZoom", "--map-top"):
    assert old not in js, old
for i in ("mapSearch", "mapShow", "mapFloor", "mapStatus", "mapResults"):
    assert f'id="{i}"' in html, i
for gone in ("mapTools", "legendBody", "layerSwitches"):
    assert gone not in html, gone
# Lumbridge (3222, 3218): zoom-8 tile column (x-960)//64 and TMS row (y-1216)//64 must exist on disk
assert (S / f"data/map/assets/0/8/{(3222-960)//64}/{(3218-1216)//64}.png").exists()
print("PASS31.77 map rewrite gate: simple CRS, one control bar, deep links, tile maths, errors=0")
