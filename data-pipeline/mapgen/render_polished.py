#!/usr/bin/env python3
"""Polished flat-style test render of a small area (not shipped). usage: render_polished.py out.png x0 y0 w h [plane]"""
import sys, math, numpy as np
from pathlib import Path
from PIL import Image, ImageDraw
from numpy.lib.stride_tricks import sliding_window_view
sys.path.insert(0, str(Path(__file__).parent))
from cache import Cache
from world import CACHE_DIR, load_floor_defs, parse_terrain, parse_locs, load_xteas
from objects import Objects

SS = 32          # supersample px per tile
OUT = 16         # output px per tile
TEX = {669: 0x4F86B8, 651: 0x2E4A3A}
c = Cache(CACHE_DIR / "cache"); under, over = load_floor_defs(c); xt = load_xteas(CACHE_DIR / "configs/xteas.json"); OBJ = Objects(c)
rgb = lambda v: ((v >> 16) & 255, (v >> 8) & 255, v & 255)
_cache = {}

def region(rx, ry):
    if (rx, ry) in _cache: return _cache[(rx, ry)]
    g = c.group_by_name(5, f"m{rx}_{ry}")
    terr = parse_terrain(next(iter(c.files(5, g).values()))) if g is not None else None
    locs = []
    lg = c.group_by_name(5, f"l{rx}_{ry}")
    if lg is not None:
        try: locs = parse_locs(next(iter(c.files(5, lg, xt.get((rx << 8) | ry)).values())))
        except Exception as e: print("locs fail", rx, ry, e)
    _cache[(rx, ry)] = (terr, locs); return _cache[(rx, ry)]

def classify(name):
    n = name.lower()
    for words, kind in (
        (("dead tree",), "deadtree"), (("tree", "oak", "willow", "yew", "maple", "magic tree", "evergreen", "palm", "jungle"), "tree"),
        (("bush", "shrub", "fern", "hedge"), "bush"), (("rock", "ore", "boulder"), "rock"),
        (("bank booth", "bank chest", "bank"), "bank"), (("range", "cooking", "fire", "stove", "oven"), "fire"),
        (("furnace",), "furnace"), (("anvil",), "anvil"), (("altar",), "altar"), (("well", "fountain", "pump"), "well"),
        (("stairs", "staircase", "ladder", "trapdoor", "steps"), "stairs"), (("door", "gate"), "door"),
        (("fence", "railing", "wall", "barrier"), "fence"), (("wheat", "crop", "flax", "cabbage", "potato", "onion"), "crop"),
        (("table", "chair", "stool", "bed", "shelves", "drawers", "wardrobe", "barrel", "crate", "sack", "bookcase", "cupboard", "counter", "stall"), "furniture"),
        (("sign", "post", "lamp", "lantern", "candle", "torch", "painting", "plaque", "banner"), "minor")):
        if any(w in n for w in words): return kind
    return "other" if n else "unnamed"

def build(x0, y0, w, h, plane=0):
    rx0, rx1 = x0 // 64, (x0 + w - 1) // 64; ry0, ry1 = y0 // 64, (y0 + h - 1) // 64
    PADT = 3
    W, H = w, h
    base = np.zeros((W + 2 * PADT, H + 2 * PADT, 3)); ovl = np.full((W + 2 * PADT, H + 2 * PADT, 3), -1.0); shp = np.zeros((W + 2 * PADT, H + 2 * PADT, 2), int)
    objs = []
    for rx in range(rx0 - 1, rx1 + 2):
        for ry in range(ry0 - 1, ry1 + 2):
            terr, locs = region(rx, ry)
            if terr is None: continue
            for x in range(64):
                for y in range(64):
                    gx, gy = rx * 64 + x - x0 + PADT, ry * 64 + y - y0 + PADT
                    if not (0 <= gx < W + 2 * PADT and 0 <= gy < H + 2 * PADT): continue
                    u = terr["under"][plane][x][y]
                    if u: base[gx, gy] = rgb(under.get(u - 1, {"rgb": 0})["rgb"])
                    o = terr["over"][plane][x][y] & 255
                    if o > 0 and (o - 1) in over:
                        d = over[o - 1]; col = d["rgb"]
                        if d["water"] is not None and col == 0xFFFFFF: col = TEX.get(d["texture"], 0x4F86B8) if d["texture"] != 651 else d["water"]
                        elif col in (0xFFFFFF, 0xFF00FF): col = TEX.get(d["texture"], 0x8A8A8A)
                        ovl[gx, gy] = rgb(col); shp[gx, gy] = (terr["shape"][plane][x][y], terr["rot"][plane][x][y])
            for oid, typ, rot, x, y, z in locs:
                gx, gy = rx * 64 + x - x0, ry * 64 + y - y0
                if z == plane and -4 <= gx < W + 4 and -4 <= gy < H + 4: objs.append((oid, typ, rot, gx, gy))
    # classic 5x5 underlay blend
    pad = np.pad(base, ((2, 2), (2, 2), (0, 0)), mode="edge")
    bl = sliding_window_view(pad, (5, 5), axis=(0, 1)).mean(axis=(-1, -2))
    return bl[PADT:PADT + W, PADT:PADT + H], ovl[PADT:PADT + W, PADT:PADT + H], shp[PADT:PADT + W, PADT:PADT + H], objs

