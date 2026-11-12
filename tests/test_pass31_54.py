#!/usr/bin/env python3
"""PASS31.54 gate: Slayer data (tasks, masters, rewards, rules) comes from the 2009Scape server source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site/data/slayer.json").read_text())
assert doc["formatVersion"] == 1 and doc["source"] == "2009Scape" and doc["sourceCommit"]
assert doc["counts"] == {"tasks": 93, "masters": 6, "rewards": 10, "total": 109}
tasks = {t["key"]: t for t in doc["tasks"]}
ids = [t["id"] for t in doc["tasks"]] + [m["id"] for m in doc["masters"]]
assert len(ids) == len(set(ids)), "duplicate row ids"
assert [t["ordinal"] for t in doc["tasks"]] == list(range(93)), "ordinals must follow the source enum order (saves store them)"
for r in doc["tasks"] + doc["masters"]:
    assert r["skill"] == "Slayer" and r["provenance"]["file"].startswith("Server/src/main/content/global/skill/slayer/")
    assert r["provenance"]["source"] == "2009Scape"
assert (tasks["ABERRANT_SPECTRES"]["minCombatLevel"], tasks["ABERRANT_SPECTRES"]["level"]) == (65, 60)
assert tasks["ABYSSAL_DEMONS"]["level"] == 85 and tasks["BANSHEE"]["undead"] and tasks["BLACK_DRAGONS"]["dragon"]
assert tasks["BRINE_RATS"]["quest"] == "Olaf's Quest" and tasks["DARK_BEASTS"]["quest"] == "Mourning's End Part II" and tasks["CAVE_HORRORS"]["quest"] == "Cabin Fever"
assert tasks["KILLERWATTS"]["npcIds"] == [3201, 3202] and tasks["BIRDS"]["npcIds"].count(1475) == 1
assert [t["key"] for t in doc["tasks"] if not t["assignedBy"]] == ["FEVER_SPIDER", "MOLANISKS", "MUTATED_ZYGOMITES", "SCABARITES", "SEA_SNAKES", "SHADOW_WARRIORS", "WALL_BEASTS", "WARPED_TERROR_BIRD", "WARPED_TORTOISE"], \
    "tasks the server never assigns (commented out of every master) must stay flagged"
m = {x["key"]: x for x in doc["masters"]}
assert [(x["key"], x["npcId"], x["minCombatLevel"], x["level"]) for x in doc["masters"]] == [
    ("TURAEL", 8273, 3, 0), ("MAZCHNA", 8274, 20, 0), ("VANNAKA", 1597, 40, 0), ("CHAELDAR", 1598, 70, 0), ("SUMONA", 7780, 85, 35), ("DURADEL", 8275, 100, 50)]
assert m["TURAEL"]["defaultAmountRange"] == [15, 50] and m["DURADEL"]["completionPoints"] == {"every": 15, "tenth": 75, "fiftieth": 225}
assert [len(x["tasks"]) for x in doc["masters"]] == [23, 27, 44, 40, 26, 22]
assert [x["totalWeight"] for x in doc["masters"]] == [165, 197, 315, 321, 287, 170]
croc = [e for e in m["VANNAKA"]["tasks"] if e["taskId"].endswith("crocodiles")][0]
assert croc["weight"] == 6 and croc["amountRange"] == [30, 60]
task_ids = {t["id"] for t in doc["tasks"]}
assert all(e["taskId"] in task_ids for x in doc["masters"] for e in x["tasks"])
rw = {r["name"]: r for r in doc["rewards"]}
assert rw["Learn: Slayer helm"]["cost"] == 400 and rw["10,000 Slayer experience"]["cost"] == 400 and rw["Ring of slaying"]["items"][0]["itemId"] == 13281
for r in doc["rewards"]:
    for i in r.get("items", []):
        assert (ROOT / f"site/data/items/{i['itemId']}.json").exists()
rules = doc["rules"]
assert rules["pointsStartAfterTasks"] == 4 and rules["pointCap"] == 64000 and rules["maxBlockedTasks"] == 4 and rules["turaelAwardsPoints"] is False
print("PASS31.54 slayer data gate: 109 rows, errors=0")

_d = json.loads((ROOT / "site/data/slayer.json").read_text())
assert all(t["xpPerKill"] and t["xpPerKill"]["min"] <= t["xpPerKill"]["max"] for t in _d["tasks"])  # PASS31.62: xp per kill = NPC life points
assert {t["name"]: t["xpPerKill"]["max"] for t in _d["tasks"]}["Abyssal demons"] == 150
