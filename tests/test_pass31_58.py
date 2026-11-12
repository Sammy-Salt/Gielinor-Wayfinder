#!/usr/bin/env python3
"""PASS31.58 gate: Fishing Trawler and Gnome Restaurant data come from the 2009Scape server source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site/data/minigames.json").read_text())
assert doc["counts"] == {"minigames": 8, "rows": 126}
games = {g["name"]: g for g in doc["minigames"]}
assert {"Fishing Trawler", "Gnome Restaurant"} <= set(games)
ft = games["Fishing Trawler"]
assert ft["requirements"] == [{"skill": "Fishing", "level": 15}] and ft["totalWeight"] == 2078 and len(ft["loot"]) == 15
w = {(r["kind"], tuple(r["itemIds"])): r["weight"] for r in ft["loot"]}
assert w[("fish", ())] == 1430 and w[("misc", (405,))] == 60 and w[("misc", (2651,))] == 2 and w[("misc", (7140,))] == 2 and w[("misc", (985,))] == 7
assert sum(1 for r in ft["loot"] if r["kind"] == "junk") == 9 and ft["loot"][0]["chancePercent"] == round(1430 / 2078 * 100, 3)
assert [(f["itemId"], f["level"]) for f in ft["fish"]] == [(317, 1), (327, 5), (321, 15), (359, 35), (377, 40), (371, 50), (383, 76), (395, 79), (389, 81)]
assert "0.015 × level² × rolls" in ft["rules"]["xp"]
gr = games["Gnome Restaurant"]["jobs"]
assert len(gr) == 15 and sum(j["difficulty"] == "easy" for j in gr) == 8 and gr[0]["npcId"] == 3811
for g in (ft,):
    for r in g["loot"]:
        for i in r["itemIds"]:
            assert (ROOT / f"site/data/items/{i}.json").exists(), i
ids = [r["id"] for g in doc["minigames"] for k in ("rewards", "rooms", "brothers", "table", "shop", "bars", "exchange", "loot", "jobs") for r in g.get(k, [])]
assert len(ids) == len(set(ids)) == 126
print("PASS31.58 minigame data gate: 8 minigames, 126 rows, errors=0")
