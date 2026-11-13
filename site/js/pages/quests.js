import {Quests} from '../core/quest-service.js';
import {Player} from '../core/player-service.js';

let rows=[];
const key=v=>String(v??'').trim().toLowerCase();
const completed=()=>new Set((Player.get()?.quests?.completed||[]).map(q=>key(q?.name??q)));
function requirementState(q,done){
 const missing=[]; for(const r of Array.isArray(q.requirements)?q.requirements:[]){
  if(r?.type==='skill'){const s=Player.getSkill(r.skill),cur=Number(s?.current??s?.level??1);if(cur<Number(r.level||0))missing.push(`${r.skill}: ${cur}/${r.level}`);}
  else if(r?.type==='quest'&&!done.has(key(r.name)))missing.push(`Quest: ${r.name}`);
  else if(r?.type==='quest_points'){const cur=Number(Player.get()?.quests?.questPoints||0);if(cur<Number(r.level||0))missing.push(`Quest Points: ${cur}/${r.level}`);}
 } return missing;
}
function render(){
 const list=document.getElementById('questList'),filter=document.getElementById('filter'),summary=document.getElementById('summary');if(!list||!filter)return;
 const q="",f=filter.value,done=completed();
 const filtered=rows.filter(x=>{const match=!q||key(`${x.name} ${x.shortName} ${x.series}`).includes(q);if(!match)return false;const isDone=done.has(key(x.name));const missing=requirementState(x,done);return f==='completed'?isDone:f==='ready'?!isDone&&!missing.length:f==='blocked'?!isDone&&missing.length>0:true;});
 if(summary){summary.replaceChildren();const a=document.createElement('strong');a.textContent=`Quest database loaded`;const b=document.createElement('div');b.textContent=`Quest Points: ${Number(Player.get()?.quests?.questPoints||0)} • Completed: ${done.size} • Quests: ${rows.length}`;summary.append(a,b);}
 list.replaceChildren();if(!filtered.length){const e=document.createElement('div');e.className='empty';e.textContent='No quests available.';list.append(e);return;}
 const fgm=document.createDocumentFragment();for(const x of filtered){const isDone=done.has(key(x.name)),missing=requirementState(x,done);const card=document.createElement('article');card.className='quest-card'+(isDone?' completed':'');const a=document.createElement('a');a.className='quest-card-link';a.href=`quest.html?id=${encodeURIComponent(x.id)}`;const title=document.createElement('div');title.className='quest-title';title.textContent=x.name||'Unnamed Quest';const meta=document.createElement('div');meta.className='quest-meta';meta.textContent=`${x.difficulty||'Quest'} · ${Number(x.questPoints||0)} quest point${Number(x.questPoints||0)===1?'':'s'}`;a.append(title,meta);card.append(a);const status=document.createElement('div');status.className='quest-status '+(isDone?'complete':missing.length?'blocked':'ready');status.textContent=isDone?'Completed':missing.length?'Missing requirements':'Ready to start';card.append(status);if(missing.length){const req=document.createElement('div');req.className='quest-requirements';req.textContent=missing.slice(0,5).join(' • ')+(missing.length>5?` • +${missing.length-5} more`:'' );card.append(req);}fgm.append(card);}list.append(fgm);
}
async function initialize(){const debug=document.getElementById('questDebug');try{rows=await Quests.load(true);if(debug)debug.textContent=`Quest DB: LOADED • ${rows.length} quests`;document.getElementById('filter')?.addEventListener('change',render);render();}catch(e){console.error(e);if(debug)debug.textContent=`Quest DB: ERROR — ${e.message}`;const list=document.getElementById('questList');if(list){const x=document.createElement('div');x.className='empty';x.textContent='Unable to load the quest database. '+e.message;list.replaceChildren(x);}}}
initialize();
