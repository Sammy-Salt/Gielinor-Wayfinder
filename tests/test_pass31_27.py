import json, pathlib, subprocess
R=pathlib.Path(__file__).resolve().parents[1]; S=R/'site'
def chk(ok,msg):
    if not ok: raise AssertionError(msg)
rel=json.loads((S/'release.json').read_text()); chk(rel['release']=='PASS31.49','release mismatch'); chk(rel['buildId'] in (S/'sw.js').read_text(),'SW build mismatch')
boot=(S/'js/bootstrap.js').read_text(); chk('?v=42' in boot,'bootstrap route version not standardized')
chk('appendRelationships' not in boot,'obsolete runtime relationship component still wired')
chk(not (S/'js/components/relationships.js').exists(),'obsolete relationship component still shipped')
idx=json.loads((S/'data/relationships/index.json').read_text()); chk(idx['relationshipCount']==52557,'canonical relationship count mismatch'); chk(idx['categoryCounts']['tertiary']==100,'tertiary relationships missing')
rs=(S/'js/services/relationship-service.js').read_text(); chk('getGzipJson' in (S/'js/core/data-service.js').read_text(),'shared gzip data access missing'); chk('relationships/index.json' in rs,'drop index missing')
for fn in ['drop-time.js','drop-stats.js']:
    s=(S/'js/pages'/fn).read_text(); chk('Drops.probability' in s and 'Drops.rateLabel' in s,fn+' is not using canonical rate adapter')
for p in S.rglob('*.js'):
    r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True); chk(r.returncode==0,f'JS syntax: {p}: {r.stderr}')
print('PASS31.27 regression gate: updated for PASS31.49 canonical drop shards')
