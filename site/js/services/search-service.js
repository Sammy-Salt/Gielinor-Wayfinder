import {normalize} from '../core/utils.js';
const indexes=new Map();
export function buildIndex(records,fields=['name']){return records.map(record=>({record,searchText:fields.map(f=>normalize(record?.[f])).filter(Boolean).join(' ')}));}
export function index(key,records,fields=['name']){const value=buildIndex(records,fields);indexes.set(key,value);return value;}
function score(text,needle){if(!needle)return 0;if(text===needle)return 1000;if(text.startsWith(needle))return 700;if(text.includes(` ${needle}`))return 600;if(text.includes(needle))return 500;const parts=needle.split(' ').filter(Boolean);if(parts.length>1&&parts.every(x=>text.includes(x)))return 350;return 0;}
export function filter(source,query,limit=Infinity){const needle=normalize(query),rows=Array.isArray(source)?source:(indexes.get(source)||[]),ranked=[];for(const entry of rows){const record=entry.record??entry,text=entry.searchText??normalize(record?.name),s=score(text,needle);if(!needle||s>0)ranked.push({record,score:s});}return ranked.sort((a,b)=>b.score-a.score||String(a.record?.name||'').localeCompare(String(b.record?.name||''))).slice(0,limit).map(x=>x.record);}
export function clear(){indexes.clear()}
export const Search=Object.freeze({normalize,buildIndex,index,filter,clear});
