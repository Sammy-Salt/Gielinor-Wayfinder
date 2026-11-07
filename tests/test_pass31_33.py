#!/usr/bin/env python3
"""PASS31.33 Smithing and item-stat normalization gate."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
recipes = json.loads((SITE / "data/recipes.json").read_text())
rows = recipes["recipes"]
smithing = [r for r in rows if r.get("skill") == "Smithing" and any(p.get("source") == "2009Scape" for p in r.get("provenance", []))]
generated_smithing = [r for r in smithing if str(r.get("id", "")).startswith("2009scape-smithing-")]
assert len(generated_smithing) == 157, f"expected 157 generated Smithing recipes, got {len(generated_smithing)}"
outputs = {r["output"]["itemId"] for r in smithing}
for item_id in (1277, 1117, 1075, 1155, 1205, 1321):
    assert item_id in outputs, f"missing Smithing output item {item_id}"
for recipe in generated_smithing:
    assert recipe["inputs"] and recipe["inputs"][0]["itemId"] in {2349, 2351, 2353, 2359, 2361, 2363, 9467}
    assert recipe["level"] >= 1 and recipe["xp"] is not None
    assert (SITE / f"data/items/{recipe['output']['itemId']}.json").exists()
blurite = json.loads((SITE / "data/items/9139.json").read_text())
assert blurite["bonusStats"]["rangedStrength"] == 28
assert blurite["requirementsParsed"] == [{"typeId": 4, "level": 16}]
normalized = 0
for path in (SITE / "data/items").glob("[0-9]*.json"):
    item = json.loads(path.read_text())
    if "bonusStats" in item:
        assert set(item["bonusStats"]) == {"stabAttack", "slashAttack", "crushAttack", "magicAttack", "rangedAttack", "stabDefence", "slashDefence", "crushDefence", "magicDefence", "rangedDefence", "summoning", "strength", "prayer", "magicStrength", "rangedStrength"}
        normalized += 1
assert normalized == 2969, f"expected 2969 normalized bonus records, got {normalized}"
print(f"PASS31.33 data gate: recipes={len(rows)} generatedSmithing={len(generated_smithing)} authoritativeSmithing={len(smithing)} normalizedBonusItems={normalized} outputsChecked=6")
