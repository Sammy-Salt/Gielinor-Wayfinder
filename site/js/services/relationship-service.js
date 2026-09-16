import {Knowledge} from './knowledge-service.js';
import {Data} from '../core/data-service.js';
let dropPromise;
async function loadCanonicalDrops(){
  if(!dropPromise) dropPromise=Data.get('relationships/monster-drops.json');
  return dropPromise;
}
export const Relationships=Object.freeze({
 async monsterDrops(monster){
  const mid=Number(monster?.id??monster);
  const d=await loadCanonicalDrops();
  const rows=d.byMonster?.[String(mid)]||[];
  return rows.map(x=>{
    const rate=x.rate||{};
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
      rate:rate.status==='fallback' && Number.isFinite(Number(rate.denominator)) && Number(rate.denominator)>0
        ? Number(rate.denominator) : null,
      rateDisplay:rate.display||null,
      rateNumerator:rate.numerator??null,
      rateDenominator:rate.denominator??null,
      rateSource:rate.source??null,
      rateStatus:rate.status||'unknown',
      rateReason:rate.reason||null,
      rateApproximate:Boolean(rate.approximate)
    };
  });
 },
 async itemSources(item){return (await Knowledge.related('item',item?.id??item,{limit:500})).filter(x=>x.relation==='drops').map(x=>({id:x.entity.id,name:x.entity.name,monsterId:x.entity.id}));},
 async related(type,id){return Knowledge.related(type,id)},
 clear:()=>{Knowledge.clear();dropPromise=null;}
});
