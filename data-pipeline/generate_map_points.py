#!/usr/bin/env python3
"""Generate site/data/map/points.js (map points for the Map Key) from the 2009Scape server source.

Sources with real coordinates: fairy rings, fishing spot tile groups, shooting-star crash sites, enchanted-jewellery teleport
destinations, dungeon ladders (`SpecialLadders`), banker and Slayer-master NPC spawns (`npc_spawns.json`) and the clue dig spots
already extracted to `site/data/clues.json`. Each point has a `legend` category that matches a Map Key entry. Shape assertions make
a source change fail loudly; nothing is invented for categories the server repo has no coordinates for.

Usage: generate_map_points.py --source-root <upstream repo root> --source-commit <sha> [--output site/data/map/points.js]
"""
import argparse
import json
import math
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
C = "Server/src/main/content/"
FAIRY = C + "global/handlers/iface/FairyRingInterface.kt"
FISH = C + "global/skill/fishing/FishSpots.kt"
STAR = C + "global/activity/shootingstar/ShootingStar.kt"
JEWEL = C + "data/EnchantedJewellery.kt"
LADDERS = "Server/src/main/core/game/global/action/SpecialLadders.java"
SPAWNS = "Server/data/configs/npc_spawns.json"
EXPECTED = {"Fairy ring": 35, "Fishing spot": 18, "Shooting star": 42}


class GeneratorError(Exception):
    pass


def read(root, rel):
    p = Path(root) / rel
    if not p.exists():
        raise GeneratorError(f"missing source file {rel}")
    return p.read_text(errors="ignore")


def title(s):
    return " ".join(w.capitalize() for w in s.lower().split("_"))


def point(name, legend, x, y, plane, description="", **extra):
    return OrderedDict(name=name, legend=legend, x=int(x), y=int(y), plane=int(plane), description=description, **extra)


def places():
    text = (ROOT / "site/data/map/locations.js").read_text()
    out = []
    for m in re.finditer(r"name:\s*\"([^\"]+)\",\s*type:\s*\"([^\"]+)\".*?x:\s*(\d+),\s*y:\s*(\d+)", text, re.S):
        if m.group(2) in ("City", "Town", "Village", "Settlement", "Port", "Island"):
            out.append((m.group(1), int(m.group(3)), int(m.group(4))))
    if len(out) < 20:
        raise GeneratorError(f"too few named places parsed: {len(out)}")
    return out


def nearest_place(pl, x, y):
    name, px, py = min(pl, key=lambda p: (p[1] - x) ** 2 + (p[2] - y) ** 2)
    return name if math.hypot(px - x, py - y) <= 60 else None


def fairy_rings(root):
    text = read(root, FAIRY)
    rows = re.findall(r"^\s{4}([A-Z]{3})\(Location\.create\((\d+), (\d+), (\d+)\), \"([^\"]*)\"", text, re.M)
    if len(rows) != EXPECTED["Fairy ring"]:
        raise GeneratorError(f"fairy rings: expected {EXPECTED['Fairy ring']}, parsed {len(rows)}")
    return [point(f"Fairy ring {c}", "Fairy ring", x, y, z, tip) for c, x, y, z, tip in rows]


def fishing_spots(root):
    text = read(root, FISH)
    out = []
    for name, body in re.findall(r"^\s{4}([A-Z_]+)\(\s*\n(.*?)\n\s{4}\)", text, re.M | re.S):
        tiles = [tuple(map(int, t)) for t in re.findall(r"Location\((\d+), (\d+), (\d+)\)", body)]
        if not tiles:
            continue
        uniq = sorted(set(tiles))
        cx, cy = round(sum(t[0] for t in uniq) / len(uniq)), round(sum(t[1] for t in uniq) / len(uniq))
        out.append(point(f"Fishing spots: {title(name)}", "Fishing spot", cx, cy, uniq[0][2], f"{len(uniq)} possible spot tiles; the spot moves between them"))
    if len(out) != EXPECTED["Fishing spot"]:
        raise GeneratorError(f"fishing spot groups: expected {EXPECTED['Fishing spot']}, parsed {len(out)}")
    return out


def stars(root):
    text = read(root, STAR)
    body = text.split("crash_locations = mapOf(", 1)[1].split("\n    )", 1)[0]
    rows = re.findall(r"^\s*\"([^\"]+)\" to Location\.create\((\d+), (\d+), (\d+)\)", body, re.M)
    if len(rows) != EXPECTED["Shooting star"]:
        raise GeneratorError(f"shooting star sites: expected {EXPECTED['Shooting star']}, parsed {len(rows)}")
    return [point(n, "Shooting star", x, y, z, "A shooting star can crash here") for n, x, y, z in rows]


def jewellery(root):
    text = read(root, JEWEL)
    out = []
    head = text.split("enum class EnchantedJewellery", 1)[1]
    blocks = re.split(r"^    ([A-Z_0-9]+)\(", head, flags=re.M)
    for item, body in zip(blocks[1::2], blocks[2::2]):
        first = body.find("Location.create")
        options = [o for o in re.findall(r"\"([^\"]*)\"", body[:first] if first >= 0 else "") if not o.lower().startswith("nowhere")]
        tiles = re.findall(r"Location\.create\((\d+),\s*(\d+),\s*(\d+)\)", body)
        if not options:
            continue  # aliases (glory charged) and items without a destination list
        if len(options) != len(tiles):
            raise GeneratorError(f"{item}: {len(options)} options vs {len(tiles)} locations")
        for o, (x, y, z) in zip(options, tiles):
            out.append(point(o.rstrip("."), "Teleport destination", x, y, z, f"Teleport option of the {title(item).lower()}"))
    if len(out) < 20:
        raise GeneratorError(f"jewellery destinations: only {len(out)}")
    return out


