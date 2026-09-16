import {Storage} from "./storage.js";
import {Events} from "./events.js";
export const PLAYER_KEY="osrsPlayer";
export const PLAYER_SCHEMA_VERSION=4;
export const DEFAULT_PLAYER=Object.freeze({version:PLAYER_SCHEMA_VERSION,skills:{},quests:{completed:[],questPoints:0},goals:[],settings:{members:false},sync:{loaded:false,source:null,syncedAt:null}});
let state;const listeners=new Set();
const clone=v=>structuredClone(v);
function fresh(){return clone(DEFAULT_PLAYER)}
function migrate(raw){
 const p=raw&&typeof raw==="object"?raw:{}; const completed=Array.isArray(p.quests?.completed)?p.quests.completed:Array.isArray(p.completedQuests)?p.completedQuests:[];
 return {...fresh(),...p,version:PLAYER_SCHEMA_VERSION,skills:{...(p.skills||{})},quests:{...fresh().quests,...(p.quests||{}),completed:[...new Map(completed.map(q=>[String(q?.name??q).trim().toLowerCase(),q])).values()]},goals:Array.isArray(p.goals)?p.goals:[],settings:{...fresh().settings,...(p.settings||{})},sync:{...fresh().sync,...(p.sync||{})}};
}
function emit(){const snap=clone(state);for(const fn of listeners){try{fn(snap)}catch(e){console.error("[OSRS Guide] player subscriber",e)}}Events.emit("player:changed",snap)}
function persist(){Storage.jsonSet(PLAYER_KEY,state)}
export function load(){if(state)return clone(state);const raw=Storage.jsonGet(PLAYER_KEY,null);state=migrate(raw);persist();return clone(state)}
export function get(){return load()}
export function set(next){state=migrate(next);persist();emit();return get()}
export function update(fn){return set(fn(get())||get())}
export function reset(){state=fresh();persist();emit();return get()}
export function subscribe(fn){listeners.add(fn);return()=>listeners.delete(fn)}
export function getSkill(name){const s=load().skills,wanted=String(name).trim().toLowerCase(),key=Object.keys(s).find(k=>String(k).toLowerCase()===wanted||(wanted==="ranged"&&String(k).toLowerCase()==="range")||(wanted==="runecrafting"&&String(k).toLowerCase()==="runecraft"));return key?s[key]:null}
export function getSkills(){return clone(load().skills)}
export function setSkill(name,current,target=current,xp=undefined){return update(p=>({...p,skills:{...p.skills,[name]:{...(p.skills[name]||{}),current:Math.max(1,Number(current)||1),target:Math.max(1,Number(target)||Number(current)||1),...(xp===undefined?{}:{xp:Math.max(0,Number(xp)||0)})}}}))}
export function updateSkills(skills){return update(p=>({...p,skills:{...p.skills,...skills}}))}
export function isQuestCompleted(name){const n=String(name).trim().toLowerCase();return load().quests.completed.some(q=>String(q?.name??q).trim().toLowerCase()===n)}
export function setQuestCompleted(name,completed=true){return update(p=>{const key=String(name).trim().toLowerCase(),rows=p.quests.completed.filter(q=>String(q?.name??q).trim().toLowerCase()!==key);if(completed)rows.push(name);return {...p,quests:{...p.quests,completed:rows}}})}
export function setQuestPoints(points){return update(p=>({...p,quests:{...p.quests,questPoints:Math.max(0,Number(points)||0)}}))}
export function getGoals(){return clone(load().goals)}
export function addGoal(goal){return update(p=>({...p,goals:[...p.goals,{...goal,id:goal?.id??crypto.randomUUID?.()??String(Date.now()),created:goal?.created??Date.now()}]}))}
export function removeGoal(idOrIndex){return update(p=>({...p,goals:p.goals.filter((g,i)=>g?.id===idOrIndex?false:i!==idOrIndex)}))}
export const PlayerStore={load,get,set,update,reset,subscribe,getSkill,getSkills,setSkill,updateSkills,isQuestCompleted,setQuestCompleted,setQuestPoints,getGoals,addGoal,removeGoal};
