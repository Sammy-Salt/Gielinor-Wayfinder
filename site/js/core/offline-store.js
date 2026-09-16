const DB_NAME='osrs-guide-cache';
const DB_VERSION=2;
const STORE='records';
let dbPromise;
function open(){if(dbPromise)return dbPromise;dbPromise=new Promise((resolve,reject)=>{if(!globalThis.indexedDB)return resolve(null);const req=indexedDB.open(DB_NAME,DB_VERSION);req.onupgradeneeded=()=>{const db=req.result;if(!db.objectStoreNames.contains(STORE))db.createObjectStore(STORE,{keyPath:'key'});};req.onsuccess=()=>resolve(req.result);req.onerror=()=>{dbPromise=null;reject(req.error)};});return dbPromise;}
export const OfflineStore=Object.freeze({
 async get(key){const db=await open();if(!db)return null;return new Promise((resolve,reject)=>{const r=db.transaction(STORE,'readonly').objectStore(STORE).get(String(key));r.onsuccess=()=>resolve(r.result?.value??null);r.onerror=()=>reject(r.error);});},
 async set(key,value){const db=await open();if(!db)return value;return new Promise((resolve,reject)=>{const r=db.transaction(STORE,'readwrite').objectStore(STORE).put({key:String(key),value});r.onsuccess=()=>resolve(value);r.onerror=()=>reject(r.error);});},
 async remove(key){const db=await open();if(!db)return;return new Promise((resolve,reject)=>{const r=db.transaction(STORE,'readwrite').objectStore(STORE).delete(String(key));r.onsuccess=resolve;r.onerror=()=>reject(r.error);});},
 available:()=>Boolean(globalThis.indexedDB)
});
