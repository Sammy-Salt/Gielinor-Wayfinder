#!/usr/bin/env python3
"""Crafting recipe/item-catalog wiring regression gate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
errors = []

def check(condition, message):
    if not condition:
        errors.append(message)

recipes_payload = json.loads((SITE / "data/recipes.json").read_text())
recipes = recipes_payload.get("recipes", [])
item_index = json.loads((SITE / "data/items/index.json").read_text())
item_ids = {int(row["id"]) for row in item_index}
referenced_ids = set()

for recipe in recipes:
    output = recipe.get("output") or {}
    check("itemId" in output, f"recipe missing output item: {recipe.get('id')}")
    if "itemId" in output:
        referenced_ids.add(int(output["itemId"]))
    for item in recipe.get("inputs", []):
        check("itemId" in item, f"recipe input missing item: {recipe.get('id')}")
        if "itemId" in item:
            referenced_ids.add(int(item["itemId"]))

missing_index = sorted(referenced_ids - item_ids)
check(not missing_index, f"recipe references missing catalog IDs: {missing_index[:10]}")
missing_details = sorted(
    item_id for item_id in referenced_ids
    if not (SITE / "data/items" / f"{item_id}.json").is_file()
)
check(not missing_details, f"recipe references missing detail files: {missing_details[:10]}")

crafting_js = (SITE / "js/pages/crafting.js").read_text()
check('OSRS.Catalog.list("items")' in crafting_js, "crafting page does not load the shared item catalog")
check('OSRS.Catalog.get("items", id)' in crafting_js, "crafting page lacks item detail fallback")
check("normalizeRecipe" in crafting_js, "crafting page lacks recipe normalization")
check("unresolvedItemIds" in crafting_js, "crafting page does not expose unresolved catalog references")

syntax = subprocess.run(
    ["node", "--check", str(SITE / "js/pages/crafting.js")],
    capture_output=True,
    text=True,
)
check(syntax.returncode == 0, f"crafting.js syntax error: {syntax.stderr.strip()}")

print(
    f"PASS31.32 crafting catalog gate: recipes={len(recipes)} "
    f"referencedItems={len(referenced_ids)} catalogItems={len(item_ids)} "
    f"missingIndex={len(missing_index)} missingDetails={len(missing_details)} "
    f"errors={len(errors)}"
)
if errors:
    for error in errors[:50]:
        print("FAIL:", error)
    raise SystemExit(1)
