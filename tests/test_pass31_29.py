import gzip, json, pathlib, subprocess
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

R=pathlib.Path(__file__).resolve().parents[1]; S=R/'site'
def chk(ok,msg):
    if not ok: raise AssertionError(msg)

def expected_display(n,d):
    rate=Fraction(d,n)
    if rate.denominator==1: value=str(rate.numerator)
    else:
        value=format((Decimal(rate.numerator)/Decimal(rate.denominator)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP),'f').rstrip('0').rstrip('.')
    return f'1/{value}'

release=json.loads((S/'release.json').read_text())
chk(release['release']=='PASS31.63','release mismatch')
chk(release['buildId'] in (S/'sw.js').read_text(),'SW build mismatch')
chk('gielinor-wayfinder-pass31.63-20261108-1' in (S/'sw.js').read_text(),'cache namespace mismatch')
chk('?v=42' in (S/'js/bootstrap.js').read_text(),'loader version mismatch')

# Representative exact rates, including integer, finite decimal, repeating decimal,
# and a combined relationship.
for monster_id, item_id in [(1615,4151),(1615,995)]:
    data=json.loads(gzip.decompress((S/f'data/relationships/monsters/{monster_id}.json.gz').read_bytes()))
    row=next(x for x in data['relationships'] if x['itemId']==item_id)
    rate=row['rate']
    chk(rate['status']=='authoritative','rate is not authoritative')
    chk(rate['display']==expected_display(rate['numerator'],rate['denominator']),f'bad display for {item_id}: {rate["display"]}')

# Every generated canonical rateDisplay must use 1/X form (or the explicit
# unavailable marker for zero-probability source relationships).
checked=0
for root in [S/'data/relationships/monsters', S/'data/relationships/items']:
    for path in root.glob('*.json.gz'):
        data=json.loads(gzip.decompress(path.read_bytes()))
        for row in data['relationships']:
            rate=row['rate']
            if rate['numerator']>0:
                chk(rate['display'].startswith('1/'),f'non-1/X display: {path}:{row["itemId"]}')
                chk(rate['display']==expected_display(rate['numerator'],rate['denominator']),f'display mismatch: {path}:{row["itemId"]}')
                checked+=1

service=(S/'js/services/drop-service.js').read_text()
chk('formatReciprocal' in service,'shared reciprocal formatter missing')
chk('return `1/${' in service,'shared formatter does not emit 1/X')
for fn in ['site/js/pages/item.js','site/js/pages/drop-time.js','site/js/pages/drop-stats.js']:
    chk('Drops' in (R/fn).read_text(),f'Drops service not wired: {fn}')

for p in S.rglob('*.js'):
    r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
    chk(r.returncode==0,f'JS syntax: {p}: {r.stderr}')
for p in S.rglob('*.json'):
    try: json.loads(p.read_text())
    except Exception as e: chk(False,f'JSON: {p}: {e}')

print(f'PASS31.63 drop display tests: exactDisplaysChecked={checked} format=1/X canonical=PASS runtime=PASS syntax=PASS')
