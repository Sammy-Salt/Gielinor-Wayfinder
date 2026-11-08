import {OSRSSync} from "../services/player-sync.js";
import {Catalog} from "../services/catalog-service.js";
import {SaveImport} from "../services/save-import.js";

const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));

async function itemName(id){
  try{
    const d=await Catalog.get("items",Number(id));
    return d?.name||`Item ${id}`;
  }catch{
    return `Item ${id}`;
  }
}

async function renderItems(el,rows){
  el.replaceChildren();
  if(!rows.length){
    el.innerHTML='<div class="empty">None recorded</div>';
    return;
  }
  for(const r of rows){
    const n=await itemName(r.id);
    const d=document.createElement("div");
    d.className="item-chip";
    d.innerHTML=`<a href="item.html?id=${Number(r.id)}">${esc(n)}</a><small>× ${Number(r.amount).toLocaleString()} · slot ${Number(r.slot)+1}</small>`;
    el.append(d);
  }
}

function setImportStatus(text, ok){
  const el=$("import-status");
  if(!el) return;
  el.textContent=text;
  el.className="import-status"+(ok===true?" is-ok":ok===false?" is-bad":"");
}

function refreshImportMeta(){
  const meta=SaveImport.getImportMeta();
  const label=$("import-file-label");
  if(!label) return;
  if(!meta){
    label.textContent="No local save linked yet.";
    return;
  }
  const when=meta.importedAt?new Date(meta.importedAt).toLocaleString():"unknown time";
  const handle=meta.hasHandle?" · will try to re-read this file on open":" · snapshot cached (re-pick to refresh from disk)";
  label.textContent=`${meta.fileName||"save.json"} · last loaded ${when}${handle}`;
}

async function renderCharacter(){
  const d=OSRSSync.getData();
  if(!d){
    $("status").textContent=`🔴 Character data not loaded`;
    return;
  }
  const p=d.player;
  const imported=Boolean(d.source?.importMode);
  $("status").textContent=imported
    ?`🟢 Imported save · ${d.source?.fileName||d.source?.character||"local file"} · save v${d.metadata?.saveVersion??d.source?.sourceVersion??"?"}`
    :`🟢 2009Scape save loaded · save v${d.metadata?.saveVersion??d.source?.sourceVersion??"?"}`;
  $("subtitle").textContent=`${p.name||"Player"} · ${imported?"local imported character":"read-only local character data"}`;

  const skills=d.skills||[];
  const totalLevel=skills.reduce((n,s)=>n+Number(s.level||1),0);
  $("overview").innerHTML=`<div class="grid"><div class="stat"><div class="stat-label">TOTAL LEVEL</div><div class="stat-value">${totalLevel}</div></div><div class="stat"><div class="stat-label">TOTAL XP</div><div class="stat-value">${Math.round(Number(p.totalXP)||0).toLocaleString()}</div></div><div class="stat"><div class="stat-label">QUEST POINTS</div><div class="stat-value">${Number(p.questPoints||0)}</div></div><div class="stat"><div class="stat-label">QUESTS COMPLETE</div><div class="stat-value">${d.quests?.completed||0} / ${d.quests?.totalTracked||0}</div></div></div>`;

  const sk=$("skills");
  sk.replaceChildren();
  for(const s of skills){
    const x=document.createElement("div");
    x.className="character-skill";
    const xp=Math.round(Number(s.xp)||0);
    const level=Number(s.level)||1;
    x.innerHTML=`<div class="top"><span>${esc(s.name)}</span><b>${level}</b></div><div class="xp">${xp.toLocaleString()} XP</div>`;
    sk.append(x);
  }

  $("combat").innerHTML=`<div class="stat"><div class="stat-label">HITPOINTS</div><b>${p.lifepoints??"—"}</b></div><div class="stat"><div class="stat-label">PRAYER POINTS</div><b>${p.prayerPoints??"—"}</b></div><div class="stat"><div class="stat-label">RUN ENERGY</div><b>${p.runEnergy??"—"}%</b></div><div class="stat"><div class="stat-label">SPECIAL ENERGY</div><b>${p.specialEnergy??"—"}%</b></div><div class="stat"><div class="stat-label">SPELLBOOK ID</div><b>${p.spellbook??"—"}</b></div>`;

  await renderItems($("inventory"),d.inventory||[]);
  await renderItems($("equipment"),d.equipment||[]);
  await renderItems($("bank"),d.bank||[]);

  const q=$("quests");
  q.replaceChildren();
  for(const v of d.quests?.items||[]){
    const row=document.createElement("div");
    row.className="quest-row";
    const name=document.createElement("span");
    name.textContent=v.name;
    const st=document.createElement("span");
    st.className=v.completed?"quest-complete":"muted";
    st.textContent=v.completed?"✓ Complete":`Stage ${v.stage}`;
    row.append(name,st);
    q.append(row);
  }

  const stats=d.statistics||{};
  const labels={logsChopped:"Logs chopped",enemiesKilled:"Enemies killed",fishCaught:"Fish caught",foodCooked:"Food cooked",rocksMined:"Rocks mined",deaths:"Deaths"};
  $("stats").innerHTML=Object.entries(labels).map(([k,l])=>`<div class="stat"><div class="stat-label">${l.toUpperCase()}</div><b>${Number(stats[k]||0).toLocaleString()}</b></div>`).join("");

  const loc=p.location||d.location||{};
  $("location").textContent=`${loc.x??"—"}, ${loc.y??"—"}, Plane ${loc.plane??"—"}`;
  refreshImportMeta();
}

function bindImportUi(){
  const pick=$("btn-pick-save");
  const clear=$("btn-clear-save");
  pick?.addEventListener("click",async()=>{
    pick.disabled=true;
    setImportStatus("Opening file picker…");
    try{
      await SaveImport.importWithFilePicker();
      setImportStatus("Save imported. Character data updated.",true);
      await renderCharacter();
    }catch(error){
      if(error?.name==="AbortError") setImportStatus("File pick cancelled.");
      else setImportStatus(`Import failed: ${error.message}`,false);
    }finally{
      pick.disabled=false;
    }
  });
  clear?.addEventListener("click",async()=>{
    await SaveImport.clearImport();
    setImportStatus("Cleared linked save. Reloading bundled sample…");
    try{
      await OSRSSync.load({force:true});
      await renderCharacter();
      setImportStatus("Using bundled player-sync data.",true);
    }catch(error){
      setImportStatus(`Reload failed: ${error.message}`,false);
    }
  });
}

async function init(){
  bindImportUi();
  try{
    await OSRSSync.load({force:true});
    await renderCharacter();
  }catch(e){
    $("status").textContent=`🔴 Character data error: ${e.message}`;
    refreshImportMeta();
  }
}

init();
