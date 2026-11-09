import pathlib
import subprocess

R = pathlib.Path(__file__).resolve().parents[1]
S = R / "site"

def chk(ok, msg):
    if not ok:
        raise AssertionError(msg)

rel = __import__('json').loads((S / 'release.json').read_text())
chk(rel['release'] in ('PASS31.22', 'PASS31.23','PASS31.24','PASS31.25','PASS31.26','PASS31.27','PASS31.30','PASS31.34','PASS31.35','PASS31.36','PASS31.39','PASS31.40','PASS31.41','PASS31.42','PASS31.45','PASS31.46','PASS31.47','PASS31.48'), 'release mismatch')
chk(rel['buildId'] in (S / 'sw.js').read_text(), 'SW build mismatch')

# PASS31.22's two-row runtime-wrapper design is superseded by PASS31.23.
css = (S / 'site.css').read_text()
js = (S / 'js/components/app-enhancer.js').read_text()
shell = (S / 'js/core/shell.js').read_text()
chk('nav-primary' not in css, 'obsolete nav-primary CSS remains')
chk('nav-primary' not in js, 'obsolete nav-primary runtime wrapper remains')
chk('document.createElement("nav")' not in shell, 'runtime nav recreation remains')

for p in S.rglob('*.js'):
    r = subprocess.run(['node', '--check', str(p)], capture_output=True, text=True)
    chk(r.returncode == 0, f'JS syntax: {p}: {r.stderr}')

print('PASS31.22 compatibility regression: superseded-nav remnants=0 js=syntax-ok')
