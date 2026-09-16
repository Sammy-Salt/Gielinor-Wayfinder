import {Knowledge} from './knowledge-service.js';
export async function sourcesForItem(id,limit=25){return (await Knowledge.related('item',id,{limit:limit*3})).filter(x=>x.relation==='drops').slice(0,limit).map(x=>x.entity);}
export async function dropsForMonster(id,limit=100){return (await Knowledge.related('monster',id,{limit})).filter(x=>x.relation==='drops').map(x=>x.entity);}
export const Acquisition=Object.freeze({sourcesForItem,dropsForMonster});
