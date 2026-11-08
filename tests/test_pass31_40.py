#!/usr/bin/env python3
"""PASS31.40 gate: Herblore, Crafting, Cooking and Runecrafting recipes are generated from 2009Scape server source."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "site/data/recipes.json").read_text())
rows = data["recipes"]
by = lambda p: [r for r in rows if r["id"].startswith(p)]
expected = {"2009scape-herblore-": 146, "2009scape-cooking-": 158, "2009scape-runecrafting-": 44}
for prefix, n in expected.items():
    assert len(by(prefix)) == n, f"{prefix}: expected {n}, got {len(by(prefix))}"
crafting = [r for r in by("2009scape-crafting-") if "battlestaff" not in r["id"]]
assert len(crafting) == 142, f"expected 142 generated Crafting rows, got {len(crafting)}"
assert data["counts"]["total"] == len(rows)
assert len({r["id"] for r in rows}) == len(rows), "duplicate recipe ids"
for r in by("2009scape-herblore-") + by("2009scape-cooking-") + by("2009scape-runecrafting-") + crafting:
    assert r["provenance"][0]["source"] == "2009Scape" and r["provenance"][0]["commit"]
    assert r["level"] >= 1 and r["xp"] is not None
    for i in [r["output"]] + r["inputs"]:
        assert (ROOT / f"site/data/items/{i['itemId']}.json").exists(), f"{r['id']}: missing item {i['itemId']}"


def one(rid):
    return next(r for r in rows if r["id"] == rid)


def ins(r):
    return {i["itemId"]: i["quantity"] for i in r["inputs"]}


# spot checks against the server tables
r = one("2009scape-crafting-gem-dragonstone"); assert (r["level"], r["xp"], r["output"]["itemId"], ins(r)) == (55, 137.5, 1615, {1631: 1})
r = one("2009scape-crafting-jewellery-ruby_amulet"); assert (r["level"], r["xp"], ins(r)) == (50, 85.0, {1603: 1, 2357: 1})
r = one("2009scape-crafting-dragonhide-black_d_hide_body"); assert (r["level"], ins(r)) == (84, {2509: 3, 1734: 1})
r = one("2009scape-crafting-glass-molten-glass"); assert ins(r) == {1781: 1, 1783: 1}
r = one("2009scape-cooking-lobster"); assert (r["level"], r["xp"], ins(r)) == (40, 120.0, {377: 1})
assert "2009scape-cooking-ugthanki" not in {x["id"] for x in rows}  # shadowed by CHICKEN in cookingMap
r = one("2009scape-runecrafting-blood"); assert (r["level"], r["xp"], r["output"]["itemId"]) == (77, 10.5, 565)
r = one("2009scape-runecrafting-combination-lava"); assert r["level"] == 23 and ins(r) == {7936: 1, 557: 1}
r = one("2009scape-herblore-potion-super_attack"); assert (r["level"], r["xp"], ins(r)) == (45, 100.0, {101: 1, 221: 1})
assert len(by("2009scape-crafting-battlestaff-")) == 4, "staff rows from PASS31.37 must survive"
print(f"PASS31.40 skill recipes gate: generated={sum(expected.values()) + len(crafting)} total={len(rows)} errors=0")
