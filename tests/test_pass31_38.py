#!/usr/bin/env python3
"""PASS31.38: shipped drop fractions match the traced 2009Scape roll rules."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    script = ROOT / "scripts/validate_drop_relationships.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(result.returncode)
    if "DROP VALIDATION: PASS" not in result.stdout:
        raise SystemExit("validator did not report PASS")
    if "sentinel source main id 31:" not in result.stdout:
        raise SystemExit("validator did not report the rare-drop-table sentinel")
    print("PASS31.38 drop roll validation gate: PASS")


if __name__ == "__main__":
    main()
