#!/usr/bin/env python3
"""PASS31.68 gate: page headings carry no emoji, developer-voice copy is gone, map panel styling is scoped to the map page."""
import re
from pathlib import Path

S = Path(__file__).resolve().parents[1] / "site"
emoji = re.compile(r"<h[12][^>]*>\s*[☀-➿\U0001F300-\U0001FAFF]")
for f in S.glob("*.html"):
    assert not emoji.search(f.read_text(encoding="utf-8")), f.name
item = (S / "js/pages/item.js").read_text(encoding="utf-8")
for bad in ("Trusted acquisition", "canonical data model", "No trusted", "Trusted ground-spawn"):
    assert bad not in item, bad
css = (S / "site.css").read_text()
assert 'body[data-page="map"] #results' not in css  # old map panels removed in PASS31.77
assert "PASS31.68 spacing" in css
print("PASS31.68 copy and spacing gate: no heading emoji, plain-language item copy, scoped map panels, errors=0")
