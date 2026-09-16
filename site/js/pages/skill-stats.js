import { OSRS } from "../core/osrs.js";

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
