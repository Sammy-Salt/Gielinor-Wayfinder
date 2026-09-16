import { OSRS } from "../core/osrs.js";
import { Catalog } from "../services/catalog-service.js";
const app=document.getElementById("app");
const id=Number(new URLSearchParams(location.search).get("id"));
const esc=v=>OSRS.escapeHTML(v??"—");
const val=v=>v===null||v===undefined||v===""?"—":esc(v);
const row=(k,v)=>`<div class="row"><span class="k">${esc(k)}</span><span class="v">${val(v)}</span></div>`;
function basicBoss(index){return index.find(x=>Number(x.id)===id&&x.boss===true)||index.find(x=>Number(x.id)===id)||null}
(async()=>{try{
 if(!Number.isInteger(id)||id<1)throw new Error("Missing boss ID");
 const index=await OSRS.Data.list("monsters"),meta=basicBoss(index);if(!meta)throw new Error("Boss not found");
 let monster;try{monster=await Catalog.get("monsters",id)}catch(e){monster=meta}
 const locations=monster.locations||[];
 const drops=await OSRS.Relationships.monsterDrops(id);
 const combat=[["Combat level",monster.combat_level],["Lifepoints",monster.lifepoints],["Hitpoints",monster.hitpoints],["Max hit",monster.max_hit],["Attack style",monster.attack_style],["Attack",monster.attack_level],["Strength",monster.strength_level],["Defence",monster.defence_level],["Ranged",monster.range_level??monster.ranged_level],["Magic",monster.magic_level],["Attack speed",monster.attack_speed]];
 const stats=["combat_level","lifepoints","hitpoints","max_hit","aggressive","size","respawn_delay","attack_bonus","strength_bonus","magic_attack","magic_strength","ranged_attack","ranged_strength","defensive_stab","defensive_slash","defensive_crush","defensive_magic","defensive_light_ranged","defensive_standard_ranged","defensive_heavy_ranged","elemental_weakness_type","elemental_weakness_percent","immunities","attributes","slayer_category","slayer_assigned_by"];
 const groups={};for(const x of locations){const name=x.location||x.name||"Unknown Location";(groups[name]??=[]).push(x)}
 const locationHtml=Object.keys(groups).length?Object.entries(groups).map(([name,list])=>`<details class="location"><summary>${esc(name)} <span class="spawn">(${list.length} spawns)</span></summary>${list.map(x=>`<div class="note">X: ${val(x.x)} · Y: ${val(x.y)} · Plane: ${val(x.plane??0)}</div>`).join("")}</details>`).join(""):'<div class="note">No location data available.</div>';
 const dropHtml=drops.length?drops.map(x=>`<div class="drop"><span><a href="item.html?id=${encodeURIComponent(x.itemId)}">${esc(x.itemName||x.name||"Unknown")}</a></span><span>2009Scape</span></div>`).join(""):'<div class="note">No known drops in 2009Scape data.</div>';
 document.title=monster.name||meta.name||"Boss";
 OSRS.setHTML(app,`<a class="back" href="bosses.html">← Bosses</a><div class="card"><h1>👑 ${esc(monster.name||meta.name)}</h1><div class="sub">NPC ID: ${esc(monster.id??id)} · Boss</div><div class="muted small">Primary source: 2009Scape · Wiki used only as a secondary fallback where available</div><h2>⚔️ Combat</h2><div class="grid">${combat.map(x=>row(x[0],x[1])).join("")}</div><h2>📊 Detailed Stats</h2><div class="grid">${stats.map(k=>row(k.replaceAll("_"," "),monster[k])).join("")}</div><h2>💀 Mechanics & Strategy</h2><div class="note">Strategy information has not been added yet.</div><h2>📍 Locations</h2>${locationHtml}<h2>💰 Drops</h2>${dropHtml}</div>`);
}catch(e){app.replaceChildren();const c=document.createElement("div");c.className="card";const h=document.createElement("h2");h.textContent="Unable to load boss";const p=document.createElement("p");p.textContent=e?.message||String(e);const a=document.createElement("a");a.className="back";a.href="bosses.html";a.textContent="← Back to Bosses";c.append(h,p,a);app.appendChild(c);console.error(e)}})();
