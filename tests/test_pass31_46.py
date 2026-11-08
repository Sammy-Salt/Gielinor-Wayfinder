#!/usr/bin/env python3
"""PASS31.46 gate: remaining Crafting, Cooking and Runecrafting recipes come from 2009Scape source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "site/data/recipes.json").read_text())["recipes"]
by_id = {r["id"]: r for r in rows}
assert len(by_id) == len(rows) == 904
for prefix, n in {"2009scape-runecrafting-tiara-": 12, "2009scape-runecrafting-staff-": 12, "2009scape-cooking-brew-": 11, "2009scape-cooking-skewer-": 4, "2009scape-crafting-spiky-vambraces-": 5}.items():
    assert sum(r["id"].startswith(prefix) for r in rows) == n, prefix


def ins(r):
    return {i["itemId"]: i["quantity"] for i in r["inputs"]}


r = by_id["2009scape-crafting-spiky-vambraces-10077"]; assert (r["level"], r["xp"], ins(r)) == (32, 6.0, {1063: 1, 10113: 1})
r = by_id["2009scape-crafting-sapphire-lantern"]; assert (r["level"], ins(r), r["output"]["itemId"]) == (20, {4544: 1, 1607: 1}, 4700)
r = by_id["2009scape-crafting-limestone-brick"]; assert (r["level"], r["xp"], ins(r), r["output"]["itemId"]) == (12, 6.0, {3211: 1}, 3420)
r = by_id["2009scape-cooking-skewer-7230"]; assert (r["level"], ins(r)) == (30, {2876: 1, 7225: 1})
assert by_id["2009scape-cooking-wine"]["xp"] == 200.0 and by_id["2009scape-cooking-wine"]["level"] == 35
r = by_id["2009scape-cooking-watermelon-slices"]; assert r["output"]["quantity"] == 3
r = by_id["2009scape-cooking-brew-dwarven_stout"]; assert (r["level"], r["xp"], ins(r)) == (19, 215.0, {5994: 4})
assert ins(by_id["2009scape-cooking-brew-axemans_folly"]) == {6043: 1}
r = by_id["2009scape-runecrafting-tiara-air"]; assert (r["xp"], ins(r), r["output"]["itemId"]) == (25.0, {1438: 1, 5525: 1}, 5527)
r = by_id["2009scape-runecrafting-staff-blood"]; assert (r["xp"], ins(r), r["output"]["itemId"]) == (0.0, {1450: 1, 13629: 1}, 13641)
assert "2009scape-runecrafting-tiara-omni" not in by_id, "OMNI is not an altar; the enchanting listener cannot make it"
for r in rows:
    if r["id"].startswith("2009scape-") and any(k in r["id"] for k in ("spiky", "lantern", "limestone", "skewer", "kebab", "wine", "brew-", "tiara", "staff-", "watermelon", "chocolate-dust")):
        assert r["provenance"][0]["source"] == "2009Scape"
        for i in [r["output"]] + r["inputs"]:
            assert (ROOT / f"site/data/items/{i['itemId']}.json").exists(), (r["id"], i["itemId"])
print("PASS31.46 remaining recipes gate: total=904 errors=0")
