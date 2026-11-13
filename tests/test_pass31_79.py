#!/usr/bin/env python3
"""PASS31.79 gate: tap-an-icon hit areas (cache-derived spots + shops) and the drop-a-pin tool."""
import json, re, subprocess
from pathlib import Path
R = Path(__file__).resolve().parents[1]; S = R / "site"
js = (S / "js/pages/map.js").read_text(encoding="utf-8")
assert subprocess.run(["node", "--check", str(S / "js/pages/map.js")]).returncode == 0
assert "__map" not in js and len(js.splitlines()) < 380
for n in ("iconSpots", "refreshHits", "syncHits", "fillOpacity: 0", "bubblingMouseEvents: false", "function dropPin", "popupClosedAt", "navigator.clipboard"):
    assert n in js, n
html = (S / "map.html").read_text(encoding="utf-8")
assert html.index("points.js") < html.index("icons.js") < html.index("js/pages/map.js")
t = (S / "data/map/icons.js").read_text(encoding="utf-8")
spots = json.loads(re.search(r"OSRS_MAP_ICONS = (\[.*\]);", t, re.S).group(1))
meta = json.loads(re.search(r"OSRS_MAP_ICON_META = (\{.*\});", t).group(1))
assert 200 < len(spots) < 600 and meta["count"] == len(spots)
names = {s["name"] for s in spots}
assert {"Bank", "Altar", "Anvil", "Furnace", "Cooking range", "Spinning wheel"} <= names
assert all(n in meta["descriptions"] for n in names)
assert any(s["name"] == "Bank" and abs(s["x"] - 3185.5) < 3 and abs(s["y"] - 3439.5) < 3 for s in spots), "Varrock west bank missing"
assert (R / "data-pipeline/generate_map_icons.py").exists()
print(f"PASS31.79 map icons and pin gate: {len(spots)} icon spots, drop pin, errors=0")
