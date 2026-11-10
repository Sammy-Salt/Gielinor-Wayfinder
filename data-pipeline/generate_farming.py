#!/usr/bin/env python3
"""Generate site/data/farming.json (crops, patch types, patches, compost/yield rules) from the 2009Scape server source.

`Plantable.kt` is the crop table (planting/harvest/check-health xp, level, patch type, harvest item, protection payment).
`PatchType.kt` gives minutes per growth stage, `FarmingPatch.kt` the patches, `Patch.kt` the yield rules. Shape assertions
(61 crops, 13 patch types, 45 patches) and literal checks on the rules make a source change fail loudly. Item ids are
verified against the item catalog.

Usage: generate_farming.py --source-root <upstream repo root> --source-commit <sha> [--output site/data/farming.json]
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "Server/src/main/content/global/skill/farming/"
EXPECTED = {"crops": 61, "patchTypes": 13, "patches": 45}
COMPASS = {"NW": "north-west", "NE": "north-east", "SE": "south-east", "SW": "south-west", "N": "north", "S": "south", "C": "centre", "CE": "centre"}


class GeneratorError(Exception):
    pass


def read(root, rel):
    p = Path(root) / rel
    if not p.exists():
        raise GeneratorError(f"missing source file {rel}")
    return p.read_text(errors="ignore")


def prov(rel, commit, **kw):
    return {"source": "2009Scape", "file": rel, "commit": commit, **kw}


def key(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def item_ids(expr):
    return [OrderedDict(itemId=int(i), quantity=int(q) if q else 1) for i, q in re.findall(r"Item\(Items\.[A-Z0-9_]+?_(\d+)(?:,\s*(\d+))?\)", expr)]


def patch_types(root):
    text = read(root, BASE + "PatchType.kt")
    return OrderedDict((n, int(m)) for n, m in re.findall(r"^\s{4}([A-Z_]+)\((\d+)\)[,;]", text, re.M))


def crops(root, commit, ptypes):
    rel = BASE + "Plantable.kt"
    text = read(root, rel)
    body = text.split("enum class Plantable", 1)[1].split("constructor(", 1)[0]
    names = re.findall(r"^\s{4}([A-Z_]+)\(Items\.", body, re.M)
    rows = []
    for m in re.finditer(r"^\s{4}([A-Z_]+)\(Items\.[A-Z0-9_]+?_(\d+),\s*\"([^\"]*)\",\s*(\d+),\s*(-?\d+),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*(\d+),\s*PatchType\.([A-Z_]+),\s*(?:Items\.[A-Z0-9_]+?_(\d+)|(0))(.*)$", body, re.M):
        name, seed, disp, value, stages, plant, harvest, check, level, ptype, hitem, zero, tail = m.groups()
        if ptype not in ptypes:
            raise GeneratorError(f"unknown patch type {ptype}")
        pay = item_ids(tail)
        flower = [f for f in re.findall(r"(?<![A-Za-z_.])([A-Z][A-Z_]+_SEED|SCARECROW)\b", tail) if f in names]
        stages_i = int(stages)
        row = OrderedDict(
            id=f"2009scape-farming-{key(name)}", skill="Farming", kind="scarecrow" if stages_i < 0 else "crop", name=disp[:1].upper() + disp[1:], level=int(level),
            xp=float(plant), plantingXp=float(plant), harvestXp=float(harvest), checkHealthXp=float(check),
            seedItemId=int(seed), harvestItemId=int(hitem) if hitem else None, patchType=ptype, stages=stages_i,
            stageMinutes=ptypes[ptype], growthMinutes=stages_i * ptypes[ptype] if stages_i > 0 else None,
            protectionPayment=pay, protectionFlower=f"2009scape-farming-{key(flower[-1])}" if flower else None,
            provenance=prov(rel, commit, enum=name))
        rows.append(row)
    if len(rows) != len(names):
        raise GeneratorError(f"crop parse mismatch: {len(rows)} parsed of {len(names)}")
    return rows


def patches(root, commit, ptypes):
    rel = BASE + "FarmingPatch.kt"
    text = read(root, rel)
    rows = []
    for name, varbit, ptype in re.findall(r"^\s{4}([A-Z_]+)\((\d+),\s*PatchType\.([A-Z_]+)\)", text, re.M):
        parts = name.split("_")
        label = " ".join(COMPASS.get(p, p.capitalize()) if p in COMPASS else p.capitalize() for p in parts)
        rows.append(OrderedDict(id=f"2009scape-farming-patch-{key(name)}", kind="patch", name=label[:1].upper() + label[1:], patchType=ptype, varbit=int(varbit),
                                provenance=prov(rel, commit, enum=name)))
    return rows


def rules(root, commit):
    rel = BASE + "Patch.kt"
    text = read(root, rel)
    must = ["CompostType.COMPOST -> 1", "CompostType.SUPERCOMPOST -> 2", "cropLives = 3 + compostMod",
            "Plantable.LIMPWURT_SEED, Plantable.WOAD_SEED -> 3", "Plantable.MUSHROOM_SPORE -> 6", "PatchType.ALLOTMENT -> 8", "PatchType.HOPS_PATCH -> 6", "PatchType.CACTUS_PATCH -> 3"]
    for s in must:
        if s not in text:
            raise GeneratorError(f"rule literal not in Patch.kt: {s}")
    return OrderedDict(
        baseCropLives=3, compostBonus=OrderedDict(NONE=0, COMPOST=1, SUPERCOMPOST=2),
        note="harvest amount = base amount + compost bonus (flowers, belladonna, mushrooms and evil turnips get no compost bonus); crop lives = 3 + compost bonus",
        baseHarvestAmount=OrderedDict(default=1, limpwurt=3, woad=3, mushroom=6, willow=0),
        lifeLossChance=OrderedDict(allotment=8, hops=6, cactus=3, note="1-in-N chance per pick to lose a life (source comment: inauthentic averages); herbs use a separate formula"),
        growthCycleMinutes=5, fruitRegrowMinutes=40, willowBranchRegrowMinutes=5,
        provenance=prov(rel, commit))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--output", default=str(ROOT / "site/data/farming.json"))
    a = ap.parse_args()
    c = a.source_commit
    ptypes = patch_types(a.source_root)
    cr, pa = crops(a.source_root, c, ptypes), patches(a.source_root, c, ptypes)
    pt = [OrderedDict(patchType=k, stageMinutes=v, provenance=prov(BASE + "PatchType.kt", c, enum=k)) for k, v in ptypes.items()]
    for k, rows in (("crops", cr), ("patchTypes", pt), ("patches", pa)):
        if len(rows) != EXPECTED[k]:
            raise GeneratorError(f"{k}: expected {EXPECTED[k]} rows, parsed {len(rows)}")
    ids = [r["id"] for r in cr + pa]
    if len(ids) != len(set(ids)):
        raise GeneratorError("duplicate row ids")
    flowers = {r["id"] for r in cr}
    for r in cr:
        if r["protectionFlower"] and r["protectionFlower"] not in flowers:
            raise GeneratorError(f"protection flower missing: {r['id']}")
    have = {p.stem for p in (ROOT / "site/data/items").glob("*.json")}
    used = {(r["id"], i) for r in cr for i in [r["seedItemId"], r["harvestItemId"], *[p["itemId"] for p in r["protectionPayment"]]] if i}
    missing = sorted(x for x in used if str(x[1]) not in have)
    if missing:
        raise GeneratorError(f"item ids missing from the catalog: {missing[:10]}")
    cr.sort(key=lambda r: (r["level"], r["id"]))
    doc = OrderedDict(formatVersion=1, source="2009Scape", sourceCommit=c,
                      counts={"crops": len(cr), "patchTypes": len(pt), "patches": len(pa), "total": len(cr) + len(pt) + len(pa)},
                      rules=rules(a.source_root, c), patchTypes=pt, crops=cr, patches=pa)
    Path(a.output).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
