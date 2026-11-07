"""Minimal read-only reader for the 2009Scape (RS #530) Jagex cache. Pure Python, stdlib only."""
from __future__ import annotations
import bz2, gzip, struct, zlib
from pathlib import Path

SECTOR = 520


def jag_hash(name: str) -> int:
    h = 0
    for ch in name:
        h = (ord(ch) + ((h << 5) - h)) & 0xFFFFFFFF
    return h - (1 << 32) if h >= 1 << 31 else h


def xtea_decrypt(data: bytes, key: list[int]) -> bytes:
    out = bytearray(data[: len(data) // 8 * 8])
    for off in range(0, len(out), 8):
        v0, v1 = struct.unpack(">II", out[off:off + 8])
        s = (0x9E3779B9 * 32) & 0xFFFFFFFF
        for _ in range(32):
            v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (s + key[(s >> 11) & 3]))) & 0xFFFFFFFF
            s = (s - 0x9E3779B9) & 0xFFFFFFFF
            v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (s + key[s & 3]))) & 0xFFFFFFFF
        out[off:off + 8] = struct.pack(">II", v0, v1)
    return bytes(out) + data[len(out):]


def unpack_container(raw: bytes, key: list[int] | None = None) -> bytes:
    comp = raw[0]
    length = struct.unpack(">I", raw[1:5])[0]
    if comp == 0:
        body = raw[5:5 + length]
        return xtea_decrypt(body, key) if key else body
    body = raw[9:9 + length]
    if key:
        body = xtea_decrypt(body, key)
    if comp == 1:
        return bz2.decompress(b"BZh1" + body)
    if comp == 2:
        return zlib.decompress(body, 31)
    raise ValueError(f"unknown compression {comp}")


class Cache:
    def __init__(self, directory: Path):
        self.dir = Path(directory)
        self.dat = (self.dir / "main_file_cache.dat2").read_bytes()
        self._idx: dict[int, bytes] = {}
        self._ref: dict[int, dict] = {}

    def idx(self, n: int) -> bytes:
        if n not in self._idx:
            self._idx[n] = (self.dir / f"main_file_cache.idx{n}").read_bytes()
        return self._idx[n]

    def read(self, index: int, group: int) -> bytes | None:
        entry = self.idx(index)[group * 6:group * 6 + 6]
        if len(entry) < 6:
            return None
        size = int.from_bytes(entry[:3], "big"); sector = int.from_bytes(entry[3:], "big")
        if size == 0 or sector == 0:
            return None
        out = bytearray(); chunk = 0
        big = group > 65535
        while len(out) < size:
            base = sector * SECTOR
            hdr = 10 if big else 8
            block = self.dat[base:base + SECTOR]
            take = min(size - len(out), SECTOR - hdr)
            out += block[hdr:hdr + take]
            sector = int.from_bytes(block[4:7], "big") if not big else int.from_bytes(block[6:9], "big")
            chunk += 1
        return bytes(out)

    def reference(self, index: int) -> dict:
        """Parse the reference table: {'groups': {id: {'name': hash|None, 'files': [ids]}}}."""
        if index in self._ref:
            return self._ref[index]
        data = unpack_container(self.read(255, index))
        p = 0
        proto = data[p]; p += 1
        if proto >= 6:
            p += 4
        flags = data[p]; p += 1
        big = proto >= 7
        def rd_count():
            nonlocal p
            if big:
                v = struct.unpack(">I", data[p:p + 4])[0]; p += 4; return v
            v = struct.unpack(">H", data[p:p + 2])[0]; p += 2; return v
        n = rd_count()
        ids = []; acc = 0
        for _ in range(n):
            acc += rd_count(); ids.append(acc)
        groups = {i: {"name": None, "files": []} for i in ids}
        if flags & 1:
            for i in ids:
                groups[i]["name"] = struct.unpack(">i", data[p:p + 4])[0]; p += 4
        p += 4 * n  # crcs
        if flags & 4: p += 64 * n  # whirlpool
        p += 4 * n  # revisions
        counts = []
        for _ in ids:
            counts.append(rd_count())
        for i, c in zip(ids, counts):
            acc = 0
            for _ in range(c):
                acc += rd_count(); groups[i]["files"].append(acc)
        if flags & 1:
            for i, c in zip(ids, counts):
                p += 4 * c
        self._ref[index] = {"groups": groups, "byname": {g["name"]: i for i, g in groups.items() if g["name"] is not None}}
        return self._ref[index]

    def group_by_name(self, index: int, name: str) -> int | None:
        return self.reference(index)["byname"].get(jag_hash(name))

    def files(self, index: int, group: int, key: list[int] | None = None) -> dict[int, bytes]:
        """Decode a group into its files {file_id: bytes}."""
        raw = self.read(index, group)
        if raw is None:
            return {}
        data = unpack_container(raw, key)
        ids = self.reference(index)["groups"][group]["files"]
        if len(ids) == 1:
            return {ids[0]: data}
        chunks = data[-1]
        n = len(ids)
        sizes = []
        p = len(data) - 1 - chunks * n * 4
        per = [[0] * n for _ in range(chunks)]
        for c in range(chunks):
            acc = 0
            for f in range(n):
                acc += struct.unpack(">i", data[p:p + 4])[0]; p += 4
                per[c][f] = acc
        out = {fid: bytearray() for fid in ids}
        off = 0
        for c in range(chunks):
            for f, fid in enumerate(ids):
                out[fid] += data[off:off + per[c][f]]; off += per[c][f]
        return {k: bytes(v) for k, v in out.items()}
