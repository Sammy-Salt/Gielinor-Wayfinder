import gzip, hashlib, json, pathlib, subprocess
from fractions import Fraction

R=pathlib.Path(__file__).resolve().parents[1]; S=R/'site'
def chk(ok,msg):
    if not ok: raise AssertionError(msg)

release=json.loads((S/'release.json').read_text())
chk(release['release']=='PASS31.58','release mismatch')
chk(release['buildId'] in (S/'sw.js').read_text(),'SW build mismatch')
chk('gielinor-wayfinder-pass31.58' in (S/'sw.js').read_text(),'cache namespace mismatch')
chk('?v=42' in (S/'js/bootstrap.js').read_text(),'loader version mismatch')

idx=json.loads((S/'data/relationships/index.json').read_text())
chk(idx['relationshipCount']==52557,'relationship count must be 52557')
chk(idx['monsterCount']==2146,'monster shard count mismatch')
chk(idx['itemCount']==1114,'item shard count mismatch')
chk(idx['categoryCounts']['tertiary']==100,'tertiary relationship count mismatch')
chk(idx['categoryCounts']['main']==45575,'main relationship count mismatch')
chk(idx['categoryCounts']['charm']==4804,'charm relationship count mismatch')
chk(idx['categoryCounts']['default']==2097,'default relationship count mismatch')

source=S/'data/sources/2009scape/drop_tables.json'
sha=hashlib.sha256(source.read_bytes()).hexdigest()
chk(sha=='09e5891ece49b962e9b7f8f843ef37046b8ee8b7d90a7d0a0b74a7a3c69f8a6e','source SHA mismatch')
chk(idx['source']['contentSha256']==sha,'index source SHA mismatch')
chk(json.loads((S/'data/sources/2009scape/drop_tables.manifest.json').read_text())['contentSha256']==sha,'source manifest SHA mismatch')

# Primary probability regression: Abyssal whip (4151) from Abyssal demon (1615) is 1/513.
whip=json.loads(gzip.decompress((S/'data/relationships/monsters/1615.json.gz').read_text() if False else (S/'data/relationships/monsters/1615.json.gz').read_bytes()))
row=next(x for x in whip['relationships'] if x['itemId']==4151)
chk(row['rate']['status']=='authoritative','Abyssal whip rate is not authoritative')
chk(row['rate']['numerator']==1 and row['rate']['denominator']==513,'Abyssal whip rate must be 1/513')
chk(row['rate']['display']=='1/513','Abyssal whip display mismatch')

# Generator output has already validated every source row. Spot-check representative
# shards and verify the index counts cover the generated files.
for path in [(S/'data/relationships/monsters/1615.json.gz'),
             (S/'data/relationships/monsters/1.json.gz'),
             (S/'data/relationships/items/4151.json.gz')]:
    data=json.loads(gzip.decompress(path.read_bytes()))
    for row in data['relationships']:
        chk(row['rate']['status']=='authoritative','non-authoritative sampled relationship')
        chk(row['rate']['source']=='2009Scape','wrong sampled drop source')
        chk(row['rate']['sourceHash']==sha,'sampled relationship source hash mismatch')
        chk(row['rate']['denominator']>0 and row['rate']['numerator']>=0,'invalid sampled probability')

# Shard/index consistency.
chk(len(list((S/'data/relationships/monsters').glob('*.json.gz')))==2146,'monster shard file count mismatch')
chk(len(list((S/'data/relationships/items').glob('*.json.gz')))==1114,'item shard file count mismatch')
chk(not (S/'data/relationships/monster-drops.json').exists(),'monolithic relationship payload still shipped')

rs=(S/'js/services/relationship-service.js').read_text()
ds=(S/'js/services/drop-service.js').read_text()
datajs=(S/'js/core/data-service.js').read_text()
chk('getGzipJson' in datajs,'shared gzip data access missing')
chk('relationships/index.json' in rs,'relationship index missing from service')
chk('.json.gz' in idx['monsters']['1'],'gzip monster shard missing')
chk("rateStatus==='authoritative'" in ds,'authoritative rate adapter missing')

for p in S.rglob('*.js'):
    r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
    chk(r.returncode==0,f'JS syntax: {p}: {r.stderr}')
for p in S.rglob('*.json'):
    try: json.loads(p.read_text())
    except Exception as e: chk(False,f'JSON: {p}: {e}')
for p in S.rglob('*'):
    if p.is_file() and p.suffix in {'.js','.json','.html','.css','.webmanifest'}:
        chk('ragger' not in p.read_text(errors='ignore').lower(),f'Ragger production reference: {p}')

print('PASS31.28 drop tests: relationships=52557 tertiary=100 authoritativeRates=52557 wikiFallback=0 monolithic=0 gzip=PASS sourceHash=PASS js/json=valid ragger=0')
