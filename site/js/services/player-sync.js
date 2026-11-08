import {Data} from '../core/data-service.js';
import {PlayerStore} from '../core/player-store.js';
const FORMAT_VERSION=2;let data=null,loadPromise=null,lastError=null;
function finite(value,label,min=Number.NEGATIVE_INFINITY){const n=Number(value);if(!Number.isFinite(n)||n<min)throw new Error(`Player snapshot ${label} is invalid`);return n;}
function validateRows(rows,label,validator){if(!Array.isArray(rows))throw new Error(`Player snapshot ${label} must be an array`);rows.forEach(validator);}
export function validateSnapshot(candidate){
 if(!candidate||typeof candidate!=='object'||Array.isArray(candidate))throw new Error('Player snapshot is not an object');
 if(Number(candidate.formatVersion)!==FORMAT_VERSION)throw new Error(`Unsupported player snapshot format: ${candidate.formatVersion}`);
 if(!candidate.player||typeof candidate.player!=='object'||Array.isArray(candidate.player))throw new Error('Player snapshot is missing player data');
 if(typeof candidate.player.name!=='string'||candidate.player.name.length>120)throw new Error('Player snapshot player.name is invalid');
 if(candidate.source!==undefined&&(!candidate.source||typeof candidate.source!=='object'||typeof candidate.source.character!=='string'||candidate.source.character.length>120))throw new Error('Player snapshot source is invalid');
 validateRows(candidate.skills,'skills',x=>{if(!x||typeof x!=='object'||typeof x.name!=='string'||!x.name.trim())throw new Error('Player snapshot skill row is invalid');finite(x.level??x.static,'skill level',1);finite(x.xp??x.experience,'skill xp',0);});
 validateRows(candidate.quests?.items,'quests.items',x=>{if(!x||typeof x!=='object'||typeof x.name!=='string'||typeof x.completed!=='boolean')throw new Error('Player snapshot quest row is invalid');});
 for(const key of ['inventory','bank','equipment']){
  if(candidate[key]!==undefined)validateRows(candidate[key],key,x=>{if(!x||typeof x!=='object')throw new Error(`Player snapshot ${key} row is invalid`);finite(x.id,`${key}.id`,0);finite(x.amount,`${key}.amount`,0);});
 }
 return candidate;
}
function applySnapshot(s){const skills={};for(const x of s.skills){const name=String(x.name||'').trim();if(!name)continue;const current=Math.max(1,Number(x.level??x.static??1)||1);const xp=Math.max(0,Number(x.xp??x.experience)||0);skills[name]={current,target:PlayerStore.getSkill(name)?.target||current,xp};}const completed=s.quests.items.filter(q=>q?.completed===true).map(q=>q.name).filter(Boolean);PlayerStore.update(p=>({...p,name:s.player.name||p.name||'Player',skills,quests:{...p.quests,questPoints:Math.max(0,Number(s.player.questPoints??s.quests?.questPoints??0)||0),completed},sync:{loaded:true,source:s.source?.character||'2009Scape',syncedAt:s.source?.syncedAt||null}}));data=s;lastError=null;}
/** Apply a validated external snapshot (imported save) without fetching player-sync.json. */
export function applyExternalSnapshot(snapshot){const s=validateSnapshot(snapshot);applySnapshot(s);return s;}
export async function load({force=false}={}){if(loadPromise&&!force)return loadPromise;loadPromise=(async()=>{
  // Prefer a remembered / imported save when present.
  try{
    const {SaveImport}=await import('./save-import.js');
    const remembered=await SaveImport.loadRememberedSave({forceFileRead:true});
    if(remembered?.snapshot){return remembered.snapshot;}
  }catch(e){console.warn('[Gielinor Wayfinder] save-import probe failed',e);}
  return Data.get('player-sync.json',{force}).then(validateSnapshot).then(s=>{applySnapshot(s);return s});
})().catch(e=>{lastError=e;throw e}).finally(()=>{loadPromise=null});return loadPromise;}
export const getData=()=>data,getError=()=>lastError,getQuests=()=>data?.quests?.items||[],getSkills=()=>data?.skills||[],getPlayer=()=>{const p=PlayerStore.get();return {name:p.name||data?.player?.name||'Player',totalXP:Number(data?.player?.totalXP||Object.values(p.skills||{}).reduce((n,s)=>n+Number(s?.xp||0),0)),questPoints:Number(p.quests?.questPoints||0),skills:Object.fromEntries(Object.entries(p.skills||{}).map(([k,v])=>[k,Number(v?.current??v?.level??1)])),completedQuests:(p.quests?.completed||[]).map(q=>q?.name??q),synced:p.sync?.loaded===true,readOnly:data?.source?.readOnly===true,syncedAt:p.sync?.syncedAt||data?.source?.syncedAt||null}};
export const getSkill=name=>getSkills().find(s=>String(s.name).toLowerCase()===String(name).toLowerCase()||String(s.name).toLowerCase()===({ranged:'range',runecrafting:'runecrafting'}[String(name).toLowerCase()]||''))||null,getSkillLevel=name=>Number(getSkill(name)?.level||1),getSkillXP=name=>Number(getSkill(name)?.xp||0),getQuestPoints=()=>Number(PlayerStore.get()?.quests?.questPoints||0),isQuestCompleted=name=>PlayerStore.isQuestCompleted(name),getCompletedQuests=()=>getQuests().filter(q=>q.completed===true),getInventory=()=>data?.inventory||[],getBank=()=>data?.bank||[],getEquipment=()=>data?.equipment||[],getLocation=()=>data?.location||null,getSlayer=()=>data?.slayer||{},getDiaries=()=>data?.achievementDiaries||[],isLoaded=()=>data!==null;
export const OSRSSync={load,getData,getError,getPlayer,getSkills,getSkill,getSkillLevel,getSkillXP,getQuests,getQuestPoints,isQuestCompleted,getCompletedQuests,getInventory,getBank,getEquipment,getLocation,getSlayer,getDiaries,isLoaded,validateSnapshot,applyExternalSnapshot};
