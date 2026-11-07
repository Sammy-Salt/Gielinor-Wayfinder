#!/usr/bin/env python3
"""Delete solid-black map tiles (the map background is black, so they add nothing).

  prune_blank_map_tiles.py [--dry-run]

PASS31.39: 23k of 29k tiles were identical solid-black PNGs on planes 1-3 and outside the world.
map.js sets errorTileUrl to a transparent tile and the map container is black, so missing tiles look identical.
Idempotent.
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "site/data/map/assets"
dry = "--dry-run" in sys.argv
removed = kept = freed = 0
for p in ROOT.rglob("*.png"):
    with Image.open(p) as im:
        cols = im.convert("RGBA").getcolors(2)
    if cols and len(cols) == 1 and cols[0][1] == (0, 0, 0, 255):
        freed += p.stat().st_size; removed += 1
        if not dry: p.unlink()
    else:
        kept += 1
if not dry:
    for d in sorted((x for x in ROOT.rglob("*") if x.is_dir()), key=lambda x: -len(x.parts)):
        if not any(d.iterdir()): d.rmdir()
print(f"removed={removed} kept={kept} bytes_freed={freed}{' (dry run)' if dry else ''}")
