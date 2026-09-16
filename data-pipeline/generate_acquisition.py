#!/usr/bin/env python3
import json,re,glob
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
ITEMS=SITE/'data/items'
INDEX=json.loads((ITEMS/'index.json').read_text())

def norm(s): return re.sub(r'[^a-z0-9]+',' ',str(s).lower()).strip()

by_name=defaultdict(list)
for rec in INDEX:
    by_name[norm(rec.get('name',''))].append(int(rec['id']))

shops_by_item=defaultdict(list)
for p in glob.glob(str(SITE/'data/npcs/*.json')):
    try: d=json.loads(Path(p).read_text())
    except Exception: continue
    if not isinstance(d,dict): continue
    for shop in d.get('shops',[]) or []:
        if not isinstance(shop,dict): continue
        for entry in shop.get('items',[]) or []:
            if not isinstance(entry,dict): continue
            ids=by_name.get(norm(entry.get('item_name','')),[])
            # Only publish an item-shop relationship when exact normalized name is unique.
            if len(ids)!=1: continue
            item_id=ids[0]
            shops_by_item[item_id].append({
                'shopId': shop.get('id'),
                'shopName': shop.get('name'),
                'location': shop.get('location'),
                'owner': shop.get('owner'),
                'members': shop.get('members'),
                'shopType': shop.get('shop_type'),
                'stock': entry.get('stock'),
                'restock': entry.get('restock'),
                'sellPrice': entry.get('sell_price'),
                'buyPrice': entry.get('buy_price'),
                'source': '2009Scape',
                'status': 'authoritative'
            })

# Wiki drops are secondary only. Keep only relationships already resolved by the trusted Wiki identity layer.
wiki_path=SITE/'data/wiki/pass31.13/relationships/drops.json'
wiki=json.loads(wiki_path.read_text())
monsters_dir=SITE/'data/monsters'
wiki_drops=defaultdict(list)
for item_key, rows in (wiki.get('byItem') or {}).items():
    try: item_id=int(item_key)
    except: continue
    if not (ITEMS/f'{item_id}.json').exists(): continue
    for row in rows or []:
        if not isinstance(row,dict): continue
        src=row.get('source') or {}
        mid=src.get('monsterId', row.get('monsterId'))
        try: mid=int(mid)
        except: continue
        if not (monsters_dir/f'{mid}.json').exists(): continue
        name=src.get('page_name') or src.get('page_name_sub') or f'Monster {mid}'
        drop_json=src.get('drop_json')
        rarity=None; approximate=None; quantity=None
        if drop_json:
            try:
                dj=json.loads(drop_json)
                rarity=dj.get('Rarity')
                approximate=dj.get('Approx')
                quantity={'min':dj.get('Quantity Low'),'max':dj.get('Quantity High')}
            except Exception: pass
        wiki_drops[item_id].append({
            'monsterId':mid,
            'name':name,
            'quantity':quantity,
            'rarity':rarity,
            'approximate':approximate,
            'source':'OSRS Wiki',
            'status':'fallback'
        })

for item_id in [int(r['id']) for r in INDEX]:
    p=ITEMS/f'{item_id}.json'
    d=json.loads(p.read_text())
    shops=shops_by_item.get(item_id,[])
    # deterministic de-duplication
    seen=set(); shops=[x for x in shops if not ((k:=(x.get('shopId'),x.get('shopName'),x.get('location')) ) in seen or seen.add(k))]
    drops=wiki_drops.get(item_id,[])
    seen=set(); unique=[]
    for x in drops:
        q=x.get('quantity') or {}
        k=(x.get('monsterId'),x.get('name'),x.get('rarity'),q.get('min'),q.get('max'))
        if k not in seen:
            seen.add(k); unique.append(x)
    drops=unique
    d['_acquisition']={
        'schemaVersion':1,
        'policy':'2009Scape-primary; OSRS-Wiki-secondary; unresolved=unknown',
        'shops':shops,
        'monsterDrops':drops,
        'groundSpawns':{'status':'unknown','source':'2009Scape','reason':'No trusted ground-spawn catalog is present in this release.'}
    }
    p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')

print(f'Generated acquisition data for {len(INDEX)} items; 2009Scape shops={sum(map(len,shops_by_item.values()))}; Wiki fallback drops={sum(map(len,wiki_drops.values()))}')
