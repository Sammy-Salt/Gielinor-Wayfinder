#!/usr/bin/env python3
"""PASS31.45 gate: the 2009Scape save importer (PASS31.43/44) parses the documented real layout."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
r = subprocess.run(["node", str(ROOT / "tests/save_import_check.mjs")], capture_output=True, text=True)
assert r.returncode == 0, r.stdout + r.stderr
svc = (ROOT / "site/js/services/save-import.js").read_text()
assert "core_data" in svc and "questStages" in svc
assert "ragger" not in svc.lower()
doc = (ROOT / "docs/history/PASS31.43-45_SAVE_IMPORT_2026-11-08.md").read_text()
assert "synthetic" in doc.lower()
print("PASS31.45 save import gate: parser check OK")
