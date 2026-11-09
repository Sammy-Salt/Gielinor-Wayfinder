#!/usr/bin/env python3
"""PASS31.48 gate: tool/quest/unlock checks, and quest names come from the server's Quest.index table."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for script in ("tests/recipe_ready_check.mjs", "tests/save_import_check.mjs"):
    r = subprocess.run(["node", str(ROOT / script)], capture_output=True, text=True)
    assert r.returncode == 0, script + "\n" + r.stdout + r.stderr

table = {int(a): json.loads('"' + b + '"') for a, b in re.findall(r'^\s+(\d+): "((?:[^"\\]|\\.)*)"', (ROOT / "site/js/services/quest-ids.js").read_text(), re.M)}
assert len(table) == 70 and table[15] == "Cook's Assistant" and table[27] == "Rune Mysteries" and table[30] == "Vampire Slayer"

# the bundled save must agree with the table, and its completed quests must add up to its quest points
sync = json.loads((ROOT / "site/data/player-sync.json").read_text())
assert all(table[q["id"]] == q["name"] for q in sync["quests"]["items"]), "bundled quest names must match quest-ids.js"
points = {15: 1, 19: 4, 27: 1, 28: 1}  # Quest ctor point values in the server source
done = {q["id"] for q in sync["quests"]["items"] if q["completed"]}
assert done == set(points) and sum(points.values()) == sync["quests"]["questPoints"] == 7

# the old hand-written table must stay gone
svc = (ROOT / "site/js/services/save-import.js").read_text()
assert "quest-ids.js" in svc and "Sheep Shearer'" not in svc and "normalizeAttributes" in svc

recipes = json.loads((ROOT / "site/data/recipes.json").read_text())["recipes"]
assert all(q["type"] in ("quest", "unlock") for r in recipes for q in r["requirements"])
unlock = [q for r in recipes for q in r["requirements"] if q["type"] == "unlock"]
assert len(unlock) == 29 and all(q["attribute"] == "barbtraining:herblore" and q["min"] == 1 for q in unlock)
tooled = [r for r in recipes if r["tools"]]
assert sum(len(r.get("toolItemIds", [])) >= len(set(r["tools"])) for r in tooled) == 336 and len(tooled) == 340
for r in tooled:
    for t in r.get("toolItemIds", []):
        assert (ROOT / f"site/data/items/{t}.json").exists(), (r["id"], t)
print("PASS31.48 tool/quest/unlock gate: OK")
