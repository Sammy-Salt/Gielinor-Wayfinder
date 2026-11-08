#!/usr/bin/env python3
"""PASS31.47 gate: recipes are checked against the player's levels, inventory, bank and equipment."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
r = subprocess.run(["node", str(ROOT / "tests/recipe_ready_check.mjs")], capture_output=True, text=True)
assert r.returncode == 0, r.stdout + r.stderr
crafting = (ROOT / "site/js/pages/crafting.js").read_text()
service = (ROOT / "site/js/services/recipe-service.js").read_text()
assert "recipe-ready.js" in crafting and "recipe-ready.js" in service
assert "player.bank" not in crafting, "crafting page must use shared holdings (inventory + bank + equipment)"
assert "Missing level/materials" not in crafting
assert "recipe-ready" in (ROOT / "site/css/pages/item.css").read_text()
print("PASS31.47 recipe readiness gate: OK")
