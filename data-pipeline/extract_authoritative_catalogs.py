#!/usr/bin/env python3
"""Extract 2009Scape catalogs and normalize compound item combat fields."""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path
from typing import Any, Iterable

PIPELINE_VERSION = "1.1.0"
BONUS_FIELDS = (
    "stabAttack", "slashAttack", "crushAttack", "magicAttack", "rangedAttack",
    "stabDefence", "slashDefence", "crushDefence", "magicDefence", "rangedDefence",
    "summoning", "strength", "prayer", "magicStrength", "rangedStrength",
)
COMBAT_STAT_FIELDS = ("combat_level", "lifepoints", "attack_level", "strength_level", "defence_level", "magic_level", "range_level")
BOOL_FIELDS = {"tradeable", "two_handed", "lendable", "destroy", "general_store", "safespot"}
INT_FIELDS = {"id", "archery_ticket_price", "attack_level", "attack_speed", "clue_level", "defence_level", "defence_animation", "death_animation", "ge_buy_limit", "lifepoints", "magic_level", "magic_animation", "melee_animation", "range_level", "range_animation", "respawn_delay", "shop_price", "slayer_exp", "strength_level"}
FLOAT_FIELDS = {"weight"}
SPAWN_RE = re.compile(r"\{([^{}]+)\}")

class PipelineError(RuntimeError): pass

def as_number(value: Any) -> int | float | None:
    if isinstance(value, bool): return int(value)
    if isinstance(value, (int, float)): return value
    if not isinstance(value, str) or not value.strip(): return None
    try:
        n = float(value.strip())
        return int(n) if n.is_integer() else n
    except ValueError: return None

def normalize_value(field: str, value: Any) -> Any:
    if value is None or not isinstance(value, str): return value
    text = value.strip()
    if field in BOOL_FIELDS and text.lower() in {"true", "false"}: return text.lower() == "true"
    if field in INT_FIELDS:
        n = as_number(text)
        if isinstance(n, int): return n
    if field in FLOAT_FIELDS:
        n = as_number(text)
        if isinstance(n, (int, float)): return float(n)
    return value

def parse_bonuses(value: Any) -> tuple[str, list[int]] | None:
    if not isinstance(value, str): return None
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != len(BONUS_FIELDS): return None
    try: values = [int(p) for p in parts]
    except ValueError: return None
    return value, values

def parse_requirements(value: Any) -> list[dict[str, int]] | None:
    if not isinstance(value, str): return None
    pairs = re.findall(r"-?\d+", value)
    if len(pairs) % 2 or not pairs: return None
    return [{"typeId": int(pairs[i]), "level": int(pairs[i + 1])} for i in range(0, len(pairs), 2)]

def normalize_item_record(record: dict[str, Any]) -> dict[str, Any]:
    out = {k: normalize_value(k, v) for k, v in record.items()}
    parsed = parse_bonuses(record.get("bonuses"))
    if parsed:
        raw, values = parsed
        out["bonusesRaw"] = raw
        out["bonusStats"] = dict(zip(BONUS_FIELDS, values))
    reqs = parse_requirements(record.get("requirements"))
    if reqs:
        out["requirementsRaw"] = record["requirements"]
        out["requirementsParsed"] = reqs
    return out

def load_json(path: Path) -> Any:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e: raise PipelineError(f"Missing required input: {path}") from e
    except json.JSONDecodeError as e: raise PipelineError(f"Invalid JSON in {path}: {e}") from e

def source_info(commit: str, path: str) -> dict[str, str]: return {"provider": "2009Scape", "commit": commit, "file": path}

