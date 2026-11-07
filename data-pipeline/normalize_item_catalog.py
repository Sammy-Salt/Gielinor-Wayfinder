#!/usr/bin/env python3
"""Normalize compound 2009Scape item fields in an existing catalog."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

BONUS_FIELDS = ("stabAttack", "slashAttack", "crushAttack", "magicAttack", "rangedAttack", "stabDefence", "slashDefence", "crushDefence", "magicDefence", "rangedDefence", "summoning", "strength", "prayer", "magicStrength", "rangedStrength")

def parse_bonuses(value):
    if not isinstance(value, str): return None
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != len(BONUS_FIELDS): return None
    try: return [int(p) for p in parts]
    except ValueError: return None

def parse_requirements(value):
    if not isinstance(value, str): return None
    values = [int(x) for x in re.findall(r"-?\d+", value)]
    if not values or len(values) % 2: return None
    return [{"typeId": values[i], "level": values[i + 1]} for i in range(0, len(values), 2)]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--items", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args(); count = bonus_count = requirement_count = 0
    a.output.mkdir(parents=True, exist_ok=True)
    sources = [source for source in a.items.glob("*.json") if source.stem.isdigit()]
    for source in sorted(sources, key=lambda x: int(x.stem)):
        item = json.loads(source.read_text(encoding="utf-8"))
        values = parse_bonuses(item.get("bonuses"))
        if values:
            item["bonusesRaw"] = item["bonuses"]
            item["bonusStats"] = dict(zip(BONUS_FIELDS, values)); bonus_count += 1
        requirements = parse_requirements(item.get("requirements"))
        if requirements:
            item["requirementsRaw"] = item["requirements"]
            item["requirementsParsed"] = requirements; requirement_count += 1
        (a.output / source.name).write_text(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        count += 1
    print(json.dumps({"items": count, "bonusStats": bonus_count, "requirementsParsed": requirement_count, "output": str(a.output)}, indent=2))

if __name__ == "__main__": main()
