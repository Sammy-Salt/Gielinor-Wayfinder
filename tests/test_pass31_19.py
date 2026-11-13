#!/usr/bin/env python3
import json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]; S=R/'site'; errors=[]
def chk(c,m):
    if not c: errors.append(m)
player=json.loads((S/'data/player-sync.json').read_text()); recipes=json.loads((S/'data/recipes.json').read_text())
chk(player['formatVersion']==2,'player format mismatch'); chk(len(player['skills'])==24,'skill count mismatch'); chk(player['player']['totalXP']>147000,'total XP missing'); chk(len(player['bank'])==65,'bank count mismatch'); chk(len(player['inventory'])==7,'inventory count mismatch'); chk(len(player['equipment'])==3,'equipment count mismatch'); chk(player['player']['location']=={'x':3222,'y':3218,'plane':0},'location mismatch'); chk(player['quests']['questPoints']==7,'quest points mismatch'); chk(player['statistics']['logsChopped']==953,'stats mismatch'); chk(len(recipes['recipes'])>150,'recipe dataset unexpectedly small'); chk(recipes.get('sourcePolicy')=={'primary':'2009Scape','secondary':'OSRS Wiki'},'recipe source policy mismatch (PASS31.33 schema: sourcePolicy primary=2009Scape, secondary=OSRS Wiki)');
for p in S.rglob('*'):
 if p.is_file() and p.suffix.lower() in {'.js','.json','.html','.css','.webmanifest'}: chk('ragger' not in p.read_text(errors='ignore').lower(),f'retired source reference: {p.relative_to(R)}')
for p in [S/'character.html',S/'crafting.html',S/'js/pages/character.js',S/'js/pages/crafting.js',S/'data/recipes.json']:
 chk(p.exists(),f'missing {p.relative_to(R)}')
for p in S.rglob('*.js'):
 r=subprocess.run(['node','--check',str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if r.returncode: errors.append(f'JS syntax: {p.relative_to(R)}')
rel=json.loads((S/'release.json').read_text()); chk(rel['release'] in ('PASS31.19','PASS31.20','PASS31.21','PASS31.22','PASS31.23','PASS31.24','PASS31.25','PASS31.26','PASS31.27','PASS31.30','PASS31.34','PASS31.35','PASS31.36','PASS31.39','PASS31.40','PASS31.41','PASS31.42','PASS31.45','PASS31.46','PASS31.47','PASS31.48','PASS31.49','PASS31.50','PASS31.51','PASS31.52','PASS31.53','PASS31.54','PASS31.55','PASS31.56','PASS31.57','PASS31.58','PASS31.59','PASS31.60','PASS31.61','PASS31.62','PASS31.63','PASS31.64','PASS31.65','PASS31.66','PASS31.67','PASS31.68','PASS31.69','PASS31.70','PASS31.71','PASS31.72','PASS31.73','PASS31.74','PASS31.75','PASS31.76','PASS31.77'),'release mismatch'); chk(rel['buildId'] in (S/'sw.js').read_text(),'SW build mismatch')
# map boundary
for line in (R/'audit/map-boundary.sha256').read_text().splitlines():
 h,relp=line.split('  ',1); p=R/relp; chk(p.exists(),f'map missing {relp}'); chk(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==h,f'map changed {relp}')
print(f'PASS31.19 tests: skills={len(player["skills"])} bank={len(player["bank"])} inventory={len(player["inventory"])} equipment={len(player["equipment"])} recipes={len(recipes["recipes"])} js={len(list(S.rglob("*.js")))} errors={len(errors)}')
if errors:
 [print('FAIL:',e) for e in errors[:50]]; raise SystemExit(1)
