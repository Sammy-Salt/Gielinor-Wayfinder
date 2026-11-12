#!/usr/bin/env python3
"""Repository integrity gate for Gielinor Wayfinder."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ERRORS: list[str] = []

def check(ok: bool, message: str) -> None:
    if not ok:
        ERRORS.append(message)

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

for required in [
    "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", ".github/copilot-instructions.md",
    "docs/development/AI_CHANGE_PROTOCOL.md", "docs/development/PROJECT_ANALYSIS.md",
    "docs/development/GIT_WORKFLOW.md", "docs/development/TESTING.md",
]:
    check((ROOT / required).is_file(), f"missing governance file: {required}")

release = json.loads((SITE / "release.json").read_text())
root_manifest = json.loads((ROOT / "release-manifest.json").read_text())
site_manifest = json.loads((SITE / "release-manifest.json").read_text())
check(release["release"] == "PASS31.61", "site release must be PASS31.61")
check(root_manifest["release"] == release["release"], "root manifest release mismatch")
check(site_manifest["release"] == release["release"], "site manifest release mismatch")
check(root_manifest["buildId"] == release["buildId"], "root manifest build mismatch")
check(site_manifest["buildId"] == release["buildId"], "site manifest build mismatch")

drop_index = json.loads((SITE / 'data/relationships/index.json').read_text())
check(drop_index['relationshipCount'] == 52557, 'canonical drop relationship count mismatch')
check(drop_index['categoryCounts']['tertiary'] == 100, 'canonical tertiary relationship count mismatch')
check(drop_index['monsterCount'] == 2146, 'canonical monster shard count mismatch')
check(drop_index['itemCount'] == 1114, 'canonical item shard count mismatch')
check((SITE / 'data/sources/2009scape/drop_tables.json').is_file(), 'canonical 2009Scape source payload missing')
check(not (SITE / 'data/relationships/monster-drops.json').exists(), 'obsolete monolithic drop payload still shipped')
check(not (SITE / 'js/components/relationships.js').exists(), 'obsolete runtime relationship component still shipped')

pages = [p for p in SITE.glob("*.html") if '<nav id="site-nav"' in read(p)]
check(len(pages) == 23, f"expected 23 shell pages, found {len(pages)}")
for page in pages:
    text = read(page)
    check(text.count('<nav id="site-nav"') == 1, f"multiple navs: {page.name}")
    check(text.count('id="app-tools-host"') == 1, f"tools host count: {page.name}")
    check(text.count('id="app-tools"') == 1, f"tools count: {page.name}")
    check(text.count('href="character.html"') == 1, f"Character link count: {page.name}")
    check(text.count('href="crafting.html"') == 1, f"Crafting link count: {page.name}")

enhancer = read(SITE / "js/components/app-enhancer.js")
check('document.createElement("nav")' not in enhancer, "enhancer creates nav")
check('nav.appendChild' not in enhancer, "enhancer appends to nav")
check('document.getElementById("app-tools-host")' in enhancer, "enhancer missing tools host")
shell = read(SITE / "js/core/shell.js")
check('document.createElement("nav")' not in shell, "shell creates nav")
check('nav.remove' not in shell and 'nav.replaceChildren' not in shell, "shell removes/replaces nav")

ragger = []
for ext in ("*.js", "*.json", "*.html", "*.css", "*.webmanifest"):
    for path in SITE.rglob(ext):
        if "ragger" in read(path).lower():
            ragger.append(str(path.relative_to(ROOT)))
check(not ragger, f"Ragger production references: {ragger[:5]}")

for path in SITE.rglob("*.json"):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        ERRORS.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")

for path in SITE.rglob("*.js"):
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    check(result.returncode == 0, f"JS syntax {path.relative_to(ROOT)}: {result.stderr.strip()}")

result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT, capture_output=True, text=True)
check(result.returncode == 0 and result.stdout.strip() == "true", "Git repository is not initialized")

if ERRORS:
    print("PROJECT VERIFY: FAIL")
    for error in ERRORS:
        print("-", error)
    raise SystemExit(1)

print(f"PROJECT VERIFY: PASS | shellPages={len(pages)} | JS={len(list(SITE.rglob('*.js')))} | JSON={len(list(SITE.rglob('*.json')))} | Ragger=0 | metadata=PASS31.61 | git=present")
