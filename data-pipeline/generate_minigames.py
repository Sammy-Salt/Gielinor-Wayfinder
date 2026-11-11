#!/usr/bin/env python3
"""Generate site/data/minigames.json (minigame reward shops and rules) from the 2009Scape server source.

Minigame logic is embedded in code, so each minigame has its own parser with rule-literal assertions that fail loudly
if the source changes. Currently modelled: Pest Control (Void Knight commendation shop and xp conversion) and
Pyramid Plunder (rooms, xp, artifact and sceptre rates). Item ids are verified against the item catalog.

Usage: generate_minigames.py --source-root <upstream repo root> --source-commit <sha> [--output site/data/minigames.json]
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MG = "Server/src/main/content/minigame/"
PC = MG + "pestcontrol/reward/PCRewardInterface.java"
PP_UTILS = MG + "pyramidplunder/PlunderUtils.kt"
PP_DATA = MG + "pyramidplunder/PlunderData.kt"


class GeneratorError(Exception):
    pass


def read(root, rel):
    p = Path(root) / rel
    if not p.exists():
        raise GeneratorError(f"missing source file {rel}")
    return p.read_text(errors="ignore")


def prov(rel, commit, **kw):
    return {"source": "2009Scape", "file": rel, "commit": commit, **kw}


def need(text, literals, where):
    for s in literals:
        if s not in text:
            raise GeneratorError(f"rule literal not in {where}: {s}")


def key(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def herb_ids(root):
    text = read(root, "Server/src/main/content/global/skill/herblore/Herbs.java")
    return {n: int(i) for n, i in re.findall(r"\b([A-Z_]+)\(new Item\((\d+)\),", text)}


def pest_control(root, commit):
    text = read(root, PC)
    herbs = herb_ids(root)
    need(text, ["SKILL_POINTS = new int[] { 1, 10, 100 }", "CHARM_POINTS = new int[] { 2, 28, 56 }", "CHARM_AMOUNTS = new int[] { 1, 14, 28 }",
                "(int) ((double) (level * level) / 600) * N", "bonus = 1.1", "bonus = 1.01", "points >= 100", "points >= 10",
                "N = 18", "N = 32", "N = 35", "MIN_BUILD = 13", "MAX_BUILD = 18", "< 25", "!= Skills.PRAYER ? 42 : 22"], PC)
    body = text.split("public enum Reward {", 1)[1]
    rewards = []
    for skill in re.findall(r"\b([A-Z]+)\(Skills\.([A-Z]+),\s*new int\[\]", body):
        rewards.append(OrderedDict(id=f"2009scape-pestcontrol-xp-{key(skill[1])}", kind="xp", name=("Ranged" if skill[1] == "RANGE" else skill[1].capitalize()) + " experience",
                                   skill="Ranged" if skill[1] == "RANGE" else skill[1].capitalize(), pointOptions=[1, 10, 100],
                                   note="xp per point = floor(level² ÷ 600) × N (Prayer 18, Magic/Ranged 32, Attack/Strength/Defence/Hitpoints 35), ×1.01 from 10 points, ×1.1 from 100"))
    for k, name, cost, items in re.findall(r"\b([A-Z_]+)\(\"([^\"]+)\",\s*(\d+),\s*new Item\[\]\s*\{(.*?)\},\s*new int\[\]", body, re.S):
        ids = [int(i) for i in re.findall(r"new Item\((\d+)\)", items)]
        for h in re.findall(r"Herbs\.([A-Z_]+)\.getHerb\(\)", items):
            if h not in herbs:
                raise GeneratorError(f"unknown herb {h}")
            ids.append(herbs[h])
        if not ids:
            raise GeneratorError(f"reward without items: {k}")
        row = OrderedDict(id=f"2009scape-pestcontrol-{key(k)}", kind="pack" if k.endswith("PACK") else "item", name=name, points=int(cost), itemIds=ids)
        if k in ("HERB_PACK", "MINERAL_PACK", "SEED_PACK"):
            skill = {"HERB_PACK": "Herblore", "MINERAL_PACK": "Mining", "SEED_PACK": "Farming"}[k]
            row["requirements"] = [{"skill": skill, "level": 25}]
            row["note"] = "a pack is a random build of 13-18 items (seed/herb packs) or 38-43 (mineral pack); herbs and ore come noted"
        elif k.startswith("VOID_") and k != "VOID_KNIGHT_SEAL":
            row["requirements"] = [{"skill": s, "level": 42} for s in ("Hitpoints", "Attack", "Defence", "Strength", "Ranged", "Magic")] + [{"skill": "Prayer", "level": 22}]
        rewards.append(row)
    for k, name, item in re.findall(r"\b([A-Z_]+_CHARM)\(\"([^\"]+)\",\s*new Item\((\d+)\)", body):
        rewards.append(OrderedDict(id=f"2009scape-pestcontrol-{key(k)}", kind="charm", name=name, itemIds=[int(item)],
                                   options=[OrderedDict(points=p, quantity=q) for p, q in ((2, 1), (28, 14), (56, 28))]))
    for r in rewards:
        r["provenance"] = prov(PC, commit)
    return OrderedDict(
        id="2009scape-minigame-pest-control", name="Pest Control", currency="Void Knight commendation points",
        xpRule=OrderedDict(formula="points × floor(level² ÷ 600) × N × bonus", N=OrderedDict(Prayer=18, Magic=32, Ranged=32, Attack=35, Strength=35, Defence=35, Hitpoints=35),
                           bonus=OrderedDict(under10Points=1.0, from10Points=1.01, from100Points=1.1), pointOptions=[1, 10, 100],
                           note="the shop shows 'Must reach level 25 first' under 25; the divide happens in integer arithmetic before multiplying by N"),
        rewards=rewards, provenance=prov(PC, commit))


def pyramid_plunder(root, commit):
    util = read(root, PP_UTILS)
    data = read(root, PP_DATA)
    need(util, ["11 + (10 * getRoom(player)!!.room)", "* 0.66", "reward /= 2.0", "val divisor = (room * 2) * (tier * 35)", "divisor / 650.0", "divisor / 250.0",
                "1 -> 1500", "2 -> 1350", "3 -> 1250", "4 -> 1150", "else -> 1000", "(room * if(charmed) 2 else 4)", "60000 * 15"], PP_UTILS)
    urn_check = [20.0, 30.0, 50.0, 70.0, 100.0, 150.0, 225.0, 275.0]
    urn_open = [60.0, 90.0, 150.0, 215.0, 300.0, 450.0, 675.0, 825.0]
    for i, v in enumerate(urn_check, 1):
        need(util, [f"{i} -> {v}"], PP_UTILS)
    for i, v in enumerate(urn_open, 1):
        need(util, [f"{i} -> {v}"], PP_UTILS)
    rooms = re.findall(r"PlunderRoom\((\d+),\s*Location\.create\((\d+), (\d+), (\d+)\),\s*Location\.create\((\d+), (\d+), (\d+)\),\s*Direction\.(\w+)\)", data)
    if len(rooms) != 8:
        raise GeneratorError(f"expected 8 plunder rooms, parsed {len(rooms)}")
    sceptre = {1: 1500, 2: 1350, 3: 1250, 4: 1150}
    rows = []
    for n, ex, ey, ez, mx, my, mz, d in rooms:
        n = int(n)
        rows.append(OrderedDict(
            id=f"2009scape-pyramidplunder-room-{n}", kind="room", room=n, name=f"Room {n}", requirements=[{"skill": "Thieving", "level": 11 + 10 * n}],
            urnCheckXp=urn_check[n - 1], urnOpenXp=urn_open[n - 1], sarcophagusXp=urn_check[n - 1],
            chestXp=round(urn_open[n - 1] * 0.66, 2), doorXp=round(urn_open[n - 1] * 0.66, 2), lockpickDoorXp=round(urn_open[n - 1] * 0.66 / 2, 2),
            sceptreOneIn=sceptre.get(n, 1000), spearDirection=d.lower(),
            entrance=OrderedDict(x=int(ex), y=int(ey), plane=int(ez)), mummy=OrderedDict(x=int(mx), y=int(my), plane=int(mz)),
            provenance=prov(PP_UTILS, commit)))
    arts = re.search(r"val artifacts = arrayOf\((.*?)\n    \)", data, re.S).group(1)
    tiers = [[int(i) for i in re.findall(r"_(\d+)\b", g)] for g in re.findall(r"arrayOf\(([^)]*)\)", arts)]
    if [len(t) for t in tiers] != [3, 3, 3]:
        raise GeneratorError(f"artifact tiers not parsed: {tiers}")
    return OrderedDict(
        id="2009scape-minigame-pyramid-plunder", name="Pyramid Plunder", rooms=rows,
        artifacts=OrderedDict(common=tiers[0], stone=tiers[1], gold=tiers[2],
                              rule="per search of tier t (urn 1, sarcophagus 2, chest 3) in room r: divisor = r×2×t×35; gold if divisor÷650 beats the roll, else stone if divisor÷250 does, else common"),
        sceptre=OrderedDict(itemId=9050, oneInByRoom=sceptre | {"5-8": 1000}),
        rules=OrderedDict(entranceRotationMinutes=15, urnSuccess="random(thieving level) > room × 4 (room × 2 when charmed)", timeLimitTicks=500,
                          note="chest and door xp are 66% of the listed open xp; lockpicked doors give half"),
        provenance=[prov(PP_UTILS, commit), prov(PP_DATA, commit)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--output", default=str(ROOT / "site/data/minigames.json"))
    a = ap.parse_args()
    c = a.source_commit
    games = [pest_control(a.source_root, c), pyramid_plunder(a.source_root, c)]
    have = {p.stem for p in (ROOT / "site/data/items").glob("*.json")}
    used = []
    for g in games:
        for r in g.get("rewards", []):
            used += r.get("itemIds", [])
        if "artifacts" in g:
            used += g["artifacts"]["common"] + g["artifacts"]["stone"] + g["artifacts"]["gold"] + [g["sceptre"]["itemId"]]
    missing = sorted({i for i in used if str(i) not in have})
    if missing:
        raise GeneratorError(f"item ids missing from the catalog: {missing}")
    doc = OrderedDict(formatVersion=1, source="2009Scape", sourceCommit=c,
                      counts={"minigames": len(games), "rows": sum(len(g.get("rewards", [])) + len(g.get("rooms", [])) for g in games)}, minigames=games)
    Path(a.output).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