def render(x0, y0, w, h, plane=0):
    bl, ovl, shp, objs = build(x0, y0, w, h, plane)
    im = Image.new("RGB", (w * SS, h * SS)); px = ImageDraw.Draw(im, "RGBA")
    T = lambda gx, gy: (gx * SS, (h - 1 - gy) * SS)      # top-left of tile, north up
    small = Image.fromarray(bl.astype("uint8").transpose(1, 0, 2)[::-1])
    im.paste(small.resize((w * SS, h * SS), Image.BICUBIC), (0, 0))
    has = lambda gx, gy: 0 <= gx < w and 0 <= gy < h and ovl[gx, gy][0] >= 0
    for gx in range(w):
        for gy in range(h):
            if ovl[gx, gy][0] < 0: continue
            L, Tp = T(gx, gy); col = tuple(int(v) for v in ovl[gx, gy]); s, r = shp[gx, gy]
            if s == 0 or s > 4: px.rectangle((L, Tp, L + SS, Tp + SS), fill=col)
            else:  # diagonal tile: keep the half that faces the neighbouring overlay tiles
                W_, E_, N_, S_ = has(gx - 1, gy), has(gx + 1, gy), has(gx, gy + 1), has(gx, gy - 1)
                cands = [(W_ + N_, [(L, Tp), (L + SS, Tp), (L, Tp + SS)]), (E_ + N_, [(L, Tp), (L + SS, Tp), (L + SS, Tp + SS)]),
                         (E_ + S_, [(L + SS, Tp), (L + SS, Tp + SS), (L, Tp + SS)]), (W_ + S_, [(L, Tp), (L, Tp + SS), (L + SS, Tp + SS)])]
                best = max(cands, key=lambda cnd: cnd[0])
                if best[0] == 0: px.rectangle((L, Tp, L + SS, Tp + SS), fill=col)
                else: px.polygon(best[1], fill=col)
    wall, wall_hi = (62, 46, 34, 255), (200, 185, 160, 255)
    walls, decor, big = [], [], []
    for oid, typ, rot, gx, gy in objs:
        d = OBJ.get(oid); k = classify(d["name"])
        if typ in (0, 1, 2, 3, 9): walls.append((oid, typ, rot, gx, gy, k))
        elif typ in (10, 11): decor.append((oid, typ, rot, gx, gy, k, d))
    def edge(L, Tp, rot):
        R, B = L + SS, Tp + SS
        return [((L, B), (L, Tp)), ((L, Tp), (R, Tp)), ((R, Tp), (R, B)), ((R, B), (L, B))][rot % 4]
    for oid, typ, rot, gx, gy, k in walls:
        L, Tp = T(gx, gy); segs = []
        if typ == 0: segs = [edge(L, Tp, rot)]
        elif typ == 2: segs = [edge(L, Tp, rot), edge(L, Tp, rot + 1)]
        elif typ == 1 or typ == 3: segs = []
        elif typ == 9: segs = [((L, Tp + SS), (L + SS, Tp))] if rot % 2 == 0 else [((L, Tp), (L + SS, Tp + SS))]
        for a, b in segs:
            if k == "door":
                px.line([a, b], fill=(150, 110, 60, 255), width=6)
            elif k == "fence":
                px.line([a, b], fill=(110, 80, 50, 255), width=3)
            else:
                px.line([a, b], fill=wall, width=7); px.line([a, b], fill=wall_hi, width=2)
    for oid, typ, rot, gx, gy, k, d in sorted(decor, key=lambda t: t[3] + t[4]):
        sx, sy = (d["sx"], d["sy"]) if rot % 2 == 0 else (d["sy"], d["sx"])
        L, Tp = T(gx, gy + sy - 1); wpx, hpx = sx * SS, sy * SS; cx, cy = L + wpx / 2, Tp + hpx / 2
        r = min(wpx, hpx) / 2
        if k == "tree":
            px.ellipse((cx - r * .95 + 3, cy - r * .95 + 4, cx + r * .95 + 3, cy + r * .95 + 4), fill=(0, 0, 0, 55))
            px.ellipse((cx - r * .95, cy - r * .95, cx + r * .95, cy + r * .95), fill=(46, 104, 40, 255), outline=(28, 70, 28, 255), width=2)
            px.ellipse((cx - r * .5, cy - r * .6, cx + r * .2, cy + r * .1), fill=(86, 150, 60, 200))
        elif k == "deadtree":
            px.line((cx - r * .7, cy + r * .7, cx + r * .7, cy - r * .7), fill=(96, 70, 48, 255), width=5); px.line((cx - r * .5, cy - r * .2, cx + r * .6, cy + r * .5), fill=(96, 70, 48, 255), width=4)
        elif k == "bush":
            px.ellipse((cx - r * .8, cy - r * .7, cx + r * .8, cy + r * .7), fill=(80, 140, 56, 255), outline=(48, 98, 40, 255), width=2)
        elif k == "rock":
            px.polygon([(cx - r * .8, cy + r * .5), (cx - r * .4, cy - r * .7), (cx + r * .5, cy - r * .6), (cx + r * .8, cy + r * .4), (cx, cy + r * .8)], fill=(120, 116, 108, 255), outline=(70, 66, 60, 255))
        elif k == "bank":
            px.rounded_rectangle((cx - r * .8, cy - r * .8, cx + r * .8, cy + r * .8), radius=5, fill=(230, 190, 60, 255), outline=(120, 90, 20, 255), width=2)
        elif k in ("fire", "furnace"):
            px.rounded_rectangle((L + 4, Tp + 4, L + wpx - 4, Tp + hpx - 4), radius=4, fill=(200, 80, 40, 255) if k == "fire" else (230, 130, 40, 255), outline=(90, 40, 20, 255), width=2)
        elif k == "anvil":
            px.polygon([(cx - r * .8, cy - r * .3), (cx + r * .8, cy - r * .3), (cx + r * .4, cy + r * .5), (cx - r * .4, cy + r * .5)], fill=(90, 90, 100, 255))
        elif k == "altar":
            px.rectangle((L + 4, Tp + 4, L + wpx - 4, Tp + hpx - 4), fill=(235, 235, 240, 255), outline=(120, 120, 140, 255), width=2)
            px.line((cx, cy - r * .6, cx, cy + r * .6), fill=(120, 120, 140, 255), width=3); px.line((cx - r * .4, cy - r * .15, cx + r * .4, cy - r * .15), fill=(120, 120, 140, 255), width=3)
        elif k == "well":
            px.ellipse((cx - r * .85, cy - r * .85, cx + r * .85, cy + r * .85), fill=(70, 130, 190, 255), outline=(110, 100, 90, 255), width=4)
        elif k == "stairs":
            px.rectangle((L + 2, Tp + 2, L + wpx - 2, Tp + hpx - 2), fill=(170, 160, 145, 255), outline=(80, 70, 60, 255), width=2)
            for i in range(1, 5): px.line((L + 2, Tp + 2 + i * (hpx - 4) / 5, L + wpx - 2, Tp + 2 + i * (hpx - 4) / 5), fill=(80, 70, 60, 255), width=2)
        elif k == "furniture":
            px.rectangle((L + 6, Tp + 6, L + wpx - 6, Tp + hpx - 6), fill=(150, 110, 70, 235), outline=(90, 62, 36, 255), width=2)
        elif k == "crop":
            px.rectangle((L + 3, Tp + 3, L + wpx - 3, Tp + hpx - 3), fill=(190, 170, 70, 150))
        elif k in ("minor", "other"):
            px.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(60, 50, 40, 140))
        # fence/door/unnamed scenery: nothing
    return im.resize((w * OUT, h * OUT), Image.LANCZOS)

if __name__ == "__main__":
    out, x0, y0, w, h = sys.argv[1], *map(int, sys.argv[2:6])
    render(x0, y0, w, h, int(sys.argv[6]) if len(sys.argv) > 6 else 0).save(out); print("ok")
