#!/usr/bin/env python3
"""PASS31.37 authoritative Fletching and staff recipe gate."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
recipes = json.loads((ROOT / "site/data/recipes.json").read_text())
rows = recipes["recipes"]
fletching = [r for r in rows if r.get("id", "").startswith("2009scape-fletching-")]
staffs = [r for r in rows if r.get("id", "").startswith("2009scape-crafting-battlestaff-")]
assert len(fletching) == 75, f"expected 75 generated Fletching recipes, got {len(fletching)}"
assert len(staffs) == 4, f"expected 4 generated staff recipes, got {len(staffs)}"
for item_id in (50, 54, 56, 60, 58, 64, 62, 68, 66, 72, 841, 839, 849, 847, 853, 851, 857, 855, 861, 859):
    assert any(r["output"]["itemId"] == item_id for r in fletching), f"missing bow output {item_id}"
for item_id in (882, 884, 886, 888, 890, 892, 53, 2865):
    assert any(r["output"]["itemId"] == item_id for r in fletching), f"missing arrow output {item_id}"
for item_id in (1397, 1399, 1393, 1395):
    assert any(r["output"]["itemId"] == item_id for r in staffs), f"missing battlestaff output {item_id}"
shortbow = next(r for r in fletching if r["output"]["itemId"] == 50)
assert shortbow["inputs"] == [{"itemId": 1511, "quantity": 1}]
headless = next(r for r in fletching if r["output"]["itemId"] == 53)
assert {x["itemId"] for x in headless["inputs"]} == {52, 314}
flighted = next(r for r in fletching if r["output"]["itemId"] == 2865)
assert {x["itemId"]: x["quantity"] for x in flighted["inputs"]} == {2864: 1, 314: 4}
air = next(r for r in staffs if r["output"]["itemId"] == 1397)
assert {x["itemId"]: x["quantity"] for x in air["inputs"]} == {1391: 1, 573: 1}
for row in fletching + staffs:
    assert row["provenance"][0]["source"] == "2009Scape"
    assert row["level"] >= 1 and row["xp"] is not None
    assert (ROOT / f"site/data/items/{row['output']['itemId']}.json").exists()
print(f"PASS31.37 data gate: recipes={len(rows)} fletching={len(fletching)} battlestaves={len(staffs)} outputsChecked=30")
