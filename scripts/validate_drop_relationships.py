#!/usr/bin/env python3
"""Recalculate pinned 2009Scape drop odds and compare them to shipped shards.

Read-only. Does not call the generator and does not write under site/.
Fraction mismatches fail the process. Sentinel slots, rounded displays, and
the exclusive quantity maximum are reported as findings.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SOURCE = SITE / "data/sources/2009scape/drop_tables.json"
MANIFEST = SITE / "data/sources/2009scape/drop_tables.manifest.json"
REL = SITE / "data/relationships"
CATEGORIES = ("default", "main", "charm", "tertiary")
SENTINELS = {
    31: "rare drop table, not a tinderbox",
    1: "easy clue scroll, not toolkit",
    5733: "medium clue scroll, not rotten potato",
    12070: "hard clue scroll, not granite lobster pouch",
    799: "CEL minor table",
    14422: "uncommon seed table",
    14424: "herb table",
    14426: "gem table",
    14428: "rare seed table",
    14430: "allotment seed table",
}


def frac(value: object) -> Fraction:
    return Fraction(str(value or "0"))


def stored_fraction(obj: dict) -> Fraction:
    return Fraction(int(obj["numerator"]), int(obj["denominator"]))


def npc_ids(table: dict) -> list[int]:
    return [
        int(part.strip())
        for part in str(table.get("ids", "")).split(",")
        if part.strip().isdigit()
    ]


def expected_relationships(tables: list) -> tuple[dict, dict]:
    """Return {(npc, item): categories} plus audit counters.

    Category math matches DropTableParser plus WeightBasedTable:
    default is guaranteed, and the other three categories are separate
    weight/total rolls. Item 0 stays in the total and is not emitted.
    """
    pairs: dict[tuple[int, int], dict[str, dict]] = {}
    audit = {
        "zero_source_rows": [],
        "sentinel_source_rows": defaultdict(int),
        "npc_tables": defaultdict(list),
        "exclusive_quantity_rows": 0,
    }
    for table_index, table in enumerate(tables):
        ids = npc_ids(table)
        for npc_id in ids:
            audit["npc_tables"][npc_id].append(table_index)
        for category in CATEGORIES:
            entries = table.get(category) or []
            if not entries:
                continue
            total_weight = sum((frac(entry.get("weight")) for entry in entries), Fraction())
            if category != "default" and total_weight <= 0:
                raise SystemExit(
                    f"non-positive {category} total at table {table_index}: {table.get('ids')}"
                )
            for entry in entries:
                weight = frac(entry.get("weight"))
                item_id = int(entry["id"])
                minimum = int(entry["minAmount"])
                maximum = int(entry["maxAmount"])
                if minimum != maximum:
                    audit["exclusive_quantity_rows"] += 1
                if weight == 0:
                    audit["zero_source_rows"].append(
                        {"table": table_index, "category": category, "itemId": item_id, "npcs": ids}
                    )
                if item_id in SENTINELS:
                    audit["sentinel_source_rows"][(category, item_id)] += 1
                if item_id == 0:
                    continue
                for npc_id in ids:
                    slot = pairs.setdefault((npc_id, item_id), {}).setdefault(
                        category,
                        {
                            "weight": Fraction(),
                            "totalWeight": total_weight,
                            "tableIndex": table_index,
                            "quantities": set(),
                        },
                    )
                    slot["weight"] += weight
                    slot["quantities"].add((minimum, maximum))
    return pairs, audit


def combined(probabilities: list[Fraction]) -> Fraction:
    missing = Fraction(1, 1)
    for probability in probabilities:
        missing *= 1 - probability
    return 1 - missing


def load_shard(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.loads(handle.read())


def main() -> int:
    source_bytes = SOURCE.read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    manifest = json.loads(MANIFEST.read_text())
    tables = json.loads(source_bytes)
    index = json.loads((REL / "index.json").read_text())
    errors: list[str] = []

    def fail(message: str) -> None:
        errors.append(message)

    if hashlib.sha256(source_bytes).hexdigest() != manifest["contentSha256"]:
        fail("drop_tables.json does not match drop_tables.manifest.json")
    if index.get("source", {}).get("contentSha256") != source_hash:
        fail("relationship index source hash does not match drop_tables.json")
    if len(tables) != 444:
        fail(f"expected 444 pinned tables, found {len(tables)}")

    pairs, audit = expected_relationships(tables)
    multi = [npc for npc, indexes in audit["npc_tables"].items() if len(indexes) > 1]
    if multi:
        fail(f"{len(multi)} NPC ids appear on more than one source table: {multi[:8]}")

    seen: set[tuple[int, int]] = set()
    decimal_display_marked_exact = 0
    zero_relationships = 0
    sentinel_relationships = defaultdict(int)
    compared = 0

    for monster_id, records in _shards("monsters", "monsterId"):
        for record in records:
            key = (int(record["monsterId"]), int(record["itemId"]))
            if key in seen:
                fail(f"duplicate relationship {key}")
                continue
            seen.add(key)
            compared += 1
            if key not in pairs:
                fail(f"shipped relationship missing from source: {key}")
                continue
            _compare_record(record, pairs[key], source_hash, fail)
            if record["rate"]["numerator"] == 0:
                zero_relationships += 1
            if "." in record["rate"]["display"] and record["rate"].get("approximate") is False:
                decimal_display_marked_exact += 1
            for category in record["categories"]:
                if category["type"] != "default" and int(record["itemId"]) in SENTINELS:
                    sentinel_relationships[int(record["itemId"])] += 1
            if int(record["itemId"]) in SENTINELS and any(
                category["type"] == "default" for category in record["categories"]
            ):
                sentinel_relationships[int(record["itemId"])] += 1

    missing = sorted(set(pairs) - seen)
    if missing:
        fail(f"{len(missing)} source relationships missing from shards, first {missing[:8]}")
    if compared != index.get("relationshipCount"):
        fail(
            f"compared {compared} relationships, index says {index.get('relationshipCount')}"
        )

    category_counts = {
        category: sum(1 for categories in pairs.values() if category in categories)
        for category in CATEGORIES
    }
    if category_counts != index.get("categoryCounts"):
        fail(f"category counts {category_counts} != index {index.get('categoryCounts')}")

    item_keys: set[tuple[int, int]] = set()
    for _item_id, records in _shards("items", "itemId"):
        for record in records:
            item_keys.add((int(record["monsterId"]), int(record["itemId"])))
    if item_keys != seen:
        fail(
            f"item shards and monster shards disagree "
            f"(only monsters {len(seen - item_keys)}, only items {len(item_keys - seen)})"
        )

    print(
        "DROP VALIDATION: "
        + ("FAIL" if errors else "PASS")
        + f" | tables={len(tables)} relationships={compared} "
        + f"sourceSha256={source_hash}"
    )
    print(
        "categories "
        + " ".join(f"{name}={category_counts[name]}" for name in CATEGORIES)
    )
    print(
        "FIDELITY findings (not rewritten): "
        f"sentinelSourceRows={sum(audit['sentinel_source_rows'].values())} "
        f"sentinelRelationships={sum(sentinel_relationships.values())} "
        f"zeroWeightSourceRows={len(audit['zero_source_rows'])} "
        f"zeroWeightRelationships={zero_relationships} "
        f"roundedDisplayMarkedExact={decimal_display_marked_exact} "
        f"exclusiveMaxQuantityRows={audit['exclusive_quantity_rows']} "
        f"multiTableNpcs={len(multi)}"
    )
    for (category, item_id), count in sorted(audit["sentinel_source_rows"].items()):
        print(f"  sentinel source {category} id {item_id}: {count} ({SENTINELS[item_id]})")
    for message in errors[:30]:
        print("FAIL:", message)
    if len(errors) > 30:
        print(f"FAIL: {len(errors) - 30} more")
    return 1 if errors else 0


def _shards(kind: str, id_field: str):
    folder = REL / kind
    for path in sorted(folder.glob("*.json.gz")):
        payload = load_shard(path)
        if payload.get(id_field) != int(path.name.split(".", 1)[0]):
            raise SystemExit(f"{path} {id_field} does not match filename")
        yield payload[id_field], payload["relationships"]


def _compare_record(record: dict, categories: dict, source_hash: str, fail) -> None:
    key = (record["monsterId"], record["itemId"])
    shipped = {category["type"]: category for category in record["categories"]}
    if set(shipped) != set(categories):
        fail(f"{key} categories {sorted(shipped)} != {sorted(categories)}")
        return
    probabilities = []
    for name, expected in categories.items():
        got = shipped[name]
        probability = Fraction(1, 1) if name == "default" else expected["weight"] / expected["totalWeight"]
        probabilities.append(probability)
        if stored_fraction(got["probability"]) != probability:
            fail(f"{key} {name} probability {got['probability']} != {probability}")
        if stored_fraction(got["weight"]) != expected["weight"]:
            fail(f"{key} {name} weight mismatch")
        if stored_fraction(got["totalWeight"]) != expected["totalWeight"]:
            fail(f"{key} {name} totalWeight mismatch")
        if bool(got["guaranteed"]) != (name == "default"):
            fail(f"{key} {name} guaranteed flag mismatch")
    expect_combined = combined(probabilities)
    if Fraction(int(record["rate"]["numerator"]), int(record["rate"]["denominator"])) != expect_combined:
        fail(f"{key} combined rate != {expect_combined}")
    if record["rate"].get("sourceHash") != source_hash:
        fail(f"{key} sourceHash mismatch")
    if record.get("source") != "2009Scape" or record["rate"].get("sourcePolicy") != "primary":
        fail(f"{key} source policy mismatch")


if __name__ == "__main__":
    sys.exit(main())
