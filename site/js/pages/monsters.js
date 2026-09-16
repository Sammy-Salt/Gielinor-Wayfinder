import { OSRS } from "../core/osrs.js";

(async function () {
  "use strict";
  const data = await OSRS.Data.get("monsters/display-index.json");
  const results=document.getElementById("results"), count=document.getElementById("count");
  function render(){
    count.textContent=data.length+" monster identities ("+data.reduce((n,x)=>n+(x.variant_count||1),0).toLocaleString()+" game variants)";
    results.replaceChildren();
    const f=document.createDocumentFragment();
    data.slice(0,150).forEach(x=>{
      const card=document.createElement("div");card.className="card";
      const a=document.createElement("a");a.href="./monster.html?id="+encodeURIComponent(x.id);a.className="catalog-link";a.textContent=x.name||"Unknown Monster";card.appendChild(a);
      if(x.boss){const b=document.createElement("div");b.className="badge";b.textContent="Boss";card.appendChild(b)}
      if(x.variant_count>1){const v=document.createElement("div");v.className="small";v.textContent=x.variant_count.toLocaleString()+" game variants";card.appendChild(v)}
      if(x.combat_levels?.length){const sm=document.createElement("div");sm.className="small";sm.textContent="Combat "+x.combat_levels.join(", ");card.appendChild(sm)}
      f.appendChild(card);
    });
    results.appendChild(f);
  }
  render();
})().catch(error=>{const r=document.getElementById("results"),c=document.getElementById("count");if(c)c.textContent="Unable to load monsters";if(r){const p=document.createElement("p");p.className="empty";p.textContent=error.message;r.replaceChildren(p)}});
