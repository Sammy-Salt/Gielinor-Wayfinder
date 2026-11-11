#!/usr/bin/env python3
"""PASS31.55 gate: Treasure Trail data (reward tables, levels, coordinate/map/emote clues) comes from the 2009Scape source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site/data/clues.json").read_text())
assert doc["formatVersion"] == 1 and doc["source"] == "2009Scape" and doc["sourceCommit"]
assert doc["counts"] == {"coordinate": 57, "map": 25, "emote": 49, "rewardItems": 362, "total": 131}
rows = doc["coordinate"] + doc["map"] + doc["emote"]
ids = [r["id"] for r in rows]
assert len(ids) == len(set(ids)), "duplicate row ids"
clue_ids = [r["clueItemId"] for r in rows]
assert len(clue_ids) == len(set(clue_ids)), "duplicate clue scroll item ids"
for r in rows:
    assert r["level"] in ("easy", "medium", "hard")
    assert r["provenance"]["source"] == "2009Scape" and r["provenance"]["file"].startswith("Server/src/main/content/global/activity/ttrail/")
    assert (ROOT / f"site/data/items/{r['clueItemId']}.json").exists()
tiers = doc["rewards"]
assert {k: (v["totalWeight"], len(v["items"])) for k, v in tiers.items()} == {"easy": (625.0, 125), "medium": (520.0, 104), "hard": (575.0, 115), "rare": (320.0, 18)}
for k, v in tiers.items():
    assert abs(sum(i["chancePercent"] for i in v["items"]) - 100) < 0.2, k
    for i in v["items"]:
        assert i["min"] >= 1 and i["max"] >= i["min"] and (ROOT / f"site/data/items/{i['itemId']}.json").exists(), (k, i)
assert tiers["rare"]["items"][0] == {"itemId": 10362, "min": 1, "max": 1, "weight": 50.0, "chancePercent": 15.625}
lv = doc["levels"]
assert (lv["easy"]["casketItemId"], lv["easy"]["maxSteps"], lv["medium"]["maxSteps"], lv["hard"]["maxSteps"]) == (2714, 5, 6, 8)
assert "random(100) == 50" in lv["rewardRolls"]["rareTable"]
import collections
by = collections.Counter((r["kind"], r["level"]) for r in rows)
assert by == {("coordinate", "medium"): 31, ("coordinate", "hard"): 26, ("map", "easy"): 7, ("map", "medium"): 10, ("map", "hard"): 8,
              ("emote", "easy"): 26, ("emote", "medium"): 16, ("emote", "hard"): 7}
dups = [r for r in doc["coordinate"] if r["provenance"]["key"] == "bandit-camp-coord"]
assert len(dups) == 2 and dups[0]["name"] != dups[1]["name"], "the two bandit-camp clues must stay distinct"
e = {r["id"].split("emote-")[1]: r for r in doc["emote"]}
assert e["al-kharid-headbang"]["emote"] == "Headbang" and e["al-kharid-headbang"]["equipment"] == [[1833], [1059], [1061]]
assert len(e["games-room-cheer"]["emptySlots"]) == 11 and e["games-room-cheer"]["equipment"] == []
assert sum(1 for r in doc["emote"] if r["commenceEmote"]) == 15
assert any(len(g) > 3 for r in doc["emote"] for g in r["equipment"]), "item-alternative groups (capes, duelling rings) must survive"
m = {r["id"].split("map-")[1]: r for r in doc["map"]}
assert m["mcgruber-crate"]["searchObjectId"] == 357 and m["mcgruber-crate"]["location"] == {"x": 2658, "y": 3488, "plane": 0}
assert "searchObjectId" not in m["wizard-tower-dig"]
print("PASS31.55 clue data gate: 131 clues + 362 reward rows, errors=0")
