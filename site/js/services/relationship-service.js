import {Data} from '../core/data-service.js';

let indexPromise;
const shardCache=new Map();

async function loadIndex(){
  if(!indexPromise) indexPromise=Data.get('relationships/index.json');
  return indexPromise;
}
async function loadShard(path){
  if(!shardCache.has(path)) shardCache.set(path,Data.getGzipJson(path));
  return shardCache.get(path);
}
function normalizeRate(rate){
  const r=rate&&typeof rate==='object'?rate:{};
  const numerator=Number(r.numerator),denominator=Number(r.denominator);
  const exact=Number.isFinite(numerator)&&Number.isFinite(denominator)&&numerator>0&&denominator>0;
  return {
    status:r.status||'unknown',source:r.source||null,display:r.display||null,
    numerator:exact?numerator:null,denominator:exact?denominator:null,
    approximate:Boolean(r.approximate),reason:r.reason||null,
    evidencePage:r.evidencePage||null,resolution:r.resolution||null,
    sourcePolicy:r.sourcePolicy||null
  };
}
function mapDrop(x){
  const rate=normalizeRate(x.rate);
  return {
    id:x.itemId,name:x.itemName,itemId:x.itemId,itemName:x.itemName,
    monsterId:x.monsterId,monsterName:x.monsterName,quantity:x.quantity,
    source:x.source,status:x.status,dropTypes:x.dropTypes||[],
    categories:x.categories||[],
    rate:rate.status==='authoritative'||rate.status==='fallback'?(rate.numerator>0?rate.denominator:null):null,
    rateDisplay:rate.display,rateNumerator:rate.numerator,rateDenominator:rate.denominator,
    rateSource:rate.source,rateStatus:rate.status,rateReason:rate.reason,
    rateApproximate:rate.approximate,rateResolution:rate.resolution,
    rateEvidencePage:rate.evidencePage,rateSourcePolicy:rate.sourcePolicy,dropRate:rate
  };
}
async function monsterDrops(id){
  const index=await loadIndex(),path=index.monsters?.[String(Number(id))];
  if(!path)return [];
  const shard=await loadShard(path);
  return (shard.relationships||[]).map(mapDrop);
}
async function itemDrops(id){
  const index=await loadIndex(),path=index.items?.[String(Number(id))];
  if(!path)return [];
  const shard=await loadShard(path);
  return (shard.relationships||[]).map(mapDrop);
}
export const Relationships=Object.freeze({
  monsterDrops(monster){return monsterDrops(Number(monster?.id??monster));},
  itemDrops(item){return itemDrops(Number(item?.id??item));},
  itemSources(item){return itemDrops(Number(item?.id??item));},
  async firstMonsterWithExactRate(monsters=[]){
    const index=await loadIndex(),ids=new Set(index.exactRateMonsters||[]);
    return monsters.find(x=>ids.has(String(x.id)))||null;
  },
  related(type,id){
    if(type==='monster')return monsterDrops(id);
    if(type==='item')return itemDrops(id);
    return Promise.resolve([]);
  },
  clear:()=>{indexPromise=null;shardCache.clear();}
});
