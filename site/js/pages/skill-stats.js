import { OSRS } from "../core/osrs.js";
import { Player } from "../core/player-service.js";

const skills=[
"Attack","Strength","Defence","Ranged","Prayer","Magic","Runecraft",
"Construction","Hitpoints","Agility","Herblore","Thieving","Crafting",
"Fletching","Slayer","Hunter","Mining","Smithing","Fishing","Cooking",
"Firemaking","Woodcutting","Farming"
];

const S=document.getElementById("skill");
const C=document.getElementById("current");
const T=document.getElementById("target");
const X=document.getElementById("xpAction");
const A=document.getElementById("actions");
const R=document.getElementById("result");
const M=document.getElementById("methods");

skills.forEach(x=>{
 let o=document.createElement("option");
 o.textContent=x;o.value=x;S.appendChild(o);
});

function xpForLevel(level){
 if(level<=1)return 0;
 let total=0;
 for(let i=1;i<level;i++)
  total+=Math.floor(i+300*Math.pow(2,i/7));
 return Math.floor(total/4);
}

function timeText(hours){
 if(!Number.isFinite(hours))return "—";
 let mins=Math.ceil(hours*60);
 let d=Math.floor(mins/1440);
 mins%=1440;
 let h=Math.floor(mins/60);
 let m=mins%60;
 return (d?d+"d ":"")+(h?h+"h ":"")+m+"m";
}

function fmt(n){
 return Number.isFinite(n)?
 n.toLocaleString(undefined,{maximumFractionDigits:2}):"—";
}

function calc(){
 let cur=Math.max(1,Math.min(99,Number(C.value)||1));
 let tar=Math.max(1,Math.min(99,Number(T.value)||1));
 if(tar<cur)tar=cur;

 let curXP=xpForLevel(cur);
 let tarXP=xpForLevel(tar);
 let remaining=Math.max(0,tarXP-curXP);
 let per=Number(X.value)||0;
 let perHour=Number(A.value)||0;

 let actions=per>0?Math.ceil(remaining/per):Infinity;
 let xpHour=per*perHour;
 let hours=xpHour>0?remaining/xpHour:Infinity;
 let progress=tarXP>curXP?
   ((curXP-tarXP+remaining)/remaining):1;

 progress=tarXP>0?Math.min(100,(curXP/tarXP)*100):100;

 OSRS.setHTML(R, `
 <div class="card">
 <h2 class="result-heading">${S.value}: ${cur} → ${tar}</h2>

 <div class="grid">
  <div class="stat">Current XP<b>${fmt(curXP)}</b></div>
  <div class="stat">Target XP<b>${fmt(tarXP)}</b></div>
  <div class="stat">XP remaining<b>${fmt(remaining)}</b></div>
  <div class="stat">Actions required<b>${fmt(actions)}</b></div>
  <div class="stat">XP / hour<b>${fmt(xpHour)}</b></div>
  <div class="stat">Estimated time<b>${timeText(hours)}</b></div>
 </div>

 <div class="small result-note">
 Progress toward target
 </div>
 <div class="bar"><div class="fill" data-progress-fill></div></div>
 <div class="small result-percent">${progress.toFixed(2)}%</div>
 </div>`);
 const fill = R.querySelector("[data-progress-fill]");
 if (fill) fill.style.width = `${progress}%`;
}

[S,C,T,X,A].forEach(x=>{
 x.addEventListener("input",calc);
 x.addEventListener("change",calc);
});

calc();

/* Training methods: 2009Scape-derived rows from the offline data files (gathering, thieving, agility, hunter, farming). */
const METHOD_FILES={Woodcutting:"gathering.json",Mining:"gathering.json",Fishing:"gathering.json",Firemaking:"gathering.json",
 Thieving:"thieving.json",Agility:"agility.json",Hunter:"hunter.json",Farming:"farming.json"};
