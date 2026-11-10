#!/usr/bin/env python3
"""PASS31.50 gate: Thieving data (pickpockets, stalls, chests) comes from the 2009Scape server source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site/data/thieving.json").read_text())
assert doc["formatVersion"] == 1 and doc["source"] == "2009Scape" and doc["sourceCommit"]
assert doc["counts"] == {"pickpockets": 18, "stalls": 18, "chests": 6, "total": 42}
rows = doc["pickpockets"] + doc["stalls"] + doc["chests"]
ids = [r["id"] for r in rows]
assert len(ids) == len(set(ids)), "duplicate row ids"
for r in rows:
    assert r["skill"] == "Thieving" and r["level"] >= 1 and r["xp"] > 0
    assert r["provenance"]["source"] == "2009Scape" and r["provenance"]["file"].startswith("Server/src/main/content/global/skill/thieving/")
    for l in r["loot"]:
        if "itemId" in l:
            assert (ROOT / f"site/data/items/{l['itemId']}.json").exists(), (r["id"], l["itemId"])
by = {r["id"].split("-", 3)[-1]: r for r in rows}
p = {r["name"]: r for r in doc["pickpockets"]}
assert (p["Man"]["level"], p["Man"]["xp"], p["Man"]["loot"][0]["itemId"], p["Man"]["loot"][0]["chancePercent"]) == (1, 8.0, 995, 100.0)
assert (p["Hero"]["level"], p["Hero"]["xp"]) == (80, 273.3) and p["Hero"]["successLow"] == 6.0 and p["Hero"]["successHigh"] == 100.0
assert len(p["Master farmer"]["loot"]) == 38 and len(p["Guard"]["npcIds"]) >= 30
assert p["Knight of Ardougne"]["xp"] == 84.3
for name in ("Male ham member", "Female ham member"):  # the only tables with an easy-clue roll
    clue = [l for l in p[name]["loot"] if l.get("clue") == "easy"]
    assert len(clue) == 1 and clue[0]["chancePercent"] > 0
    assert abs(sum(l["chancePercent"] for l in p[name]["loot"]) - 100) < 0.1
s = {r["name"]: r for r in doc["stalls"]}
assert (s["Gem stall"]["level"], s["Gem stall"]["xp"], s["Gem stall"]["respawnTicks"]) == (75, 160.0, 300)
assert [l["itemId"] for l in s["Vegetable stall"]["loot"]] == [1957, 1965, 1942, 1982, 1550]
assert s["Vegetable stall"]["emptyObjectIds"] == [634]  # one shared empty id for two full ids
assert s["Crossbow stall"]["loot"][0] == {"itemId": 877, "quantity": 3}
assert s["Candles"]["objectIds"] == [19127] and s["Candles"]["loot"][0]["itemId"] == 36
c = {r["name"]: r for r in doc["chests"]}
assert (c["Paladin"]["level"], c["Paladin"]["xp"]) == (72, 500.0) and len(c["Paladin"]["loot"]) == 4
print("PASS31.50 thieving data gate: 42 rows, errors=0")
