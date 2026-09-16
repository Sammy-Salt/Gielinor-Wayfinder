import { Relationships } from "../services/relationship-service.js";
const href=(type,id)=>({item:`item.html?id=${id}`,monster:`monster.html?id=${id}`,npc:`npc.html?id=${id}`,boss:`boss.html?id=${id}`}[type]||`index.html`);
function ready(target){const text=(target.textContent||"").trim().toLowerCase();return target.children.length>0&&!/^(loading|loading\.\.\.|loading data|please wait)/.test(text);}
async function waitForRender(target,timeout=10000){const start=Date.now();while(Date.now()-start<timeout){if(ready(target))return true;await new Promise(r=>setTimeout(r,100));}return false;}
export async function appendRelationships({type,id,target=document.getElementById("app")||document.getElementById("content")}={}){
 if(!target||!id||!["item","monster","boss"].includes(type))return;
 try{
  if(!await waitForRender(target))return;
  if(target.querySelector(".relationship-card"))return;
  const rows=type==="item"?await Relationships.itemSources(id):await Relationships.monsterDrops(id);if(!rows.length)return;
  const section=document.createElement("section");section.className="card relationship-card";const h=document.createElement("h2");h.textContent=type==="item"?"🔗 Where It Comes From":"💰 Related Drops";section.appendChild(h);
  const grid=document.createElement("div");grid.className="relationship-grid";
  for(const r of rows.slice(0,100)){const a=document.createElement("a");a.className="relationship-link";const relType=type==="item"?"monster":"item";const rid=type==="item"?r.id:r.itemId;if(rid==null)continue;a.href=href(relType,rid);const strong=document.createElement("strong");strong.textContent=r.name||r.itemName||"Unknown";const span=document.createElement("span");span.textContent=type==="item"?"Monster drop":"Item drop";a.append(strong,span);grid.appendChild(a);}
  section.appendChild(grid);if(rows.length>100){const more=document.createElement("div");more.className="muted";more.textContent=`Showing 100 of ${rows.length.toLocaleString()} relationships.`;section.appendChild(more);}target.appendChild(section);
 }catch(error){console.warn("Relationship panel unavailable",error);}
}
