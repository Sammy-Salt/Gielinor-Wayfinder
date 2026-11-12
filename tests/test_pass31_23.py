import pathlib
import subprocess

R = pathlib.Path(__file__).resolve().parents[1]
S = R / "site"

def check(condition, message):
    if not condition:
        raise AssertionError(message)

release = (S / "release.json").read_text()
check(any(f'\"release\": \"PASS31.{v}\"' in release for v in (24,25,26,27,28,29,30,34,35,36,39,40,41,42,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70)), "release mismatch")
check('pass31.70-' in release, "build ID missing")

shell = (S / "js/core/shell.js").read_text()
check('document.getElementById("site-nav")' in shell, "shell must use existing nav")
check('document.createElement("nav")' not in shell, "shell must not create a second nav")
check('querySelectorAll("#site-nav,.osrs-header,.osrs-skip-link")' not in shell, "shell must not remove canonical nav")

enhancer = (S / "js/components/app-enhancer.js").read_text()
check('document.createElement("nav")' not in enhancer, "enhancer must not create a nav")
check('nav-primary' not in enhancer, "obsolete nav wrapper must be gone")
check('document.getElementById("app-tools-host")' in enhancer, "search enhancement must use static tools host")
check('nav.appendChild' not in enhancer, "search enhancement must not append to nav")

css = (S / "site.css").read_text()
check('nav-primary' not in css, "obsolete nav-primary CSS must be gone")
check('#app-tools-host' in css, "static tools host CSS missing")
check('#site-nav .app-tools' not in css, "search must not be coupled to nav")

html_files = []
for page in S.glob("*.html"):
    text = page.read_text()
    if '<nav id="site-nav"' not in text:
        continue
    html_files.append(page)
    check(text.count('<nav id="site-nav"') == 1, f"multiple canonical navs: {page.name}")
    check('href="character.html"' in text, f"Character link missing: {page.name}")
    check('href="crafting.html"' in text, f"Crafting link missing: {page.name}")
    check(text.count('href="crafting.html"') == 1, f"duplicate Crafting nav link: {page.name}")
    check(text.count('href="character.html"') == 1, f"duplicate Character nav link: {page.name}")

for path in S.rglob("*.js"):
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    check(result.returncode == 0, f"JS syntax: {path}: {result.stderr}")

print(f"PASS31.23 compatibility nav tests: pages={len(html_files)} oneNav=all staticLinks=character+crafting noDynamicNav=1 js=syntax-ok")
