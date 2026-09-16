import { OSRS } from "../core/osrs.js";
import { Catalog } from "../services/catalog-service.js";
import { Drops } from "../services/drop-service.js";


(async function(){
const M=document.getElementById("monster");
const D=document.getElementById("drop");
const K=document.getElementById("kph");
const R=document.getElementById("result");

const monsters=(await Catalog.list("monsters"))
.filter(x=>Number.isFinite(Number(x.id)))
.sort((a,b)=>(a.name||"").localeCompare(b.name||""));

/* esc() comes from js/core/utils.js (global.esc = escapeHTML), loaded before this file. */

const fmt=n=>Number.isFinite(n)?
n.toLocaleString(undefined,{maximumFractionDigits:2}):"—";

const pct=n=>Number.isFinite(n)?
(n*100).toLocaleString(undefined,{maximumFractionDigits:4})+"%":"—";

function time(seconds){
 if(!Number.isFinite(seconds))return "—";
 seconds=Math.max(0,Math.round(seconds));
 let d=Math.floor(seconds/86400); seconds%=86400;
 let h=Math.floor(seconds/3600); seconds%=3600;
 let m=Math.floor(seconds/60); let s=seconds%60;
 let out=[];
 if(d)out.push(d+"d");
 if(h)out.push(h+"h");
 if(m)out.push(m+"m");
 if(!d&&!h&&!m||s)out.push(s+"s");
 return out.join(" ");
}

function load(id){
 return Catalog.get("monsters",id);
}

function calc(){
 let o=D.selectedOptions[0];
 let numerator=Number(o?.dataset.rateNumerator);
 let denominator=Number(o?.dataset.rateDenominator);
 let p=Drops.probability({rateNumerator:numerator,rateDenominator:denominator,rateStatus:o?.dataset.rateStatus,rateApproximate:o?.dataset.rateApproximate==="true"});
 let r=p==null?null:1/p;
 let expectedKills=r;
 let kph=Math.max(1,Number(K.value)||1);

 if(r==null || r <= 0){
  OSRS.setHTML(R, '<div class="card"><div class="warn">⚠️ No trusted exact drop rate is available for this relationship. Conflicting, approximate, variable, and unknown rates are intentionally not calculated.</div></div>');
  return;
 }

 let expectedTime=expectedKills/kph*3600;

 let levels=[
  ["10%",.10],
  ["25%",.25],
  ["50%",.50],
  ["75%",.75],
  ["90%",.90],
  ["95%",.95],
  ["99%",.99]
 ];

 let rows=levels.map(x=>{
  let kills=Math.ceil(Math.log(1-x[1])/Math.log(1-p));
  return `<div class="stat">${x[0]} chance<b>${fmt(kills)} kills</b><span class="small">${time(kills/kph*3600)}</span></div>`;
 }).join("");

 OSRS.setHTML(R, `
 <div class="card">
 <h2 class="result-heading">${OSRS.escapeHTML(o.dataset.item)}</h2>
 <div class="small">${OSRS.escapeHTML(o.dataset.monster)} · Monster ID: ${OSRS.escapeHTML(o.dataset.id)}</div>
 <div class="small">Rate source: ${OSRS.escapeHTML(o.dataset.rateSource||"unknown")}</div>

 <div class="grid result-grid">
  <div class="stat">Drop rate<b>${OSRS.escapeHTML(o.dataset.rateDisplay||(`1 / ${fmt(1/r)}`))}</b></div>
  <div class="stat">Chance per kill<b>${pct(p)}</b></div>
  <div class="stat">Kills / hour<b>${fmt(kph)}</b></div>
  <div class="stat">Expected kills<b>${fmt(expectedKills)}</b></div>
  <div class="stat">Expected drops / hour<b>${fmt(kph*p)}</b></div>
  <div class="stat">Expected time<b>${time(expectedTime)}</b></div>
 </div>

 <h3>⏱️ Chance milestones</h3>
 <div class="grid">${rows}</div>

 <p class="small">
 These are probability estimates assuming independent rolls at the
 displayed drop rate. Only exact, unambiguous rates are calculated; unknown,
 conflicting, variable, and approximate rates remain unavailable.
 </p>
 </div>`);
}

let requestId=0;
async function choose(){
 let currentRequest=++requestId;
 let m=monsters[M.selectedIndex];
 if(!m)return;

 D.replaceChildren(Object.assign(document.createElement("option"), {textContent:"Loading drops..."}));

 try{
  let data=await load(m.id);
  if(currentRequest!==requestId)return;
  let drops=await OSRS.Relationships.monsterDrops(data.id||m.id);

  D.replaceChildren();
  drops.sort((a,b)=>Number(Drops.isExactRate(b))-Number(Drops.isExactRate(a))||String(a.itemName||a.name||"").localeCompare(String(b.itemName||b.name||"")));
  if (!drops.length) {
   D.appendChild(Object.assign(document.createElement("option"), {textContent:"No drops found"}));
  } else {
   for (const x of drops) {
    const option=document.createElement("option");
    option.dataset.rateNumerator=x.rateNumerator??"";
    option.dataset.rateDenominator=x.rateDenominator??"";
    option.dataset.rateSource=x.rateSource??"";
    option.dataset.rateStatus=x.rateStatus??"unknown";
    option.dataset.rateApproximate=String(Boolean(x.rateApproximate));
    option.dataset.rateDisplay=x.rateDisplay??"";
    option.dataset.item=x.itemName||x.name||"Unknown";
    option.dataset.monster=data.name||m.name;
    option.dataset.id=String(data.id||m.id);
    option.textContent=`${x.itemName||x.name||"Unknown"} — ${Drops.rateLabel(x)}`;
    D.appendChild(option);
   }
  }

  calc();
 }catch(e){
  D.replaceChildren(Object.assign(document.createElement("option"), {textContent:"Could not load drops"}));
  OSRS.setHTML(R, '<div class="card"><div class="warn">⚠️ Could not load this monster.</div></div>');
 }
}

monsters.forEach(x=>{
 let o=document.createElement("option");
 o.value=x.id;
 o.textContent=x.name+" (ID: "+x.id+")";
 M.appendChild(o);
});

M.onchange=choose;
D.onchange=calc;
K.oninput=calc;
K.onchange=calc;

const preferred=await OSRS.Relationships.firstMonsterWithExactRate(monsters);
if(preferred){M.value=String(preferred.id);await choose();}else choose();

})();
