import gzip, json, pathlib, subprocess, hashlib
R=pathlib.Path(__file__).resolve().parents[1]; S=R/'site'
def chk(ok,msg):
    if not ok: raise AssertionError(msg)
rel=json.loads((S/'release.json').read_text()); chk(rel['release']=='PASS31.78','release mismatch'); chk(rel['buildId'] in (S/'sw.js').read_text(),'SW build mismatch')
p=json.loads((S/'data/player-sync.json').read_text()); chk(p['formatVersion']==2,'player format')
idx=json.loads((S/'data/relationships/index.json').read_text()); chk(idx['formatVersion']==3,'relationship format'); chk(idx['relationshipCount']==52557,'relationship count'); chk(idx['categoryCounts']['tertiary']==100,'tertiary relationship count'); chk(idx['itemCount']==1114,'item shard count')
sha=hashlib.sha256((S/'data/sources/2009scape/drop_tables.json').read_bytes()).hexdigest(); chk(idx['source']['contentSha256']==sha,'source hash')
m=json.loads(gzip.decompress((S/'data/relationships/monsters/1615.json.gz').read_bytes())); row=next(x for x in m['relationships'] if x['itemId']==4151); chk(row['rate']['numerator']==1 and row['rate']['denominator']==513,'Abyssal whip 1/513 regression')
rs=(S/'js/services/relationship-service.js').read_text(); chk('relationships/index.json' in rs,'runtime not using canonical relationship index'); chk('drop-rates.json' not in rs,'legacy rate index still referenced')
for fn in ['drop-stats.js']:
    s=(S/'js/pages'/fn).read_text(); chk('rateNumerator' in s and 'rateDenominator' in s,fn+' does not use structured probabilities')
chk(not (S/'data/knowledge/drop-rates.json').exists(),'legacy drop-rate file still shipped')
for p in S.rglob('*.js'):
    r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True); chk(r.returncode==0,f'JS syntax: {p}: {r.stderr}')
print('PASS31.21 regression gate: adapted to PASS31.78 canonical lazy drop shards')
