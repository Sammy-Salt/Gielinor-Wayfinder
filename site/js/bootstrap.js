import { initShell } from "./core/shell.js";
import { Router } from "./core/router.js";
import { Logger } from "./core/logger.js";
import { Events } from "./core/events.js";
import { enhanceAppShell } from "./components/app-enhancer.js";
import { Platform } from "./core/platform.js";
import { initAssistant } from "./components/assistant.js";
import { Locations } from "./services/location-service.js";
import { appendWikiIntegration } from "./components/wiki-integration.js";

const routes = Object.freeze({
  "index.html":"./pages/index.js","quest.html":"./pages/quest.js","quests.html":"./pages/quests.js","progress.html":"./pages/progress.js","character.html":"./pages/character.js","crafting.html":"./pages/crafting.js","goals.html":"./pages/goals.js",
  "monsters.html":"./pages/monsters.js","monster.html":"./pages/monster.js","bosses.html":"./pages/bosses.js","boss.html":"./pages/boss.js",
  "items.html":"./pages/items.js","item.html":"./pages/item.js","npcs.html":"./pages/npcs.js","npc.html":"./pages/npc.js",
  "calculators.html":"./pages/calculators.js","combat-stats.html":"./pages/combat-stats.js","skill-stats.html":"./pages/skill-stats.js",
  "drop-stats.html":"./pages/drop-stats.js","drop-time.html":"./pages/drop-time.js"
});
for(const [path,modulePath] of Object.entries(routes)) Router.register(path,()=>import(`${modulePath}?v=40`));

initShell();
enhanceAppShell();
const page=Router.current();
const loader=Router.resolve();
if(loader){
  try { await loader(); await Platform.init();
    if(page==="index.html") await initAssistant();
    if(page==="item.html"||page==="monster.html"||page==="boss.html"){
      const type=page==="item.html"?"item":"monster"; const id=Router.params().get("id");
      if(id && (type==="item" || type==="monster")) await appendWikiIntegration({type,id});
    }
    if(page==="monster.html"||page==="boss.html"||page==="npc.html"){ try { const id=Router.params().get('id'); const type=page==="npc.html"?'npc':page==="boss.html"?'boss':'monster'; const loc=await Locations.get(type,id); const main=document.querySelector('main,.osrs-content,.container,.content'); if(main&&loc.locations.length&&!main.querySelector('.location-panel')){ const sec=document.createElement('section'); sec.className='card location-panel'; const h=document.createElement('h2'); h.textContent='📍 Locations'; sec.append(h); const seen=new Set(); for(const row of loc.locations){const key=`${row.name}|${row.x}|${row.y}|${row.plane}`; if(seen.has(key)) continue; seen.add(key); const d=document.createElement('div'); d.className='location-row'; d.textContent=`${row.name} · ${row.x}, ${row.y}${row.plane?` · Plane ${row.plane}`:''}`; sec.append(d); if(seen.size>=8) break;} const a=document.createElement('a'); a.href=Locations.mapHref(); a.textContent='🗺 Open world map'; sec.append(a); main.append(sec); } } catch(e){} }
    Events.emit("app:ready",{page}); }
  catch(error){ Logger.error(`Failed to initialize ${page}`,error); Events.emit("app:error",{page,error}); }
} else {
  Logger.warn(`No production page module registered for ${page}`);
}