def ladders(root):
    text = read(root, LADDERS)
    out = []
    for m in re.finditer(r"^\s{4}([A-Z_0-9]+)\((?:new Location|Location\.create)\(\s*(\d+),\s*(\d+),\s*(\d+)\)\s*,\s*(?:new Location|Location\.create)\(\s*(\d+),\s*(\d+),\s*(\d+)\)\)", text, re.M):
        name, x, y, z, dx, dy, dz = m.group(1), *map(int, m.groups()[1:])
        if y < 4000 and dy >= 9000:  # surface tile whose destination is in the underground map area
            label = re.sub(r"_(DOWN|UP|ENTER|LEAVE|ENTRANCE)$", "", name)
            out.append(point(title(label), "Dungeon", x, y, z, f"Ladder or steps down underground (source: {name})"))
    if len(out) < 8:
        raise GeneratorError(f"dungeon ladders: only {len(out)}")
    return out


def spawns(root):
    data = json.loads(read(root, SPAWNS))
    return {int(r["npc_id"]): [tuple(map(int, t[:3])) for t in re.findall(r"\{(\d+),(\d+),(\d+),", r["loc_data"])] for r in data}


def npc_name(nid):
    p = ROOT / "site/data/npcs" / f"{nid}.json"
    return json.loads(p.read_text()).get("name") if p.exists() else None


def banks(root, pl, sp):
    ids = [n for n in sp if npc_name(n) == "Banker"]
    if len(ids) < 10:
        raise GeneratorError(f"banker ids: {ids}")
    tiles = sorted({t for n in ids for t in sp[n]})
    clusters = []
    for x, y, z in tiles:
        for c in clusters:
            if c["z"] == z and math.hypot(c["x"] / c["n"] - x, c["y"] / c["n"] - y) <= 8:
                c["x"] += x; c["y"] += y; c["n"] += 1
                break
        else:
            clusters.append(dict(x=x, y=y, z=z, n=1))
    out = []
    for c in clusters:
        x, y = round(c["x"] / c["n"]), round(c["y"] / c["n"])
        near = nearest_place(pl, x, y)
        out.append(point(f"Bank near {near}" if near else f"Bank ({x}, {y})", "Bank", x, y, c["z"], f"{c['n']} banker{'s' if c['n'] > 1 else ''} here"))
    if len(out) < 20:
        raise GeneratorError(f"bank clusters: {len(out)}")
    return out


def slayer_masters(sp):
    doc = json.loads((ROOT / "site/data/slayer.json").read_text())
    out = []
    for m in doc["masters"]:
        for i, (x, y, z) in enumerate(sorted(set(sp.get(m["npcId"], [])))):
            out.append(point(m["name"], "Slayer Master", x, y, z, f"Slayer master: combat level {m['minCombatLevel']}+, Slayer level {m['level']}+"))
        if m["npcId"] not in sp:
            raise GeneratorError(f"no spawn for Slayer master {m['name']}")
    return out


def clue_spots():
    doc = json.loads((ROOT / "site/data/clues.json").read_text())
    out = []
    for r in doc["coordinate"]:
        out.append(point(f"{r['name']} ({r['level']})", "Clue dig spot", r["location"]["x"], r["location"]["y"], r["location"]["plane"], r["clue"]))
    for r in doc["map"]:
        out.append(point(f"{r['name']} map clue ({r['level']})", "Clue dig spot", r["location"]["x"], r["location"]["y"], r["location"]["plane"], "Treasure map clue: dig or search here"))
    if len(out) != 82:
        raise GeneratorError(f"clue spots: expected 82, got {len(out)}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--output", default=str(ROOT / "site/data/map/points.js"))
    a = ap.parse_args()
    pl, sp = places(), spawns(a.source_root)
    groups = OrderedDict([("Fairy ring", fairy_rings(a.source_root)), ("Fishing spot", fishing_spots(a.source_root)), ("Shooting star", stars(a.source_root)),
                          ("Teleport destination", jewellery(a.source_root)), ("Dungeon", ladders(a.source_root)), ("Bank", banks(a.source_root, pl, sp)),
                          ("Slayer Master", slayer_masters(sp)), ("Clue dig spot", clue_spots())])
    srcs = {"Fairy ring": FAIRY, "Fishing spot": FISH, "Shooting star": STAR, "Teleport destination": JEWEL, "Dungeon": LADDERS, "Bank": SPAWNS,
            "Slayer Master": SPAWNS, "Clue dig spot": "site/data/clues.json (2009Scape clue plugins)"}
    rows = [p for g in groups.values() for p in g]
    for i, p in enumerate(rows):
        p["id"] = f"2009scape-map-{re.sub(r'[^a-z0-9]+', '-', p['legend'].lower())}-{i}"
    meta = OrderedDict(source="2009Scape", sourceCommit=a.source_commit, counts={k: len(v) for k, v in groups.items()} | {"total": len(rows)},
                       files=OrderedDict((k, srcs[k]) for k in groups))
    out = ("/* Generated by data-pipeline/generate_map_points.py from the 2009Scape server source. Do not edit by hand. */\n"
           f"window.OSRS_MAP_POINTS_META = {json.dumps(meta, ensure_ascii=False)};\n"
           f"window.OSRS_MAP_POINTS = {json.dumps(rows, ensure_ascii=False, separators=(',', ':'))};\n")
    Path(a.output).write_text(out)
    print(json.dumps(meta["counts"]))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
