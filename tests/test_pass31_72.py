#!/usr/bin/env python3
"""PASS31.72 gate: skill-calculator method rows link to encyclopedia pages and the map; map accepts deep links."""
import hashlib, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "site"
sk = (S / "js/pages/skill-stats.js").read_text(encoding="utf-8")
mp = (S / "js/pages/map.js").read_text(encoding="utf-8")
for f in ("skill-stats.js", "map.js"):
    assert subprocess.run(["node", "--check", str(S / "js/pages" / f)]).returncode == 0, f
for needle in ("method-links", "<th>Links</th>", "map.html?npc=", "map.html?legend=Fishing%20spot", "item.html?id=", 'npcLinks("monster"', 'npcLinks("npc"'):
    assert needle in sk, needle
assert 'if(e.target.closest("a"))return;' in sk
for needle in ("applyDeepLink", 'params.get("legend")', 'params.get("npc")', '.filter(Boolean).map(Number)'):
    assert needle in mp, needle
for line in (ROOT / "audit/map-boundary.sha256").read_text().splitlines():
    h, rel = line.split("  ", 1)
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, rel
print("PASS31.72 gate: method rows link to Info/Item/Map, map deep links, errors=0")
