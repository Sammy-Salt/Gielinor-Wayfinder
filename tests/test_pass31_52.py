#!/usr/bin/env python3
"""PASS31.52 gate: Hunter data (traps, butterflies, implings, falconry, tracking, pitfalls) comes from the 2009Scape source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site/data/hunter.json").read_text())
assert doc["formatVersion"] == 1 and doc["source"] == "2009Scape" and doc["sourceCommit"]
assert doc["counts"] == {"traps": 45, "butterflies": 4, "implings": 10, "falconry": 3, "tracking": 2, "pitfalls": 3, "total": 67}
groups = ("traps", "butterflies", "implings", "falconry", "tracking", "pitfalls")
rows = [r for g in groups for r in doc[g]]
ids = [r["id"] for r in rows]
assert len(ids) == len(set(ids)), "duplicate row ids"
GAPS = {10092}  # Ferret is used by the server but absent from the item catalog
for r in rows:
    assert r["skill"] == "Hunter" and r["level"] >= 1 and r["xp"] >= 0
    assert r["provenance"]["source"] == "2009Scape" and r["provenance"]["file"].startswith("Server/src/main/content/global/skill/hunter/")
    used = [x["itemId"] for x in r.get("rewards", []) + r.get("loot", [])] + ([r["itemId"]] if "itemId" in r else [])
    for i in used:
        assert i in GAPS or (ROOT / f"site/data/items/{i}.json").exists(), (r["id"], i)
t = {}
for r in doc["traps"]:
    t.setdefault(r["trap"], []).append(r)
assert {k: len(v) for k, v in t.items()} == {"BIRD_SNARE": 6, "BOX_TRAP": 24, "DEAD_FALL": 5, "NET_TRAP": 9, "IMP_BOX": 1}
chin = [r for r in t["BOX_TRAP"] if r["npcIds"] == [5079]][0]
assert (chin["level"], chin["xp"], chin["rewards"][0]["itemId"]) == (53, 198.0, 10033)
grenwall = [r for r in t["BOX_TRAP"] if r["npcIds"] == [7010, 7011]][0]
assert grenwall["xp"] == 0.0, "server grants 0 xp for grenwalls (documented in the source)"
assert [r["level"] for r in t["BIRD_SNARE"]] == [1, 5, 9, 11, 19, 39]
assert {r["name"]: r["nameSource"] for r in doc["traps"] if r["nameSource"] != "2009Scape NPC catalog"}["Barb-tailed kebbit"].startswith("OSRS Wiki")
types = {x["trap"]: x for x in doc["trapTypes"]}
assert types["NET_TRAP"]["level"] == 29 and types["NET_TRAP"]["layItemIds"] == [303, 954] and types["DEAD_FALL"]["level"] == 23
b = {r["name"]: r for r in doc["butterflies"]}
assert (b["Black Warlock"]["level"], b["Black Warlock"]["xp"], b["Black Warlock"]["bareHandLevel"], b["Black Warlock"]["agilityLevel"]) == (45, 54.0, 95, 90)
i = {r["name"]: r for r in doc["implings"]}
assert (i["Dragon Impling"]["level"], i["Dragon Impling"]["xp"], i["Dragon Impling"]["puroPuroXp"]) == (83, 300.0, 65.0)
assert i["Magpie Impling"]["respawnTicks"] == 500 and all(x["loot"] for x in doc["implings"])
assert len(doc["implingSpawners"]) == 6 and abs(sum(w["weight"] for w in doc["implingSpawners"][0]["weights"]) - 100) < 0.01
assert [(r["level"], r["xp"]) for r in doc["falconry"]] == [(43, 104.0), (57, 132.0), (69, 156.0)]
assert [(r["name"], r["level"], r["xp"]) for r in doc["pitfalls"]] == [("Spined larupia", 31, 180.0), ("Horned graahk", 41, 240.0), ("Sabre-toothed kyatt", 55, 300.0)]
print("PASS31.52 hunter data gate: 67 rows, errors=0")
