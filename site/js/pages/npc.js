import { OSRS } from "../core/osrs.js";
import { escapeHTML as esc } from "../core/utils.js";
import { Catalog } from "../services/catalog-service.js";

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
const itemNameIndex=await OSRS.Data.itemNameIndex();

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
const name=loc.name||"Unknown Location";
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
Y: ${esc(loc.y??"—")}
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

if(npc.shops?.length){
html+=`<details>
<summary>🏪 Shops — ${npc.shops.length} ▸</summary><div>`;

for(const shop of npc.shops){
html+=`<div class="location">
<strong>${esc(shop.name)}</strong>
<div class="muted">${esc(shop.location||"")}</div>`;

if(shop.items?.length){
html+=`<div class="table-scroll"><table>
<thead><tr><th>Item</th><th>Stock</th><th>Restock</th><th>Sell</th><th>Buy</th></tr></thead><tbody>`;

for(const item of shop.items){
let name=esc(item.item_name);
const iid=itemNameIndex[String(item.item_name).toLowerCase()];
if(iid)name=`<a href="item.html?id=${encodeURIComponent(iid)}">${name}</a>`;

html+=`<tr>
<td>${name}</td>
<td>${esc(item.stock)}</td>
<td>${esc(item.restock)}</td>
<td>${esc(item.sell_price)}</td>
<td>${esc(item.buy_price)}</td>
</tr>`;
}
html+=`</tbody></table></div>`;
}
html+=`</div>`;
}
html+=`</div></details>`;
}

OSRS.setHTML(app,html);
} catch(error) { OSRS.setHTML(app,'<div class="card">NPC detail data could not be loaded.</div>'); }
})();
