import { Player } from "../core/player-service.js";
const skillValue=(name)=>{const s=Player.getSkill(name);return Number(s?.current??s?.level??s??1);};
export const Requirements=Object.freeze({
 evaluate(req){
  if(!req||!req.type)return {met:true,missing:null};
  if(req.type==="skill"){const current=skillValue(req.skill),required=Number(req.level||0);return {met:current>=required,missing:current<required?{type:"skill",skill:req.skill,current,required,missing:required-current,boostable:!!req.boostable}:null};}
  if(req.type==="quest"){const met=Player.isQuestCompleted(req.name);return {met,missing:met?null:{type:"quest",name:req.name}};}
  if(req.type==="quest_points"){const current=Number(Player.get()?.quests?.questPoints||0),required=Number(req.level||0);return {met:current>=required,missing:current<required?{type:"quest_points",current,required,missing:required-current}:null};}
  if(req.type==="combat"){const current=Number(Player.get()?.combatLevel||0),required=Number(req.level||0);return {met:current>=required,missing:current<required?{type:"combat",current,required,missing:required-current}:null};}
  return {met:true,missing:null};
 },
 evaluateAll(reqs=[]){const results=reqs.map(r=>this.evaluate(r));return {met:results.every(x=>x.met),results,missing:results.filter(x=>!x.met).map(x=>x.missing)};}
});
