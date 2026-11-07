#!/usr/bin/env python3
"""Parse 2009Scape smithing enums and merge authoritative recipes."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

BAR_RE = re.compile(r"^\s*([A-Z][A-Z0-9_]+)\(BarType\.([A-Z]+),\s*SmithingType\.([A-Z0-9_]+),\s*(\d+),\s*(\d+)\)\s*[,;]", re.M)
TYPE_RE = re.compile(r"^\s*(TYPE_[A-Z0-9_]+)\((\d+),[^,]*,[^,]*,\s*new int\[\]\s*\{[^}]*\},\s*(\d+)\)\s*[,;]", re.M)
BAR_TYPE_RE = re.compile(r"^\s*([A-Z]+)\((\d+),\s*([0-9.]+),\s*\"([^\"]+)\"\)\s*[,;]", re.M)

class GeneratorError(RuntimeError): pass

def parse(path: Path):
    text = path.read_text(encoding="utf-8")
    types = {m.group(1): {"bars": int(m.group(2)), "quantity": int(m.group(3))} for m in TYPE_RE.finditer(text)}
    bars = {m.group(1): {"barType": m.group(2), "smithingType": m.group(3), "product": int(m.group(4)), "level": int(m.group(5))} for m in BAR_RE.finditer(text)}
    return types, bars

def parse_bar_types(path: Path):
    result = {}
    for m in BAR_TYPE_RE.finditer(path.read_text(encoding="utf-8")):
        result[m.group(1)] = {"barId": int(m.group(2)), "xpPerBar": float(m.group(3)), "name": m.group(4)}
    return result

def recipe_id(bar_type, entry): return f"2009scape-smithing-{bar_type.lower()}-{entry['smithingType'][5:].lower()}-{entry['product']}"

def build(bars, types, bar_types, commit):
    result = []
    for name, entry in bars.items():
        smithing_type = entry["smithingType"]
        if smithing_type not in types: raise GeneratorError(f"Missing SmithingType definition: {smithing_type}")
        bt = bar_types.get(entry["barType"])
        if not bt: raise GeneratorError(f"Missing BarType definition: {entry['barType']}")
        st = types[smithing_type]
        xp = bt["xpPerBar"] * st["bars"]
        if xp.is_integer(): xp = int(xp)
        result.append({
            "id": recipe_id(entry["barType"], entry),
            "output": {"itemId": entry["product"], "quantity": st["quantity"]},
            "inputs": [{"itemId": bt["barId"], "quantity": st["bars"]}],
            "skill": "Smithing", "skills": ["Smithing"], "level": entry["level"], "xp": xp,
            "tools": ["Hammer"], "facilities": ["Anvil"], "requirements": [],
            "method": [f"Smith {bt['name'].replace(' Smithing','').lower()} at an anvil"],
            "provenance": [{"source": "2009Scape", "file": "Server/src/main/content/global/skill/smithing/Bars.java", "commit": commit, "barType": entry["barType"], "smithingType": smithing_type, "enum": name}],
        })
    return sorted(result, key=lambda r: (r["level"], r["output"]["itemId"], r["id"]))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", type=Path, required=True, help="Extracted 2009Scape repository root")
    p.add_argument("--recipes", type=Path, required=True, help="Existing recipes.json")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--source-commit", default="unknown")
    a = p.parse_args()
    skill = a.source_root / "Server/src/main/content/global/skill/smithing"
    types, bars = parse(skill / "Bars.java")
    types2, _ = parse(skill / "SmithingType.java")
    # parse() accepts the shared SmithingType format; its bar entries are irrelevant here.
    type_defs = types2 or types
    if not type_defs: raise GeneratorError("No SmithingType definitions found")
    bar_types = parse_bar_types(skill / "BarType.java")
    generated = build(bars, type_defs, bar_types, a.source_commit)
    payload = json.loads(a.recipes.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("recipes"), list): raise GeneratorError("recipes.json must contain a recipes array")
    existing = payload["recipes"]
    key = lambda r: (r.get("skill"), (r.get("output") or {}).get("itemId"), tuple(sorted((x.get("itemId"), x.get("quantity")) for x in r.get("inputs", []))))
    generated_by_key = {key(r): r for r in generated}
    replaced = sum(1 for r in existing if key(r) in generated_by_key)
    merged = [generated_by_key.pop(key(r), r) for r in existing]
    added = list(generated_by_key.values())
    payload["recipes"] = sorted(merged + added, key=lambda r: (str(r.get("skill", "")), int(r.get("level") or 0), str(r.get("id", ""))))
    payload["generation"] = {"smithing": {"provider": "2009Scape", "sourceFiles": ["Server/src/main/content/global/skill/smithing/Bars.java", "Server/src/main/content/global/skill/smithing/SmithingType.java", "Server/src/main/content/global/skill/smithing/BarType.java"], "commit": a.source_commit, "generated": len(generated), "added": len(added), "replaced": replaced}}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"generated": len(generated), "added": len(added), "total": len(payload["recipes"]), "output": str(a.output)}, indent=2))

if __name__ == "__main__": main()
