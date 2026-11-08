import { OSRS } from "../core/osrs.js";
import { escapeHTML as esc } from "../core/utils.js";

let cache = null;
async function load() {
  if (!cache) cache = Promise.all([OSRS.Data.get("recipes.json"), OSRS.Data.list("items")]).then(([doc, items]) => {
    const recipes = Array.isArray(doc) ? doc : doc?.recipes || [];
    const madeBy = new Map(), usedIn = new Map();
    const push = (m, id, r) => { id = Number(id); if (!m.has(id)) m.set(id, []); m.get(id).push(r); };
    for (const r of recipes) {
      push(madeBy, r.output?.itemId, r);
      for (const i of new Set((r.inputs || []).map(x => x.itemId))) push(usedIn, i, r);
    }
    return { madeBy, usedIn, names: new Map(items.map(i => [Number(i.id), i.name])) };
  }).catch(() => ({ madeBy: new Map(), usedIn: new Map(), names: new Map() }));
  return cache;
}

const link = (names, id) => `<a href="item.html?id=${encodeURIComponent(id)}">${esc(names.get(Number(id)) || "Item " + id)}</a>`;
const qty = (names, e) => `${e.quantity > 1 ? esc(e.quantity) + " × " : ""}${link(names, e.itemId)}`;

function entry(names, r) {
  const ins = (r.inputs || []).map(i => qty(names, i)).join(" + ") || "—";
  const extra = [...(r.tools || []), ...(r.facilities || [])].filter(Boolean);
  const xp = r.xp ? ` · ${esc(r.xp)} xp` : "";
  return `<div class="source-entry"><strong>${esc(r.skill)} ${esc(r.level)}</strong>${xp}<div>${ins} → ${qty(names, r.output)}</div>${extra.length ? `<div class="muted">${esc(extra.join(", "))}</div>` : ""}</div>`;
}

const block = (title, names, rows) => `<details><summary>${title} <span class="count">(${rows.length})</span></summary><div class="source-body">${
  rows.length ? rows.map(r => entry(names, r)).join("") : '<div class="empty">None found in the recipe data.</div>'}</div></details>`;

/** "Made by / Used in" card for an item id, computed from recipes.json; "" when the item has no recipes at all. */
export async function recipesHTML(itemId) {
  const { madeBy, usedIn, names } = await load();
  const made = madeBy.get(Number(itemId)) || [], used = usedIn.get(Number(itemId)) || [];
  if (!made.length && !used.length) return "";
  const byLevel = (a, b) => (a.level || 0) - (b.level || 0);
  return `<div class="card"><h2>🛠️ Recipes</h2><div class="subtitle">2009Scape server data first; OSRS Wiki rows are secondary.</div>${block("🔨 Made by", names, [...made].sort(byLevel))}${block("🧰 Used in", names, [...used].sort(byLevel))}</div>`;
}
