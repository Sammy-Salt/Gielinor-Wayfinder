#!/usr/bin/env python3
import json,hashlib,sys,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]; S=R/'site'; errors=[]
def chk(c,m):
    if not c: errors.append(m)
idx=json.loads((S/'data/items/index.json').read_text()); ids={int(x['id']) for x in idx}; files={int(p.stem) for p in (S/'data/items').glob('[0-9]*.json')}
chk(len(idx)==11978,f'item index count changed: {len(idx)}'); chk(ids==files,'item index/detail IDs differ')
shops=drops=0
for i in ids:
 d=json.loads((S/'data/items'/f'{i}.json').read_text()); chk(d.get('id')==i,f'item {i} id mismatch'); chk(bool(d.get('name')),f'item {i} missing name'); a=d.get('_acquisition'); chk(isinstance(a,dict) and a.get('schemaVersion')==1,f'item {i} acquisition schema missing')
 for x in a.get('shops',[]): shops+=1; chk(x.get('source')=='2009Scape','shop source is not 2009Scape')
 for x in a.get('monsterDrops',[]): drops+=1; chk(x.get('source')=='OSRS Wiki','drop source is not OSRS Wiki'); chk((S/'data/monsters'/f"{x['monsterId']}.json").exists(),f'missing monster endpoint {x.get("monsterId")}')
for p in S.rglob('*'):
 if p.is_file() and p.suffix.lower() in {'.js','.json','.html','.css','.webmanifest'}: chk('ragger' not in p.read_text(errors='ignore').lower(),f'retired source reference: {p.relative_to(R)}')
rel=json.loads((S/'release.json').read_text()); cat=json.loads((S/'data/catalog-manifest.json').read_text()); sw=(S/'sw.js').read_text()
chk(rel['release'] in ('PASS31.19','PASS31.20','PASS31.21','PASS31.22','PASS31.23','PASS31.24','PASS31.25','PASS31.26','PASS31.27'),'release mismatch'); chk(cat['release']==rel['release'],'catalog release mismatch'); chk(cat['buildId']==rel['buildId'],'catalog build mismatch'); chk(rel['buildId'] in sw,'service worker build mismatch'); chk('js/pages/item.js?v=39' in sw,'item.js missing from precache')
bad=[]
for p in S.rglob('*.js'):
 r=subprocess.run(['node','--check',str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if r.returncode: bad.append(str(p.relative_to(R)))
chk(not bad,f'JS syntax failures: {bad[:5]}')
for line in (R/'audit/map-boundary.sha256').read_text().splitlines():
 h,relp=line.split('  ',1); p=R/relp; chk(p.exists(),f'map file missing {relp}'); chk(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==h,f'map boundary changed {relp}')
print(f'PASS31.18 tests: items={len(ids)} shops={shops} wikiDrops={drops} js={len(list(S.rglob("*.js")))} errors={len(errors)}')
if errors:
 [print('FAIL:',e) for e in errors[:50]]; sys.exit(1)
