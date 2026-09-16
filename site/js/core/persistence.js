import {Storage} from './storage.js';
const PREFIX='osrsGuide:';
export const Persistence=Object.freeze({
 get(key,fallback=null){return Storage.jsonGet(PREFIX+key,fallback)},
 set(key,value){Storage.jsonSet(PREFIX+key,value);return value},
 remove(key){Storage.remove(PREFIX+key)},
 clear(){for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k?.startsWith(PREFIX))localStorage.removeItem(k)}},
 export(){const out={formatVersion:1,createdAt:new Date().toISOString(),data:{}};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k?.startsWith(PREFIX))out.data[k.slice(PREFIX.length)]=Storage.jsonGet(k,null)}return out},
 import(snapshot){if(!snapshot||snapshot.formatVersion!==1||!snapshot.data||typeof snapshot.data!=='object')throw new Error('Invalid OSRS Guide backup');for(const [k,v] of Object.entries(snapshot.data))this.set(k,v);return true}
});
