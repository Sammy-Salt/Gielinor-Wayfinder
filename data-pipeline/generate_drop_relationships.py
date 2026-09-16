#!/usr/bin/env python3
"""Build the canonical monster->item drop relationship dataset.

Relationship existence comes from the local 2009Scape-derived relationship graph.
OSRS Wiki is secondary evidence used only to enrich an existing relationship with
an unambiguous published probability. Conflicting/approximate Wiki rates remain
unavailable. Ragger is intentionally not read.
"""
import json, re
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
GRAPH=json.loads((SITE/'data/knowledge/index.json').read_text())
WIKI=json.loads((SITE/'data/wiki/pass31.13/relationships/drops.json').read_text())
OUT=SITE/'data/relationships/monster-drops.json'

# Index local game-data entities for stable names.
entities={(e.get('type'), int(e['id'])): e for e in GRAPH.get('entities',[]) if str(e.get('id','')).isdigit()}

# Parse Wiki evidence by exact monster/item pair. A pair is usable only when all
# retained exact evidence agrees. Approximate Wiki rows are not calculator rates.
# The Wiki snapshot uses its own identity layer, so a secondary evidence row is
# also eligible when its monster/item names each resolve to exactly one local
# 2009Scape entity. This is deterministic identity resolution, not fuzzy matching.
wiki=defaultdict(list)
for mid_s, rows in (WIKI.get('byMonster') or {}).items():
    try: mid=int(mid_s)
    except Exception: continue
    for row in rows or []:
        try: iid=int(row.get('itemId'))
        except Exception: continue
        src=row.get('source') or {}
        if not isinstance(src, dict):
            continue
        raw=src.get('drop_json')
        if not raw: continue
        try: dj=json.loads(raw)
        except Exception: continue
        rarity=str(dj.get('Rarity') or '').strip()
        approx=bool(dj.get('Approx'))
        if approx or not rarity or rarity in {'-', 'N/A', 'n/a'}: continue
        m=re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*/\s*([\d,]+(?:\.\d+)?)\s*', rarity)
        if not m: continue
        num=float(m.group(1)); den=float(m.group(2).replace(',',''))
        if not (num>0 and den>0): continue
        wiki[(mid,iid)].append({
            'display': rarity,
            'numerator': num,
            'denominator': den,
            'approximate': False,
            'source': 'OSRS Wiki',
            'page': src.get('page_name') or src.get('page_name_sub'),
            'quantity': {'min': dj.get('Quantity Low'), 'max': dj.get('Quantity High')}
        })

# Build deterministic exact-name indexes for secondary evidence.
def normalize_name(value):
    return re.sub(r'[^a-z0-9]+', ' ', str(value or '').lower()).strip()

monster_name_ids=defaultdict(list)
item_name_ids=defaultdict(list)
for (etype,eid), entity in entities.items():
    key=normalize_name(entity.get('name'))
    if not key:
        continue
    if etype == 'monster':
        monster_name_ids[key].append(eid)
    elif etype == 'item':
        item_name_ids[key].append(eid)

# A second index lets us safely map Wiki evidence when the Wiki snapshot's
# numeric IDs differ from the local 2009Scape IDs. Ambiguous names are skipped.
wiki_name_evidence=defaultdict(list)
for mid_s, rows in (WIKI.get('byMonster') or {}).items():
    for row in rows or []:
        src=row.get('source') or {}
        if not isinstance(src, dict):
            continue
        raw=src.get('drop_json')
        if not raw:
            continue
        try:
            dj=json.loads(raw)
        except Exception:
            continue
        mname=normalize_name(dj.get('Dropped from') or src.get('page_name') or src.get('page_name_sub'))
        iname=normalize_name(dj.get('Dropped item') or src.get('item_name'))
        mids=monster_name_ids.get(mname,[])
        iids=item_name_ids.get(iname,[])
        if len(mids)==1 and len(iids)==1:
            wiki_name_evidence[(mids[0],iids[0])].append(row)

def same(a,b):
    return abs(float(a)-float(b)) <= max(1e-12, abs(float(a))*1e-12)

