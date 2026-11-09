#!/usr/bin/env python3
"""Generate site/data/gathering.json (Woodcutting, Mining, Fishing, Firemaking) from the 2009Scape server source.

Every table is parsed from the Kotlin/Java source with shape assertions (row counts, literals), so a source
change fails loudly instead of silently producing wrong data. Item ids are verified against the item catalog.

Usage: generate_gathering.py --source-root <upstream repo root> --source-commit <sha> [--output site/data/gathering.json]
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "Server/src/main/content/global/skill/"
T = r"Items\.[A-Z0-9_]+?_(\d+)"


class GeneratorError(Exception):
    pass


def read(root, rel):
    p = Path(root) / rel
    if not p.exists():
        raise GeneratorError(f"missing source file {rel}")
    return p.read_text(errors="ignore")


def title(base):
    return base.replace("_", " ").capitalize()


def ticks(text):
    if re.search(r"respawnRate\s*=\s*-1\s*;", text):
        return None  # the node never depletes (dramen tree, swaying tree)
    m = re.search(r"respawnRate\s*=\s*(\d+)\s*\|\s*(\d+)\s*<<\s*16", text)
    if not m:
        raise GeneratorError("respawnRate not found in case block")
    return [int(m.group(1)), int(m.group(2))]


def switch_blocks(text):
    """{identifier: block text} for `case N: case M: ... break;` groups of a node constructor switch."""
    out = {}
    for labels, body in re.findall(r"((?:case\s+\d+:\s*)+)(.*?)break;", text, re.S):
        for n in re.findall(r"case\s+(\d+):", labels):
            out[int(n)] = body
    return out


def row(skill, rid, name, level, xp, item, rel, enum, commit, **extra):
    r = OrderedDict(id=f"2009scape-{skill.lower()}-{rid}", skill=skill, name=name, level=level, xp=xp, itemId=item)
    r.update(extra)
    r["provenance"] = {"source": "2009Scape", "file": rel, "enum": enum, "commit": commit}
    return r


def woodcutting(root, commit):
    rel = BASE + "gather/woodcutting/WoodcuttingNode.java"
    text = read(root, rel)
    head, ctor = text.split("WoodcuttingNode(int full, int empty,byte identifier){", 1)
    ctor = ctor.split("WoodcuttingNode(int full, int empty, byte identifier, boolean farming)")[0]
    blocks = switch_blocks(ctor)
    groups = OrderedDict()  # base -> {identifier: count}; farming (patch) trees are excluded
    for base, ident, farming in re.findall(r"^\s*([A-Z_]+?)(?:_\d+)?\(\s*\d+,\s*-?\d+,\s*\(byte\)\s*(\d+)(,\s*true)?\)", head, re.M):
        if farming:
            continue
        groups.setdefault(base, OrderedDict()).setdefault(int(ident), 0)
        groups[base][int(ident)] += 1
    rows = []
    for base, idents in groups.items():
        if len(idents) != 1:
            raise GeneratorError(f"woodcutting {base}: several identifiers {sorted(idents)}")
        (ident, count), = idents.items()
        b = blocks.get(ident)
        if b is None:
            raise GeneratorError(f"woodcutting {base}: identifier {ident} has no case block")
        reward = int(re.search(r"reward\s*=\s*(\d+)", b).group(1))
        xp = float(re.search(r"experience\s*=\s*([0-9.]+)", b).group(1))
        level = int(re.search(r"level\s*=\s*(\d+)", b).group(1))
        name = "Tree" if base == "STANDARD_TREE" else title(base)
        rows.append(row("Woodcutting", base.lower(), name, level, xp, reward, rel, base, commit, respawnTicks=ticks(b), objectCount=count))
    if len(rows) != 19:
        raise GeneratorError(f"woodcutting: expected 19 tree types, parsed {len(rows)}")
    return rows


def mining(root, commit):
    rel = BASE + "gather/mining/MiningNode.java"
    text = read(root, rel)
    head, ctor = text.split("MiningNode(int full, int empty, byte identifier){", 1)
    blocks = switch_blocks(ctor.split("private static HashMap")[0])
    groups = OrderedDict()
    for base, ident in re.findall(r"^\s*([A-Z_]+?)(?:_\d+)?\(\s*\d+,\s*-?\d+,\s*\(byte\)\s*(\d+)\)", head, re.M):
        groups.setdefault((base, int(ident)), 0)
        groups[(base, int(ident))] += 1
    gems = [(int(i), int(w)) for i, _q, w in re.findall(r"WeightedChanceItem\((\d+),\s*(\d+),\s*(\d+)\)", head)]
    if len(gems) != 7:
        raise GeneratorError(f"mining: expected 7 gem rock outcomes, parsed {len(gems)}")
    rows = []
    for (base, ident), count in groups.items():
        b = blocks.get(ident)
        if b is None:
            raise GeneratorError(f"mining {base}: identifier {ident} has no case block")
        m = re.search(r"reward\s*=\s*identifier\s*==\s*(\d+)\s*\?\s*(\d+)\s*:\s*(\d+)", b)
        reward = (int(m.group(2)) if ident == int(m.group(1)) else int(m.group(3))) if m else int(re.search(r"reward\s*=\s*(\d+)", b).group(1))
        xp = float(re.search(r"experience\s*=\s*([0-9.]+)", b).group(1))
        level = int(re.search(r"level\s*=\s*(\d+)", b).group(1))
        extra = {"gemOutcomes": [{"itemId": i, "weight": w} for i, w in gems]} if base == "GEM_ROCK" else {}
        rows.append(row("Mining", base.lower(), title(base), level, xp, reward, rel, base, commit, respawnTicks=ticks(b), objectCount=count, **extra))
    if len(rows) != 18:
        raise GeneratorError(f"mining: expected 18 rock types, parsed {len(rows)}")
    return rows


def fishing(root, commit):
    frel = BASE + "fishing/Fish.kt"
    ftext = read(root, frel)
    fish = {}
    for e, item, lv, xp in re.findall(r"^\s*([A-Z_]+)\(" + T + r", (\d+), ([0-9.]+), [0-9.]+, [0-9.]+\)", ftext, re.M):
        fish[e] = (int(item), int(lv), float(xp))
    if len(fish) != 31:
        raise GeneratorError(f"fishing: expected 31 fish, parsed {len(fish)}")
    orel = BASE + "fishing/FishingOption.kt"
    otext = read(root, orel).split("enum class FishingOption(")[1].split("companion object")[0]
    pat = r"^\s*([A-Z_]+)\(" + T + r", (\d+), Animation\(\d+\), (null|intArrayOf\((.*?)\)), \"(\w+)\", ((?:Fish\.[A-Z_]+(?:, )?)+)\)"
    rows = []
    opts = re.findall(pat, otext, re.M)
    if len(opts) != 17:
        raise GeneratorError(f"fishing: expected 17 options, parsed {len(opts)}")
    for e, tool, tlv, _bait, baitlist, op, fl in opts:
        bait = [int(x) for x in re.findall(T, baitlist or "")]
        for f in re.findall(r"Fish\.([A-Z_]+)", fl):
            item, lv, xp = fish[f]
            rows.append(row("Fishing", f"{e.lower()}-{f.lower()}", None, max(lv, int(tlv)), xp, item, orel, f"{e}/{f}", commit,
                            option=op, tools=[int(tool)], bait=bait, fishLevel=lv, toolLevel=int(tlv)))
    # barehand (Barbarian training): levels and strength requirements are literals in Fish.kt
    if not re.search(r"barehandFishingReq = mapOf\(TUNA to 55, SWORDFISH to 70, SHARK to 96\)", ftext) or \
       not re.search(r"barehandStrengthReq = mapOf\(TUNA to 35, SWORDFISH to 50, SHARK to 76\)", ftext) or \
       not re.search(r"barehandStrengthXp = mapOf\(TUNA to 8.0, SWORDFISH to 10.0, SHARK to 11.0\)", ftext):
        raise GeneratorError("fishing: barehand literals changed")
    for f, fl, sl, sxp in (("TUNA", 55, 35, 8.0), ("SWORDFISH", 70, 50, 10.0), ("SHARK", 96, 76, 11.0)):
        item, _lv, xp = fish[f]
        rows.append(row("Fishing", f"barehand-{f.lower()}", None, fl, xp, item, frel, f"BAREHAND/{f}", commit, option="barehand", tools=[], bait=[],
                        requirements=[{"skill": "Strength", "level": sl}], extraXp=[{"skill": "Strength", "xp": sxp}], notes="Barbarian training: bare-hand fishing"))
    # barbarian fishing (Barbarian Outpost): rod + feather/bait; str/agi requirements and xp per BarbFishingPulse.kt
    brel = BASE + "gather/fishing/barbfishing/BarbFishingPulse.kt"
    btext = read(root, brel)
    need = ["hasLevelDyn(player, Skills.AGILITY, 15)", "hasLevelDyn(player, Skills.STRENGTH, 15)", "f == Fish.LEAPING_SALMON && (strength < 30 || agility < 30)",
            "f == Fish.LEAPING_STURGEON && (strength < 45 || agility < 45)", "Fish.LEAPING_TROUT    -> 5.0", "Fish.LEAPING_SALMON   -> 6.0", "Fish.LEAPING_STURGEON -> 7.0", "BARBARIAN_ROD_11323"]
    if not all(n in btext or n in read(root, BASE + "gather/fishing/barbfishing/BarbFishInteractionListeners.kt") for n in need):
        raise GeneratorError("fishing: barbarian fishing literals changed")
    for f, sa, bxp in (("LEAPING_TROUT", 15, 5.0), ("LEAPING_SALMON", 30, 6.0), ("LEAPING_STURGEON", 45, 7.0)):
        item, lv, xp = fish[f]
        rows.append(row("Fishing", f"barbarian-{f.lower()}", None, lv, xp, item, brel, f"BARBARIAN/{f}", commit, option="barbarian", tools=[11323], bait=[314, 313],
                        requirements=[{"skill": "Strength", "level": sa}, {"skill": "Agility", "level": sa}], extraXp=[{"skill": "Strength", "xp": bxp}, {"skill": "Agility", "xp": bxp}],
                        notes="Barbarian outpost fishing with a barbarian rod and feather or bait"))
    return rows


def firemaking(root, commit):
    rel = BASE + "firemaking/Log.java"
    text = read(root, rel)
    rows = []
    for e, log, lv, life, fire, xp, barb in re.findall(r"^\s*([A-Z_]+)\((\d+), (\d+), (\d+), (\d+), ([0-9.]+), (-?\d+)\)", text, re.M):
        rows.append(row("Firemaking", e.lower(), None, int(lv), float(xp), int(log), rel, e, commit, burnTicks=int(life), fireObjectId=int(fire),
                        **({"bowLevel": int(barb)} if int(barb) > 0 else {})))
    if len(rows) != 18:
        raise GeneratorError(f"firemaking: expected 18 logs, parsed {len(rows)}")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--output", default=str(ROOT / "site/data/gathering.json"))
    a = ap.parse_args()
    skills = OrderedDict()
    for name, fn in (("Woodcutting", woodcutting), ("Mining", mining), ("Fishing", fishing), ("Firemaking", firemaking)):
        skills[name] = sorted(fn(a.source_root, a.source_commit), key=lambda r: (r["level"], r["id"]))
    ids = {p.stem for p in (ROOT / "site/data/items").glob("*.json")}
    missing = sorted({(r["id"], i) for rows in skills.values() for r in rows for i in [r["itemId"], *r.get("tools", []), *r.get("bait", [])] if str(i) not in ids})
    if missing:
        raise GeneratorError(f"item ids missing from the catalog: {missing[:10]}")
    doc = OrderedDict(formatVersion=1, source="2009Scape", sourceCommit=a.source_commit,
                      counts={k: len(v) for k, v in skills.items()} | {"total": sum(len(v) for v in skills.values())}, skills=skills)
    Path(a.output).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
