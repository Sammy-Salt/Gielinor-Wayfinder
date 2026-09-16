import {Data} from '../core/data-service.js';

let dropPromise;

async function loadCanonicalDrops(){
  if(!dropPromise) dropPromise=Data.get('relationships/monster-drops.json');
  return dropPromise;
}

function normalizeRate(rate){
  const r=rate&&typeof rate==='object'?rate:{};
  const numerator=Number(r.numerator);
  const denominator=Number(r.denominator);
  const exact=Number.isFinite(numerator)&&Number.isFinite(denominator)&&numerator>0&&denominator>0;
  return {
    status:r.status||'unknown',
    source:r.source||null,
    display:r.display||null,
    numerator:exact?numerator:null,
    denominator:exact?denominator:null,
    approximate:Boolean(r.approximate),
    reason:r.reason||null,
    evidencePage:r.evidencePage||null,
    resolution:r.resolution||null
  };
}

function mapDrop(x){
  const rate=normalizeRate(x.rate);
  return {
    id:x.itemId,
    name:x.itemName,
    itemId:x.itemId,
    itemName:x.itemName,
    monsterId:x.monsterId,
    monsterName:x.monsterName,
    quantity:x.quantity,
    source:x.source,
    status:x.status,
    rate:rate.status==='fallback'&&rate.denominator!=null?rate.denominator:null,
    rateDisplay:rate.display,
    rateNumerator:rate.numerator,
    rateDenominator:rate.denominator,
    rateSource:rate.source,
    rateStatus:rate.status,
    rateReason:rate.reason,
    rateApproximate:rate.approximate,
    rateResolution:rate.resolution,
    rateEvidencePage:rate.evidencePage,
    dropRate:rate
  };
}

export const Relationships=Object.freeze({
  async monsterDrops(monster){
    const mid=Number(monster?.id??monster);
    const d=await loadCanonicalDrops();
    return (d.byMonster?.[String(mid)]||[]).map(mapDrop);
  },
  async itemDrops(item){
    const iid=Number(item?.id??item);
    const d=await loadCanonicalDrops();
    const rows=d.relationshipsByItem?.[String(iid)];
    if(Array.isArray(rows)) return rows.map(mapDrop);
    return (d.relationships||[]).filter(x=>Number(x.itemId)===iid).map(mapDrop);
  },
  async itemSources(item){
    return this.itemDrops(item);
  },
  async firstMonsterWithExactRate(monsters=[]){
    const d=await loadCanonicalDrops();
    const ids=new Set();
    for(const [id,rows] of Object.entries(d.byMonster||{})){
      if((rows||[]).some(x=>{const r=normalizeRate(x.rate);return r.status==='fallback'&&r.denominator!=null&&!r.approximate;})) ids.add(String(id));
    }
    return monsters.find(x=>ids.has(String(x.id)))||null;
  },
  async related(type,id){
    const d=await loadCanonicalDrops();
    if(type==='monster') return this.monsterDrops(id);
    if(type==='item') return this.itemDrops(id);
    return [];
  },
  clear:()=>{dropPromise=null;}
});
