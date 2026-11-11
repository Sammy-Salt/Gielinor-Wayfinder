#!/usr/bin/env python3
"""Generate site/data/clues.json (clue reward tables, clue levels, coordinate/map/emote clues) from the 2009Scape source.

Rewards come straight from `Server/data/configs/clue_rewards.json` (weighted tables, one roll per reward slot; see
`ClueLevel.rollLoot`). The solver data comes from the clue plugins in `content/global/activity/ttrail/`. Shape
assertions (row counts, rule literals) make a source change fail loudly; item ids are verified against the item catalog.

Usage: generate_clues.py --source-root <upstream repo root> --source-commit <sha> [--output site/data/clues.json]
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TT = "Server/src/main/content/global/activity/ttrail/"
REWARDS = "Server/data/configs/clue_rewards.json"
EXPECTED = {"coordinate": 0, "map": 25, "emote": 49}  # coordinate count is pinned after the first parse (see COORDINATE_COUNT)
COORDINATE_COUNT = 57


class GeneratorError(Exception):
    pass


def read(root, rel):
    p = Path(root) / rel
    if not p.exists():
        raise GeneratorError(f"missing source file {rel}")
    return p.read_text(errors="ignore")


def prov(rel, commit, **kw):
    return {"source": "2009Scape", "file": rel, "commit": commit, **kw}


def uncomment(text):
    return "\n".join(l for l in text.splitlines() if not l.strip().startswith("//"))


def words(s):
    return re.sub(r"[-_]+", " ", s).strip().capitalize()


def clean(text):
    return re.sub(r"\s+", " ", text.replace("<br>", " ")).strip()


def item_ids(expr):
    return [int(x) for x in re.findall(r"Items\.[A-Z0-9_]*_(\d+)\b|\b(\d{2,})\b", expr) for x in x if x]


def rewards(root, commit):
    data = json.loads(read(root, REWARDS))
    if set(data) != {"easy", "medium", "hard", "rare"}:
        raise GeneratorError(f"unexpected reward tables: {sorted(data)}")
    out = OrderedDict()
    for tier in ("easy", "medium", "hard", "rare"):
        rows = data[tier]
        total = sum(float(r["weight"]) for r in rows)
        table = [OrderedDict(itemId=int(r["id"]), min=int(r["minAmount"]), max=int(r["maxAmount"]), weight=float(r["weight"]),
                             chancePercent=round(float(r["weight"]) / total * 100, 3)) for r in rows]
        table.sort(key=lambda r: (-r["weight"], r["itemId"]))
        out[tier] = OrderedDict(totalWeight=total, items=table, provenance=prov(REWARDS, commit))
    return out


def levels(root, commit):
    rel = TT + "ClueLevel.java"
    text = read(root, rel)
    for s in ["EASY(Items.CASKET_2714, 1, 5)", "MEDIUM(Items.CASKET_2717, 1, 6)", "HARD(Items.CASKET_2720, 1, 8)", "RandomFunction.random(1,6)",
              "Math.max(itemCount, RandomFunction.random(4,6))", "RandomFunction.random(100) == 50", "getRareTable().roll"]:
        if s not in text:
            raise GeneratorError(f"level literal not in ClueLevel.java: {s}")
    return OrderedDict(
        easy=OrderedDict(casketItemId=2714, minSteps=1, maxSteps=5), medium=OrderedDict(casketItemId=2717, minSteps=1, maxSteps=6),
        hard=OrderedDict(casketItemId=2720, minSteps=1, maxSteps=8),
        rewardRolls=OrderedDict(slots="random(1, 6) rolls on the level's table; Hard takes the larger of that and random(4, 6)",
                                rareTable="Hard only: one extra roll on the rare table when random(100) == 50"),
        provenance=prov(rel, commit))


def coordinate(root, commit):
    rel = TT + "CoordinateCluePlugin.java"
    text = uncomment(read(root, rel))
    rows = []
    for name, cid, lvl, x, y, z, clue in re.findall(r"register\(new CoordinateCluePlugin\(\"([^\"]+)\",\s*(\d+),\s*ClueLevel\.(\w+),\s*new Location\((\d+),\s*(\d+),\s*(\d+)\),\s*\"([^\"]+)\"\)\)", text):
        rows.append(OrderedDict(id=f"2009scape-clue-coordinate-{name}-{cid}", kind="coordinate", level=lvl.lower(), name=words(name.replace("-coord", "")),
                                clueItemId=int(cid), clue=clean(clue), location=OrderedDict(x=int(x), y=int(y), plane=int(z)),
                                provenance=prov(rel, commit, key=name)))
    names = [r["name"] for r in rows]
    for r in rows:  # the source reuses "bandit-camp-coord" for two different clues
        if names.count(r["name"]) > 1:
            r["name"] += f" ({r['location']['x']}, {r['location']['y']})"
    return rows


def maps(root, commit):
    rel = TT + "MapCluePlugin.kt"
    text = uncomment(read(root, rel))
    rows = []
    pat = r"register\(MapCluePlugin\(\"([^\"]+)\",\s*(?:Items\.CLUE_SCROLL_)?(\d+),\s*ClueLevel\.(\w+),\s*Components\.TRAIL_MAP(\d+)_(\d+),\s*Location\.create\((\d+),\s*(\d+),\s*(\d+)\)(?:,\s*(\d+),\s*ZoneBorders\(([^)]*)\))?\)\)"
    for name, cid, lvl, mapno, comp, x, y, z, obj, zone in re.findall(pat, text):
        row = OrderedDict(id=f"2009scape-clue-map-{name}", kind="map", level=lvl.lower(), name=words(name), clueItemId=int(cid),
                          interfaceId=int(comp), location=OrderedDict(x=int(x), y=int(y), plane=int(z)))
        if obj:
            row["searchObjectId"] = int(obj)
            row["area"] = [int(n) for n in re.findall(r"\d+", zone)]
        row["provenance"] = prov(rel, commit, key=name)
        rows.append(row)
    return rows


def emotes(root, commit):
    rel = TT + "EmoteCluePlugin.kt"
    wild = re.search(r"WILDY_CAPES = new int\[\] \{(.*?)\}", read(root, TT + "ClueScrollPlugin.java"), re.S)
    capes = [int(n) for n in re.findall(r"_(\d+)\b", wild.group(1))] if wild else []
    if not capes:
        raise GeneratorError("WILDY_CAPES not parsed")
    rows, current = [], None
    for line in read(root, rel).splitlines():
        s = line.strip()
        if s.startswith("//"):
            continue
        e = re.match(r"(?:var )?emote = Emotes\.(\w+)", s)
        if e:
            current = e.group(1)
            continue
        m = re.match(r"register\(EmoteCluePlugin\(\"([^\"]+)\",\s*Items\.CLUE_SCROLL_(\d+),\s*ClueLevel\.(\w+),\s*(emote|Emotes\.\w+),\s*(?:(Emotes\.\w+),\s*)?(.*?),\s*\"((?:[^\"\\]|\\.)*)\"(.*)\)\)\s*$", s)
        if not m:
            continue
        name, cid, lvl, emote, commence, mid, text, tail = m.groups()
        emote = current if emote == "emote" else emote.split(".")[1]
        equipment, slots = [], []
        for g in re.findall(r"intArrayOf\(([^)]*)\)", mid):
            if "EquipmentSlot" in g:
                slots = [x.lower() for x in re.findall(r"EquipmentSlot\.(\w+)\.ordinal", g)]
            else:
                equipment.append(item_ids(g))
        if "WILDY_CAPES" in mid:
            equipment.append(capes)
        zone = re.search(r"ZoneBorders\(([^)]*)\)", tail)
        row = OrderedDict(id=f"2009scape-clue-emote-{name}", kind="emote", level=lvl.lower(), name=words(name), clueItemId=int(cid),
                          emote=words(emote), commenceEmote=words(commence.split(".")[1]) if commence else None, clue=clean(text),
                          equipment=equipment, emptySlots=slots, area=[int(n) for n in re.findall(r"\d+", zone.group(1))] if zone else None,
                          provenance=prov(rel, commit, key=name))
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--output", default=str(ROOT / "site/data/clues.json"))
    a = ap.parse_args()
    c = a.source_commit
    groups = OrderedDict(coordinate=coordinate(a.source_root, c), map=maps(a.source_root, c), emote=emotes(a.source_root, c))
    want = dict(EXPECTED, coordinate=COORDINATE_COUNT)
    for k, n in want.items():
        if len(groups[k]) != n:
            raise GeneratorError(f"{k}: expected {n} rows, parsed {len(groups[k])}")
    allrows = [r for g in groups.values() for r in g]
    ids = [r["id"] for r in allrows]
    if len(ids) != len(set(ids)):
        raise GeneratorError("duplicate row ids")
    cids = [r["clueItemId"] for r in allrows]
    if len(cids) != len(set(cids)):
        raise GeneratorError("duplicate clue scroll item ids")
    have = {p.stem for p in (ROOT / "site/data/items").glob("*.json")}
    rw = rewards(a.source_root, c)
    used = {i["itemId"] for t in rw.values() for i in t["items"]} | set(cids) | {i for r in groups["emote"] for g in r["equipment"] for i in g}
    missing = sorted(i for i in used if str(i) not in have)
    if missing:
        raise GeneratorError(f"item ids missing from the catalog: {missing[:12]}")
    order = {"easy": 0, "medium": 1, "hard": 2}
    for rows in groups.values():
        rows.sort(key=lambda r: (order[r["level"]], r["id"]))
    doc = OrderedDict(formatVersion=1, source="2009Scape", sourceCommit=c,
                      counts={k: len(v) for k, v in groups.items()} | {"rewardItems": sum(len(t["items"]) for t in rw.values()), "total": len(allrows)},
                      levels=levels(a.source_root, c), rewards=rw, **groups)
    Path(a.output).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
