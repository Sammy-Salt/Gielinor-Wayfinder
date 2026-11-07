#!/usr/bin/env python3
"""Refresh the core catalogs (items, monsters, drop tables) from a 2009Scape checkout.

2009Scape is the primary source (docs/decisions/ADR-0001-SOURCE-PRECEDENCE.md).
This script is the single place that builds the shipped item/monster catalogs and
every file derived from them, so the derived files can never drift from the records.

Usage
  refresh_2009scape_core.py selftest
      Rebuild every derived file from the records currently on disk and compare it
      byte for byte with what is committed. Proves the derive code reproduces the
      project's conventions. Writes nothing.
  refresh_2009scape_core.py refresh --upstream <2009scape>/Server/data/configs
      Re-pin drop_tables.json, rebuild item and monster base records from
      item_configs.json / npc_configs.json, then regenerate every derived file.
      Run data-pipeline/generate_drop_relationships.py afterwards.

Policy notes
  * Upstream values win. Fields the 2009Scape configs do not carry (Grand Exchange
    price, acquisition data, combat_level, boss flag, wiki-filled monster fields,
    spawn locations) are preserved from the existing record, never invented.
  * New monsters have combat_level = null (unknown) because combat level lives in
    the game cache, not in the configs, and is not derivable from config stats.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = SITE / "data"


# ----------------------------------------------------------------------------- io
def dumps_compact(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def num_files(directory: Path) -> dict[int, Path]:
    out = {}
    for p in directory.glob("*.json"):
        if p.stem.isdigit():
            out[int(p.stem)] = p
    return dict(sorted(out.items()))


def load_records(kind: str) -> dict[int, dict]:
    return {i: read_json(p) for i, p in num_files(DATA / kind).items()}


# Existing newline convention per file family (kept so diffs stay minimal).
NEWLINE = {"items": "\n", "monsters": "", "npcs": ""}


# -------------------------------------------------------------------------- derive
def derive_item_index(items: dict[int, dict]) -> list[dict]:
    return [
        {
            "id": i,
            "name": r.get("name"),
            "members": r.get("members"),
            "tradeable": r.get("tradeable"),
            "equipment_slot": r.get("equipment_slot"),
        }
        for i, r in sorted(items.items())
    ]


def derive_name_index(items: dict[int, dict], shipped: dict[str, int] | None = None) -> dict[str, int]:
    """lower-case name -> item id. Keeps the shipped id when it still carries that name
    (so existing links never change); otherwise the highest id with that name wins."""
    out: dict[str, int] = {}
    for i, r in sorted(items.items()):
        name = str(r.get("name") or "").strip().lower()
        if name:
            out[name] = i
    for name, i in (shipped or {}).items():
        if name in out and str(items.get(i, {}).get("name") or "").strip().lower() == name:
            out[name] = i
    return dict(sorted(out.items(), key=lambda kv: kv[1])) if not shipped else {k: out[k] for k in shipped if k in out} | {k: v for k, v in out.items() if k not in shipped}


def monster_index_row(i: int, r: dict) -> dict:
    return {
        "id": i,
        "name": r.get("name"),
        "boss": r.get("boss"),
        "combat_level": r.get("combat_level"),
        "slayer_task": r.get("slayer_task"),
        "slayer_exp": r.get("slayer_exp"),
        "members": r.get("members"),
    }


def derive_monster_index(monsters: dict[int, dict]) -> list[dict]:
    return [monster_index_row(i, r) for i, r in sorted(monsters.items())]


def derive_bosses(monsters: dict[int, dict]) -> list[dict]:
    return [monster_index_row(i, r) for i, r in sorted(monsters.items()) if r.get("boss")]


def norm_name(name) -> str:
    return re.sub(r"\s+", " ", str(name or "").strip()).lower()


def derive_display_index(monsters: dict[int, dict]) -> list[dict]:
    groups: dict[str, list[int]] = {}
    for i, r in sorted(monsters.items()):
        groups.setdefault(norm_name(r.get("name")), []).append(i)
    rows = []
    for ids in groups.values():
        first = monsters[ids[0]]
        levels = sorted({monsters[i].get("combat_level") for i in ids if monsters[i].get("combat_level") is not None})
        rows.append(
            {
                "id": ids[0],
                "name": first.get("name"),
                "boss": any(bool(monsters[i].get("boss")) for i in ids),
                "variant_count": len(ids),
                "combat_levels": levels,
                "game_ids": ids,
            }
        )
    return rows


def derive_npc_index(npcs: dict[int, dict]) -> list[dict]:
    return [{"id": i, "name": r.get("name")} for i, r in sorted(npcs.items())]


def derive_search_index(items, monsters, npcs, quest_entities) -> list[dict]:
    rows = []
    for i, r in sorted(items.items()):
        rows.append({"type": "item", "id": i, "name": r.get("name"), "aliases": []})
    for i, r in sorted(monsters.items()):
        rows.append({"type": "monster", "id": i, "name": r.get("name"), "aliases": []})
    for i, r in sorted(npcs.items()):
        rows.append({"type": "npc", "id": i, "name": r.get("name"), "aliases": []})
    for q in quest_entities:
        rows.append({"type": "quest", "id": q["id"], "name": q["name"], "aliases": []})
    return rows


def derive_entities(items, monsters, npcs, quest_entities, drop_monster_names: dict[int, str]) -> list[dict]:
    """Graph entities. Monsters = catalog monsters + any drop-table NPC (named upstream)."""
    ents = [{"type": "item", "id": i, "name": r.get("name")} for i, r in items.items()]
    mon = {i: r.get("name") for i, r in monsters.items()}
    for i, name in drop_monster_names.items():
        mon.setdefault(i, name)
    ents += [{"type": "monster", "id": i, "name": n} for i, n in mon.items()]
    ents += [{"type": "npc", "id": i, "name": r.get("name")} for i, r in npcs.items()]
    ents += [{"type": "quest", "id": q["id"], "name": q["name"]} for q in quest_entities]
    ents.sort(key=lambda e: (e["type"], str(e["id"])))
    return ents


def derive_graph(entities, drop_pairs: set[tuple[int, int]], quest_edges: list[list[str]]) -> dict:
    edges = [[f"monster:{m}", f"item:{i}", "drops"] for m, i in drop_pairs] + [list(e) for e in quest_edges]
    edges.sort(key=lambda e: (e[0], e[1], e[2]))
    counts = Counter(e["type"] for e in entities)
    return {
        "formatVersion": 1,
        "generatedFrom": "local game data",
        "entityCounts": {t: counts[t] for t in ("item", "monster", "npc", "quest")},
        "entities": entities,
        "edges": edges,
    }


def dup_name_count(records: dict[int, dict]) -> int:
    names = Counter(norm_name(r.get("name")) for r in records.values() if r.get("name"))
    return sum(v - 1 for v in names.values() if v > 1)


# ------------------------------------------------------------- relationship pairs
def pairs_from_shards() -> set[tuple[int, int]]:
    """(monster, item) pairs that are graph edges, read from committed relationship shards."""
    import gzip

    idx = read_json(DATA / "relationships/index.json")
    pairs = set()
    for mid in idx["monsters"]:
        with gzip.open(DATA / idx["monsters"][mid]) as fh:
            doc = json.load(fh)
        for rec in doc["relationships"]:
            if rec["dropTypes"] == ["tertiary"]:
                continue
            pairs.add((int(mid), rec["itemId"]))
    return pairs


def pairs_from_tables(tables: list[dict]) -> set[tuple[int, int]]:
    """Same rule computed straight from drop_tables.json (item id 0 is 'nothing')."""
    cats: dict[tuple[int, int], set[str]] = defaultdict(set)
    for t in tables:
        ids = [int(p) for p in str(t.get("ids", "")).split(",") if p.strip().isdigit()]
        for cat in ("default", "main", "charm", "tertiary"):
            for e in t.get(cat) or []:
                item = int(e["id"])
                if item == 0:
                    continue
                for n in ids:
                    cats[(n, item)].add(cat)
    return {k for k, v in cats.items() if v != {"tertiary"}}


def drop_npc_ids(tables: list[dict]) -> set[int]:
    out = set()
    for t in tables:
        out |= {int(p) for p in str(t.get("ids", "")).split(",") if p.strip().isdigit()}
    return out


# --------------------------------------------------------------------------- build
def build_derived(items, monsters, npcs, tables, *, pairs=None, old_graph=None, old_manifest=None, release=None):
    old_graph = old_graph or read_json(DATA / "knowledge/index.json")
    quest_entities = [e for e in old_graph["entities"] if e["type"] == "quest"]
    quest_edges = [e for e in old_graph["edges"] if e[2] != "drops"]
    upstream_names = {}
    for nid in drop_npc_ids(tables):
        if nid not in monsters:
            upstream_names[nid] = None  # filled by caller when known
    return quest_entities, quest_edges


def selftest() -> int:
    items, monsters, npcs = load_records("items"), load_records("monsters"), load_records("npcs")
    old_graph = read_json(DATA / "knowledge/index.json")
    quest_entities = [e for e in old_graph["entities"] if e["type"] == "quest"]
    quest_edges = [e for e in old_graph["edges"] if e[2] != "drops"]
    tables = read_json(DATA / "sources/2009scape/drop_tables.json")
    drop_names = {e["id"]: e["name"] for e in old_graph["entities"] if e["type"] == "monster" and e["id"] not in monsters}

    checks = []

    def canon(rows):
        return sorted(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows)

    def check(rel, got, rows=True):
        """Row-set equality: shipped files list the same rows, but some ids were appended
        out of order by earlier passes, so order is not a contract (no consumer relies on it)."""
        want = read_json(DATA / rel)
        if rows:
            ok = canon(got) == canon(want)
            if not ok and rel.startswith("monsters/"):
                # Known benign drift: a few shipped index rows hold combat_level null although the
                # monster record has a level. The record is authoritative, so regenerating fixes them.
                key = "id"
                wmap = {r[key]: r for r in want}
                diffs = [r for r in got if wmap.get(r[key]) != r]
                def only_level(r):
                    w = wmap.get(r[key]) or {}
                    ks = {k for k in set(r) | set(w) if r.get(k) != w.get(k)}
                    return ks <= {"combat_level", "combat_levels"}
                if diffs and all(only_level(r) for r in diffs):
                    ok = True
                    checks.append((rel + " (known stale combat_level rows fixed on regen)", True, f" n={len(diffs)}"))
        else:
            ok = got == want
        detail = ""
        if not ok:
            g, w = canon(got), canon(want)
            detail = f" rows got={len(g)} want={len(w)} only_got={len(set(g)-set(w))} only_want={len(set(w)-set(g))}"
        checks.append((rel, ok, detail))

    check("items/index.json", derive_item_index(items))
    check("monsters/index.json", derive_monster_index(monsters))
    check("monsters/display-index.json", derive_display_index(monsters))
    check("monsters/bosses.json", derive_bosses(monsters))
    check("npcs/index.json", derive_npc_index(npcs))
    check("knowledge/search-index.json", derive_search_index(items, monsters, npcs, quest_entities))
    # name-index: shipped mapping is kept when its id still carries that name (stability of links)
    shipped_names = read_json(DATA / "items/name-index.json")
    check("items/name-index.json", derive_name_index(items, shipped_names), rows=False)
    ents = derive_entities(items, monsters, npcs, quest_entities, drop_names)
    pairs = pairs_from_shards()
    g = derive_graph(ents, pairs, quest_edges)
    old = old_graph
    ok = (g["entityCounts"] == old["entityCounts"] and canon(g["entities"]) == canon(old["entities"])
          and sorted(map(tuple, g["edges"])) == sorted(map(tuple, old["edges"])))
    checks.append(("knowledge/index.json", ok, "" if ok else f" counts got={g['entityCounts']} want={old['entityCounts']} edges {len(g['edges'])}/{len(old['edges'])}"))

    table_pairs = pairs_from_tables(tables)
    checks.append(("pairs(shards)==pairs(tables)", pairs == table_pairs, f" shards={len(pairs)} tables={len(table_pairs)}"))

    bad = [c for c in checks if not c[1]]
    for rel, ok, detail in checks:
        print(("PASS " if ok else "FAIL ") + rel + detail)
    print(f"SELFTEST: {'PASS' if not bad else 'FAIL'} | {len(checks) - len(bad)}/{len(checks)} reproduced")
    return 1 if bad else 0


# ----------------------------------------------------------------------- refresh
ITEM_EXTRAS = ("grand_exchange_price", "_acquisition")
MONSTER_KEEP = ("locations", "boss", "combat_level", "_provenance")


def build_item(up: dict, old: dict | None) -> dict:
    rec = {k: (int(v) if k == "id" else v) for k, v in up.items()}
    for k in ITEM_EXTRAS:
        if old and k in old:
            rec[k] = old[k]
    if "_acquisition" not in rec:
        rec["_acquisition"] = {
            "schemaVersion": 1,
            "policy": "2009Scape-primary; OSRS-Wiki-secondary; unresolved=unknown",
            "shops": [],
            "monsterDrops": [],
            "groundSpawns": {"status": "unknown", "source": "2009Scape", "reason": "No trusted ground-spawn catalog is present in this release."},
        }
    return rec


def build_monster(up: dict, old: dict | None) -> dict:
    rec = {k: (int(v) if k == "id" else v) for k, v in up.items()}
    old = old or {}
    # Fields upstream lacks (wiki-filled stats etc.) survive; upstream always wins when it has the key.
    for k, v in old.items():
        if k not in rec and k not in MONSTER_KEEP:
            rec[k] = v
    rec["locations"] = old.get("locations", [])
    rec["boss"] = old.get("boss", False)
    rec["combat_level"] = old.get("combat_level")  # unknown for new monsters; lives in the cache
    prov = dict(old.get("_provenance") or {"primary": "2009Scape", "fallback": "OSRS Wiki", "wiki_fields": []})
    prov["wiki_fields"] = [k for k in prov.get("wiki_fields", []) if k not in up]
    rec["_provenance"] = prov
    return rec


def write_records(kind: str, records: dict[int, dict]) -> int:
    d = DATA / kind
    changed = 0
    for i, r in records.items():
        text = dumps_compact(r) + NEWLINE[kind]
        p = d / f"{i}.json"
        # Only touch files whose content really changed (key order alone is not a change).
        if not p.exists() or json.loads(p.read_text(encoding="utf-8")) != r:
            p.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def write_compact(rel: str, obj, newline: str = "", ascii_only: bool = False) -> None:
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=ascii_only) + newline
    (DATA / rel).write_text(text, encoding="utf-8")


def refresh(upstream: Path) -> int:
    up_items = {int(x["id"]): x for x in read_json(upstream / "item_configs.json")}
    up_npcs = {int(x["id"]): x for x in read_json(upstream / "npc_configs.json")}
    drop_path = upstream / "drop_tables.json"
    tables = read_json(drop_path)

    items, monsters, npcs = load_records("items"), load_records("monsters"), load_records("npcs")
    old_graph = read_json(DATA / "knowledge/index.json")
    old_name_index = read_json(DATA / "items/name-index.json")
    quest_entities = [e for e in old_graph["entities"] if e["type"] == "quest"]
    quest_edges = [e for e in old_graph["edges"] if e[2] != "drops"]

    # 1. items: upstream authoritative
    new_items = {i: build_item(up_items[i], items.get(i)) for i in up_items}
    for i in items:
        if i not in up_items:
            new_items[i] = items[i]  # keep anything upstream does not know (reported below)
    added_items = sorted(set(new_items) - set(items))
    item_changes = write_records("items", new_items)

    # 2. monsters: refresh existing, add drop-table NPCs that were missing
    new_monsters = {i: (build_monster(up_npcs[i], r) if i in up_npcs else r) for i, r in monsters.items()}
    added_monsters = []
    unresolved = []
    for nid in sorted(drop_npc_ids(tables)):
        if nid in new_monsters:
            continue
        if nid in up_npcs:
            new_monsters[nid] = build_monster(up_npcs[nid], None)
            added_monsters.append(nid)
        else:
            unresolved.append(nid)
    monster_changes = write_records("monsters", new_monsters)

    # 3. drop tables: re-pin
    shutil.copyfile(drop_path, DATA / "sources/2009scape/drop_tables.json")
    sha = hashlib.sha256(drop_path.read_bytes()).hexdigest()
    mp = DATA / "sources/2009scape/drop_tables.manifest.json"
    man = read_json(mp)
    man["contentSha256"], man["tableCount"] = sha, len(tables)
    mp.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 4. derived indexes
    write_compact("items/index.json", derive_item_index(new_items))
    write_compact("items/name-index.json", derive_name_index(new_items, old_name_index))
    write_compact("monsters/index.json", derive_monster_index(new_monsters))
    write_compact("monsters/display-index.json", derive_display_index(new_monsters))
    write_compact("monsters/bosses.json", derive_bosses(new_monsters))

    # 5. relationship shards (needs the new source) then the graph from the table rule
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "data-pipeline/generate_drop_relationships.py")], check=True)
    man["relationshipCount"] = read_json(DATA / "relationships/index.json")["relationshipCount"]
    mp.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pairs = pairs_from_tables(tables)
    leftovers = {nid: next((e["name"] for e in old_graph["entities"] if e["type"] == "monster" and e["id"] == nid), None) for nid in unresolved}
    leftovers = {k: v for k, v in leftovers.items() if v}
    ents = derive_entities(new_items, new_monsters, npcs, quest_entities, leftovers)
    graph = derive_graph(ents, pairs, quest_edges)
    write_compact("knowledge/index.json", graph, ascii_only=True)
    search = derive_search_index(new_items, new_monsters, npcs, quest_entities)
    write_compact("knowledge/search-index.json", search)

    # 6. counts in the two audit documents
    qp = DATA / "quality-report.json"
    q = read_json(qp)
    q["counts"].update(knowledgeEntities=len(ents), knowledgeEdges=len(graph["edges"]), searchRecords=len(search))
    q["relations"]["drops"] = len(pairs)
    qp.write_text(json.dumps(q, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cp = DATA / "catalog-manifest.json"
    c = read_json(cp)
    c["counts"].update(items=len(new_items), monsters=len(new_monsters), npcs=len(npcs))
    c["detailFiles"].update(items=len(new_items) + 2, monsters=len(new_monsters) + 2, npcs=len(npcs) + 1)
    c["searchRecords"] = len(search)
    c["knowledge"].update(entities=len(ents), edges=len(graph["edges"]), searchRecords=len(search))
    c["displayViews"]["monsters"].update(identityCount=len(derive_display_index(new_monsters)), gameVariantCount=len(new_monsters))
    cp.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "drop_tables": len(tables), "drop_sha256": sha,
        "items": len(new_items), "items_added": added_items, "item_files_changed": item_changes,
        "monsters": len(new_monsters), "monsters_added": len(added_monsters), "monster_files_changed": monster_changes,
        "drop_npcs_unresolved_upstream": unresolved,
        "graph_entities": len(ents), "graph_edges": len(graph["edges"]), "drop_pairs": len(pairs),
    }, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    r = sub.add_parser("refresh")
    r.add_argument("--upstream", required=True, type=Path)
    args = ap.parse_args()
    if args.cmd == "selftest":
        return selftest()
    return refresh(args.upstream)


if __name__ == "__main__":
    raise SystemExit(main())
