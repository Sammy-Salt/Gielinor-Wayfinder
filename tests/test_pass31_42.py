#!/usr/bin/env python3
"""PASS31.42 gate: cooking assembly, dairy, dough and remaining crafting recipes come from 2009Scape source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "site/data/recipes.json").read_text())["recipes"]
by_id = {r["id"]: r for r in rows}
assert len(by_id) == len(rows) == 904
assembly = [r for r in rows if r["id"].startswith("2009scape-cooking-assembly-")]
assert len(assembly) == 75, len(assembly)
extra = [r for r in rows if r["id"].startswith(("2009scape-crafting-studded-", "2009scape-crafting-weaving-", "2009scape-crafting-snelm-", "2009scape-crafting-tanning-", "2009scape-crafting-amulet-string-"))]
assert len(extra) == 29, len(extra)


def ins(r):
    return {i["itemId"]: i["quantity"] for i in r["inputs"]}


r = by_id["2009scape-cooking-assembly-curry_leaf"]; assert (r["level"], ins(r), r["output"]["itemId"]) == (60, {2001: 1, 5970: 3}, 2009)
r = by_id["2009scape-cooking-assembly-pineapple_pizza_1"]; assert (r["level"], r["xp"]) == (65, 52.0)
r = by_id["2009scape-cooking-assembly-potato_with_butter"]; assert (r["level"], r["xp"]) == (39, 40.5)
r = by_id["2009scape-cooking-assembly-cake_mix"]; assert ins(r) == {1944: 1, 1927: 1, 1933: 1, 1887: 1} and r["level"] == 40
r = by_id["2009scape-cooking-assembly-pizza_dough_bucket"]; assert (r["level"], ins(r), r["output"]["itemId"]) == (35, {1929: 1, 1933: 1}, 2283)
r = by_id["2009scape-cooking-assembly-dairy_cheese_from_1927"]; assert (r["level"], r["xp"]) == (48, 64.0)
r = by_id["2009scape-crafting-studded-body"]; assert (r["level"], r["xp"], ins(r)) == (41, 40.0, {1129: 1, 2370: 1})
r = by_id["2009scape-crafting-weaving-cloth"]; assert (r["level"], r["xp"], ins(r)) == (10, 12.0, {1759: 4})
r = by_id["2009scape-crafting-amulet-string-dragonstone_amulet"]; assert (r["level"], r["xp"], r["output"]["itemId"]) == (80, 0.0, 1702)
# stringing awards no experience in the server source
for k in ("holy", "unholy"):
    assert by_id[f"2009scape-crafting-silver-string-{k}"]["xp"] == 0.0
for r in assembly + extra:
    assert r["provenance"][0]["source"] == "2009Scape"
    for i in [r["output"]] + r["inputs"]:
        assert (ROOT / f"site/data/items/{i['itemId']}.json").exists(), (r["id"], i["itemId"])
print("PASS31.42 skill recipes gate: assembly=75 crafting-extra=29 errors=0")
