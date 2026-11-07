#!/usr/bin/env python3
"""Lumbridge prototype: terrain + walls + scenery from the 2009Scape cache -> PNG (not shipped)."""
import sys, numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).parent))
from cache import Cache
from world import CACHE_DIR, load_floor_defs, parse_terrain, parse_locs, load_xteas

PX = 8
TEX = {669: 0x3C6E9F, 651: 0x17281B}
UNK = set()
c = Cache(CACHE_DIR / "cache")
under, over = load_floor_defs(c)
xt = load_xteas(CACHE_DIR / "configs/xteas.json")

def region(rx, ry):
    g = c.group_by_name(5, f"m{rx}_{ry}")
    if g is None: return None, []
    terr = parse_terrain(next(iter(c.files(5, g).values())))
    locs = []
    lg = c.group_by_name(5, f"l{rx}_{ry}")
    key = xt.get((rx << 8) | ry)
    if key and not any(key): key = None
    if lg is not None:
        try: locs = parse_locs(next(iter(c.files(5, lg, key).values())))
        except Exception as e: print("locs fail", rx, ry, e)
    return terr, locs

def rgb(v): return ((v >> 16) & 255, (v >> 8) & 255, v & 255)

def render(rx0, ry0, nx, ny, plane=0):
    W, H = nx * 64, ny * 64
    base = np.zeros((W, H, 3), float); ovl = np.full((W, H, 3), -1.0)
    walls, scen = [], []
    for ix in range(nx):
        for iy in range(ny):
            terr, locs = region(rx0 + ix, ry0 + iy)
            if terr is None: continue
            for x in range(64):
                for y in range(64):
                    u = terr["under"][plane][x][y]
                    if u: base[ix*64+x, iy*64+y] = rgb(under.get(u-1, {"rgb": 0})["rgb"])
                    o = terr["over"][plane][x][y] & 255
                    if o > 0:
                        d = over.get(o-1)
                        if d:
                            col = d["rgb"]
                            if d["water"] is not None: col = d["water"]
                            elif col == 0xFFFFFF or col == 0xFF00FF: col = TEX.get(d["texture"], 0x808080); UNK.add(d["texture"]) if d["texture"] not in TEX else None
                            if not d["hide"] or True: ovl[ix*64+x, iy*64+y] = rgb(col)
            for oid, typ, rot, x, y, z in locs:
                if z != plane: continue
                (walls if typ <= 3 else scen if typ in (9, 10, 11) else []).append((oid, typ, rot, ix*64+x, iy*64+y))
    # blur underlay over 5x5 (classic client blend)
    k = np.ones(5) / 5
    pad = np.pad(base, ((2, 2), (2, 2), (0, 0)), mode="edge")
    for ax in (0, 1):
        pad = np.apply_along_axis(lambda m: np.convolve(m, k, mode="same"), ax, pad) if False else pad
    from numpy.lib.stride_tricks import sliding_window_view
    base = sliding_window_view(pad, (5, 5), axis=(0, 1)).mean(axis=(-1, -2))
    img = np.where(ovl[..., :1] >= 0, ovl, base)
    # tiles -> pixels, north up
    im = Image.fromarray(img.astype("uint8").transpose(1, 0, 2)[::-1])
    im = im.resize((W * PX, H * PX), Image.NEAREST)
    d = ImageDraw.Draw(im)
    def P(x, y): return x * PX, (H - 1 - y) * PX
    for oid, typ, rot, x, y in walls:
        px, py = P(x, y)
        L, R, T, B = px, px + PX, py, py + PX
        seg = {0: [(L, T, L, B), (L, B, R, B)][:1], 1: [(L, T, R, T)], 2: [(R, T, R, B)], 3: [(L, B, R, B)]}
        if typ == 0: lines = {0: [(L, T, L, B)], 1: [(L, T, R, T)], 2: [(R, T, R, B)], 3: [(L, B, R, B)]}[rot]
        elif typ == 2: lines = {0: [(L, T, L, B), (L, T, R, T)], 1: [(L, T, R, T), (R, T, R, B)], 2: [(R, T, R, B), (L, B, R, B)], 3: [(L, B, R, B), (L, T, L, B)]}[rot]
        else: lines = [(L, T, R, B)] if rot % 2 == 0 else [(L, B, R, T)]
        for l in lines: d.line(l, fill=(40, 30, 20), width=2)
    for oid, typ, rot, x, y in scen:
        px, py = P(x, y)
        d.rectangle((px + 1, py + 1, px + PX - 2, py + PX - 2), fill=(70, 90, 50) if typ == 10 else (120, 100, 80))
    return im

if __name__ == "__main__":
    out = sys.argv[1]
    im = render(50, 49, 2, 2)   # Lumbridge area: x 3200-3327, y 3136-3263
    im.save(out); print(im.size, "unknown textures:", sorted(UNK))
