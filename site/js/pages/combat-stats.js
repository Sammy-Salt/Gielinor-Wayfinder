import { OSRS } from "../core/osrs.js";
import { Catalog } from "../services/catalog-service.js";
import { calculate } from "../calculators/combat.js";

const M=document.getElementById("monster"),S=document.getElementById("style"),
AT=document.getElementById("attack"),PO=document.getElementById("power"),
AB=document.getElementById("attBonus"),SB=document.getElementById("strBonus"),
MH=document.getElementById("maxHit"),SP=document.getElementById("speed"),R=document.getElementById("result");

const fmt=n=>Number.isFinite(Number(n))?Number(n).toLocaleString(undefined,{maximumFractionDigits:2}):"—";
const pct=n=>Number.isFinite(Number(n))?(Number(n)*100).toLocaleString(undefined,{maximumFractionDigits:2})+"%":"—";
let monsters=[];
let selectedMonster=null;

function selected(){
  const id=String(M?.value||"");
  selectedMonster=monsters.find(x=>String(x.id)===id)||null;
  return selectedMonster;
}
function defence(monster){
  if(!monster)return 1;
  if(S.value==="ranged")return Number(monster.range_level??monster.defence_level??1);
  if(S.value==="magic")return Number(monster.magic_level??monster.defence_level??1);
  return Number(monster.defence_level??1);
}
function calc(){
  const monster=selected(); if(!monster){R.replaceChildren();return;}
  const result=calculate({monster,style:S.value,attack:AT.value,power:PO.value,attackBonus:AB.value,strengthBonus:SB.value,weaponMax:MH.value,speed:SP.value});
  OSRS.setHTML(R,`<div class="card"><h2 class="result-heading">${OSRS.escapeHTML(monster.name)}</h2><div class="small">Monster ID: ${OSRS.escapeHTML(monster.id)} · Defence used: ${fmt(result.defence)}</div><div class="grid result-grid"><div class="stat">Attack accuracy<b>${pct(result.accuracy)}</b></div><div class="stat">Approx. max hit<b>${fmt(result.maxHit)}</b></div><div class="stat">Average hit<b>${fmt(result.avgHit)}</b></div><div class="stat">Approx. DPS<b>${fmt(result.dps)}</b></div><div class="stat">Kills / hour<b>${fmt(result.killsPerHour)}</b></div><div class="stat">Combat XP / hour<b>${fmt(result.xpHour)}</b></div><div class="stat">Monster HP<b>${fmt(result.hp)}</b></div><div class="stat">Attack speed<b>${result.ticks} ticks</b></div></div><p class="small">⚠️ Approximate calculator; gear effects, prayers, special attacks, defence reductions and other mechanics are not included.</p></div>`);
}
function choose(){selected();calc();}
async function init(){
  try{
    monsters=(await Catalog.list("monsters")).filter(x=>Number.isFinite(Number(x.id))).sort((a,b)=>String(a.name||"").localeCompare(String(b.name||"")));
    M.replaceChildren();
    const first=document.createElement("option");first.value="";first.textContent="Select a monster…";M.appendChild(first);
    for(const x of monsters){const o=document.createElement("option");o.value=String(x.id);o.textContent=`${x.name||"Unknown"} (ID: ${x.id})`;M.appendChild(o)}
    if(monsters.length)M.value=String(monsters[0].id);
    choose();
  }catch(error){console.error("Combat calculator data load failed",error);R.textContent="Unable to load monster data."}
}
M.addEventListener("change",choose);
[S,AT,PO,AB,SB,MH,SP].forEach(x=>{x.addEventListener("input",calc);x.addEventListener("change",calc)});
init();
