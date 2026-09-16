import {Data} from '../core/data-service.js';
import {normalize} from '../core/utils.js';
let indexPromise;
const TYPE_LABEL={item:'Item',monster:'Monster',npc:'NPC',quest:'Quest',boss:'Boss'};
const TYPE_PATH={item:'item.html',monster:'monster.html',npc:'npc.html',quest:'quest.html',boss:'boss.html'};
async function load(){if(!indexPromise)indexPromise=Data.get('knowledge/search-index.json');return indexPromise;}
function score(row,q){const n=normalize(row.name),needle=normalize(q);if(n===needle)return 1000;if(n.startsWith(needle))return 700;if(n.includes(needle))return 500;if((row.aliases||[]).some(a=>normalize(a).includes(needle)))return 350;return 0;}
export const UniversalSearch=Object.freeze({
 async search(query,{limit=20,type=null}={}){const q=normalize(query);if(!q)return[];const rows=await load(),out=rows.filter(r=>!type||r.type===type).map(r=>({...r,_score:score(r,q)})).filter(r=>r._score>0).sort((a,b)=>b._score-a._score||String(a.name).localeCompare(String(b.name))).slice(0,limit);return out.map(r=>({...r,label:TYPE_LABEL[r.type]||r.type,path:TYPE_PATH[r.type]||'index.html'}));},
 warm:load,count:()=>0,clear:()=>{indexPromise=null}
});
