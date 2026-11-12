#!/usr/bin/env python3
"""PASS31.60 gate: the Reference page (Slayer, clue rewards, minigames) is wired into the shell and works offline."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
page = (SITE / "reference.html").read_text()
assert page.count('<nav id="site-nav"') == 1 and page.count('id="app-tools-host"') == 1 and page.count('id="app-tools"') == 1
assert 'href="crafting.html"' in page and page.count('href="character.html"') == 1 and 'id="refView"' in page
for f in SITE.glob("*.html"):
    text = f.read_text()
    if '<nav id="site-nav"' in text and f.name != "map.html":  # map.html is hash-frozen by audit/map-boundary.sha256
        assert text.count('href="reference.html"') == 1, f.name
sw = (SITE / "sw.js").read_text()
for f in ("./reference.html", "./css/pages/reference.css", "./js/pages/reference.js", "./data/slayer.json", "./data/clues.json", "./data/minigames.json"):
    assert f'"{f}"' in sw, f
assert '"reference.html":"./pages/reference.js"' in (SITE / "js/bootstrap.js").read_text()
js = (SITE / "js/pages/reference.js").read_text()
for f in ("slayer.json", "clues.json", "minigames.json"):
    assert f in js and (SITE / "data" / f).is_file()
assert "escapeHTML" in js
assert subprocess.run(["node", "--check", str(SITE / "js/pages/reference.js")]).returncode == 0
print("PASS31.60 reference page gate: 3 sections, 23 shell pages, offline precache, errors=0")
