#!/usr/bin/env python3
"""PASS31.70 gate: unused generated snapshots are gone and everything the app loads from data/wiki still exists."""
import re
from pathlib import Path

S = Path(__file__).resolve().parents[1] / "site"
for gone in ("data/wiki/pass31.8", "data/wiki/pass31.9", "data/wiki/pass31.13/review", "data/map/assets-osrswikimaps-staging"):
    assert not (S / gone).exists(), gone
base = S / "data/wiki/pass31.13"
for need in ("manifest.json", "summary.json", "relationships/drops.json", "relationships/recipes.json",
             "entities/items/index.json", "entities/equipment/index.json", "entities/monsters/index.json"):
    assert (base / need).is_file(), need
sw = (S / "sw.js").read_text()
for ref in re.findall(r"\./(data/wiki/[^\"']+)", sw):
    assert (S / ref).is_file(), ref
for ref in re.findall(r"data/wiki/pass31\.\d+", sw):
    assert ref == "data/wiki/pass31.13", ref
print("PASS31.70 slim-down gate: 4 unused folders removed, wiki fallback files intact, errors=0")
