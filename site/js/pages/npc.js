import { OSRS } from "../core/osrs.js";
import { escapeHTML as esc } from "../core/utils.js";
import { Catalog } from "../services/catalog-service.js";
import { shopsHTML } from "../services/shop-service.js";

const params=new URLSearchParams(location.search);
const id=Number(params.get("id"));
let meta=null;
const app=document.getElementById("app");

function formatValue(v){
if(v===null||v===undefined||v==="")return '<span class="muted">—</span>';
if(typeof v==="boolean")return v?"Yes":"No";
if(Array.isArray(v))return v.length?v.map(x=>`<span class="badge">${esc(x)}</span>`).join(""):'<span class="muted">—</span>';
return esc(v);
}

function stat(key,value){
return `<div class="stat"><div class="label">${esc(key.replace(/_/g," "))}</div><div class="value">${formatValue(value)}</div></div>`;
}

(async function(){
try {
meta=(await OSRS.Data.list("npcs")).find(x=>Number(x.id)===id)||null;
if(!meta){OSRS.setHTML(app,'<div class="card">NPC not found.</div>');return;}
const npc=await Catalog.get("npcs",id);

document.title=npc.name||"NPC";

let html=`
<h1>👤 ${esc(npc.name)}</h1>
<div class="sub">NPC ID: ${esc(npc.id)}</div>
`;

const interactionOptions = Array.isArray(npc.options) ? npc.options : (npc.options == null || npc.options === '' ? [] : [npc.options]);

if(interactionOptions.length){
html+=`<div class="card npc-interactions"><h2>Interactions</h2><div class="interaction-list">${interactionOptions.map((option,i)=>`<div class="interaction-row"><span class="interaction-index">${i+1}</span><span class="interaction-name">${esc(option)}</span></div>`).join("")}</div></div>`;
}

if(npc.aliases?.length){
html+=`
<div class="card">
<h2>Aliases</h2>
<div>${npc.aliases.map(x=>`<span class="badge">${esc(x)}</span>`).join("")}</div>
</div>`;
}

const locations=npc.locations||[];
let locationHTML="";

if(locations.length){
const groups={};
locations.forEach(loc=>{
const name=loc.name||(Number(loc.plane)?`Floor ${loc.plane}`:"Ground floor");
(groups[name]??=[]).push(loc);
});

locationHTML=Object.entries(groups).map(([name,spawns])=>`
<details class="location">
<summary><strong>${esc(name)}</strong>
<span class="muted">${spawns.length} spawn${spawns.length===1?"":"s"}</span>
</summary>
<div class="coords">
${spawns.map(loc=>`
<div>
X: ${esc(loc.x??"—")}&nbsp;&nbsp;
Y: ${esc(loc.y??"—")}&nbsp;&nbsp;
Plane: ${esc(loc.plane??0)}
</div>`).join("")}
</div>
</details>`).join("");
}else{
locationHTML='<div class="muted">No spawn locations available.</div>';
}

html+=`
<details>
<summary>📍 Locations — ${locations.length.toLocaleString()} spawn${locations.length===1?"":"s"} ▸</summary>
<div>${locationHTML}</div>
</details>`;

html+=await shopsHTML(id);

OSRS.setHTML(app,html);
} catch(error) { OSRS.setHTML(app,'<div class="card">NPC detail data could not be loaded.</div>'); }
})();
