#!/usr/bin/env python3
"""PASS31.35: rebuild NPC catalog, NPC/monster spawns and item ground spawns from 2009Scape.

  refresh_2009scape_spawns.py --upstream <2009scape>/Server/data/configs

* npc_spawns.json  loc_data tokens are {x,y,plane,walks,direction} (NPCSpawner.kt).
  The earlier shipped monster fields "face"/"walk" were these last two tokens under the wrong names.
* The NPC catalog is rebuilt in 2009Scape ids: every upstream NPC that has a spawn and is not already
  a monster. The previous catalog was OSRS-Wiki data in a different id space.
* ground_spawns.json loc_data tokens are {amount,x,y,plane,respawn} (GroundSpawnLoader.kt).
  Items without an upstream ground spawn stay 'unknown' (other acquisition routes exist).
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import refresh_2009scape_core as C

DATA, ROOT = C.DATA, C.ROOT
TOK = re.compile(r"\{([^}]*)\}")


def parse_npc_spawns(path: Path) -> dict[int, list[dict]]:
    out = {}
    for row in C.read_json(path):
        locs = []
        for tok in TOK.findall(row["loc_data"]):
            x, y, z, walks, direction = (int(v) for v in tok.split(","))
            locs.append({"x": x, "y": y, "plane": z, "walks": bool(walks), "direction": direction})
        out[int(row["npc_id"])] = locs
    return out


def parse_ground(path: Path) -> dict[int, list[dict]]:
    out = {}
    for row in C.read_json(path):
        locs = []
        for tok in TOK.findall(row["loc_data"]):
            amount, x, y, z, respawn = (int(v) for v in tok.split(","))
            locs.append({"amount": amount, "x": x, "y": y, "plane": z, "respawn": respawn})
        out[int(row["item_id"])] = locs
    return out


def legacy_to_new(loc: dict) -> dict:
    if "walks" in loc:
        return loc
    return {"x": loc["x"], "y": loc["y"], "plane": loc.get("plane", 0), "walks": bool(loc.get("face", 0)), "direction": loc.get("walk", 0)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream", required=True, type=Path)
    up = ap.parse_args().upstream
    spawns = parse_npc_spawns(up / "npc_spawns.json")
    ground = parse_ground(up / "ground_spawns.json")
    up_npcs = {int(x["id"]): x for x in C.read_json(up / "npc_configs.json")}
    tables = C.read_json(DATA / "sources/2009scape/drop_tables.json")

    items, monsters = C.load_records("items"), C.load_records("monsters")
    old_graph = C.read_json(DATA / "knowledge/index.json")
    quests = [e for e in old_graph["entities"] if e["type"] == "quest"]
    quest_edges = [e for e in old_graph["edges"] if e[2] != "drops"]

    # monsters: upstream spawns win; otherwise keep (converted) shipped locations
    m_changed = 0
    for i, r in monsters.items():
        new = spawns.get(i) or [legacy_to_new(l) for l in r.get("locations", [])]
        if r.get("locations") != new:
            r["locations"] = new
            m_changed += 1
    # NPCs: rebuild
    npcs = {}
    for i in sorted(spawns):
        if i in monsters or i not in up_npcs:
            continue
        cfg = up_npcs[i]
        if str(cfg.get("name", "")).strip().lower() in ("", "null"):
            continue
        rec = {"id": i, "name": cfg["name"]}
        if cfg.get("examine"):
            rec["examine"] = cfg["examine"]
        rec.update(options=None, locations=spawns[i], aliases=[], shops=[])
        npcs[i] = rec
    old_npc_files = C.num_files(DATA / "npcs")
    for i, p in old_npc_files.items():
        if i not in npcs:
            p.unlink()
    for i, r in npcs.items():
        (DATA / "npcs" / f"{i}.json").write_text(C.dumps_compact(r), encoding="utf-8")
    C.write_records("monsters", monsters)

    # items: ground spawns
    g_items = 0
    for i, locs in ground.items():
        if i not in items:
            continue
        r = items[i]
        r["_acquisition"]["groundSpawns"] = {"status": "known", "source": "2009Scape", "spawns": locs}
        g_items += 1
    C.write_records("items", items)

    # derived files
    C.write_compact("npcs/index.json", C.derive_npc_index(npcs))
    C.write_compact("monsters/index.json", C.derive_monster_index(monsters))
    pairs = C.pairs_from_tables(tables)
    left = {nid: next((e["name"] for e in old_graph["entities"] if e["type"] == "monster" and e["id"] == nid), None)
            for nid in C.drop_npc_ids(tables) if nid not in monsters}
    ents = C.derive_entities(items, monsters, npcs, quests, {k: v for k, v in left.items() if v})
    graph = C.derive_graph(ents, pairs, quest_edges)
    C.write_compact("knowledge/index.json", graph, ascii_only=True)
    search = C.derive_search_index(items, monsters, npcs, quests)
    C.write_compact("knowledge/search-index.json", search)
    qp = DATA / "quality-report.json"; q = C.read_json(qp)
    q["counts"].update(knowledgeEntities=len(ents), knowledgeEdges=len(graph["edges"]), searchRecords=len(search))
    qp.write_text(json.dumps(q, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cp = DATA / "catalog-manifest.json"; c = C.read_json(cp)
    c["counts"]["npcs"] = len(npcs); c["detailFiles"]["npcs"] = len(npcs) + 1
    c["searchRecords"] = len(search)
    c["knowledge"].update(entities=len(ents), edges=len(graph["edges"]), searchRecords=len(search))
    cp.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # map marker data (map boundary hashes are refreshed by the caller)
    npc_marks = [{"id": i, "name": r["name"], "type": "NPC", "x": l["x"], "y": l["y"], "plane": l["plane"]}
                 for i, r in npcs.items() for l in r["locations"]]
    mon_marks = [{"id": i, "name": r["name"], "type": "Monster", "x": l["x"], "y": l["y"], "plane": l["plane"]}
                 for i, r in monsters.items() for l in r.get("locations", [])]
    (DATA / "map/npcs.js").write_text("/* Generated from 2009Scape npc_spawns.json. */\nwindow.OSRS_MAP_NPCS=" + C.dumps_compact(npc_marks) + ";\n", encoding="utf-8")
    (DATA / "map/monsters.js").write_text("// Generated from 2009Scape npc_spawns.json.\nconst monsters=" + C.dumps_compact(mon_marks) + ";\n", encoding="utf-8")
    print(json.dumps({"npcs": len(npcs), "npc_spawns": len(npc_marks), "monsters_with_locations": sum(1 for r in monsters.values() if r.get("locations")),
                      "monster_spawn_markers": len(mon_marks), "monster_files_changed": m_changed, "items_with_ground_spawns": g_items,
                      "ground_spawn_points": sum(len(v) for k, v in ground.items() if k in items),
                      "ground_items_not_in_catalog": [k for k in ground if k not in items]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
