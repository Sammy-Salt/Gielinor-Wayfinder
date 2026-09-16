import {Data} from "../core/data-service.js";
import {Search} from "./search-service.js";
const configs=Object.freeze({items:"items",monsters:"monsters",npcs:"npcs"});
const lists=new Map();
export const Catalog=Object.freeze({
 async list(type){ if(!configs[type])throw new Error(`Unknown catalog: ${type}`); if(!lists.has(type)) lists.set(type,Data.list(configs[type])); return lists.get(type); },
 async get(type,id){ if(!configs[type])throw new Error(`Unknown catalog: ${type}`); if(id==null||id==="")throw new Error(`Missing ${type} id`); return Data.get(`${configs[type]}/${encodeURIComponent(id)}.json`); },
 async search(type,q,limit=250){ const rows=await Catalog.list(type); const fields=["name","shortName","examine"]; return Search.filter(Search.buildIndex(rows,fields),q,limit); },
 clear(){lists.clear();Search.clear()}
});
