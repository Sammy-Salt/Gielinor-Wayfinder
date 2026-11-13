import { OSRS } from "../core/osrs.js";
import { escapeHTML as esc } from "../core/utils.js";
import { OSRSSync } from "./player-sync.js";
import { assess, describe, buildHoldings, buildLevels, buildContext } from "./recipe-ready.js";
import { QUEST_NAMES } from "./quest-ids.js";

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

/** Character context from the loaded (bundled or imported) save, or null when none can be loaded. */
async function character() {
  try {
    await OSRSSync.load();
    const snap = OSRSSync.getData();
    return snap ? { levels: buildLevels(snap), held: buildHoldings(snap), ctx: buildContext(snap, Object.values(QUEST_NAMES)), who: snap.source?.character || "" } : null;
  } catch { return null; }
}

function entry(names, r, who) {
  const ins = (r.inputs || []).map(i => qty(names, i)).join(" + ") || "—";
  const extra = [...(r.tools || []), ...(r.facilities || [])].filter(Boolean);
  const xp = r.xp ? ` · ${esc(r.xp)} xp` : "";
  const badge = who ? describe(assess(r, who.levels, who.held, who.ctx), (id) => names.get(Number(id)) || `Item ${id}`) : null;
  const status = badge ? `<div class="${badge.cls === "ready" ? "recipe-ready" : "recipe-missing"}">${esc(badge.text)}</div>` : "";
  return `<div class="source-entry"><strong>${esc(r.skill)} ${esc(r.level)}</strong>${xp}${status}<div>${ins} → ${qty(names, r.output)}</div>${extra.length ? `<div class="muted">${esc(extra.join(", "))}</div>` : ""}</div>`;
}

const block = (title, names, rows, who) => `<details><summary>${title} <span class="count">(${rows.length})</span></summary><div class="source-body">${
  rows.length ? rows.map(r => entry(names, r, who)).join("") : '<div class="empty">None found in the recipe data.</div>'}</div></details>`;

/** "Made by / Used in" card for an item id, computed from recipes.json; "" when the item has no recipes at all. */
export async function recipesHTML(itemId) {
  const { madeBy, usedIn, names } = await load();
  const made = madeBy.get(Number(itemId)) || [], used = usedIn.get(Number(itemId)) || [];
  if (!made.length && !used.length) return "";
  const who = await character();
  const byLevel = (a, b) => (a.level || 0) - (b.level || 0);
  return `<div class="card"><h2>Recipes</h2><div class="subtitle">2009Scape server data first; OSRS Wiki rows are secondary.${who ? ` Checked against ${esc(who.who || "your save")}'s levels, inventory, bank and equipment.` : ""}</div>${block("Made by", names, [...made].sort(byLevel), who)}${block("Used in", names, [...used].sort(byLevel), who)}</div>`;
}
