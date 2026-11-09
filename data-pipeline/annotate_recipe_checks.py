#!/usr/bin/env python3
"""Make recipe tool and unlock requirements machine-checkable (idempotent).

Run after data-pipeline/generate_skill_recipes.py:
  * every recipe tool name that maps to a catalog item gets its id in `toolItemIds`
    (all listed tools are required; no recipe in the 2009Scape data has interchangeable tools);
  * generic "Mould <id>" tool names are replaced with the catalog item name;
  * requirement "Barbarian Herblore training (Otto Godblessed)" gets the save attribute that
    BarbarianMixListener.kt checks (`/save:barbtraining:herblore` != 0), recorded as
    {"type": "unlock", "attribute": "barbtraining:herblore", "min": 1}.
Tool names with no item (the OSRS-only "Costume needle") stay unchecked and are reported.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPES = ROOT / "site/data/recipes.json"
TOOL_IDS = {
    "Hammer": 2347, "Knife": 946, "Needle": 1733, "Chisel": 1755, "Pestle and mortar": 233,
    "Glassblowing pipe": 1785, "Ring mould": 1592, "Necklace mould": 1597, "Bracelet mould": 11065, "Amulet mould": 1595,
    # silver-product moulds (SilverProduct.kt); the generator emits them as "Mould <id>" and this script renames them
    "Holy mould": 1599, "Unholy mould": 1594, "Sickle mould": 2976, "Conductor mould": 4200, "Bolt mould": 9434,
    "Tiara mould": 5523, "Rod clay mould": 7649, "Chain link mould": 13153,
    "Fishing rod": 307, "Oily fishing rod": 1585,
}
UNLOCKS = {"Barbarian Herblore training (Otto Godblessed)": {"attribute": "barbtraining:herblore", "min": 1}}


def item_name(item_id):
    return json.loads((ROOT / f"site/data/items/{item_id}.json").read_text())["name"]


def main():
    doc = json.loads(RECIPES.read_text())
    unmapped, changed = {}, 0
    for r in doc["recipes"]:
        before = json.dumps(r, sort_keys=True)
        tools, ids = [], []
        for t in r.get("tools", []):
            m = re.fullmatch(r"Mould (\d+)", t)
            if m:
                t = item_name(int(m.group(1)))
                TOOL_IDS.setdefault(t, int(m.group(1)))
            tools.append(t)
            if t in TOOL_IDS:
                ids.append(TOOL_IDS[t])
            else:
                unmapped[t] = unmapped.get(t, 0) + 1
        r["tools"] = tools
        if ids:
            r["toolItemIds"] = sorted(set(ids) | set(r.get("toolItemIds", [])))
        for q in r.get("requirements", []):
            if q.get("name") in UNLOCKS:
                q["type"] = "unlock"
                q.update(UNLOCKS[q["name"]])
        changed += before != json.dumps(r, sort_keys=True)
    RECIPES.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    print(f"annotated {changed} recipes; tool names with no item id: {unmapped or 'none'}")


if __name__ == "__main__":
    sys.exit(main())
