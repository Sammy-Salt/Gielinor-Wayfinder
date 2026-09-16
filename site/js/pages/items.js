import { OSRS } from "../core/osrs.js";
import { debounce } from "../core/utils.js";
import { Catalog } from "../services/catalog-service.js";

(async function () {
  "use strict";
  const results = document.getElementById("results");
  const count = document.getElementById("count");
  if (!results || !count) return;
  try {
    const data = (await Catalog.list("items")).map(item => ({ ...item, searchName: String(item.name || "").toLocaleLowerCase() }));
    function render() {
      const filtered = data;
      count.textContent = filtered.length + " items";
      results.replaceChildren();
      const fragment = document.createDocumentFragment();
      filtered.slice(0, 200).forEach(x => {
        const card = document.createElement("div"); card.className = "card";
        const link = document.createElement("a"); link.className = "catalog-link"; link.href = "./item.html?id=" + encodeURIComponent(x.id); link.textContent = x.name || "Unknown Item";
        card.appendChild(link);
        if (x.members) { const b=document.createElement("div"); b.className="badge"; b.textContent="Members"; card.appendChild(b); }
        if (x.tradeable) { const b=document.createElement("div"); b.className="badge"; b.textContent="Tradeable"; card.appendChild(b); }
        fragment.appendChild(card);
      });
      results.appendChild(fragment);
    }
    render();
  } catch (error) {
    count.textContent = "Unable to load items"; const p=document.createElement("p"); p.className="empty"; p.textContent=error.message; results.replaceChildren(p);
  }
})();
