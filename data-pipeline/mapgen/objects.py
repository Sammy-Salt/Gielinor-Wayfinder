"""Object definitions (cache index 16, group = id >> 8, file = id & 255) for map rendering."""
from __future__ import annotations
from world import Reader


def parse_object(data: bytes) -> dict:
    r = Reader(data)
    d = {"name": "", "sx": 1, "sy": 1, "solid": True, "mapscene": -1, "icon": -1, "interactive": None}
    try:
        while not r.eof():
            op = r.u8()
            if op == 0: break
            if op == 1:
                for _ in range(r.u8()): r.u16(); r.u8()
            elif op == 2: d["name"] = r.string()
            elif op == 3: r.string()
            elif op == 5:
                for _ in range(r.u8()): r.u16()
            elif op == 14: d["sx"] = r.u8()
            elif op == 15: d["sy"] = r.u8()
            elif op == 17: d["solid"] = False
            elif op == 18: pass
            elif op == 19: d["interactive"] = r.u8()
            elif op in (21, 22, 23, 62, 64, 73, 74): pass
            elif op == 102: r.u16()
            elif op == 24: r.u16()
            elif op == 27: pass
            elif op == 28: r.u8()
            elif op == 29: r.u8()
            elif 30 <= op < 35: r.string()
            elif op == 39: r.u8()
            elif op == 40:
                for _ in range(r.u8()): r.u16(); r.u16()
            elif op == 41:
                for _ in range(r.u8()): r.u16(); r.u16()
            elif op == 42:
                for _ in range(r.u8()): r.u8()
            elif op in (65, 66, 67): r.u16()
            elif op == 68: d["mapscene"] = r.u16()
            elif op == 69: r.u8()
            elif op in (70, 71, 72): r.u16()
            elif op == 75: r.u8()
            elif op in (77, 92):
                r.u16(); r.u16()
                if op == 92: r.u16()
                for _ in range(r.u8() + 1): r.u16()
            elif op == 78: r.u16(); r.u8()
            elif op == 79:
                r.u16(); r.u16(); r.u8()
                for _ in range(r.u8()): r.u16()
            elif op == 81: r.u8()
            elif op == 82: d["icon"] = r.u16()
            elif op == 89: pass
            elif op == 249:
                for _ in range(r.u8()):
                    is_str = r.u8(); r.u24()
                    r.string() if is_str else r.i32()
            else:
                d["_stopped"] = op; break
    except IndexError:
        d["_stopped"] = "eof"
    return d


class Objects:
    def __init__(self, cache):
        self.c, self._g, self._d = cache, {}, {}

    def get(self, oid: int) -> dict:
        if oid in self._d: return self._d[oid]
        g = oid >> 8
        if g not in self._g:
            try: self._g[g] = self.c.files(16, g)
            except Exception: self._g[g] = {}
        raw = self._g[g].get(oid & 255)
        self._d[oid] = parse_object(raw) if raw else {"name": "", "sx": 1, "sy": 1, "solid": True, "mapscene": -1, "icon": -1}
        return self._d[oid]
