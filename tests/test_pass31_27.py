import json, pathlib, subprocess
R=pathlib.Path(__file__).resolve().parents[1]; S=R/'site'
def chk(ok,msg):
    if not ok: raise AssertionError(msg)
rel=json.loads((S/'release.json').read_text()); chk(rel['release']=='PASS31.27','release mismatch'); chk(rel['buildId'] in (S/'sw.js').read_text(),'SW build mismatch'); chk('osrs-guide-pass31.27' in (S/'sw.js').read_text(),'cache namespace mismatch')
boot=(S/'js/bootstrap.js').read_text(); chk('?v=39' in boot,'bootstrap route version not standardized')
chk('appendRelationships' not in boot,'obsolete runtime relationship component still wired')
chk(not (S/'js/components/relationships.js').exists(),'obsolete relationship component still shipped')
rs=(S/'js/services/relationship-service.js').read_text(); chk('relationshipsByItem' in json.loads((S/'data/relationships/monster-drops.json').read_text()),'item relationship index missing'); chk('async itemDrops' in rs,'item canonical drop lookup missing')
for fn in ['item.js','character.js','crafting.js']:
    s=(S/'js/pages'/fn).read_text(); chk('fetch(' not in s,fn+' still performs page-local fetch')
for fn in ['drop-time.js','drop-stats.js']:
    s=(S/'js/pages'/fn).read_text(); chk('Drops.probability' in s and 'Drops.rateLabel' in s,fn+' is not using canonical rate adapter')
for p in S.rglob('*.js'):
    r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True); chk(r.returncode==0,f'JS syntax: {p}: {r.stderr}')
for p in S.rglob('*.json'):
    try: json.loads(p.read_text())
    except Exception as e: chk(False,f'JSON: {p}: {e}')
for p in S.rglob('*'):
    if p.is_file() and p.suffix in {'.js','.json','.html','.css','.webmanifest'}:
        chk('ragger' not in p.read_text(errors='ignore').lower(),f'Ragger production reference: {p}')
for name in ['map-grid-test.css','tile-test.css','test-quest-db.css']:
    chk(not (S/'css/pages'/name).exists(),f'obsolete test CSS still shipped: {name}')
print('PASS31.27 architecture/data tests: canonicalDrops=1 sharedDataAccess=1 sharedRateAdapter=1 obsoleteRuntimeRelationship=0 obsoleteProductionTestCSS=0 js/json=valid ragger=0')
