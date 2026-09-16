import {Data} from './data-service.js';
import {normalize} from './utils.js';
let quests=null,loadPromise=null,byId=new Map(),nameIndex=new Map();
function rebuild(list){byId=new Map();nameIndex=new Map();for(const q of list){if(!q||typeof q!=='object')continue;if(q.id!=null)byId.set(String(q.id),q);for(const n of [q.name,q.shortName])if(n)nameIndex.set(normalize(n),q);}}
export async function load(force=false){if(quests&&!force)return quests;if(loadPromise&&!force)return loadPromise;loadPromise=Data.get('quests.json',{force}).then(list=>{if(!Array.isArray(list))throw new Error('Quest database is not an array');quests=list.filter(q=>q&&typeof q==='object');rebuild(quests);return quests;}).finally(()=>{loadPromise=null});return loadPromise;}
export function all(){return quests||[];}
export function get(id){return byId.get(String(id))||null;}
export function byName(name){return nameIndex.get(normalize(name))||null;}
export function search(query,limit=250){const q=normalize(query);if(!q)return all().slice(0,limit);return all().filter(x=>normalize(`${x.name||''} ${x.shortName||''} ${x.series||''}`).includes(q)).slice(0,limit);}
export function clear(){quests=null;loadPromise=null;byId.clear();nameIndex.clear();}
export const Quests=Object.freeze({load,all,get,byName,search,clear});
