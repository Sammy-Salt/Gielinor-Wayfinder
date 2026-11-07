import { OSRS } from "../core/osrs.js";
import { escapeHTML as esc } from "../core/utils.js";

let cache = null;
async function load() {
  if (!cache) cache = Promise.all([OSRS.Data.get("shops.json"), OSRS.Data.list("items")]).then(([doc, items]) => ({
    shops: doc?.shops || [],
    names: new Map(items.map(i => [Number(i.id), i.name]))
  })).catch(() => ({ shops: [], names: new Map() }));
  return cache;
}

const stockText = n => (n < 0 ? "Unlimited" : String(n));

/** HTML for the shops run by an NPC/monster id (2009Scape shops.json), or "" when none. */
export async function shopsHTML(npcId) {
  const { shops, names } = await load();
  const mine = shops.filter(s => s.npcs.includes(Number(npcId)));
  if (!mine.length) return "";
  const body = mine.map(s => `<div class="location"><strong>${esc(s.title)}</strong>
<div class="muted">${esc(s.shopType)}${s.currency !== 995 ? " · special currency (item " + esc(s.currency) + ")" : ""}${s.generalStore ? " · buys anything" : ""}</div>
<div class="table-scroll"><table><thead><tr><th>Item</th><th>Stock</th><th>Restock</th></tr></thead><tbody>${
    s.stock.map(e => `<tr><td><a href="item.html?id=${encodeURIComponent(e.itemId)}">${esc(names.get(e.itemId) || "Item " + e.itemId)}</a></td><td>${esc(stockText(e.amount))}</td><td>${esc(e.restock)}</td></tr>`).join("")
  }</tbody></table></div></div>`).join("");
  return `<details><summary>🏪 Shops — ${mine.length} ▸</summary><div>${body}</div></details>`;
}
