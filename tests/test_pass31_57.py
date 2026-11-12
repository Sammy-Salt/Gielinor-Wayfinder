#!/usr/bin/env python3
"""PASS31.57 gate: Barrows, Mage Training Arena shop, Blast Furnace and Castle Wars data come from the 2009Scape server source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site/data/minigames.json").read_text())
assert doc["counts"]["minigames"] >= 6
games = {g["name"]: g for g in doc["minigames"]}
assert {"Pest Control", "Pyramid Plunder", "Barrows", "Mage Training Arena", "Blast Furnace", "Castle Wars"} <= set(games)
br = games["Barrows"]
assert [b["name"] for b in br["brothers"]] == ["Ahrim", "Dharok", "Guthan", "Karil", "Torag", "Verac"]
assert [b["npcId"] for b in br["brothers"]] == list(range(2025, 2031)) and all(len(b["itemIds"]) == 4 for b in br["brothers"])
assert br["brothers"][0]["itemIds"] == [4708, 4710, 4712, 4714] and br["brothers"][4]["itemIds"] == [4745, 4747, 4749, 4751]
assert len(br["table"]) == 9 and br["totalWeight"] == 1012.0
t = {r["itemIds"][0]: r for r in br["table"]}
assert t[995]["weight"] == 380.0 and t[995]["max"] == 777 and t[1149]["weight"] == 1.0 and t[985]["weight"] == 3.0 and t[558]["min"] == 250
assert "450 − 58" in br["rules"]["brotherItemChance"]
mta = games["Mage Training Arena"]["shop"]
assert len(mta) == 24 and mta[0]["itemIds"] == [6908] and mta[0]["pizazzPoints"] == {"telekinetic": 30, "alchemist": 30, "enchantment": 300, "graveyard": 30}
assert mta[9]["itemIds"] == [6889] and mta[9]["pizazzPoints"]["enchantment"] == 6000
bf = games["Blast Furnace"]
bars = {b["name"]: b for b in bf["bars"]}
assert len(bars) == 9 and bars["Steel bar"]["level"] == 30 and bars["Steel bar"]["coalPerBar"] == 1 and bars["Runite bar"]["coalPerBar"] == 4 and bars["Mithril bar"]["coalPerBar"] == 2
assert bars["Gold bar"]["smithingXp"] == 22.5 and bars["Iron bar"]["coalPerBar"] == 0
assert bf["rules"]["entranceFeeCoins"] == 2500 and bf["rules"]["smithingRequired"] == 60 and bf["rules"]["limits"]["coal"] == 226
cw = games["Castle Wars"]
assert len(cw["exchange"]) == 19 and cw["rules"]["gameMinutes"] == 20 and len(cw["rules"]["supplyTableItemIds"]) == 7
for g in doc["minigames"]:
    for k in ("brothers", "table", "shop", "exchange"):
        for r in g.get(k, []):
            for i in r["itemIds"]:
                assert (ROOT / f"site/data/items/{i}.json").exists(), i
ids = [r["id"] for g in doc["minigames"] for k in ("rewards", "rooms", "brothers", "table", "shop", "bars", "exchange", "loot", "jobs") for r in g.get(k, [])]
assert len(ids) == len(set(ids)) >= 96
print("PASS31.57 minigame data gate: Barrows, MTA, Blast Furnace, Castle Wars, errors=0")