def parse_wiki_rows(rows):
    evidence=[]
    for row in rows or []:
        src=row.get('source') or {}
        if not isinstance(src, dict):
            continue
        raw=src.get('drop_json')
        if not raw:
            continue
        try: dj=json.loads(raw)
        except Exception: continue
        rarity=str(dj.get('Rarity') or '').strip()
        approx=bool(dj.get('Approx'))
        if approx or not rarity or rarity in {'-', 'N/A', 'n/a'}: continue
        m=re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*/\s*([\d,]+(?:\.\d+)?)\s*', rarity)
        if not m: continue
        num=float(m.group(1)); den=float(m.group(2).replace(',',''))
        if not (num>0 and den>0): continue
        evidence.append({
            'display': rarity, 'numerator': num, 'denominator': den,
            'approximate': False, 'source': 'OSRS Wiki',
            'page': src.get('page_name') or src.get('page_name_sub')
        })
    if not evidence: return None
    first=evidence[0]
    if any(not same(x['numerator'],first['numerator']) or not same(x['denominator'],first['denominator']) for x in evidence[1:]):
        return {'status':'conflict','source':'OSRS Wiki','reason':'Conflicting exact Wiki rates were found.'}
    return {'status':'fallback','source':'OSRS Wiki','display':first['display'],
            'numerator':first['numerator'], 'denominator':first['denominator'],
            'approximate':False, 'evidencePage':first['page'], 'sourcePolicy':'secondary'}

def wiki_rate(mid,iid):
    direct=wiki.get((mid,iid),[])
    rate=parse_wiki_rows(direct)
    if rate: return rate
    named=wiki_name_evidence.get((mid,iid),[])
    rate=parse_wiki_rows(named)
    if rate and rate.get('status')=='fallback':
        rate['resolution']='exact-unique-name'
    elif rate and rate.get('status')=='conflict':
        rate['resolution']='exact-unique-name'
    return rate


records=[]
seen=set()
for edge in GRAPH.get('edges',[]):
    if not isinstance(edge,list) or len(edge)<3 or edge[2] != 'drops': continue
    a,b=edge[0],edge[1]
    if not (str(a).startswith('monster:') and str(b).startswith('item:')):
        if str(b).startswith('monster:') and str(a).startswith('item:'): a,b=b,a
        else: continue
    try: mid=int(str(a).split(':',1)[1]); iid=int(str(b).split(':',1)[1])
    except Exception: continue
    key=(mid,iid)
    if key in seen: continue
    seen.add(key)
    me=entities.get(('monster',mid),{})
    ie=entities.get(('item',iid),{})
    wr=wiki_rate(mid,iid)
    rec={
        'relationshipType':'monster_drop',
        'monsterId':mid,
        'monsterName':me.get('name') or f'Monster {mid}',
        'itemId':iid,
        'itemName':ie.get('name') or f'Item {iid}',
        'quantity':None,
        'source':'2009Scape',
        'status':'authoritative',
        'rate':wr or {'status':'unknown','source':None,'reason':'No trusted exact probability is available in the current 2009Scape relationship export.'}
    }
    if wr and wr.get('status')=='fallback':
        rec['rate']['sourcePolicy']='secondary'
    records.append(rec)

records.sort(key=lambda r:(r['monsterId'],r['itemId']))
by_monster=defaultdict(list)
by_item=defaultdict(list)
for r in records:
    by_monster[str(r['monsterId'])].append(r)
    by_item[str(r['itemId'])].append(r)

data={
 'formatVersion':2,
 'generatedFrom':'local 2009Scape-derived relationship graph + OSRS Wiki secondary probability evidence',
 'policy':'2009Scape relationship existence is authoritative; OSRS Wiki may enrich only an existing relationship with one unambiguous exact published rate; conflicts/approximate rates remain unknown; retired third-party source excluded',
 'relationshipCount':len(records),
 'rateSummary':{
   'authoritative2009ScapeRates':0,
   'wikiFallbackRates':sum(1 for r in records if r['rate'].get('status')=='fallback'),
   'conflictingWikiRates':sum(1 for r in records if r['rate'].get('status')=='conflict'),
   'unknownRates':sum(1 for r in records if r['rate'].get('status')=='unknown')
 },
 'byMonster':dict(by_monster),
 'relationshipsByItem':dict(by_item),
 'relationships':records
}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
print(json.dumps({'relationships':len(records),**data['rateSummary']},indent=2))
