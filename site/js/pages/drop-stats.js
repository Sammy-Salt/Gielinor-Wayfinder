import { OSRS } from "../core/osrs.js";
import { Catalog } from "../services/catalog-service.js";
import { Drops } from "../services/drop-service.js";
const M=document.getElementById("monster"),D=document.getElementById("drop"),K=document.getElementById("kills"),T=document.getElementById("target"),R=document.getElementById("result");
let monsters=[];let requestId=0;
const fmt=n=>Number.isFinite(Number(n))?Number(n).toLocaleString(undefined,{maximumFractionDigits:4}):"—";
const pct=n=>Number.isFinite(Number(n))?(Number(n)*100).toLocaleString(undefined,{maximumFractionDigits:4})+"%":"—";
function binom(n,k){if(k<0||k>n)return 0;let x=1;for(let i=1;i<=k;i++)x*=((n-k+i)/i);return x}
function calc(){
 const o=D.selectedOptions[0];if(!o){R.replaceChildren();return}
 const num=Number(o.dataset.rateNumerator),den=Number(o.dataset.rateDenominator),probability=Drops.probability({rateNumerator:num,rateDenominator:den,rateStatus:o.dataset.rateStatus,rateApproximate:o.dataset.rateApproximate==="true"}),r=probability&&probability>0?1/probability:NaN,n=Math.max(1,Number(K.value)||1),target=Math.max(1,Number(T.value)||1);
 if(!Number.isFinite(r)||r<=0){OSRS.setHTML(R,'<div class="card"><div class="warn">No trusted exact drop rate is available for this relationship. Conflicting, approximate, variable, and unknown rates are intentionally not calculated.</div></div>');return}
 const p=probability,q=1-p,none=Math.pow(q,n),one=n*p*Math.pow(q,n-1),expected=n*p,variance=n*p*q,std=Math.sqrt(variance),atLeast=1-none;
 const exactTarget=target<=n?binom(n,target)*Math.pow(p,target)*Math.pow(q,n-target):0;
 const milestones=[.1,.25,.5,.75,.9,.95,.99].map(x=>q===0?1:Math.ceil(Math.log(1-x)/Math.log(q)));
 const targetKills=Math.ceil(target/p);
 OSRS.setHTML(R,`<div class="card"><h2 class="result-heading">${OSRS.escapeHTML(o.dataset.item)}</h2><div class="small">${OSRS.escapeHTML(o.dataset.monster)} · Monster ID: ${OSRS.escapeHTML(M.value)}</div><div class="small">Rate source: ${OSRS.escapeHTML(o.dataset.rateSource||"unknown")}</div>
 <div class="grid"><div class="stat">Drop rate<b>${OSRS.escapeHTML(Drops.rateDisplay({rateNumerator:Number(o.dataset.rateNumerator),rateDenominator:Number(o.dataset.rateDenominator),rateStatus:o.dataset.rateStatus,rateApproximate:o.dataset.rateApproximate==="true"})||"Rate unavailable")}</b></div><div class="stat">Chance per kill<b>${pct(p)}</b></div><div class="stat">Expected drops<b>${fmt(expected)}</b></div><div class="stat">Expected kills<b>${fmt(r)}</b></div><div class="stat">Chance of ≥1<b>${pct(atLeast)}</b></div><div class="stat">Chance of 0<b>${pct(none)}</b></div><div class="stat">Exactly 1<b>${pct(one)}</b></div>${target===1?"":`<div class="stat">Exactly ${target}<b>${pct(exactTarget)}</b></div>`}<div class="stat">Variance<b>${fmt(variance)}</b></div><div class="stat">Std. deviation<b>${fmt(std)}</b></div></div>
 <h3>Chance milestones</h3><div class="grid">${milestones.map((v,i)=>`<div class="stat">${[10,25,50,75,90,95,99][i]}%<b>${fmt(v)} kills</b></div>`).join("")}<div class="stat">Target ${target} drops<b>~${fmt(targetKills)} kills</b></div></div></div>`);
}
async function chooseMonster(){
 const req=++requestId,id=String(M.value);D.replaceChildren();R.replaceChildren();
 const base=monsters.find(x=>String(x.id)===id);if(!base)return;
 const loading=document.createElement("option");loading.textContent="Loading drops…";loading.disabled=true;D.appendChild(loading);
 try{const m=await Catalog.get("monsters",id);if(req!==requestId||String(M.value)!==id)return;const drops=await OSRS.Relationships.monsterDrops(m.id);D.replaceChildren();drops.sort((a,b)=>Number(Drops.isExactRate(b))-Number(Drops.isExactRate(a))||String(a.itemName||a.name||"").localeCompare(String(b.itemName||b.name||"")));
  if(!drops.length){const o=document.createElement("option");o.textContent="No drops available";o.disabled=true;D.appendChild(o);return}
  for(const x of drops){const o=document.createElement("option");o.dataset.rateNumerator=x.rateNumerator??"";o.dataset.rateDenominator=x.rateDenominator??"";o.dataset.rateDisplay=x.rateDisplay??"";o.dataset.rateSource=x.rateSource??"";o.dataset.rateStatus=x.rateStatus??"unknown";o.dataset.rateApproximate=String(Boolean(x.rateApproximate));o.dataset.item=x.itemName||x.name||"Unknown";o.dataset.monster=m.name||base.name;o.textContent=`${x.itemName||x.name||"Unknown"} — ${Drops.rateLabel(x)}`;D.appendChild(o)}
  D.selectedIndex=0;calc();
 }catch(error){console.error("Drop data load failed",error);D.replaceChildren();const o=document.createElement("option");o.textContent="Could not load drops";o.disabled=true;D.appendChild(o);OSRS.setHTML(R,'<div class="card"><div class="warn">Could not load this monster\'s drop table.</div></div>')}
}
async function init(){try{monsters=(await Catalog.list("monsters")).filter(x=>Number.isFinite(Number(x.id))).sort((a,b)=>String(a.name||"").localeCompare(String(b.name||"")));M.replaceChildren();const first=document.createElement("option");first.value="";first.textContent="Select a monster…";M.appendChild(first);for(const x of monsters){const o=document.createElement("option");o.value=String(x.id);o.textContent=`${x.name||"Unknown"} (ID: ${x.id})`;M.appendChild(o)}if(monsters.length){const preferred=await OSRS.Relationships.firstMonsterWithExactRate(monsters);M.value=String((preferred||monsters[0]).id);await chooseMonster()}}catch(error){console.error("Drop statistics data load failed",error);M.replaceChildren();const o=document.createElement("option");o.textContent="Unable to load monsters";o.disabled=true;M.appendChild(o)}}
M.addEventListener("change",chooseMonster);D.addEventListener("change",calc);[K,T].forEach(x=>{x.addEventListener("input",calc);x.addEventListener("change",calc)});document.getElementById("calc")?.addEventListener("click",calc);init();
