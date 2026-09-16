import {Data} from '../core/data-service.js';
const BASE='wiki/pass31.13/';
const cache=new Map();
async function get(path){ if(cache.has(path)) return cache.get(path); const p=Data.get(BASE+path); cache.set(path,p); return p; }
async function entity(type,id){
  if(!['items','equipment','monsters'].includes(type)||id==null)return null;
  try{return await get(`entities/${type}/${encodeURIComponent(id)}.json`);}catch{return null;}
}
async function relationships(){return get('relationships/drops.json');}
async function recipes(){return get('relationships/recipes.json');}
export const Wiki=Object.freeze({
  entity,
  async item(id){return entity('items',id)},
  async monster(id){return entity('monsters',id)},
  async equipment(id){return entity('equipment',id)},
  relationships,
  recipes,
  clear:()=>cache.clear()
});
