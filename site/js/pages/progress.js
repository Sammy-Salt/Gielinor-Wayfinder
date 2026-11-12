import {OSRSSync} from '../services/player-sync.js';
import {ProgressService} from '../services/progress-service.js';
import {Progression} from '../services/progression-service.js';

const $=id=>document.getElementById(id);
const fmt=n=>Math.round(n).toLocaleString();
const SORT_KEY="wayfinder.progress.sort";
let sortMode="game";
try{sortMode=localStorage.getItem(SORT_KEY)||"game";}catch{}

function remaining(s){return Math.max(0,Progression.xpForLevel(s.target)-s.xp);}
function percent(s){return s.target<=1?100:Math.max(0,Math.min(100,(s.level-1)/(s.target-1)*100));}
function link(href,text){const a=document.createElement('a');a.href=href;a.textContent=text;return a;}

function sorted(skills){
  const list=skills.map((s,i)=>({...s,order:i}));
  const open=s=>s.target>s.level;
  if(sortMode==="lowest")list.sort((a,b)=>a.level-b.level||a.order-b.order);
  else if(sortMode==="closest")list.sort((a,b)=>(open(b)?0:1)-(open(a)?0:1)||remaining(a)-remaining(b)||a.order-b.order);
  else if(sortMode==="remaining")list.sort((a,b)=>remaining(b)-remaining(a)||a.order-b.order);
  return list;
}

function row(s){
  const el=document.createElement('div');el.className='skill-row'+(s.target<=s.level?' met':'');
  const name=document.createElement('a');name.className='skill-name';name.href='skill-stats.html?skill='+encodeURIComponent(s.display)+'&target='+encodeURIComponent(s.target);name.textContent=s.display;
  const lv=document.createElement('span');lv.className='skill-level';lv.textContent=s.level;
  const tl=document.createElement('label');tl.className='skill-target';tl.append('Target ');
  const ti=document.createElement('input');ti.type='number';ti.min=String(Math.max(1,s.level));ti.max='99';ti.value=s.target;ti.setAttribute('aria-label',s.display+' target level');
  ti.addEventListener('change',()=>{ProgressService.setTarget(s.lookup,ti.value);render();});tl.append(ti);
  const left=document.createElement('span');left.className='skill-left';
  left.textContent=s.target>s.level?fmt(remaining(s))+' XP to '+s.target:'Target met';
  const bar=document.createElement('div');bar.className='skill-bar';bar.setAttribute('aria-hidden','true');
  const fill=document.createElement('div');fill.className='skill-fill';fill.style.width=percent(s)+'%';bar.append(fill);
  el.append(name,lv,tl,left,bar);
  return el;
}

function render(){
  const container=$('skills');if(!container)return;
  const snap=Progression.snapshot();
  container.replaceChildren(...sorted(snap.skills).map(row));
  const set=(id,text)=>{const e=$(id);if(e)e.textContent=text;};
  set('totalLevel',String(snap.totalLevel));set('totalXP',fmt(snap.totalXP));set('questPoints',String(snap.questPoints));
  set('targetsMet',`${snap.targetsMet} / ${snap.skillCount}`);
  set('summaryText',`${snap.overall.toFixed(1)}% of skill targets reached`);
  const fill=$('summaryFill');if(fill)fill.style.width=snap.overall+'%';
  const next=snap.skills.filter(s=>s.target>s.level).sort((a,b)=>remaining(a)-remaining(b)).slice(0,3);
  const list=$('nextUp');list.replaceChildren();
  for(const s of next){
    const li=document.createElement('li');
    li.append(link('skill-stats.html?skill='+encodeURIComponent(s.display)+'&target='+encodeURIComponent(s.target),s.display),` ${s.level} → ${s.target}, ${fmt(remaining(s))} XP left`);
    list.append(li);
  }
  $('nextUpBox').hidden=!next.length;
}

async function initialize(){
  const status=$('syncStatus');
  try{await OSRSSync.load({force:true});if(status)status.textContent=`Save loaded: ${OSRSSync.getPlayer().name}`;}
  catch(e){console.warn(e);if(status)status.textContent='Using local player data';}
  render();
}

const sort=$('sortSkills');
if(sort){sort.value=sortMode;sort.addEventListener('change',()=>{sortMode=sort.value;try{localStorage.setItem(SORT_KEY,sortMode);}catch{}render();});}
$('resetTargetsBtn')?.addEventListener('click',()=>{if(confirm('Reset all skill targets to 99?')){ProgressService.clearTargets();render();}});
$('refreshSyncBtn')?.addEventListener('click',initialize);
initialize();