let itemNames=null;
async function nameOf(id){
 if(!itemNames){
  try{const index=await OSRS.Data.get("items/name-index.json");itemNames=new Map(Object.entries(index).map(([n,i])=>[i,n]));}
  catch{itemNames=new Map();}
 }
 const n=itemNames.get(id);
 if(n)return n.charAt(0).toUpperCase()+n.slice(1);
 try{const item=await OSRS.Data.get(`items/${id}.json`);if(item&&item.name)return item.name;}catch{}
 return `Item ${id}`;
}
async function methodRows(skill,doc){
 const rows=[];
 const add=(name,level,xp,note)=>{if(Number.isFinite(xp)&&xp>0)rows.push({name,level:Number.isFinite(level)?level:1,xp,note:note||""});};
 if(skill==="Thieving"){
  doc.pickpockets.forEach(r=>add(r.name+" (pickpocket)",r.level,r.xp));
  doc.stalls.forEach(r=>add(r.name,r.level,r.xp));
  doc.chests.forEach(r=>add(r.name+" chest",r.level,r.xp));
 }else if(skill==="Agility"){
  doc.courses.forEach(r=>add(r.name+" (per lap)",r.level,r.completionXp+r.obstacleXp,r.levelNote||""));
  doc.shortcuts.forEach(r=>add(r.name+" (shortcut)",r.level,r.xp));
 }else if(skill==="Hunter"){
  doc.traps.forEach(r=>add(r.name,r.level,r.xp,r.trap.replace(/_/g," ").toLowerCase()));
  doc.butterflies.forEach(r=>add(r.name,r.level,r.xp,"butterfly net"));
  doc.implings.forEach(r=>add(r.name,r.level,r.xp,"impling"));
  doc.falconry.forEach(r=>add(r.name,r.level,r.xp,"falconry"));
  doc.tracking.forEach(r=>add(r.name,r.level,r.xp,"tracking"));
  doc.pitfalls.forEach(r=>add(r.name,r.level,r.xp,"pit trap"));
 }else if(skill==="Farming"){
  doc.crops.forEach(r=>add(r.name.replace(/ seed$/i,""),r.level,(r.plantingXp||0)+(r.harvestXp||0),"plant + one harvest, "+r.patchType.replace(/_/g," ").toLowerCase()+(r.growthMinutes?", "+r.growthMinutes+" min":"")));
 }else{
  const list=doc.skills[skill]||[];
  for(const r of list)add(r.name||await nameOf(r.itemId),r.level,r.xp,r.option||"");
 }
 return rows.sort((a,b)=>a.level-b.level||a.xp-b.xp);
}
const docs=new Map();
let methodToken=0;
async function showMethods(){
 if(!M)return;
 const skill=S.value,token=++methodToken,file=METHOD_FILES[skill];
 if(!file){M.replaceChildren();return;}
 let rows;
 try{
  if(!docs.has(file))docs.set(file,await OSRS.Data.get(file));
  rows=await methodRows(skill,docs.get(file));
 }catch{
  if(token===methodToken)OSRS.setHTML(M,'<div class="card small">Training methods are not available offline yet.</div>');
  return;
 }
 if(token!==methodToken)return;
 const level=Math.max(1,Number(C.value)||1);
 const body=rows.map(r=>`<tr class="${r.level<=level?"ok":"locked"}" data-xp="${r.xp}"><td>${OSRS.escapeHTML(r.name)}</td><td>${r.level}</td><td>${fmt(r.xp)}</td><td class="small">${OSRS.escapeHTML(r.note)}</td></tr>`).join("");
 OSRS.setHTML(M,`<div class="card"><h2 class="result-heading">${skill} training methods</h2>
 <div class="small">From the 2009Scape server source. Tap a row to use its XP as the XP per action. Greyed rows need a higher level than your current level.</div>
 <div class="table-wrap"><table class="methods"><thead><tr><th>Method</th><th>Level</th><th>XP</th><th></th></tr></thead><tbody>${body}</tbody></table></div></div>`);
}
if(M){
 M.addEventListener("click",e=>{
  const row=e.target.closest("tr[data-xp]");
  if(!row)return;
  X.value=row.dataset.xp;
  calc();
 });
 S.addEventListener("change",()=>{showMethods();});
 C.addEventListener("input",()=>{M.querySelectorAll("tr[data-xp]").forEach(r=>{r.className=Number(r.children[1].textContent)<=(Number(C.value)||1)?"ok":"locked";});});
 try{const saved=Player.getSkill(S.value);if(saved&&Number(saved.current)>0&&Number(saved.current)<=99){C.value=saved.current;calc();}}catch{}
 showMethods();
}
