#!/usr/bin/env python3
"""PASS31.35 spawn gate: NPC catalog, spawns and ground spawns come from 2009Scape."""
import json, re, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]; D = R / "site/data"; errors = []
def chk(c, m):
    if not c: errors.append(m)
npcs = {int(p.stem): json.loads(p.read_text()) for p in (D / "npcs").glob("[0-9]*.json")}
mons = {int(p.stem): json.loads(p.read_text()) for p in (D / "monsters").glob("[0-9]*.json")}
chk(len(npcs) == 1646, f"npc count {len(npcs)}")
chk(not set(npcs) & set(mons), "an id is both an NPC and a monster")
chk(all(n.get("locations") for n in npcs.values()), "NPC without a spawn")
chk((npcs.get(0) or mons.get(0) or {}).get("name") == "Hans", "id 0 must be Hans (2009Scape id space)")
for r in list(npcs.values()) + list(mons.values()):
    for l in r.get("locations", []):
        chk(set(l) == {"x", "y", "plane", "walks", "direction"}, f"bad spawn shape on {r['id']}")
        break
chk(sum(len(m.get("locations", [])) for m in mons.values()) == 8950, "monster spawn total")
def js(path, prefix):
    t = path.read_text(); return json.loads(t[t.index(prefix) + len(prefix):].rstrip().rstrip(";"))
nm = js(D / "map/npcs.js", "window.OSRS_MAP_NPCS="); mm = js(D / "map/monsters.js", "const monsters=")
chk(len(nm) == sum(len(n["locations"]) for n in npcs.values()), "map npc markers != catalog spawns")
chk(len(mm) == 8950, "map monster markers != catalog spawns")
chk(any(m["plane"] != 0 for m in nm + mm), "no marker has a plane other than 0")
ground = [json.loads(p.read_text()) for p in (D / "items").glob("[0-9]*.json")]
known = [i for i in ground if i["_acquisition"]["groundSpawns"]["status"] == "known"]
chk(len(known) == 173, f"ground-spawn items {len(known)}")
chk(sum(len(i["_acquisition"]["groundSpawns"]["spawns"]) for i in known) == 713, "ground spawn points")
r = subprocess.run([sys.executable, str(R / "data-pipeline/refresh_2009scape_core.py"), "selftest"], capture_output=True, text=True)
chk(r.returncode == 0, "derived-file selftest failed: " + r.stdout[-300:])
print(f"PASS31.35 spawn gate: npcs={len(npcs)} npcMarkers={len(nm)} monsterMarkers={len(mm)} groundItems={len(known)} errors={len(errors)}")
if errors:
    [print("FAIL:", e) for e in errors]; raise SystemExit(1)
