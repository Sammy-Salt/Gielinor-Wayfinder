import { OSRS } from "../core/osrs.js";
import { Catalog } from "../services/catalog-service.js";

(async function(){
"use strict";
const app=document.getElementById("app");
try{
const bosses=(await Catalog.list("monsters")).filter(x=>x.boss===true).sort((a,b)=>String(a.name).localeCompare(String(b.name)));
const card=document.createElement("div");card.className="card";
const h1=document.createElement("h1");h1.textContent="Bosses";
const sub=document.createElement("div");sub.className="sub";sub.textContent=`${bosses.length} bosses in the encyclopedia`;
const grid=document.createElement("div");grid.className="grid";
for(const b of bosses){const a=document.createElement("a");a.className="boss";a.href="boss.html?id="+encodeURIComponent(b.id);const name=document.createElement("div");name.className="name";name.textContent=b.name||"Unknown Boss";const meta=document.createElement("div");meta.className="meta";meta.textContent="NPC ID: "+b.id+(b.combat_level!=null?" · Combat "+b.combat_level:"");a.append(name,meta);grid.appendChild(a)}
card.append(h1,sub,grid);app.replaceChildren(card);
}catch(error){OSRS.setHTML(app,'<div class="card">Unable to load bosses.</div>');console.error(error)}
})();
