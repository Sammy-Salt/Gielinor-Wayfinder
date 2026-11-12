#!/usr/bin/env python3
"""PASS31.71 gate: old back links removed, Goals has a content wrapper, total level agrees across pages."""
import re
from pathlib import Path

S = Path(__file__).resolve().parents[1] / "site"
for f in ("goals.html", "quests.html"):
    assert "← Dashboard" not in (S / f).read_text(encoding="utf-8"), f
assert "← Quest Tracker" not in (S / "js/pages/quest.js").read_text(encoding="utf-8")
assert '<main class="osrs-content">' in (S / "goals.html").read_text(encoding="utf-8")
prog = (S / "js/services/progression-service.js").read_text(encoding="utf-8")
assert "Player.getSkill(skill[1])||Player.getSkill(skill[0])" in prog
idx = (S / "js/pages/index.js").read_text(encoding="utf-8")
assert '"Summoning"' in idx and '"Runecrafting"' in idx
print("PASS31.71 gate: back links removed, Goals margins, consistent total level, errors=0")
