import { OSRS } from "../core/osrs.js";

const esc = s => OSRS.escapeHTML(String(s ?? ""));
const pick = document.getElementById("refPick");
const label = document.getElementById("refPickLabel");
const view = document.getElementById("refView");
const tabs = [...document.querySelectorAll("[data-tab]")];
const docs = new Map();
let names = null;
let token = 0;

async function load(file) {
  if (!docs.has(file)) docs.set(file, await OSRS.Data.get(file));
  return docs.get(file);
}

async function resolveNames(ids) {
  if (!names) {
    try { names = new Map(Object.entries(await OSRS.Data.get("items/name-index.json")).map(([n, i]) => [i, n])); }
    catch { names = new Map(); }
  }
  const out = new Map();
  await Promise.all([...new Set(ids)].map(async id => {
    const n = names.get(id);
    if (n) return out.set(id, n.charAt(0).toUpperCase() + n.slice(1));
    try { const item = await OSRS.Data.get(`items/${id}.json`); if (item?.name) return out.set(id, item.name); } catch { /* offline: fall through */ }
    out.set(id, `Item ${id}`);
  }));
  return out;
}

const num = n => Number.isFinite(n) ? n.toLocaleString(undefined, { maximumFractionDigits: 3 }) : "—";
// a cell is plain text or a list of {id, text} item links (item.html?id=<id>)
const cell = c => Array.isArray(c) ? c.map(x => x.more ? "…" : `<a href="item.html?id=${encodeURIComponent(x.id)}">${esc(x.text)}</a>`).join(", ") : esc(c);
const table = (head, rows) => `<div class="table-wrap"><table class="ref-table"><thead><tr>${head.map(h => `<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.map(r => `<tr>${r.map(c => `<td>${cell(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
const link = (n, id) => [{ id, text: n.get(id) }];
const card = (title, body, note) => `<div class="card"><h2 class="result-heading">${esc(title)}</h2>${note ? `<div class="small">${esc(note)}</div>` : ""}${body}</div>`;

function flatRules(rules) {
  const lines = [];
  const walk = (k, v) => {
    if (v && typeof v === "object" && !Array.isArray(v)) Object.entries(v).forEach(([a, b]) => walk(k ? `${k} › ${a}` : a, b));
    else if (Array.isArray(v)) lines.push(`${k}: ${v.join(", ")}`);
    else lines.push(`${k}: ${v}`);
  };
  Object.entries(rules || {}).forEach(([k, v]) => walk(k, v));
  return lines.length ? `<ul class="rules small">${lines.map(l => `<li>${esc(l)}</li>`).join("")}</ul>` : "";
}

async function slayer() {
  const d = await load("slayer.json");
  label.textContent = "Slayer master";
  fill(d.masters.map(m => [m.id, `${m.name} (combat ${m.minCombatLevel}+)`]));
  const m = d.masters.find(x => x.id === pick.value) || d.masters[0];
  const byId = new Map(d.tasks.map(t => [t.id, t]));
  const rows = [...m.tasks].sort((a, b) => b.weight - a.weight).map(e => {
    const t = byId.get(e.taskId), r = e.amountRange || m.defaultAmountRange;
    return [t.name, t.level || "—", t.minCombatLevel, `${num(e.weight / m.totalWeight * 100)}%`, r.join("–"), t.quest || ""];
  });
  const rewards = d.rewards.map(r => [r.name, r.cost, r.note || ""]);
  return card(`${m.name}: assignments`, table(["Task", "Slayer lvl", "Combat", "Chance", "Amount", "Quest"], rows),
    `Task is picked by weight among those you qualify for. Points per task: ${m.completionPoints.every} (every), ${m.completionPoints.tenth} (10th), ${m.completionPoints.fiftieth} (50th).`)
    + card("Slayer rewards", table(["Reward", "Points", "Note"], rewards)) + card("Rules", flatRules(d.rules));
}

async function clues() {
  const d = await load("clues.json");
  label.textContent = "Clue tier";
  fill(["easy", "medium", "hard", "rare"].map(t => [t, t === "rare" ? "Rare table (Hard only)" : `${t[0].toUpperCase()}${t.slice(1)}`]));
  const tier = pick.value || "easy", t = d.rewards[tier];
  const n = await resolveNames(t.items.map(i => i.itemId));
  const rows = t.items.map(i => [link(n, i.itemId), i.min === i.max ? i.min : `${i.min}–${i.max}`, `${num(i.chancePercent)}%`]);
  const lv = d.levels[tier];
  const note = lv ? `${lv.minSteps}–${lv.maxSteps} steps per trail. Rolls: ${d.levels.rewardRolls.slots}.` : d.levels.rewardRolls.rareTable;
  return card(`${tier} rewards`, table(["Item", "Quantity", "Chance per roll"], rows), note);
}

const HEADS = { rewards: ["Reward", "Cost / options", "Requirements"], rooms: ["Room", "Requirement", "Details"], brothers: ["Brother", "Armour", "NPC"], table: ["Item", "Quantity", "Chance"],
  shop: ["Item", "Points (1)", "Points (2)"], bars: ["Bar", "Level", "Details"], exchange: ["Item", "", ""], loot: ["Item", "Kind", "Chance"], jobs: ["Customer", "Difficulty", "Location"] };
const TITLES = { rewards: "Rewards", rooms: "Rooms", brothers: "Brothers", table: "Reward table", shop: "Shop", bars: "Bars", exchange: "Ticket exchange", loot: "Loot table", jobs: "Delivery jobs" };

async function minigame() {
  const d = await load("minigames.json");
  label.textContent = "Minigame";
  fill(d.minigames.map(g => [g.id, g.name]));
  const g = d.minigames.find(x => x.id === pick.value) || d.minigames[0];
  const ids = [];
  for (const k of Object.keys(TITLES)) for (const r of g[k] || []) ids.push(...(r.itemIds || []));
  const n = await resolveNames(ids);
  const items = r => [...(r.itemIds || []).slice(0, 4).map(i => ({ id: i, text: n.get(i) })), ...((r.itemIds || []).length > 4 ? [{ more: true }] : [])];
  const fmt = {
    rewards: r => [r.name, r.points ?? (r.options ? r.options.map(o => `${o.points}→${o.quantity}`).join(", ") : (r.pointOptions || []).join("/")), (r.requirements || []).map(x => `${x.level} ${x.skill}`).join(", ")],
    rooms: r => [r.name, `${r.requirements[0].level} Thieving`, `urn ${num(r.urnOpenXp)} xp, sceptre 1/${num(r.sceptreOneIn)}`],
    brothers: r => [r.name, items(r), `NPC ${r.npcId}`],
    table: r => [items(r), r.min === r.max ? r.min : `${r.min}–${r.max}`, `${num(r.chancePercent)}%`],
    shop: r => [items(r), `Tele ${r.pizazzPoints.telekinetic} / Alch ${r.pizazzPoints.alchemist}`, `Ench ${r.pizazzPoints.enchantment} / Grave ${r.pizazzPoints.graveyard}`],
    bars: r => [r.name, `${r.level} Smithing`, `${num(r.smithingXp)} xp, ${r.coalPerBar} coal`],
    exchange: r => [items(r), "", ""],
    loot: r => [r.itemIds.length ? items(r) : "Raw fish (by Fishing level)", r.kind, `${num(r.chancePercent)}%`],
    jobs: r => [r.name, r.difficulty, r.location]
  };
  let html = "";
  for (const [k, title] of Object.entries(TITLES)) {
    if (!g[k]) continue;
    html += card(`${g.name}: ${title}`, table(HEADS[k], g[k].map(fmt[k])));
  }
  if (g.artifacts) html += card("Artifacts", flatRules({ rule: g.artifacts.rule }));
  if (g.xpRule) html += card("Experience rule", flatRules(g.xpRule));
  return html + card("Rules", flatRules(g.rules || {}));
}

function fill(options) {
  const keep = pick.value;
  if (pick.options.length === options.length && options.every(([v], i) => pick.options[i].value === v)) return;
  pick.replaceChildren(...options.map(([v, text]) => Object.assign(document.createElement("option"), { value: v, textContent: text })));
  if (options.some(([v]) => v === keep)) pick.value = keep;
}

let tab = "slayer";
async function render() {
  const mine = ++token;
  try {
    const html = await ({ slayer, clues, minigames: minigame }[tab])();
    if (mine === token) OSRS.setHTML(view, html);
  } catch {
    if (mine === token) OSRS.setHTML(view, '<div class="card small">This reference data is not available offline yet.</div>');
  }
}

tabs.forEach(b => b.addEventListener("click", () => {
  tab = b.dataset.tab;
  tabs.forEach(x => x.setAttribute("aria-selected", String(x === b)));
  pick.replaceChildren();
  render();
}));
pick.addEventListener("change", render);
render();
