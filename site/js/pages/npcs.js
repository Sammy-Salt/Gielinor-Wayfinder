import { OSRS } from "../core/osrs.js";
import { debounce } from "../core/utils.js";
import { Catalog } from "../services/catalog-service.js";

(async function () {
  "use strict";
  const all=(await Catalog.list("npcs")).map(n=>({...n,searchName:String(n.name||"").toLocaleLowerCase()}));
  const results=document.getElementById("results"),count=document.getElementById("count");
  function render(){const list=all;count.textContent=`${list.length.toLocaleString()} NPC${list.length===1?'':'s'}`;results.replaceChildren();const f=document.createDocumentFragment();list.slice(0,500).forEach(n=>{const a=document.createElement("a");a.className="list-item";a.href="npc.html?id="+encodeURIComponent(n.id);const strong=document.createElement("strong");strong.textContent=n.name||"Unknown NPC";const span=document.createElement("span");span.textContent="NPC ID "+n.id;a.append(strong,span);f.appendChild(a)});if(list.length>500){const p=document.createElement("p");p.textContent="Showing first 500 results. Refine your search.";f.appendChild(p)}results.appendChild(f)}
  render();
})().catch(error=>{const r=document.getElementById("results"),c=document.getElementById("count");if(c)c.textContent="Unable to load NPCs";if(r){const p=document.createElement("p");p.className="empty";p.textContent=error.message;r.replaceChildren(p)}});
