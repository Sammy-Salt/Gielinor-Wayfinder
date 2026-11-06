#!/usr/bin/env python3
"""Generate 2009Scape-primary smithing recipes from extracted server sources.

Expected inputs (paths relative to repo root or via env):
  SMITHING_BARS_JAVA   - path to Bars.java
  SMITHING_TYPE_JAVA   - path to SmithingType.java
  SMITHING_BARTYPE_JAVA - path to BarType.java
  SMITHING_SMELT_JAVA  - path to smelting/Bar.java
  ITEM_CONFIGS_JSON    - path to item_configs.json
  EXISTING_RECIPES_JSON - path to current site/data/recipes.json

Writes merged recipes JSON to stdout or --output path.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def parse_bar_types(text: str) -> dict:
    out = {}
    for m in re.finditer(r'(\w+)\((\d+),\s*([\d.]+),\s*"([^"]+)"\)', text):
        name, bar_id, xp, label = m.groups()
        out[name] = {"barId": int(bar_id), "xpPerBar": float(xp), "label": label}
    return out


def parse_smithing_types(text: str) -> dict:
    out = {}
    for m in re.finditer(
        r"TYPE_(\w+)\((\d+),\s*\d+,\s*\d+,\s*new int\[\]\s*\{[^}]+\},\s*(\d+)\)",
        text,
    ):
        name, bars_req, qty = m.groups()
        out[name] = {"barsRequired": int(bars_req), "productQty": int(qty)}
    return out


def parse_products(text: str) -> list:
    out = []
    for m in re.finditer(
        r"(\w+)\(BarType\.(\w+),\s*SmithingType\.TYPE_(\w+),\s*(\d+),\s*(\d+)\)",
        text,
    ):
        enum_name, bar_type, stype, product_id, level = m.groups()
        out.append(
            {
                "enum": enum_name,
                "barType": bar_type,
                "smithingType": stype,
                "productId": int(product_id),
                "level": int(level),
            }
        )
    return out


def parse_smelting(text: str) -> list:
    out = []
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"([A-Z]+)\((\d+),\s*([\d.]+),\s*(.+)\),?\s*$", line)
        if not m:
            continue
        name, level, xp, rest = m.groups()
        items = re.findall(r"new Item\((\d+)(?:,\s*(\d+))?\)", rest)
        if not items:
            continue
        prod_id = int(items[0][0])
        prod_qty = int(items[0][1] or 1)
        ores = [
            {"itemId": int(oid), "quantity": int(oqty or 1)} for oid, oqty in items[1:]
        ]
        out.append(
            {
                "name": name,
                "level": int(level),
                "xp": float(xp),
                "productId": prod_id,
                "productQty": prod_qty,
                "ores": ores,
            }
        )
    return out


def item_ref(names: dict, item_id: int, qty: int) -> dict:
    ref = {"itemId": int(item_id), "quantity": int(qty)}
    n = names.get(int(item_id))
    if n:
        ref["name"] = n
    return ref


def make_recipe(
    rid, output_id, output_qty, inputs, level, xp, tools, facilities, method_note, detail
):
    return {
        "id": rid,
        "output": {"itemId": int(output_id), "quantity": int(output_qty)},
        "inputs": inputs,
        "skill": "Smithing",
        "skills": ["Smithing"],
        "level": int(level),
        "xp": float(xp) if xp is not None else None,
        "tools": tools,
        "facilities": facilities,
        "requirements": [],
        "method": [method_note] if method_note else [],
        "provenance": [
            {
                "source": "2009Scape",
                "snapshot": "server-configs-and-Bars.java",
                "detail": detail,
            }
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars-java", required=True)
    ap.add_argument("--type-java", required=True)
    ap.add_argument("--bartype-java", required=True)
    ap.add_argument("--smelt-java", required=True)
    ap.add_argument("--item-configs", required=True)
    ap.add_argument("--existing-recipes", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    bars_java = Path(args.bars_java).read_text()
    type_java = Path(args.type_java).read_text()
    bartype_java = Path(args.bartype_java).read_text()
    smelt_java = Path(args.smelt_java).read_text()
    items = json.loads(Path(args.item_configs).read_text())
    names = {
        int(x["id"]): x.get("name", f"Item {x['id']}")
        for x in items
        if str(x.get("id", "")).isdigit()
    }
    existing = json.loads(Path(args.existing_recipes).read_text())

    bar_types = parse_bar_types(bartype_java)
    smith_types = parse_smithing_types(type_java)
    products = parse_products(bars_java)
    smelting = parse_smelting(smelt_java)

    recipes = []
    for s in smelting:
        recipes.append(
            make_recipe(
                rid=f"2009scape-smelt-{s['name'].lower()}",
                output_id=s["productId"],
                output_qty=s["productQty"],
                inputs=[item_ref(names, o["itemId"], o["quantity"]) for o in s["ores"]],
                level=s["level"],
                xp=s["xp"],
                tools=[],
                facilities=["Furnace"],
                method_note="Smelt ores at a furnace.",
                detail=f"smelting/Bar.java:{s['name']}",
            )
        )

    for p in products:
        st = smith_types[p["smithingType"]]
        bt = bar_types[p["barType"]]
        bars_req = st["barsRequired"]
        xp = bars_req * bt["xpPerBar"]
        recipes.append(
            make_recipe(
                rid=f"2009scape-smith-{p['enum'].lower()}",
                output_id=p["productId"],
                output_qty=st["productQty"],
                inputs=[item_ref(names, bt["barId"], bars_req)],
                level=p["level"],
                xp=xp,
                tools=["Hammer"],
                facilities=["Anvil"],
                method_note="Smith bars on an anvil with a hammer.",
                detail=f"Bars.java:{p['enum']}",
            )
        )

    covered = {r["output"]["itemId"] for r in recipes}
    kept_wiki = []
    for r in existing.get("recipes", []):
        skill = (r.get("skill") or "").lower()
        oid = (r.get("output") or {}).get("itemId")
        if skill == "smithing" and oid in covered:
            continue
        kept_wiki.append(r)

    merged = kept_wiki + recipes
    merged.sort(
        key=lambda r: ((r.get("skill") or ""), r.get("level") or 0, r.get("id") or "")
    )

    doc = {
        "schemaVersion": 1,
        "sourcePolicy": {"primary": "2009Scape", "secondary": "OSRS Wiki"},
        "sources": [
            {
                "source": "2009Scape",
                "role": "primary",
                "detail": "Server Bars.java, SmithingType.java, BarType.java, smelting/Bar.java, item_configs.json",
            },
            {
                "source": "OSRS Wiki",
                "role": "secondary",
                "snapshot": "PASS31.9",
                "detail": "Non-conflicting secondary recipes retained from prior snapshot",
            },
        ],
        "snapshot": "PASS31.33-smithing-primary",
        "counts": {
            "total": len(merged),
            "from2009ScapeSmithing": len(recipes),
            "fromWikiSecondary": len(kept_wiki),
        },
        "recipes": merged,
    }

    Path(args.output).write_text(json.dumps(doc, indent=2) + "\n")
    print(
        f"Wrote {args.output}: total={len(merged)} "
        f"2009Scape={len(recipes)} wiki={len(kept_wiki)}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
