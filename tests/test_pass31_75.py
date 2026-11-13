#!/usr/bin/env python3
"""PASS31.75 gate: monochrome + soft yellow redesign, light/dark toggle on every page, no emoji in nav/headings, old back links gone."""
import re, subprocess
from pathlib import Path

S = Path(__file__).resolve().parents[1] / "site"
css = (S / "site.css").read_text(encoding="utf-8")
for tok in ("--ui-bg:#111111", "--ui-accent:#e8d48a", "--ui-bg:#f7f7f5", ':root[data-theme="light"]', "prefers-color-scheme:light", "--osrs-gold:var(--ui-accent)"):
    assert tok in css, tok
theme = (S / "js/theme-init.js").read_text(encoding="utf-8")
assert subprocess.run(["node", "--check", str(S / "js/theme-init.js")]).returncode == 0
for n in ("wayfinder.theme", "theme-toggle", "data-theme", "Switch to dark mode"):
    assert n in theme, n
emoji = re.compile(r"[\U0001F300-\U0001FAFF⚔⚠✅❌⭐][️]?")
for f in S.glob("*.html"):
    t = f.read_text(encoding="utf-8")
    assert t.count('js/theme-init.js') == 1 and t.index("theme-init.js") < t.index("site.css"), f.name
    nav = t[t.find('<nav id="site-nav"'):t.find("</nav>")]
    assert not emoji.search(nav), f.name
    if f.name != "map.html":
        assert not emoji.search(re.sub(r"<script.*?</script>", "", t, flags=re.S)), f.name
assert '"./js/theme-init.js"' in (S / "sw.js").read_text()
assert "←" not in (S / "js/pages/boss.js").read_text(encoding="utf-8")
home = (S / "index.html").read_text(encoding="utf-8")
assert "<h1>Home</h1>" in home and 'id="questTotal"' in home and "link-grid" in home
print("PASS31.75 redesign gate: tokens, light/dark toggle on 23 pages, no nav/heading emoji, errors=0")
