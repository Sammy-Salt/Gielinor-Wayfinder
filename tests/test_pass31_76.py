#!/usr/bin/env python3
"""PASS31.76 gate: Drop & Kill Time page removed; Drop Statistics carries kills/hour time estimates."""
import re
from pathlib import Path
S = Path(__file__).resolve().parents[1] / "site"
for f in ("drop-time.html", "js/pages/drop-time.js", "css/pages/drop-time.css"):
    assert not (S / f).exists(), f
for f in list(S.glob("*.html")) + list(S.glob("js/**/*.js")) + [S / "sw.js"]:
    assert "drop-time" not in f.read_text(encoding="utf-8"), f.name
ds = (S / "js/pages/drop-stats.js").read_text(encoding="utf-8")
assert 'getElementById("kph")' in ds and "Expected time" in ds and "Drops per hour" in ds
assert 'id="kph"' in (S / "drop-stats.html").read_text(encoding="utf-8")
print("PASS31.76: drop-time removed, drop-stats has kills/hour time estimates")
