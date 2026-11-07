#!/usr/bin/env python3
"""Generate authoritative 2009Scape Fletching and staff-creation recipes."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

SOURCE_FILES = {
    "logs": "Server/src/main/content/global/skill/fletching/log/LogCraftInfo.kt",
    "arrows": "Server/src/main/content/global/skill/fletching/arrow/ArrowCraftInfo.kt",
    "bolts": "Server/src/main/content/global/skill/fletching/bolts/BoltCraftInfo.kt",
    "darts": "Server/src/main/content/global/skill/fletching/darts/DartCraftInfo.kt",
    "crossbows": "Server/src/main/content/global/skill/fletching/crossbow/UnfinishedCrossbowCraftInfo.kt",
    "stringing": "Server/src/main/content/global/skill/fletching/stringing/StringableCraftInfo.kt",
    "staffs": "Server/src/main/content/global/skill/crafting/BattlestaffListener.kt",
}

class GeneratorError(RuntimeError): pass

def records(path: Path, pattern: str):
    return [m.groups() for m in re.finditer(pattern, path.read_text(encoding="utf-8"), re.M | re.S)]

def provenance(root: Path, relative: str, commit: str, enum: str):
    return [{"source": "2009Scape", "file": relative, "commit": commit, "enum": enum}]

def recipe(rid, output_id, output_qty, inputs, skill, level, xp, tools, facilities, method, source_file, enum, commit, extra=None):
    value = {"id": rid, "output": {"itemId": output_id, "quantity": output_qty}, "inputs": [{"itemId": i, "quantity": q} for i, q in inputs], "skill": skill, "skills": [skill], "level": level, "xp": xp, "tools": tools, "facilities": facilities, "requirements": [], "method": method, "provenance": provenance(None, source_file, commit, enum)}
    if extra: value.update(extra)
    return value

def parse_logs(root, commit):
    rel = SOURCE_FILES["logs"]; path = root / rel
    pattern = r"^\s*([A-Z][A-Z0-9_]+)\(Items\.[A-Z0-9_]+_(\d+),\s*Items\.[A-Z0-9_]+_(\d+),\s*([0-9.]+),\s*(\d+)\),?"
    rows = []
    for enum, log, product, xp, level in records(path, pattern):
        product_qty = 15 if enum == "ARROW_SHAFT" else (4 if enum == "OGRE_ARROW_SHAFT" else 1)
        inputs = [(int(log), 1)]
        if enum == "OGRE_COMP_BOW": inputs.append((2859, 1))
        extra = {"outputNotes": "Variable quantity (2-6)"} if enum == "OGRE_ARROW_SHAFT" else None
        rows.append(recipe(f"2009scape-fletching-log-{enum.lower()}", int(product), product_qty, inputs, "Fletching", int(level), float(xp), ["Knife"], [], ["Cut logs with a knife"], rel, enum, commit, extra))
    return rows

def parse_arrows(root, commit):
    rel = SOURCE_FILES["arrows"]; path = root / rel
    pattern = r"^\s*([A-Z][A-Z0-9_]+)\(Items\.[A-Z0-9_]+_(\d+),\s*Items\.[A-Z0-9_]+_(\d+),\s*(\d+),\s*([0-9.]+)\),?"
    rows = [recipe(f"2009scape-fletching-arrow-{enum.lower()}", int(arrow), 1, [(53, 1), (int(tip), 1)], "Fletching", int(level), float(xp), ["Knife"], [], ["Attach an arrowhead to a headless arrow"], rel, enum, commit) for enum, tip, arrow, level, xp in records(path, pattern)]
    rows.append(recipe("2009scape-fletching-headless-arrow", 53, 1, [(52, 1), (314, 1)], "Fletching", 1, 1.0, ["Knife"], [], ["Attach a feather to an arrow shaft"], "Server/src/main/content/global/skill/fletching/arrow/HeadlessArrowCraftScript.kt", "HEADLESS_ARROW", commit))
    rows.append(recipe("2009scape-fletching-flighted-ogre-arrow", 2865, 1, [(2864, 1), (314, 4)], "Fletching", 5, 1.0, ["Knife"], [], ["Attach four feathers to an ogre arrow shaft"], "Server/src/main/content/global/skill/fletching/arrow/FlightedOgreArrowCraftScript.kt", "FLIGHTED_OGRE_ARROW", commit))
    return rows

def parse_bolts(root, commit):
    rel = SOURCE_FILES["bolts"]; path = root / rel
    pattern = r"^\s*([A-Z][A-Z0-9_]+)\(Items\.[A-Z0-9_]+_(\d+),\s*Items\.[A-Z0-9_]+_(\d+),\s*(\d+),\s*([0-9.]+)\)\s*,?"
    return [recipe(f"2009scape-fletching-bolt-{enum.lower()}", int(finished), 1, [(int(unfinished), 1), (314, 1)], "Fletching", int(level), float(xp), ["Knife"], [], ["Attach a feather to an unfinished bolt"], rel, enum, commit) for enum, unfinished, finished, level, xp in records(path, pattern)]

def parse_darts(root, commit):
    rel = SOURCE_FILES["darts"]; path = root / rel
    pattern = r"^\s*([A-Z][A-Z0-9_]+)\(Items\.[A-Z0-9_]+_(\d+),\s*Items\.[A-Z0-9_]+_(\d+),\s*(\d+),\s*([0-9.]+)\)\s*,?"
    return [recipe(f"2009scape-fletching-dart-{enum.lower()}", int(dart), 1, [(int(tip), 1), (314, 1)], "Fletching", int(level), float(xp), ["Knife"], [], ["Attach a feather to a dart tip"], rel, enum, commit) for enum, tip, dart, level, xp in records(path, pattern)]

def parse_crossbows(root, commit):
    rel = SOURCE_FILES["crossbows"]; path = root / rel
    pattern = r"^\s*([A-Z][A-Z0-9_]+)\(\s*Items\.[A-Z0-9_]+_(\d+),\s*Items\.[A-Z0-9_]+_(\d+),\s*Items\.[A-Z0-9_]+_(\d+),\s*(\d+),\s*([0-9.]+),"
    return [recipe(f"2009scape-fletching-crossbow-{enum.lower()}", int(product), 1, [(int(stock), 1), (int(limb), 1)], "Fletching", int(level), float(xp), ["Knife"], [], ["Attach crossbow limbs to a stock"], rel, enum, commit) for enum, stock, limb, product, level, xp in records(path, pattern)]

def parse_stringing(root, commit):
    rel = SOURCE_FILES["stringing"]; path = root / rel
    pattern = r"^\s*([A-Z][A-Z0-9_]+)\((?:false|true),\s*Items\.[A-Z0-9_]+_(\d+),\s*Items\.[A-Z0-9_]+_(\d+),\s*(\d+),\s*([0-9.]+),"
    rows = []
    for enum, unstrung, strung, level, xp in records(path, pattern):
        string_id = 9438 if enum.endswith("CBOW") else 1777
        rows.append(recipe(f"2009scape-fletching-string-{enum.lower()}", int(strung), 1, [(int(unstrung), 1), (string_id, 1)], "Fletching", int(level), float(xp), [], [], ["String an unstrung bow"], rel, enum, commit))
    return rows

def parse_staffs(root, commit):
    rel = SOURCE_FILES["staffs"]; path = root / rel
    pattern = r"^\s*([A-Z][A-Z0-9_]+)\(Items\.[A-Z0-9_]+_(\d+),\s*Items\.[A-Z0-9_]+_(\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)\s*[,;]"
    rows = []
    for enum, orb, product, quantity, level, xp in records(path, pattern):
        rows.append(recipe(f"2009scape-crafting-battlestaff-{enum.lower()}", int(product), int(quantity), [(1391, 1), (int(orb), 1)], "Crafting", int(level), float(xp), [], [], ["Combine an elemental orb with a battlestaff"], rel, enum, commit))
    return rows

def key(r):
    return (r.get("skill"), (r.get("output") or {}).get("itemId"), tuple(sorted((x.get("itemId"), x.get("quantity")) for x in r.get("inputs", []))))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", type=Path, required=True); p.add_argument("--recipes", type=Path, required=True); p.add_argument("--output", type=Path, required=True); p.add_argument("--source-commit", default="unknown")
    a = p.parse_args(); root = a.source_root.resolve()
    fletching_generated = parse_logs(root, a.source_commit) + parse_arrows(root, a.source_commit) + parse_bolts(root, a.source_commit) + parse_darts(root, a.source_commit) + parse_crossbows(root, a.source_commit) + parse_stringing(root, a.source_commit)
    staff_generated = parse_staffs(root, a.source_commit)
    generated = fletching_generated + staff_generated
    if not generated: raise GeneratorError("No Fletching or staff definitions were parsed")
    payload = json.loads(a.recipes.read_text(encoding="utf-8"))
    existing = payload.get("recipes") if isinstance(payload, dict) else None
    if not isinstance(existing, list): raise GeneratorError("recipes.json must contain a recipes array")
    generated_by_key = {key(r): r for r in generated}; replaced = sum(1 for r in existing if key(r) in generated_by_key)
    fletching_keys = {key(r) for r in fletching_generated}; staff_keys = {key(r) for r in staff_generated}
    fletching_replaced = sum(1 for r in existing if key(r) in fletching_keys)
    staff_replaced = sum(1 for r in existing if key(r) in staff_keys)
    merged = [generated_by_key.pop(key(r), r) for r in existing]; added = list(generated_by_key.values())
    payload["recipes"] = sorted(merged + added, key=lambda r: (str(r.get("skill", "")), int(r.get("level") or 0), str(r.get("id", ""))))
    payload.setdefault("generation", {})["fletching"] = {"provider": "2009Scape", "sourceFiles": [SOURCE_FILES[k] for k in ("logs", "arrows", "bolts", "darts", "crossbows", "stringing")], "commit": a.source_commit, "generated": len(fletching_generated), "added": len([r for r in added if key(r) in fletching_keys]), "replaced": fletching_replaced}
    payload["generation"]["staffCreation"] = {"provider": "2009Scape", "sourceFiles": [SOURCE_FILES["staffs"]], "commit": a.source_commit, "generated": len(staff_generated), "added": len([r for r in added if key(r) in staff_keys]), "replaced": staff_replaced}
    payload["snapshot"] = "PASS31.37-fletching-primary"
    sources = payload.setdefault("sources", [])
    sources[:] = [s for s in sources if not (s.get("source") == "2009Scape" and s.get("snapshot") == "PASS31.37")]
    sources.append({"source": "2009Scape", "role": "primary", "detail": "Fletching enum definitions and BattlestaffProduct", "snapshot": "PASS31.37"})
    counts = payload.setdefault("counts", {}); counts["from2009ScapeFletching"] = sum(1 for r in payload["recipes"] if r.get("skill") == "Fletching" and r.get("id", "").startswith("2009scape-fletching-")); counts["from2009ScapeStaffCreation"] = sum(1 for r in payload["recipes"] if r.get("id", "").startswith("2009scape-crafting-battlestaff-")); counts["total"] = len(payload["recipes"])
    a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"generatedFletching": len(fletching_generated), "generatedStaffCreation": len(staff_generated), "added": len(added), "replaced": replaced, "total": len(payload["recipes"]), "output": str(a.output)}, indent=2))

if __name__ == "__main__":
    try: main()
    except GeneratorError as e: raise SystemExit(f"error: {e}")
