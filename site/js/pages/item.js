import {OSRS} from "../core/osrs.js";
import {Catalog} from "../services/catalog-service.js";
import {Drops} from "../services/drop-service.js";
import {recipesHTML} from "../services/recipe-service.js";

const params=new URLSearchParams(location.search);
const id=params.get("id");
const content=document.getElementById("content");
const esc=OSRS.escapeHTML;

function row(label,value){
  if(value===undefined||value===null||value==="") return "";
  return `<div class="row"><span class="label">${esc(label)}</span><span class="value">${esc(value)}</span></div>`;
}
function yesNo(value){
  if(value===undefined||value===null||value==="") return "Unknown";
  if(value===true||value==="true"||value===1||value==="1") return "Yes";
  if(value===false||value==="false"||value===0||value==="0") return "No";
  return "Unknown";
}
function rateText(drop){
  if(drop.rateStatus==="fallback"&&Drops.rateDisplay(drop)) return `${Drops.rateDisplay(drop)} · OSRS Wiki`;
  if(drop.rateStatus==="conflict") return "Rate unresolved · conflicting Wiki evidence";
  return "Rate unavailable";
}
function rateClass(drop){return drop.rateStatus==="fallback"?"rate-known":"rate-unknown";}

async function loadItem(){
  if(!id||!/^[0-9]+$/.test(id)){
    OSRS.setHTML(content,'<div class="card"><h1>Invalid Item</h1></div>');
    return;
  }
  try{
    const item=await Catalog.get("items",id);
    const [drops,shops,recipes]=await Promise.all([
      OSRS.Relationships.itemDrops(id),
      Promise.resolve(item?._acquisition?.shops||[]),
      recipesHTML(id).catch(()=>"")
    ]);
    render(item,drops,shops,item?._acquisition?.groundSpawns||{status:"unknown"},recipes);
  }catch(error){
    console.error("[Gielinor Wayfinder] item load failed",error);
    OSRS.setHTML(content,`<div class="card"><h1>Item Not Found</h1><div class="muted">${esc(error?.message||`No item data exists for ID ${id}.`)}</div></div>`);
  }
}

function render(item,drops,shops,ground,recipes=""){
  document.title=item.name||"Item";
  let html=`<div class="card"><h1>${esc(item.name||"Unknown Item")}</h1>${row("Item ID",item.id)}${row("Members",yesNo(item.members))}${row("Tradeable",yesNo(item.tradeable))}${row("Weight",item.weight)}</div>`;

  html+=`<div class="card"><h2>Where to get it</h2><div class="subtitle">Monster drops, shops, ground spawns and recipes for this item.</div>`;
  html+=`<details><summary>Monster Drops <span class="count">(${drops.length})</span></summary><div class="source-body">`;
  if(!drops.length){
    html+=`<div class="empty">No monsters are known to drop this item.</div>`;
  }else{
    const grouped=new Map();
    for(const drop of drops){const key=String(drop.monsterId);if(!grouped.has(key))grouped.set(key,[]);grouped.get(key).push(drop);}
    [...grouped.entries()].sort((a,b)=>String(a[1][0].monsterName||"").localeCompare(String(b[1][0].monsterName||""))).forEach(([monsterId,entries])=>{
      const first=entries[0];
      html+=`<details><summary><a href="monster.html?id=${encodeURIComponent(monsterId)}">${esc(first.monsterName||`Monster ${monsterId}`)}</a> <span class="count">(${entries.length})</span></summary><div class="source-body">${row("Monster ID",monsterId)}`;
      for(const drop of entries){
        html+=`<div class="source-entry"><strong><a href="item.html?id=${encodeURIComponent(drop.itemId)}">${esc(drop.itemName||item.name||"Unknown Item")}</a></strong><div class="${rateClass(drop)}">Drop rate: ${esc(rateText(drop))}</div>${drop.rateEvidencePage?`<div class="muted">Evidence page: ${esc(drop.rateEvidencePage)}</div>`:""}${drop.rateReason?`<div class="muted">${esc(drop.rateReason)}</div>`:""}</div>`;
      }
      html+=`</div></details>`;
    });
  }
  html+=`</div></details>`;

  html+=`<details><summary>Shops <span class="count">(${shops.length})</span></summary><div class="source-body">`;
  if(!shops.length) html+=`<div class="empty">No shops sell this item.</div>`;
  else for(const shop of shops){html+=`<div class="source-entry"><strong>${esc(shop.shopName||"Unknown Shop")}</strong>${row("Shop ID",shop.shopId)}${row("Location",shop.location)}${row("Owner",shop.owner)}${row("Shop Type",shop.shopType)}${row("Stock",shop.stock<0?"Unlimited":shop.stock)}${row("Restock",shop.restock)}<div class="muted">Primary source: 2009Scape.</div></div>`;}
  html+=`</div></details>`;

  if(ground?.status==="known"&&Array.isArray(ground.spawns)&&ground.spawns.length) html+=`<div class="source-entry"><strong>Ground Spawns (${ground.spawns.length})</strong><div class="muted">Source: 2009Scape. Respawn is in game ticks.</div>${ground.spawns.map(s=>`<div>X: ${esc(s.x)}&nbsp;&nbsp;Y: ${esc(s.y)}&nbsp;&nbsp;Plane: ${esc(s.plane)}&nbsp;&nbsp;Amount: ${esc(s.amount)}&nbsp;&nbsp;Respawn: ${esc(s.respawn)}</div>`).join("")}</div>`;
  else if(ground?.status==="unknown") html+=`<div class="source-entry"><strong>Ground Spawns</strong><div class="muted">No ground-spawn data for this item.</div></div>`;
  html+=`</div>`;

  html+=recipes;
  html+=`<div class="card"><h2>Basic Information</h2>${row("Examine",item.examine)}${row("Shop Price",item.shop_price)}${row("Grand Exchange Price",item.grand_exchange_price)}${row("GE Buy Limit",item.ge_buy_limit)}</div>`;

  if(item.equipment_slot!==undefined||item.attack_speed!==undefined||item.two_handed!==undefined||item.bonuses){
    html+=`<div class="card"><h2>Combat & Equipment</h2>${row("Equipment Slot",item.equipment_slot)}${row("Attack Speed",item.attack_speed)}${row("Two-Handed",item.two_handed!==undefined?yesNo(item.two_handed):undefined)}${item.bonuses?row("Bonuses",JSON.stringify(item.bonuses)):""}</div>`;
  }
  html+=`<div class="card"><h2>⚙️ Properties</h2>${row("Bankable",item.bankable!==undefined?yesNo(item.bankable):undefined)}${row("Lendable",item.lendable!==undefined?yesNo(item.lendable):undefined)}${row("Alchemizable",item.alchemizable!==undefined?yesNo(item.alchemizable):undefined)}${row("Rare Item",item.rare_item!==undefined?yesNo(item.rare_item):undefined)}${row("Has Special",item.has_special!==undefined?yesNo(item.has_special):undefined)}</div>`;
  html+=`<div class="card"><details><summary>Additional Item Data</summary><div class="source-body"><pre>${esc(JSON.stringify(item,null,2))}</pre></div></details></div>`;
  OSRS.setHTML(content,html);
}

loadItem();
