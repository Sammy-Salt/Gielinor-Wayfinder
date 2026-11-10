#!/usr/bin/env python3
"""PASS31.53 gate: Farming data (crops, patch types, patches, yield rules) comes from the 2009Scape server source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site/data/farming.json").read_text())
assert doc["formatVersion"] == 1 and doc["source"] == "2009Scape" and doc["sourceCommit"]
assert doc["counts"] == {"crops": 61, "patchTypes": 13, "patches": 45, "total": 119}
rows = doc["crops"] + doc["patches"]
ids = [r["id"] for r in rows]
assert len(ids) == len(set(ids)), "duplicate row ids"
for r in rows + doc["patchTypes"]:
    assert r["provenance"]["source"] == "2009Scape" and r["provenance"]["file"].startswith("Server/src/main/content/global/skill/farming/")
crop_ids = {r["id"] for r in doc["crops"]}
for r in doc["crops"]:
    assert r["skill"] == "Farming" and r["level"] >= 1
    for i in [r["seedItemId"], r["harvestItemId"], *[p["itemId"] for p in r["protectionPayment"]]]:
        assert i is None or (ROOT / f"site/data/items/{i}.json").exists(), (r["id"], i)
    assert r["protectionFlower"] is None or r["protectionFlower"] in crop_ids
c = {r["id"].split("farming-")[1]: r for r in doc["crops"]}
assert (c["torstol-seed"]["level"], c["torstol-seed"]["plantingXp"], c["torstol-seed"]["harvestXp"], c["torstol-seed"]["growthMinutes"]) == (85, 199.5, 224.5, 80)
assert (c["potato-seed"]["patchType"], c["potato-seed"]["growthMinutes"], c["potato-seed"]["protectionPayment"], c["potato-seed"]["protectionFlower"]) == ("ALLOTMENT", 40, [{"itemId": 6032, "quantity": 2}], "2009scape-farming-marigold-seed")
assert (c["magic-sapling"]["level"], c["magic-sapling"]["checkHealthXp"], c["magic-sapling"]["growthMinutes"]) == (75, 13768.3, 480)
assert len(c["spirit-sapling"]["protectionPayment"]) == 3 and c["spirit-sapling"]["harvestItemId"] is None
assert c["scarecrow"]["kind"] == "scarecrow" and c["scarecrow"]["growthMinutes"] is None
assert sum(1 for r in doc["crops"] if r["kind"] == "crop") == 60
pt = {r["patchType"]: r["stageMinutes"] for r in doc["patchTypes"]}
assert pt["HERB_PATCH"] == 20 and pt["FRUIT_TREE_PATCH"] == 160 and pt["SPIRIT_TREE_PATCH"] == 295 and pt["FLOWER_PATCH"] == 5
assert {p["patchType"] for p in doc["patches"]} <= set(pt)
assert sum(1 for p in doc["patches"] if p["patchType"] == "ALLOTMENT") == 9 and sum(1 for p in doc["patches"] if p["patchType"] == "HERB_PATCH") == 5
rules = doc["rules"]
assert rules["baseCropLives"] == 3 and rules["compostBonus"] == {"NONE": 0, "COMPOST": 1, "SUPERCOMPOST": 2}
assert rules["lifeLossChance"]["allotment"] == 8 and rules["baseHarvestAmount"]["mushroom"] == 6
print("PASS31.53 farming data gate: 119 rows, errors=0")
