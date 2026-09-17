import {OfflineStore} from './offline-store.js';
const cache=new Map(),inflight=new Map();
const ROOT='data/';
function pathOf(path){return String(path).replace(/^\/+/, '').replace(/\.\.\//g,'');}
async function safeGet(key){try{return await OfflineStore.get(key);}catch{return null;}}
function safeSet(key,value){void OfflineStore.set(key,value).catch(()=>{});}
async function fetchJson(path,force){
  const r=await fetch(ROOT+path,{cache:force?'no-store':'default'});
  if(!r.ok)throw new Error(`Data request failed: ${path} (${r.status})`);
  return r.json();
}
async function fetchGzipJson(path){
  const r=await fetch(ROOT+path,{cache:'default'});
  if(!r.ok)throw new Error(`Compressed data request failed: ${path} (${r.status})`);
  const bytes=await r.arrayBuffer();
  if(typeof DecompressionStream==='undefined')throw new Error('Gzip decompression is not supported by this browser.');
  const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  return JSON.parse(await new Response(stream).text());
}
async function request(path,{force=false}={}){
 path=pathOf(path);
 if(!force&&cache.has(path))return cache.get(path);
 if(!force&&inflight.has(path))return inflight.get(path);
 const p=(async()=>{
  let networkError=null;
  try{const value=await fetchJson(path,force);cache.set(path,value);safeSet(`json:${path}`,value);return value;}
  catch(error){networkError=error;}
  const saved=await safeGet(`json:${path}`);
  if(saved!==null){cache.set(path,saved);return saved;}
  throw networkError||new Error(`Unable to load data: ${path}`);
 })();
 inflight.set(path,p);
 try{return await p;}finally{inflight.delete(path);}
}
async function requestGzip(path,{force=false}={}){
 path=pathOf(path);const key=`gzip:${path}`;
 if(!force&&cache.has(key))return cache.get(key);
 if(!force&&inflight.has(key))return inflight.get(key);
 const p=(async()=>{
  let networkError=null;
  try{const value=await fetchGzipJson(path);cache.set(key,value);safeSet(key,value);return value;}
  catch(error){networkError=error;}
  const saved=await safeGet(key);
  if(saved!==null){cache.set(key,saved);return saved;}
  throw networkError||new Error(`Unable to load compressed data: ${path}`);
 })();
 inflight.set(key,p);
 try{return await p;}finally{inflight.delete(key);}
}
export const Data=Object.freeze({
 get:(path,options)=>request(path,options),
 getGzipJson:(path,options)=>requestGzip(path,options),
 list:(name,options)=>request(`${name}/index.json`,options),
 itemNameIndex:(options)=>request('items/name-index.json',options),
 searchIndex:(options)=>request('knowledge/search-index.json',options),
 relationships:(options)=>request('knowledge/index.json',options),
 manifest:(options)=>request('catalog-manifest.json',options),
 prefetch:(paths,options)=>Promise.all(paths.map(p=>request(p,options))),
 clear:()=>cache.clear(),
 invalidate:path=>cache.delete(pathOf(path)),
 stats:()=>({entries:cache.size,inflight:inflight.size,paths:[...cache.keys()]})
});
