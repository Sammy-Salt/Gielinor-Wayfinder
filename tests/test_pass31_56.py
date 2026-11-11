#!/usr/bin/env python3
"""PASS31.56 gate: minigame data (Pest Control shop, Pyramid Plunder) comes from the 2009Scape server source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site/data/minigames.json").read_text())
assert doc["formatVersion"] == 1 and doc["source"] == "2009Scape" and doc["sourceCommit"]
assert doc["counts"] == {"minigames": 2, "rows": 29}
games = {g["name"]: g for g in doc["minigames"]}
assert set(games) == {"Pest Control", "Pyramid Plunder"}
pc = games["Pest Control"]
rw = {r["name"]: r for r in pc["rewards"]}
assert len(pc["rewards"]) == 21 and len({r["id"] for r in pc["rewards"]}) == 21
assert [r["kind"] for r in pc["rewards"]].count("xp") == 7 and rw["Ranged experience"]["skill"] == "Ranged"
assert rw["Void Knight Mace"]["points"] == 250 and rw["Void Knight Gloves"]["points"] == 150 and rw["Void Knight Mage Helm"]["points"] == 200 and rw["Void Knight Seal"]["points"] == 10
assert "requirements" not in rw["Void Knight Seal"]
req = {(x["skill"], x["level"]) for x in rw["Void Knight Top"]["requirements"]}
assert req == {("Hitpoints", 42), ("Attack", 42), ("Defence", 42), ("Strength", 42), ("Ranged", 42), ("Magic", 42), ("Prayer", 22)}
assert rw["Herb Pack"]["points"] == 30 and rw["Herb Pack"]["itemIds"] == [205, 207, 3049, 209, 211, 213, 199, 201]
assert rw["Mineral Pack"]["requirements"] == [{"skill": "Mining", "level": 25}]
assert [o["points"] for o in rw["Spinner Charm"]["options"]] == [2, 28, 56] and [o["quantity"] for o in rw["Spinner Charm"]["options"]] == [1, 14, 28]
assert pc["xpRule"]["N"] == {"Prayer": 18, "Magic": 32, "Ranged": 32, "Attack": 35, "Strength": 35, "Defence": 35, "Hitpoints": 35}
assert pc["xpRule"]["bonus"] == {"under10Points": 1.0, "from10Points": 1.01, "from100Points": 1.1}
pp = games["Pyramid Plunder"]
rooms = pp["rooms"]
assert [r["room"] for r in rooms] == list(range(1, 9)) and [r["requirements"][0]["level"] for r in rooms] == [21, 31, 41, 51, 61, 71, 81, 91]
assert [r["urnOpenXp"] for r in rooms] == [60.0, 90.0, 150.0, 215.0, 300.0, 450.0, 675.0, 825.0]
assert rooms[7]["chestXp"] == 544.5 and rooms[0]["lockpickDoorXp"] == 19.8
assert [r["sceptreOneIn"] for r in rooms] == [1500, 1350, 1250, 1150, 1000, 1000, 1000, 1000]
assert pp["artifacts"]["gold"] == [9028, 9034, 9040] and pp["sceptre"]["itemId"] == 9050
for g in doc["minigames"]:
    for i in [x for r in g.get("rewards", []) for x in r.get("itemIds", [])]:
        assert (ROOT / f"site/data/items/{i}.json").exists(), i
print("PASS31.56 minigame data gate: 2 minigames, 29 rows, errors=0")
