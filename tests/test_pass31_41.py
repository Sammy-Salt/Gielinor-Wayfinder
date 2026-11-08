#!/usr/bin/env python3
"""PASS31.41 gate: non-recipe wiki rows dropped; item pages show Made by / Used in from recipes.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "site/data/recipes.json").read_text())
rows = data["recipes"]
assert len(rows) == 904 == data["counts"]["total"], len(rows)
assert all(r["inputs"] for r in rows if r["id"].startswith("wiki")), "wiki rows without inputs are not recipes"
assert data["counts"]["fromWikiSecondary"] == sum(r["id"].startswith("wiki") for r in rows)
svc = (ROOT / "site/js/services/recipe-service.js").read_text()
assert "recipes.json" in svc and "Made by" in svc and "Used in" in svc
page = (ROOT / "site/js/pages/item.js").read_text()
assert "recipe-service.js" in page and "recipesHTML(id)" in page
print("PASS31.41 recipe relationships gate: recipes=904 errors=0")
