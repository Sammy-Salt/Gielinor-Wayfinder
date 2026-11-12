#!/usr/bin/env python3
"""PASS31.73 gate: quest requirements and crafting shortfalls link to their pages; calculator accepts ?skill=&target=."""
import subprocess
from pathlib import Path

S = Path(__file__).resolve().parents[1] / "site"
read = lambda p: (S / p).read_text(encoding="utf-8")
for f in ("quest.js", "crafting.js", "skill-stats.js"):
    assert subprocess.run(["node", "--check", str(S / "js/pages" / f)]).returncode == 0, f
assert subprocess.run(["node", "--check", str(S / "js/services/recipe-ready.js")]).returncode == 0
q = read("js/pages/quest.js")
for n in ("reqHref", "skill-stats.html?skill=", "quest.html?name=", "combat-stats.html", "CALC_SKILLS"):
    assert n in q, n
c = read("js/pages/crafting.js")
for n in ("badge.html", "item.html?id=", "quest.html?name=", "skill-stats.html?skill="):
    assert n in c, n
r = read("js/services/recipe-ready.js")
assert "html:" in r and "text:" in r and "link = null" in r
k = read("js/pages/skill-stats.js")
assert 'q.get("skill")' in k and 'q.get("target")' in k
print("PASS31.73 gate: requirement and ingredient links, calculator deep link, errors=0")
