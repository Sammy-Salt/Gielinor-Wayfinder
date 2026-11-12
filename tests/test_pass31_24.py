import pathlib
import subprocess

R = pathlib.Path(__file__).resolve().parents[1]
S = R / "site"

def check(condition, message):
    if not condition:
        raise AssertionError(message)

release = (S / "release.json").read_text()
check(any(f'\"release\": \"PASS31.{v}\"' in release for v in (24,25,26,27,28,29,30,34,35,36,39,40,41,42,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69)), "release mismatch")
check('"loaderVersion": "42"' in release, "loader version mismatch")

shell = (S / "js/core/shell.js").read_text()
check('document.getElementById("site-nav")' in shell, "shell must use existing nav")
check('document.createElement("nav")' not in shell, "shell must not create nav")
check('nav.remove()' not in shell and 'nav.removeChild' not in shell, "shell must not remove nav")

enhancer = (S / "js/components/app-enhancer.js").read_text()
check('document.getElementById("app-tools-host")' in enhancer, "enhancer must use static tools host")
check('nav.appendChild' not in enhancer, "search tools must not be appended to navigation")
check('document.createElement("nav")' not in enhancer, "enhancer must not create nav")

css = (S / "site.css").read_text()
check('#app-tools-host' in css, "static tools host CSS missing")
check('#site-nav .app-tools' not in css, "search must not be coupled to nav CSS")
check('nav-primary' not in css, "obsolete nav CSS remains")

pages = []
for page in S.glob("*.html"):
    text = page.read_text()
    if '<nav id="site-nav"' not in text:
        continue
    pages.append(page)
    check(text.count('<nav id="site-nav"') == 1, f"multiple navs: {page.name}")
    check(text.count('id="app-tools-host"') == 1, f"tools host missing/duplicated: {page.name}")
    check(text.count('href="character.html"') == 1, f"Character link count: {page.name}")
    check(text.count('href="crafting.html"') == 1, f"Crafting link count: {page.name}")
    nav = text.split('<nav id="site-nav"', 1)[1].split('</nav>', 1)[0]
    check('href="character.html"' in nav, f"Character not in nav: {page.name}")
    check('href="crafting.html"' in nav, f"Crafting not in nav: {page.name}")

sw = (S / "sw.js").read_text()
check("pass31.69-20261108-1" in sw, "service-worker build ID mismatch")
check("SKIP_WAITING" in sw, "service-worker update message missing")
check('"./js/core/shell.js?v=42"' in sw, "shell missing from app-code shell")
check('"./js/components/app-enhancer.js?v=42"' in sw, "enhancer missing from app-code shell")

loader = (S / "js/local-loader.js").read_text()
check('postMessage({type:"SKIP_WAITING"})' in loader, "loader must activate waiting worker")
check('loaderVersion' in loader and '?v=${encodeURIComponent(loaderVersion)}' in loader, "loader must cache-bust bootstrap")

for path in S.rglob("*.js"):
    result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    check(result.returncode == 0, f"JS syntax: {path}: {result.stderr}")

print(f"PASS31.24 nav/search isolation tests: pages={len(pages)} oneNav=all staticToolsHost=all character+crafting=all navCoupling=0 swUpdate=1 js=syntax-ok")
