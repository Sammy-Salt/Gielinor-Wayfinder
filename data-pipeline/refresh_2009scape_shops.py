#!/usr/bin/env python3
"""PASS31.36: rebuild shops from 2009Scape shops.json (OSRS-only shops dropped).

  refresh_2009scape_shops.py --upstream <2009scape>/Server/data/configs

Outputs
  site/data/shops.json            canonical shop list with real stock (item id, amount, restock)
  items/*.json _acquisition.shops which shops stock the item
  map/shops.js                    one marker per shopkeeper spawn (position comes from npc_spawns)
shops.json stock tokens are {itemId,amount|inf,restock?} (Shop.kt parseStock); inf = -1, default restock 100.
shopType is a PWA classification, not a 2009Scape field: carried over by title from the previous catalog,
otherwise 'General store' for general stores and 'Other'.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import refresh_2009scape_core as C
import refresh_2009scape_spawns as SP

DATA = C.DATA
TOK = re.compile(r"\{([^}]*)\}")
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


def parse_stock(text: str) -> list[dict]:
    merged: dict[int, dict] = {}
    for tok in TOK.findall(text or ""):
        p = [x.strip() for x in tok.split(",")]
        amount = -1 if p[1] == "inf" else int(p[1])
        item = int(p[0])
        if item in merged:
            merged[item]["amount"] += amount
        else:
            merged[item] = {"itemId": item, "amount": amount, "restock": int(p[2]) if len(p) > 2 and p[2].lstrip("-").isdigit() else 100}
    return list(merged.values())


def old_shop_types() -> dict[str, str]:
    t = (DATA / "map/shops.js").read_text(encoding="utf-8")
    arr = json.loads(t[t.index("=") + 1:].strip().rstrip(";"))
    out = {}
    for s in arr:
        if s.get("shopType") and s["shopType"] != "Other":
            out.setdefault(norm(s["name"]).rstrip(" ").strip(), s["shopType"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--upstream", required=True, type=Path)
    up = ap.parse_args().upstream
    raw = C.read_json(up / "shops.json")
    types = old_shop_types()
    up_npcs = {int(x["id"]): x for x in C.read_json(up / "npc_configs.json")}
    spawns = SP.parse_npc_spawns(up / "npc_spawns.json")
    tables = C.read_json(DATA / "sources/2009scape/drop_tables.json")
    items, monsters, npcs = C.load_records("items"), C.load_records("monsters"), C.load_records("npcs")

    shops = []
    for s in raw:
        ids = [int(x) for x in str(s.get("npcs", "")).split(",") if x.strip().isdigit()]
        general = str(s.get("general_store")).lower() == "true"
        shops.append({
            "id": int(s["id"]), "title": s["title"], "npcs": ids, "currency": int(s["currency"]),
            "generalStore": general, "highAlch": int(s.get("high_alch") or 0) == 1,
            "shopType": types.get(norm(s["title"])) or ("General store" if general else "Other"),
            "stock": parse_stock(s.get("stock", "")),
        })
    shops.sort(key=lambda s: s["id"])
    (DATA / "shops.json").write_text(C.dumps_compact({"formatVersion": 1, "source": "2009Scape", "shops": shops}), encoding="utf-8")

    # shopkeepers that no catalog knows yet become NPC records
    added = []
    for sh in shops:
        for n in sh["npcs"]:
            if n not in npcs and n not in monsters and n in up_npcs:
                cfg = up_npcs[n]
                rec = {"id": n, "name": cfg["name"]}
                if cfg.get("examine"): rec["examine"] = cfg["examine"]
                rec.update(options=None, locations=spawns.get(n, []), aliases=[], shops=[])
                npcs[n] = rec; added.append(n)
                (DATA / "npcs" / f"{n}.json").write_text(C.dumps_compact(rec), encoding="utf-8")
    name_of = lambda n: (npcs.get(n) or monsters.get(n) or {}).get("name")
    for r in npcs.values():  # shops now come from shops.json
        if "shops" in r:
            del r["shops"]
            (DATA / "npcs" / f"{r['id']}.json").write_text(C.dumps_compact(r), encoding="utf-8")

    # items: which shops stock them
    by_item: dict[int, list] = {}
    for sh in shops:
        owner = ", ".join(filter(None, dict.fromkeys(name_of(n) for n in sh["npcs"])))
        for e in sh["stock"]:
            by_item.setdefault(e["itemId"], []).append({
                "shopId": sh["id"], "shopName": sh["title"], "owner": owner or None, "shopType": sh["shopType"],
                "stock": e["amount"], "restock": e["restock"], "currency": sh["currency"],
                "source": "2009Scape", "status": "authoritative"})
    for i, r in items.items():
        r["_acquisition"]["shops"] = by_item.get(i, [])
    C.write_records("items", items)
    missing_items = sorted(set(by_item) - set(items))

    # map markers at the shopkeepers
    marks, unplaced = [], []
    for sh in shops:
        seen = set(); n0 = len(marks)
        for n in sh["npcs"]:
            locs = (npcs.get(n) or monsters.get(n) or {}).get("locations") or spawns.get(n, [])
            for l in locs:
                k = (l["x"], l["y"], l["plane"])
                if k in seen: continue
                seen.add(k)
                marks.append({"id": sh["id"], "name": sh["title"], "type": "Shop", "x": l["x"], "y": l["y"], "plane": l["plane"],
                              "owner": name_of(n), "members": None, "shopType": sh["shopType"]})
        if len(marks) == n0: unplaced.append(sh["id"])
    (DATA / "map/shops.js").write_text("/* Generated from 2009Scape shops.json + npc_spawns.json. */\nwindow.OSRS_MAP_SHOPS=" + C.dumps_compact(marks) + ";\n", encoding="utf-8")

    npc_marks = [{"id": i, "name": r["name"], "type": "NPC", "x": l["x"], "y": l["y"], "plane": l["plane"]}
                 for i, r in npcs.items() for l in r["locations"]]
    (DATA / "map/npcs.js").write_text("/* Generated from 2009Scape npc_spawns.json. */\nwindow.OSRS_MAP_NPCS=" + C.dumps_compact(npc_marks) + ";\n", encoding="utf-8")

    d = C.rewrite_derived(items, monsters, npcs, tables)
    print(json.dumps({"shops": len(shops), "stockLines": sum(len(s["stock"]) for s in shops), "npcsAdded": added,
                      "itemsWithShops": len(by_item), "stockedItemsNotInCatalog": missing_items,
                      "markers": len(marks), "shopsWithoutMarker": unplaced, "derived": d,
                      "types": {t: sum(1 for s in shops if s["shopType"] == t) for t in sorted({s["shopType"] for s in shops})}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
