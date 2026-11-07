#!/usr/bin/env python3
"""PASS31.34 core refresh gate: shipped catalogs match the pinned 2009Scape sources."""
import hashlib, json, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]; D = R / "site/data"; errors = []
def chk(c, m):
    if not c: errors.append(m)
man = json.loads((D / "sources/2009scape/drop_tables.manifest.json").read_text())
src = (D / "sources/2009scape/drop_tables.json").read_bytes()
chk(hashlib.sha256(src).hexdigest() == man["contentSha256"], "drop table pin mismatch")
tables = json.loads(src)
chk(len(tables) == man["tableCount"] == 444, "drop table count")
chk(len(list((D / "items").glob("[0-9]*.json"))) == 12001, "item record count")
chk(len(list((D / "monsters").glob("[0-9]*.json"))) == 3098, "monster record count")
# every drop-table NPC that upstream defines has a monster record
ids = {int(p) for t in tables for p in str(t.get("ids", "")).split(",") if p.strip().isdigit()}
missing = sorted(i for i in ids if not (D / f"monsters/{i}.json").is_file())
chk(missing == [2124, 2126, 5678], f"unexpected drop NPCs without a monster record: {missing}")
# derived files must reproduce from the records
r = subprocess.run([sys.executable, str(R / "data-pipeline/refresh_2009scape_core.py"), "selftest"], capture_output=True, text=True)
chk(r.returncode == 0, "derived-file selftest failed: " + r.stdout[-300:])
a = json.loads((D / "items/296.json").read_text())
chk("/" not in a["examine"], "item 296 examine still merged")
print(f"PASS31.34 core refresh gate: dropTables={len(tables)} items=12001 monsters=3098 errors={len(errors)}")
if errors:
    [print("FAIL:", e) for e in errors]; raise SystemExit(1)
