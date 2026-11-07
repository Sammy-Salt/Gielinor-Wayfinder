#!/usr/bin/env python3
"""PASS31.39 map gate: marker coordinates, clustering, shell wiring, pruned tiles."""
import re
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parents[1]; S = R / "site"; errors = []
def chk(c, m):
    if not c: errors.append(m)
js = (S / "js/pages/map.js").read_text(); html = (S / "map.html").read_text()
chk("map.getMaxZoom()\n    );" not in js and re.search(r"L\.point\(px, py\),\s*11\s*\)", js), "osrsToLatLng must project at zoom 11 (matches mapToOSRS)")
chk("function escapeHtml" in js, "map.js must define escapeHtml")
chk("drawKind" in js and "CLUSTER_CELL_PX" in js, "marker clustering missing")
chk("errorTileUrl" in js, "tile layers need errorTileUrl for pruned tiles")
chk('id="site-nav"' in html and "js/bootstrap.js" in html, "map.html must use the shared shell")
chk('src="js/core/utils.js"' not in html and 'src="js/core/shell.js"' not in html, "ES-module files must not load as classic scripts")
tiles = list((S / "data/map/assets").rglob("*.png"))
chk(len(tiles) == 6624, f"tile count {len(tiles)}")
black = 0
for p in tiles[::25]:
    with Image.open(p) as im:
        c = im.convert("RGBA").getcolors(2)
    black += bool(c and len(c) == 1 and c[0][1] == (0, 0, 0, 255))
chk(black == 0, f"solid-black tiles still shipped ({black} in sample)")
print(f"PASS31.39 map gate: tiles={len(tiles)} errors={len(errors)}")
if errors:
    [print("FAIL:", e) for e in errors]; raise SystemExit(1)
