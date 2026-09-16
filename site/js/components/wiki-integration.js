import {Wiki} from '../services/wiki-service.js';

function escText(v){return String(v??'');}
function card(title){const s=document.createElement('section');s.className='card wiki-integration-card';const h=document.createElement('h2');h.textContent=title;s.appendChild(h);return s;}
function line(label,value){if(value===undefined||value===null||value==='')return null;const d=document.createElement('div');d.className='row';const a=document.createElement('span');a.className='label';a.textContent=label;const b=document.createElement('span');b.className='value';b.textContent=escText(value);d.append(a,b);return d;}
function appendSourceSummary(section,records){
  const p=document.createElement('p');p.className='muted';p.textContent=`${records.length.toLocaleString()} verified Wiki snapshot record${records.length===1?'':'s'} linked by conservative identity resolution.`;section.appendChild(p);
  const details=document.createElement('details');const summary=document.createElement('summary');summary.textContent='Linked source records';details.appendChild(summary);
  for(const rec of records.slice(0,20)){
    const src=rec.source||{};const box=document.createElement('div');box.className='source-entry';
    const title=document.createElement('div');title.className='source-title';title.textContent=src.page_name_sub||src.page_name||src.name||src.item_name||'Wiki record';box.appendChild(title);
    const r=rec.resolution||{};const meta=document.createElement('div');meta.className='muted';meta.textContent=`${r.method||'resolved'} · confidence ${r.confidence??'—'}`;box.appendChild(meta);
    for(const [k,v] of Object.entries(src)){
      if(['page_name','page_name_sub','production_json','drop_json'].includes(k)||Array.isArray(v)||typeof v==='object')continue;
      const el=line(k.replaceAll('_',' '),v);if(el)box.appendChild(el);
    }
    details.appendChild(box);
  }
  if(records.length>20){const more=document.createElement('div');more.className='muted';more.textContent=`Showing 20 of ${records.length.toLocaleString()} linked records.`;details.appendChild(more);}
  section.appendChild(details);
}

async function appendDropSummary(section, type, id){
  try{
    const g=await Wiki.relationships();const rows=(type==='item'?g.byItem?.[String(id)]:g.byMonster?.[String(id)])||[];
    if(!rows.length)return;
    const details=document.createElement('details');const summary=document.createElement('summary');summary.textContent=`Verified Wiki-linked drops (${rows.length.toLocaleString()})`;details.appendChild(summary);
    for(const x of rows.slice(0,50)){
      const src=x.source||{};const d=document.createElement('div');d.className='source-entry';
      d.textContent=type==='item'?`${src.page_name||src.page_name_sub||'Monster'} · ${src.item_name||'Item'}`:`${src.item_name||'Item'} · ${src.page_name||src.page_name_sub||'Monster'}`;
      details.appendChild(d);
    }
    if(rows.length>50){const m=document.createElement('div');m.className='muted';m.textContent=`Showing 50 of ${rows.length.toLocaleString()} linked drops.`;details.appendChild(m);}
    section.appendChild(details);
  }catch{}
}

async function appendRecipeSummary(section,id){
  try{
    const g=await Wiki.recipes();const rows=(g.recipes||[]).filter(x=>x.output?.id===Number(id));
    if(!rows.length)return;
    const details=document.createElement('details');const summary=document.createElement('summary');summary.textContent=`Verified Wiki-linked production recipes (${rows.length})`;details.appendChild(summary);
    for(const x of rows){const d=document.createElement('div');d.className='source-entry';const names=(x.materials||[]).map(m=>`${m.quantity||''} ${m.name}`.trim()).join(', ');d.textContent=`${names||'Materials unavailable'} → ${x.source?.page_name_sub||x.source?.page_name||'Output'}`;details.appendChild(d);}
    section.appendChild(details);
  }catch{}
}

export async function appendWikiIntegration({type,id,target=document.getElementById('content')||document.querySelector('main')}={}){
  if(!target||!id||!['item','monster'].includes(type)||target.querySelector('.wiki-integration-card'))return;
  const entityType=type==='item'?'items':'monsters';
  const data=await Wiki.entity(entityType,id);if(!data)return;
  const records=data.records||[];if(!records.length)return;
  const section=card('📚 Wiki Snapshot Integration');
  appendSourceSummary(section,records);
  await appendDropSummary(section,type,id);
  if(type==='item')await appendRecipeSummary(section,id);
  target.appendChild(section);
}
