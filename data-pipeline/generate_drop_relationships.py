#!/usr/bin/env python3
"""Generate canonical monster-drop relationships from pinned 2009Scape data.

The source payload is shipped with the PWA and pinned by SHA-256. The generator
expands NPC IDs, calculates exact weight-based probabilities, and emits lazy
per-monster/per-item gzip shards. ID 0 ("nothing") is a roll-table outcome,
not an item relationship, so it contributes to weighted-table totals but is
never emitted as a monster->item relationship.
"""
from __future__ import annotations
import gzip, hashlib, json, shutil
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SOURCE = SITE / "data/sources/2009scape/drop_tables.json"
OUT = SITE / "data/relationships"
CATEGORIES = ("default", "main", "charm", "tertiary")

def read_fraction(value: object) -> Fraction:
    return Fraction(str(value or "0"))

def fraction_obj(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}

def reciprocal_display(probability: Fraction) -> str:
    """Return every exact drop rate in player-facing 1/X form.

    The source probability remains exact as a numerator/denominator Fraction.
    Only the UI display is rounded, to at most two decimal places when the
    reciprocal is not an integer or finite short decimal.
    """
    if probability <= 0:
        return "Rate unavailable"
    rate = Fraction(1, 1) / probability
    if rate.denominator == 1:
        value = str(rate.numerator)
    else:
        decimal = (Decimal(rate.numerator) / Decimal(rate.denominator)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        value = format(decimal, "f").rstrip("0").rstrip(".")
    return f"1/{value}"

def write_gzip_json(path: Path, value: object) -> None:
    raw = (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    with path.open("wb") as raw_file:
        with gzip.GzipFile(fileobj=raw_file, mode="wb", mtime=0) as gz:
            gz.write(raw)

def main() -> None:
    source_bytes = SOURCE.read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    tables = json.loads(source_bytes)
    if not isinstance(tables, list):
        raise SystemExit("drop_tables.json must contain an array")

    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "monsters").mkdir(parents=True)
    (OUT / "items").mkdir(parents=True)

    pairs: dict[tuple[int, int], dict[str, dict]] = {}
    for table_index, table in enumerate(tables):
        npc_ids = [
            int(part.strip()) for part in str(table.get("ids", "")).split(",")
            if part.strip().isdigit()
        ]
        for category in CATEGORIES:
            entries = table.get(category) or []
            if not entries:
                continue
            total_weight = sum((read_fraction(e.get("weight")) for e in entries), Fraction())
            if category != "default" and total_weight <= 0:
                raise SystemExit(
                    f"non-positive {category} total at table {table_index}: {table.get('ids')}"
                )
            for npc_id in npc_ids:
                for entry in entries:
                    item_id = int(entry["id"])
                    if item_id == 0:
                        continue
                    key = (npc_id, item_id)
                    category_data = pairs.setdefault(key, {}).setdefault(
                        category,
                        {
                            "weight": Fraction(),
                            "totalWeight": total_weight,
                            "entries": [],
                            "tableIndex": table_index,
                        },
                    )
                    category_data["weight"] += read_fraction(entry.get("weight"))
                    category_data["entries"].append(entry)

    # Names are resolved from the canonical local entity index.
    entities_path = SITE / "data/knowledge/index.json"
    entities = json.loads(entities_path.read_text())
    entity_map = {
        (entity.get("type"), int(entity["id"])): entity
        for entity in entities.get("entities", [])
        if str(entity.get("id", "")).isdigit()
    }

    by_monster: dict[int, list[dict]] = defaultdict(list)
    by_item: dict[int, list[dict]] = defaultdict(list)

    for (monster_id, item_id), categories in sorted(pairs.items()):
        category_records = []
        probabilities = []
        quantities = []

        for category in CATEGORIES:
            if category not in categories:
                continue
            data = categories[category]
            probability = (
                Fraction(1, 1)
                if category == "default"
                else data["weight"] / data["totalWeight"]
            )
            probabilities.append(probability)

            quantity_values = {
                (entry.get("minAmount"), entry.get("maxAmount"))
                for entry in data["entries"]
            }
            quantity = None
            if len(quantity_values) == 1:
                minimum, maximum = next(iter(quantity_values))
                quantity = {"min": int(minimum), "max": int(maximum)}
                quantities.append(quantity)

            category_records.append(
                {
                    "type": category,
                    "weight": fraction_obj(data["weight"]),
                    "totalWeight": fraction_obj(data["totalWeight"]),
                    "probability": fraction_obj(probability),
                    "rateDisplay": reciprocal_display(probability),
                    "guaranteed": category == "default",
                    "tableIndex": data["tableIndex"],
                    "quantity": quantity,
                }
            )

        combined_probability = Fraction(1, 1)
        for probability in probabilities:
            combined_probability *= 1 - probability
        combined_probability = 1 - combined_probability

        unique_quantities = {json.dumps(q, sort_keys=True) for q in quantities}
        quantity = quantities[0] if len(unique_quantities) == 1 and quantities else None

        monster = entity_map.get(("monster", monster_id), {})
        item = entity_map.get(("item", item_id), {})
        record = {
            "relationshipType": "monster_drop",
            "monsterId": monster_id,
            "monsterName": monster.get("name") or f"Monster {monster_id}",
            "itemId": item_id,
            "itemName": item.get("name") or f"Item {item_id}",
            "quantity": quantity,
            "source": "2009Scape",
            "status": "authoritative",
            "dropTypes": [record["type"] for record in category_records],
            "categories": category_records,
            "rate": {
                "status": "authoritative",
                "source": "2009Scape",
                "display": reciprocal_display(combined_probability),
                "numerator": combined_probability.numerator,
                "denominator": combined_probability.denominator,
                "approximate": False,
                "sourcePolicy": "primary",
                "sourceHash": source_hash,
            },
        }
        by_monster[monster_id].append(record)
        by_item[item_id].append(record)

    for monster_id, records in by_monster.items():
        write_gzip_json(
            OUT / "monsters" / f"{monster_id}.json.gz",
            {"formatVersion": 3, "monsterId": monster_id, "relationships": records},
        )
    for item_id, records in by_item.items():
        write_gzip_json(
            OUT / "items" / f"{item_id}.json.gz",
            {"formatVersion": 3, "itemId": item_id, "relationships": records},
        )

    index = {
        "formatVersion": 3,
        "generatedFrom": "canonical 2009Scape drop_tables.json",
        "policy": (
            "2009Scape drop-table relationships and weighted probabilities are "
            "authoritative. OSRS Wiki is secondary evidence only when primary "
            "source data cannot calculate a value."
        ),
        "source": {
            "provider": "2009Scape",
            "path": "Server/data/configs/drop_tables.json",
            "url": "https://gitlab.com/2009scape/2009scape/-/blob/master/Server/data/configs/drop_tables.json",
            "revision": None,
            "contentSha256": source_hash,
            "retrieval": "canonical source payload pinned by SHA-256",
        },
        "relationshipCount": sum(map(len, by_monster.values())),
        "monsterCount": len(by_monster),
        "itemCount": len(by_item),
        "categoryCounts": {
            category: sum(1 for records in by_monster.values() for record in records if category in record["dropTypes"])
            for category in CATEGORIES
        },
        "monsterCounts": {str(k): len(v) for k, v in by_monster.items()},
        "itemCounts": {str(k): len(v) for k, v in by_item.items()},
        "monsters": {str(k): f"relationships/monsters/{k}.json.gz" for k in by_monster},
        "items": {str(k): f"relationships/items/{k}.json.gz" for k in by_item},
        "exactRateMonsters": [str(k) for k in sorted(by_monster)],
    }
    (OUT / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n"
    )

    print(
        f"DROP GENERATION: PASS | tables={len(tables)} "
        f"relationships={index['relationshipCount']} monsters={len(by_monster)} "
        f"items={len(by_item)} sourceSha256={source_hash}"
    )

if __name__ == "__main__":
    main()
