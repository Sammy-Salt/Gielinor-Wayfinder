"""Terrain, floor definitions and object placements from the 2009Scape cache."""
from __future__ import annotations
import json
from pathlib import Path
from cache import Cache

CACHE_DIR = Path("/tmp/claude-0/-home-claude/3dc2a412-b63c-5bef-91fd-55a78bd677bb/scratchpad/upstream/2009scape-PWA-INFO/Server/data")


class Reader:
    def __init__(self, b: bytes):
        self.b, self.p = b, 0
    def u8(self): v = self.b[self.p]; self.p += 1; return v
    def s8(self): v = self.u8(); return v - 256 if v > 127 else v
    def u16(self): v = int.from_bytes(self.b[self.p:self.p + 2], "big"); self.p += 2; return v
    def u24(self): v = int.from_bytes(self.b[self.p:self.p + 3], "big"); self.p += 3; return v
    def i32(self): v = int.from_bytes(self.b[self.p:self.p + 4], "big", signed=True); self.p += 4; return v
    def smart(self):
        return self.u8() if self.b[self.p] < 128 else self.u16() - 32768
    def smart_big(self):
        if self.b[self.p] >= 128: return self.i32() & 0x7FFFFFFF
        return self.u16()
    def string(self):
        s = self.p
        while self.b[self.p] != 0: self.p += 1
        out = self.b[s:self.p].decode("latin-1"); self.p += 1; return out
    def eof(self): return self.p >= len(self.b)


def load_floor_defs(cache: Cache) -> tuple[dict, dict]:
    """Underlay (idx2 group 1) and overlay (idx2 group 4) definitions."""
    under, over = {}, {}
    for fid, data in cache.files(2, 1).items():
        r = Reader(data); d = {"rgb": 0, "texture": -1}
        while not r.eof():
            op = r.u8()
            if op == 0: break
            if op == 1: d["rgb"] = r.u24()
            elif op == 2: d["texture"] = r.u8()
            elif op == 3: r.u16()
            elif op == 4: pass
            elif op == 5: pass
            else: break
        under[fid] = d
    for fid, data in cache.files(2, 4).items():
        r = Reader(data); d = {"rgb": 0, "texture": -1, "hide": True, "secondary": -1, "water": None}
        while not r.eof():
            op = r.u8()
            if op == 0: break
            if op == 1: d["rgb"] = r.u24()
            elif op == 2:
                t = r.u8(); d["texture"] = -1 if t == 255 else t
            elif op == 3:
                t = r.u16(); d["texture"] = -1 if t == 0xFFFF else t
            elif op == 5: d["hide"] = False
            elif op == 7: d["secondary"] = r.u24()
            elif op == 8: pass
            elif op == 9: r.u16()
            elif op == 10: pass
            elif op == 11: r.u8()
            elif op == 12: pass
            elif op == 13: d["water"] = r.u24()
            elif op == 14: r.u8()
            elif op == 15: r.u16()
            elif op == 16: r.u8()
            else: break
        over[fid] = d
    return under, over


def parse_terrain(data: bytes) -> dict:
    """64x64x4 tile arrays: underlay, overlay, shape, rotation, flags."""
    r = Reader(data)
    t = {k: [[[0] * 64 for _ in range(64)] for _ in range(4)] for k in ("under", "over", "shape", "rot", "flags", "height")}
    for z in range(4):
        for x in range(64):
            for y in range(64):
                while True:
                    op = r.u8()
                    if op == 0: break
                    if op == 1:
                        t["height"][z][x][y] = r.u8(); break
                    if op <= 49:
                        t["over"][z][x][y] = r.s8()
                        t["shape"][z][x][y] = (op - 2) >> 2
                        t["rot"][z][x][y] = (op - 2) & 3
                    elif op <= 81:
                        t["flags"][z][x][y] = op - 49
                    else:
                        t["under"][z][x][y] = op - 81
    return t


def parse_locs(data: bytes) -> list[tuple[int, int, int, int, int, int]]:
    """Object placements: (object_id, type, rotation, x, y, plane) within the region."""
    r = Reader(data); out = []
    oid = -1
    while True:
        delta = r.smart_big()
        if delta == 0: break
        oid += delta
        loc = 0
        while True:
            d = r.smart()
            if d == 0: break
            loc += d - 1
            attr = r.u8()
            out.append((oid, attr >> 2, attr & 3, (loc >> 6) & 63, loc & 63, (loc >> 12) & 3))
    return out


def load_xteas(path: Path) -> dict[int, list[int]]:
    doc = json.loads(path.read_text())
    return {int(e["regionId"]): [int(k) for k in e["keys"].split(",")] for e in doc["xteas"]}
