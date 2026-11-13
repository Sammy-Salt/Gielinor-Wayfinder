import { Player } from "../core/player-service.js";
import { Quests } from "../core/quest-service.js";
import { OSRSSync } from "../services/player-sync.js";

const skills=["Attack","Strength","Defence","Ranged","Prayer","Magic","Runecrafting","Construction","Hitpoints","Agility","Herblore","Thieving","Crafting","Fletching","Slayer","Hunter","Mining","Smithing","Fishing","Cooking","Firemaking","Woodcutting","Farming","Summoning"];
function renderSkills(){
  const data=Player.getSkills(); let total=0,tracked=0;
  for(const name of skills){const entry=data[name]||data[Object.keys(data).find(k=>k.toLowerCase()===name.toLowerCase())];const level=Math.max(1,Number(entry?.current??entry?.level??1));total+=level;if(entry&&level>1)tracked++;}
  document.getElementById("totalLevel")?.replaceChildren(String(total));
  document.getElementById("averageLevel")?.replaceChildren((total/skills.length).toFixed(1));
  document.getElementById("trackedSkills")?.replaceChildren(String(tracked));
}
async function renderQuests(){
  const list=await Quests.load(); const completed=new Set(Player.get().quests.completed.map(String));
  let done=0,qp=0; for(const q of list){if(completed.has(String(q.name))||completed.has(String(q.id))){done++;qp+=Number(q.questPoints)||0;}}
  const pct=list.length?Math.round(done/list.length*100):0;
  document.getElementById("questsDone")?.replaceChildren(String(done));
  document.getElementById("questTotal")?.replaceChildren(String(list.length));
  document.getElementById("questPoints")?.replaceChildren(String(Player.get().quests.questPoints||qp));
  document.getElementById("questPercent")?.replaceChildren(`${pct}%`);
  const fill=document.getElementById("questFill");if(fill)fill.style.width=`${pct}%`;
}
function renderGoals(){
  const container=document.getElementById("goals");if(!container)return;container.replaceChildren();
  const goals=Player.getGoals(); if(!goals.length){container.append("No goals yet.",document.createElement("br"),"Open Goal Planner to create one.");return;}
  for(const goal of goals.slice(0,5)){const div=document.createElement("div");div.className="goal";const t=document.createElement("div");t.className="goal-title";t.textContent=`${goal.name||"Goal"}`;const d=document.createElement("div");d.className="goal-details";d.textContent=goal.details||"Personal OSRS goal";div.append(t,d);container.append(div);}
}
(async()=>{try{await OSRSSync.load();}catch(e){console.warn(e);}renderSkills();renderGoals();await renderQuests();})().catch(error=>{console.error(error);const el=document.getElementById("questsDone");if(el)el.textContent="—";});
