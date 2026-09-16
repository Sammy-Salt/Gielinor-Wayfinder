import {Catalog} from './catalog-service.js';
function normalizeRows(rows){return (Array.isArray(rows)?rows:[]).map(x=>({name:x?.name||x?.location||'Unknown location',x:Number(x?.x),y:Number(x?.y),plane:Number(x?.plane??0)})).filter(x=>Number.isFinite(x.x)&&Number.isFinite(x.y));}
export async function get(type,id){const key=type==='boss'?'monsters':type;const data=await Catalog.get(key,id);return {entity:data,locations:normalizeRows(data?.locations)};}
export function mapHref(){return 'map.html';}
export const Locations=Object.freeze({get,mapHref});
