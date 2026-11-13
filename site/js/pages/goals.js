import { Player } from "../core/player-service.js";
import { createTextElement } from "../core/utils.js";

function renderGoals() {
  const list = document.getElementById("goalList");
  if (!list) return;
  list.replaceChildren();
  const goals = Player.getGoals();
  if (!goals.length) { list.appendChild(createTextElement("div", "No goals yet.", "empty")); return; }
  const fragment = document.createDocumentFragment();
  goals.forEach((goal,index) => {
    const card=createTextElement("div","","goal-card");
    card.appendChild(createTextElement("div",goal.name||"Unnamed Goal","goal-name"));
    if(goal.details) card.appendChild(createTextElement("div",goal.details,"goal-details"));
    if(goal.sourceQuest){const source=createTextElement("div","","goal-source");source.append("From quest: ",goal.sourceQuest);card.appendChild(source);}
    if(goal.type==="skill"&&goal.skill){
      const skill=Player.getSkill(goal.skill), current=Math.max(0,Number(skill?.current??goal.current??1)), target=Math.max(1,Number(goal.target)||1);
      const remaining=Math.max(0,target-current), pct=Math.min(100,current/target*100);
      const progress=createTextElement("div","","goal-progress"), summary=createTextElement("strong",`${current} / ${target}`);
      progress.append(summary,remaining>0?` — ${remaining} level${remaining===1?"":"s"} remaining`:" — Complete");
      const bar=createTextElement("div","","bar"),fill=createTextElement("div","","fill");fill.style.width=`${pct}%`;fill.setAttribute("role","progressbar");fill.setAttribute("aria-valuenow",String(Math.round(pct)));fill.setAttribute("aria-valuemin","0");fill.setAttribute("aria-valuemax","100");bar.append(fill);progress.append(bar);card.append(progress);
    }
    const button=createTextElement("button","Delete","delete-btn");button.type="button";button.addEventListener("click",()=>{Player.removeGoal(index);renderGoals();});card.append(button);fragment.append(card);
  });
  list.append(fragment);
}

document.getElementById("addGoal")?.addEventListener("click",()=>{
  const name=document.getElementById("goalName"),details=document.getElementById("goalDetails");
  if(!name?.value.trim()){name?.focus();return;}
  Player.addGoal({type:"custom",name:name.value.trim(),details:details?.value.trim()||"",created:Date.now()});
  name.value=""; if(details) details.value=""; renderGoals();
});
renderGoals();

import {Planner} from '../services/planner-service.js';
const planBtn=document.getElementById('planQuestBtn');
planBtn?.addEventListener('click',async()=>{const input=document.getElementById('questPlanName'),out=document.getElementById('questPlanResult');const name=input?.value.trim();if(!name){input?.focus();return;}out.textContent='Planning…';try{const p=await Planner.quest(name);if(!p){out.textContent='Quest not found.';return;}out.replaceChildren();const h=document.createElement('strong');h.textContent=`${p.quest.name}: ${p.ready?'Ready now':'Requirements remaining'}`;out.append(h);const parts=[...p.skills.map(x=>`${x.skill} ${x.current}/${x.required}`),...p.quests.slice(0,8).map(x=>`Quest: ${x.name}`)];if(p.questPoints)parts.push(`Quest Points: ${p.questPoints}`);const ul=document.createElement('ul');for(const x of parts){const li=document.createElement('li');li.textContent=x;ul.append(li);}if(parts.length)out.append(ul);const add=document.createElement('button');add.type='button';add.textContent='Add quest as goal';add.onclick=()=>{Player.addGoal({type:'quest',name:p.quest.name,sourceQuest:p.quest.name,details:parts.length?`Missing: ${parts.join(', ')}`:'Ready to start'});renderGoals();};out.append(add);}catch(e){out.textContent='Quest planner unavailable.';}});
