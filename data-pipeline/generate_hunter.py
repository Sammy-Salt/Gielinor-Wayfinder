#!/usr/bin/env python3
"""Generate site/data/hunter.json (traps, butterflies, implings, falconry, tracking, pitfalls) from the 2009Scape source.

Parsed with regex plus shape assertions (row counts per section) so a source change fails loudly. Creature names come
from the NPC catalog (site/data/npcs), item ids are verified against the item catalog.

Usage: generate_hunter.py --source-root <upstream repo root> --source-commit <sha> [--output site/data/hunter.json]
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "Server/src/main/content/global/skill/hunter/"
CATALOG_GAPS = {10092}  # Ferret: used by the Box trap in the server, absent from the item catalog (not invented here)
EXPECTED = {"traps": 45, "butterflies": 4, "implings": 10, "falconry": 3, "tracking": 2, "pitfalls": 3}
TRAP_TYPES = {  # key -> (setting file/source, level, items required to lay it; ids from the TrapSetting constructors)
    "BIRD_SNARE": ("Traps.java", 1, [10006]),
    "BOX_TRAP": ("Traps.java", 27, [10008]),
    "RABBIT_SNARE": ("Traps.java", 27, [10031]),
    "DEAD_FALL": ("DeadfallSetting.java", 23, [946]),
    "NET_TRAP": ("NetTrapSetting.java", 29, [303, 954]),
    "IMP_BOX": ("MagicBoxSetting.java", 27, [10025]),
}


class GeneratorError(Exception):
    pass


def read(root, rel):
    p = Path(root) / rel
    if not p.exists():
        raise GeneratorError(f"missing source file {rel}")
    return p.read_text(errors="ignore")


def prov(rel, commit, **kw):
    return {"source": "2009Scape", "file": rel, "commit": commit, **kw}


def nums(expr):
    return [int(x) for x in re.findall(r"(?:[A-Za-z_]+_)?(\d+)", expr)]


def items(expr):
    out = []
    for args in re.findall(r"new (?:Item|ChanceItem)\(([^)]*)\)", expr):
        a = [x.strip() for x in args.split(",")]
        m = re.search(r"(\d+)$", a[0])
        if not m:
            raise GeneratorError(f"item not parsed: {args}")
        out.append(OrderedDict(itemId=int(m.group(1)), quantity=int(a[1]) if len(a) > 1 and a[1].isdigit() else 1))
    return out


def npc_name(root_site, nid):
    p = root_site / "site/data/npcs" / f"{nid}.json"
    if p.exists():
        return json.loads(p.read_text()).get("name")
    return None


# Creatures missing from the NPC catalog: (name, where the name comes from)
NAME_FALLBACK = {
    5080: ("Red chinchompa", "2009Scape source comment (Traps.java)"),
    5116: ("Black salamander", "2009Scape source comment (Traps.java)"),
    708: ("Imp", "2009Scape trap type IMP_BOX"),
    5088: ("Barb-tailed kebbit", "OSRS Wiki (not named in the 2009Scape source or NPC catalog)"),
}


def key(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def traps(root, commit):
    rel = BASE + "Traps.java"
    text = read(root, rel)
    body = text.split("public enum Traps", 1)[1].split("The location hooks", 1)[0]
    rows = []
    for tkey, chunk in re.findall(r"\n\t([A-Z_]+)\(((?:.|\n)*?)(?=\n\t[A-Z_]+\(|\Z)", body):
        if tkey not in TRAP_TYPES:
            continue
        segs = re.split(r"new (TrapNode|BoxTrapNode|NetTrapNode)\(", chunk)
        for cls, seg in zip(segs[1::2], segs[2::2]):
            m = re.match(r"new int\[\]\s*\{([^}]*)\},\s*(\d+),\s*([\d.]+),\s*(.*)", seg, re.S)
            if not m:
                raise GeneratorError(f"trap node not parsed in {tkey}")
            npcs, level, xp, rest = nums(m.group(1)), int(m.group(2)), float(m.group(3)), m.group(4)
            objs = []
            if cls == "TrapNode":
                om = re.match(r"new int\[\]\s*\{([^}]*)\}", rest)
                objs = nums(om.group(1)) if om else []
            summ = None
            if cls != "TrapNode":
                sm = re.search(r"Item\[\]\s*\{.*?\}\s*,\s*(\d+)\)", rest, re.S)
                summ = int(sm.group(1)) if sm else None
            rewards = items(re.search(r"Item\[\]\s*\{(.*?)\}", rest, re.S).group(1))
            rows.append(OrderedDict(trap=tkey, level=level, xp=xp, npcIds=npcs, objectIds=objs, rewards=rewards, summoningLevel=summ))
    return rows


def butterflies(root, commit):
    rel = BASE + "bnet/BNetTypes.java"
    text = read(root, rel)
    rows = []
    for name, ids, lv, xp, jar in re.findall(r"\n\t([A-Z_]+)\(new BNetNode\(new int\[\]\s*\{([^}]*)\},\s*new int\[\]\s*\{([^}]*)\},\s*new double\[\]\s*\{([^}]*)\}.*?new ChanceItem\((\d+)\)", text):
        L = nums(lv)
        rows.append(OrderedDict(
            id=f"2009scape-hunter-butterfly-{key(name)}", skill="Hunter", kind="butterfly", name=name.replace("_", " ").title(),
            level=L[0], xp=float(xp.split(",")[0]), experience=[float(x) for x in xp.split(",")], bareHandLevel=L[1], agilityLevel=L[2],
            npcIds=nums(ids), itemId=int(jar), provenance=prov(rel, commit, enum=name)))
    return rows


def implings(root, commit):
    rel = BASE + "bnet/BNetTypes.java"
    text = read(root, rel)
    rows = []
    for line in re.findall(r"\n\t([A-Z_]+_IMPLING\(new ImplingNode\(.*)", text):
        name = line.split("(", 1)[0]
        m = re.match(r"[A-Z_]+\(new ImplingNode\(new int\[\]\s*\{([^}]*)\},\s*(\d+),\s*([\d.]+),\s*([\d.]+),\s*new Item\((\d+)\)(?:,\s*(\d+))?,", line)
        if not m:
            raise GeneratorError(f"impling not parsed: {name}")
        loot = []
        for args in re.findall(r"new ChanceItem\(([^)]*)\)", line):
            a = [x.strip() for x in args.split(",")]
            freq = re.search(r"DropFrequency\.(\w+)", args)
            loot.append(OrderedDict(itemId=int(a[0]), min=int(a[1]), max=int(a[2]), frequency=freq.group(1) if freq else None))
        if not loot:
            raise GeneratorError(f"impling without loot: {name}")
        rows.append(OrderedDict(
            id=f"2009scape-hunter-impling-{key(name.replace('_IMPLING', ''))}", skill="Hunter", kind="impling",
            name=name.replace("_", " ").title(), level=int(m.group(2)), xp=float(m.group(3)), puroPuroXp=float(m.group(4)),
            npcIds=nums(m.group(1)), itemId=int(m.group(5)), respawnTicks=int(m.group(6)) if m.group(6) else None, loot=loot,
            provenance=prov(rel, commit, enum=name)))
    return rows


def spawners(root):
    text = read(root, BASE + "implings/ImplingData.kt")
    out = []
    for name, nid, body in re.findall(r"(\w+Tier)\s*\(npcId\s*=\s*(\d+),\s*WeightedTable\.create\s*\((.*?)\)\s*\)", text, re.S):
        out.append(OrderedDict(name=name, npcId=int(nid), weights=[OrderedDict(impling=i, weight=float(w)) for i, w in re.findall(r"Impling\.(\w+),\s*([\d.]+)", body)]))
    if len(out) != 6:
        raise GeneratorError(f"expected 6 impling spawner tiers, parsed {len(out)}")
    return out


def falconry(root, commit):
    rel = BASE + "falconry/FalconCatch.java"
    text = read(root, rel)
    rows = []
    for name, npc, level, xp, item in re.findall(r"([A-Z_]+_KEBBIT)\((\d+),\s*(\d+),\s*(\d+),\s*new Item\((\d+)\)\)", text):
        rows.append(OrderedDict(id=f"2009scape-hunter-falconry-{key(name)}", skill="Hunter", kind="falconry", name=name.replace("_", " ").title(),
                                level=int(level), xp=float(xp), npcIds=[int(npc)], itemId=int(item), provenance=prov(rel, commit, enum=name)))
    return rows


def tracking(root, commit):
    rows = []
    for fname, kname, lvl_default in (("PolarKebbitHunting.kt", "Polar kebbit", 1), ("CommonKebbitEast.kt", "Common kebbit", 1)):
        rel = BASE + "tracking/" + fname
        text = read(root, rel)
        xp = float(re.search(r"experience\s*=\s*([\d.]+)", text).group(1))
        lm = re.search(r"requiredLevel\s*=\s*(\d+)", text)
        rw = re.search(r"rewards\s*=\s*arrayOf\((.*?)\)\s*\n", text, re.S).group(1)
        rows.append(OrderedDict(id=f"2009scape-hunter-tracking-{key(kname)}", skill="Hunter", kind="tracking", name=kname,
                                level=int(lm.group(1)) if lm else lvl_default, xp=xp,
                                rewards=[OrderedDict(itemId=i, quantity=1) for i in nums(rw)],
                                note="level defaults to 1 when the source sets none; a kebbit-tracking trail needs the trail to be followed",
                                provenance=prov(rel, commit)))
    return rows


def pitfalls(root, commit):
    rel = BASE + "pitfall/HunterPitfall.kt"
    text = read(root, rel)
    reqs = dict((n, int(l)) for n, l in re.findall(r'"([A-Z][^"]+)" to (\d+)', text.split("val HUNTER_REQS", 1)[1].split(")", 1)[0]))
    loots = re.findall(r"lootCorpse\(player, node as Scenery, ([\d.]+), Items\.[A-Z_]+_(\d+), Items\.[A-Z_]+_(\d+)\)", text)
    names = list(reqs)
    if len(names) != 3 or len(loots) != 3:
        raise GeneratorError("pitfall shape changed")
    rows = []
    for (xp, good, bad), name in zip(loots, names):
        rows.append(OrderedDict(id=f"2009scape-hunter-pitfall-{key(name)}", skill="Hunter", kind="pitfall", name=name, level=reqs[name], xp=float(xp),
                                rewards=[OrderedDict(itemId=int(good), quantity=1), OrderedDict(itemId=int(bad), quantity=1)],
                                note="xp is the corpse-looting xp; good/tatty fur depends on the catch",
                                provenance=prov(rel, commit)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--output", default=str(ROOT / "site/data/hunter.json"))
    a = ap.parse_args()
    c = a.source_commit
    tr = traps(a.source_root, c)
    for r in tr:
        n = npc_name(ROOT, r["npcIds"][0])
        r["name"] = n
        r["nameSource"] = "2009Scape NPC catalog"
        if n is None:
            r["name"], r["nameSource"] = NAME_FALLBACK[r["npcIds"][0]]
        r["id"] = f"2009scape-hunter-{key(r['trap'])}-{r['npcIds'][0]}"
        r["skill"], r["kind"] = "Hunter", "trap-creature"
        r["provenance"] = prov(BASE + "Traps.java", c, enum=r["trap"])
    types = [OrderedDict(trap=k, level=v[1], layItemIds=v[2], provenance=prov(BASE + v[0], c)) for k, v in TRAP_TYPES.items()]
    groups = OrderedDict(traps=tr, butterflies=butterflies(a.source_root, c), implings=implings(a.source_root, c),
                         falconry=falconry(a.source_root, c), tracking=tracking(a.source_root, c), pitfalls=pitfalls(a.source_root, c))
    for k, want in EXPECTED.items():
        if len(groups[k]) != want:
            raise GeneratorError(f"{k}: expected {want} rows, parsed {len(groups[k])}")
    ids = [r["id"] for rows in groups.values() for r in rows]
    if len(ids) != len(set(ids)):
        raise GeneratorError("duplicate row ids")
    for rows in groups.values():
        rows.sort(key=lambda r: (r["level"], r["id"]))
    have = {p.stem for p in (ROOT / "site/data/items").glob("*.json")}
    used = set()
    for rows in groups.values():
        for r in rows:
            for x in r.get("rewards", []) + r.get("loot", []):
                used.add((r["id"], x["itemId"]))
            if "itemId" in r:
                used.add((r["id"], r["itemId"]))
    used |= {(t["trap"], i) for t in types for i in t["layItemIds"]}
    missing = sorted(x for x in used if str(x[1]) not in have and x[1] not in CATALOG_GAPS)
    if missing:
        raise GeneratorError(f"item ids missing from the catalog: {missing[:10]}")
    doc = OrderedDict(formatVersion=1, source="2009Scape", sourceCommit=c,
                      counts={k: len(v) for k, v in groups.items()} | {"total": sum(len(v) for v in groups.values())},
                      trapTypes=types, implingSpawners=spawners(a.source_root), **groups)
    Path(a.output).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
