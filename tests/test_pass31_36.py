#!/usr/bin/env python3
"""PASS31.36 shop gate: shops, item shop lists and map markers come from 2009Scape shops.json."""
import json
from pathlib import Path
R = Path(__file__).resolve().parents[1]; D = R / "site/data"; errors = []
def chk(c, m):
    if not c: errors.append(m)
doc = json.loads((D / "shops.json").read_text()); shops = doc["shops"]
chk(doc["source"] == "2009Scape", "shops source")
chk(len(shops) == 245, f"shop count {len(shops)}")
chk(sum(len(s["stock"]) for s in shops) == 2481, "stock line count")
items = {int(p.stem): json.loads(p.read_text()) for p in (D / "items").glob("[0-9]*.json")}
stocked = {e["itemId"] for s in shops for e in s["stock"]}
chk(stocked <= set(items), "stocked item missing from catalog")
with_shops = {i for i, r in items.items() if r["_acquisition"]["shops"]}
chk(with_shops == stocked, "item _acquisition.shops does not match shops.json")
chk(all(x["source"] == "2009Scape" for r in items.values() for x in r["_acquisition"]["shops"]), "non-2009Scape shop source")
t = (D / "map/shops.js").read_text(); marks = json.loads(t[t.index("=") + 1:].strip().rstrip(";"))
chk(len(marks) == 266, f"shop marker count {len(marks)}")
titles = {s["title"] for s in shops}
chk(all(m["name"] in titles for m in marks), "map shop marker not in 2009Scape shop list")
npcs = {int(p.stem) for p in (D / "npcs").glob("[0-9]*.json")} | {int(p.stem) for p in (D / "monsters").glob("[0-9]*.json")}
print(f"PASS31.36 shop gate: shops={len(shops)} stockLines=2481 itemsWithShops={len(with_shops)} markers={len(marks)} errors={len(errors)}")
if errors:
    [print("FAIL:", e) for e in errors]; raise SystemExit(1)
