import {Quests} from '../core/quest-service.js';
import {Player} from '../core/player-service.js';
import {Requirements} from './requirements-service.js';
const key=v=>String(v??'').trim().toLowerCase();
let dependents;
function ensureDependents(){if(dependents)return dependents;dependents=new Map();for(const q of Quests.all()){for(const r of q.requirements||[]){if(r?.type!=='quest')continue;const k=key(r.name);if(!dependents.has(k))dependents.set(k,[]);dependents.get(k).push(q);}}return dependents;}
function questByName(name){return Quests.byName(name)||Quests.search(name,1)[0]||null;}
function checkQuest(input){const quest=typeof input==='string'?questByName(input):input;if(!quest)return {quest:null,ready:false,blocked:true,completed:false,missingSkills:[],missingQuests:[],missingQuestPoints:0,requiredQuestPoints:0,currentQuestPoints:Number(Player.get()?.quests?.questPoints||0),requirements:[]};const requirements=Array.isArray(quest.requirements)?quest.requirements:[],result=Requirements.evaluateAll(requirements),missingSkills=result.missing.filter(x=>x?.type==='skill'),missingQuests=result.missing.filter(x=>x?.type==='quest'),qp=result.missing.find(x=>x?.type==='quest_points'),completed=Player.isQuestCompleted(quest.name);return {quest,ready:result.met&&!completed,blocked:!result.met&&!completed,completed,missingSkills,missingQuests,missingQuestPoints:qp?.missing||0,requiredQuestPoints:qp?.required||0,currentQuestPoints:Number(Player.get()?.quests?.questPoints||0),requirements};}
export const OSRSQuestEngine=Object.freeze({quests:()=>Quests.all(),getQuest:questByName,getRequirements:q=>Array.isArray(q?.requirements)?q.requirements:[],getPlayer:()=>Player.get(),getSkillLevel:name=>Number(Player.getSkill(name)?.current??Player.getSkill(name)?.level??1),getQuestPoints:()=>Number(Player.get()?.quests?.questPoints||0),getCompletedQuests:()=>Player.get()?.quests?.completed||[],isQuestCompleted:name=>Player.isQuestCompleted(name),checkQuest,
 collectMissingRequirements(name){const r=checkQuest(name);return {skills:r.missingSkills,quests:r.missingQuests,questPoints:r.missingQuestPoints};},
 buildQuestTree(name){const root=questByName(name),seen=new Set(),steps=[];const walk=q=>{if(!q||seen.has(key(q.name)))return;seen.add(key(q.name));for(const req of q.requirements||[])if(req?.type==='quest')walk(questByName(req.name));steps.push(q);};walk(root);return {quest:root,steps};},
 buildPlan(name){const tree=this.buildQuestTree(name),missing=this.collectMissingRequirements(name);return {...tree,...missing,ready:Boolean(tree.quest&&checkQuest(tree.quest).ready),dependents:tree.quest?(ensureDependents().get(key(tree.quest.name))||[]):[]};},
 dependents(name){return ensureDependents().get(key(name))||[];},clear(){dependents=null;}
});
