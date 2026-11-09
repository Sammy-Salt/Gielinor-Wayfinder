#!/usr/bin/env python3
"""PASS31.49 gate: gathering data (Woodcutting, Mining, Fishing, Firemaking) comes from the 2009Scape server source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site/data/gathering.json").read_text())
assert doc["formatVersion"] == 1 and doc["source"] == "2009Scape" and doc["sourceCommit"]
sk = doc["skills"]
assert {k: len(v) for k, v in sk.items()} == {"Woodcutting": 19, "Mining": 18, "Fishing": 33, "Firemaking": 18}
assert doc["counts"]["total"] == 88
ids = [r["id"] for v in sk.values() for r in v]
assert len(ids) == len(set(ids)), "duplicate row ids"
for rows in sk.values():
    for r in rows:
        assert r["provenance"]["source"] == "2009Scape" and r["provenance"]["file"].startswith("Server/src/main/content/global/skill/")
        assert r["level"] >= 1 and r["xp"] >= 0
        for i in [r["itemId"], *r.get("tools", []), *r.get("bait", [])]:
            assert (ROOT / f"site/data/items/{i}.json").exists(), (r["id"], i)
by = {s: {r["id"].split(f"2009scape-{s.lower()}-")[1]: r for r in rows} for s, rows in sk.items()}
w = by["Woodcutting"]
assert (w["yew"]["level"], w["yew"]["xp"], w["yew"]["itemId"], w["yew"]["respawnTicks"]) == (60, 175.0, 1515, [100, 162])
assert (w["magic_tree"]["level"], w["magic_tree"]["xp"]) == (75, 250.0)
assert w["arctic_pine"]["xp"] == 40.0, "live WoodcuttingNode value, not the legacy SkillingResource 140.2"
assert w["dramen_tree"]["respawnTicks"] is None and w["swaying_tree"]["respawnTicks"] is None  # never deplete
m = by["Mining"]
assert (m["runite_ore"]["level"], m["runite_ore"]["xp"], m["runite_ore"]["itemId"]) == (85, 125.0, 451)
assert (m["coal"]["level"], m["coal"]["xp"], m["coal"]["respawnTicks"]) == (30, 50.0, [50, 100])
assert m["copper_ore"]["itemId"] == 436 and m["tin_ore"]["itemId"] == 438 and m["copper_ore"]["xp"] == 17.5
assert sum(g["weight"] for g in m["gem_rock"]["gemOutcomes"]) == 128 and len(m["gem_rock"]["gemOutcomes"]) == 7
f = by["Fishing"]
assert (f["lobster_cage-lobster"]["level"], f["lobster_cage-lobster"]["xp"], f["lobster_cage-lobster"]["tools"]) == (40, 90.0, [301])
assert f["harpoon-swordfish"]["level"] == 50 and f["harpoon-tuna"]["level"] == 35  # max(fish level, option level)
assert f["lure-trout"]["bait"] == [314, 10087]
assert f["barehand-shark"]["level"] == 96 and f["barehand-shark"]["requirements"] == [{"skill": "Strength", "level": 76}]
assert f["barbarian-leaping_sturgeon"]["requirements"] == [{"skill": "Strength", "level": 45}, {"skill": "Agility", "level": 45}]
fm = by["Firemaking"]
assert (fm["yew"]["level"], fm["yew"]["xp"], fm["yew"]["burnTicks"], fm["yew"]["bowLevel"]) == (60, 202.5, 400, 80)
assert fm["jogre"]["fireObjectId"] == 3862 and "bowLevel" not in fm["jogre"]
print("PASS31.49 gathering data gate: 88 rows, errors=0")