def detect_commit(configs: Path, override: str | None) -> str:
    if override: return override
    for candidate in [configs, *configs.parents]:
        try:
            return subprocess.run(["git", "-C", str(candidate), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError): pass
    return "unknown"

def dedup(records: list[dict[str, Any]], label: str, policy: str, warnings: list[str]) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for i, record in enumerate(records):
        try: rid = int(record["id"])
        except (KeyError, TypeError, ValueError) as e: raise PipelineError(f"{label} record {i} has invalid id") from e
        grouped.setdefault(rid, []).append(record)
    result = []
    for rid in sorted(grouped):
        variants = grouped[rid]
        if len(variants) > 1:
            if policy == "error": raise PipelineError(f"Duplicate {label} id: {rid}")
            warnings.append(f"{label} id {rid}: {len(variants)} duplicates; kept {policy} record")
        result.append(variants[0] if policy == "first" else variants[-1])
    return result

def parse_locations(groups: Iterable[dict[str, Any]]) -> dict[int, list[dict[str, int]]]:
    locations: dict[int, list[dict[str, int]]] = {}
    for group in groups:
        npc_id = int(group["npc_id"]); parsed = []
        for match in SPAWN_RE.finditer(str(group.get("loc_data") or "")):
            values = [x.strip() for x in match.group(1).split(",")]
            if len(values) == 5:
                try:
                    x, y, plane, face, radius = map(int, values)
                    parsed.append({"x": x, "y": y, "plane": plane, "face": face, "walkRadius": radius})
                except ValueError: pass
        locations.setdefault(npc_id, []).extend(parsed)
    return locations

def has_combat_stats(record: dict[str, Any]) -> bool:
    return any((as_number(record.get(k)) or 0) > 0 for k in COMBAT_STAT_FIELDS)

def write_json(path: Path, value: Any, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=(indent or None), sort_keys=True) + "\n", encoding="utf-8")

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--configs", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    p.add_argument("--source-commit"); p.add_argument("--clean", action="store_true")
    p.add_argument("--duplicate-policy", choices=("error", "first", "last"), default="first"); p.add_argument("--indent", type=int, default=2)
    a = p.parse_args(); configs = a.configs.resolve(); output = a.output.resolve()
    if not configs.is_dir(): raise PipelineError(f"Config directory does not exist: {configs}")
    warnings: list[str] = []; commit = detect_commit(configs, a.source_commit)
    items = dedup(load_json(configs / "item_configs.json"), "item", a.duplicate_policy, warnings)
    npcs = dedup(load_json(configs / "npc_configs.json"), "NPC", a.duplicate_policy, warnings)
    groups = load_json(configs / "npc_spawns.json"); locations = parse_locations(groups)
    if a.clean:
        for directory in ("items", "npcs", "monsters"): shutil.rmtree(output / directory, ignore_errors=True)
    counts = {"items": 0, "npcs": 0, "monsters": 0}; output.mkdir(parents=True, exist_ok=True)
    for raw in items:
        record = normalize_item_record(dict(raw)); record["id"] = int(record["id"]); record["_source"] = source_info(commit, "Server/data/configs/item_configs.json")
        write_json(output / "items" / f"{record['id']}.json", record, a.indent); counts["items"] += 1
    for raw in npcs:
        record = {k: normalize_value(k, v) for k, v in dict(raw).items()}; record["id"] = int(record["id"]); record["locations"] = locations.get(record["id"], []); record["hasCombatStats"] = has_combat_stats(record); record["category"] = "monster" if record["hasCombatStats"] else "npc"; record["_source"] = source_info(commit, "Server/data/configs/npc_configs.json")
        directory = "monsters" if record["category"] == "monster" else "npcs"; write_json(output / directory / f"{record['id']}.json", record, a.indent); counts[directory] += 1
    metadata = {"pipeline": "extract_authoritative_catalogs", "pipelineVersion": PIPELINE_VERSION, "source": {"provider": "2009Scape", "commit": commit, "configs": str(configs)}, "itemNormalization": {"bonusFields": list(BONUS_FIELDS), "requirementsFormat": "numeric pairs retained as typeId/level"}, "counts": counts, "warnings": warnings}
    write_json(output / "_metadata.json", metadata, a.indent); print(json.dumps({"output": str(output), "sourceCommit": commit, "counts": counts, "warnings": len(warnings)}, indent=2)); return 0

if __name__ == "__main__":
    try: raise SystemExit(main())
    except PipelineError as e: print(f"error: {e}", file=sys.stderr); raise SystemExit(2)
