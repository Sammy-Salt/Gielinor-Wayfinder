import json, pathlib, subprocess
R=pathlib.Path(__file__).resolve().parents[1]; S=R/'site'
def chk(ok,msg):
    if not ok: raise AssertionError(msg)
rel=json.loads((S/'release.json').read_text()); chk(rel['release'] in ('PASS31.20','PASS31.21','PASS31.22','PASS31.23','PASS31.24','PASS31.25','PASS31.26','PASS31.27','PASS31.29'),'release mismatch'); chk(rel['buildId'] in (S/'sw.js').read_text(),'SW build mismatch')
p=json.loads((S/'data/player-sync.json').read_text()); chk(p['formatVersion']==2,'player format'); chk(len(p['skills'])==24,'skills'); chk(len(p['bank'])==65,'bank'); chk(len(p['inventory'])==7,'inventory'); chk(len(p['equipment'])==3,'equipment')
for f in ['character.html','crafting.html','item.html','drop-time.html']:
    chk((S/f).exists(),f+' missing')
nav=(S/'character.html').read_text(); chk('class="nav-primary"' not in nav,'static nav wrapper should be runtime-owned'); chk('href="crafting.html">🔨 Crafting</a>' in nav,'direct crafting link missing'); chk('<details class="card character-section" open>' in nav,'character sections not collapsible')
ps=(S/'js/services/player-sync.js').read_text(); chk('FORMAT_VERSION=2' in ps,'player validator still v1')
rs=(S/'js/services/relationship-service.js').read_text(); chk('relationships/index.json' in rs,'canonical relationship dataset missing'); chk('drop-rates.json' not in rs,'legacy rate index still referenced')
dt=(S/'js/pages/drop-time.js').read_text(); chk('rateNumerator' in dt and 'rateDenominator' in dt,'drop-time structured rate missing')
item=(S/'js/pages/item.js').read_text(); bootstrap=(S/'js/bootstrap.js').read_text(); chk('enhanceAppShell' not in item,'item page must not own shell enhancement'); chk('enhanceAppShell()' in bootstrap,'shared shell enhancement missing')
for js in S.rglob('*.js'):
    r=subprocess.run(['node','--check',str(js)],capture_output=True,text=True); chk(r.returncode==0,f'JS syntax: {js}: {r.stderr}')
for j in S.rglob('*.json'):
    try: json.loads(j.read_text())
    except Exception as e: chk(False,f'JSON: {j}: {e}')
print(f'PASS31.20 regression tests: skills={len(p["skills"])} bank={len(p["bank"])} inventory={len(p["inventory"])} equipment={len(p["equipment"])} js={len(list(S.rglob("*.js")))} errors=0')
