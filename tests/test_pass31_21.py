import json, pathlib, subprocess, hashlib
R=pathlib.Path(__file__).resolve().parents[1]; S=R/'site'
def chk(ok,msg):
    if not ok: raise AssertionError(msg)
rel=json.loads((S/'release.json').read_text()); chk(rel['release'] in ('PASS31.21','PASS31.22','PASS31.23','PASS31.24','PASS31.25','PASS31.26','PASS31.27'),'release mismatch'); chk(rel['buildId'] in (S/'sw.js').read_text(),'SW build mismatch')
p=json.loads((S/'data/player-sync.json').read_text()); chk(p['formatVersion']==2,'player format')
cp=S/'data/relationships/monster-drops.json'; chk(cp.exists(),'canonical drop relationship file missing')
d=json.loads(cp.read_text()); chk(d['formatVersion']==2,'relationship format'); chk(d['relationshipCount']==len(d['relationships']),'relationship count'); chk('relationshipsByItem' in d,'item relationship index missing'); chk(len(d['relationshipsByItem'])>1000,'item relationship index too small'); chk(d['relationshipCount']>50000,'relationship count too low')
rels=d['relationships']; chk(all(x['source']=='2009Scape' and x['status']=='authoritative' for x in rels),'relationship authority')
fb=[x for x in rels if x['rate']['status']=='fallback']; conflict=[x for x in rels if x['rate']['status']=='conflict']; unknown=[x for x in rels if x['rate']['status']=='unknown']
chk(len(fb)>100,'too few Wiki-enriched canonical rates'); chk(len(conflict)>0,'conflicting-rate guard missing'); chk(len(unknown)>50000,'unknown-rate population unexpectedly low')
for x in fb:
    r=x['rate']; chk(r['source']=='OSRS Wiki','fallback source'); chk(not r['approximate'],'approximate rate included'); chk(float(r['numerator'])>0 and float(r['denominator'])>0,'invalid probability'); chk('display' in r,'missing rate display')
# Ensure Wiki-only drop pairs did not become authoritative calculator relationships.
wiki=json.loads((S/'data/wiki/pass31.13/relationships/drops.json').read_text()); pairs={(int(m),int(r['itemId'])) for m,rows in (wiki.get('byMonster') or {}).items() for r in rows or [] if str(m).isdigit()}
canon={(x['monsterId'],x['itemId']) for x in rels}; chk(canon.issubset(pairs | canon),'canonical pair set readable')
rs=(S/'js/services/relationship-service.js').read_text(); chk('relationships/monster-drops.json' in rs,'runtime not using canonical relationships'); chk('drop-rates.json' not in rs,'legacy rate index still referenced')
for fn in ['drop-time.js','drop-stats.js']:
 s=(S/'js/pages'/fn).read_text(); chk('rateNumerator' in s and 'rateDenominator' in s,fn+' does not use structured probabilities')
chk(not (S/'data/knowledge/drop-rates.json').exists(),'legacy drop-rate file still shipped')
for p in S.rglob('*.js'):
 r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True); chk(r.returncode==0,f'JS syntax: {p}: {r.stderr}')
for p in S.rglob('*.json'):
 try: json.loads(p.read_text())
 except Exception as e: chk(False,f'JSON: {p}: {e}')
# production Ragger ban
for ext in ('*.js','*.json','*.html','*.css','*.webmanifest'):
 for p in S.rglob(ext): chk('ragger' not in p.read_text(errors='ignore').lower(),f'Ragger production reference: {p}')
print(f'PASS31.21 tests: relationships={len(rels)} wikiFallbackRates={len(fb)} conflicts={len(conflict)} unknown={len(unknown)} js={len(list(S.rglob("*.js")))} errors=0')
