/**
 * Character-aware recipe check. Pure functions (no imports) so Node tests can run them.
 *
 * A recipe is "ready" when the static skill level meets the recipe level, inventory + bank + equipment
 * hold every input and every tool that has an item id, every quest requirement is complete, and every
 * unlock requirement is satisfied by the save's attributes. Anything that cannot be decided from the
 * loaded save is reported in `unverified` instead of being silently passed or failed.
 */
export function buildHoldings(snapshot) {
  const held = new Map();
  for (const key of ["inventory", "bank", "equipment"]) {
    for (const row of snapshot?.[key] || []) {
      const id = Number(row?.id);
      const amount = Number(row?.amount);
      if (!Number.isFinite(id) || !Number.isFinite(amount) || amount <= 0) continue;
      held.set(id, (held.get(id) || 0) + amount);
    }
  }
  return held;
}

export function buildLevels(snapshot) {
  const levels = new Map();
  for (const skill of snapshot?.skills || []) {
    const name = String(skill?.name || "").toLowerCase();
    if (name) levels.set(name, Math.max(1, Number(skill.level ?? skill.static) || 1));
  }
  return levels;
}

/**
 * Quest and unlock context from a snapshot.
 * `quests`: lowercase name -> completed. `known`: quest names a save can record (the quest table), or null if unknown.
 * `attributes`: saved game attributes, or null when the snapshot has none to read (e.g. the bundled demo save).
 */
export function buildContext(snapshot, knownQuestNames = null) {
  const quests = new Map();
  for (const q of snapshot?.quests?.items || []) quests.set(String(q.name).toLowerCase(), q.completed === true);
  const known = knownQuestNames ? new Set([...knownQuestNames].map((n) => String(n).toLowerCase())) : null;
  const attributes = snapshot?.attributes && typeof snapshot.attributes === "object" ? snapshot.attributes : null;
  return { quests, known, attributes };
}

/**
 * @param {object} recipe
 * @param {Map<string,number>} levels
 * @param {Map<number,number>} held
 * @param {{quests:Map<string,boolean>, known:Set<string>|null, attributes:object|null}} [ctx]
 */
export function assess(recipe, levels, held, ctx = null) {
  const skill = String(recipe.skill || "").toLowerCase();
  const alias = skill === "ranged" ? "range" : skill;
  const level = Number(levels.get(skill) ?? levels.get(alias) ?? 1);
  const need = Number(recipe.level || 0);
  const levelOk = level >= need;

  const missing = [];
  for (const input of recipe.inputs || []) {
    const wanted = Number(input.quantity || 1);
    const have = Number(held.get(Number(input.itemId)) || 0);
    if (have < wanted) missing.push({ itemId: Number(input.itemId), need: wanted, have });
  }

  const missingTools = [];
  const toolIds = [...new Set((recipe.toolItemIds || []).map(Number))];
  for (const id of toolIds) if (!(held.get(id) > 0)) missingTools.push(id);

  const unverified = [];
  if ((recipe.tools || []).length > toolIds.length) unverified.push("tools");

  const quests = [];
  const unlocks = [];
  for (const req of recipe.requirements || []) {
    if (req.type === "quest") {
      const key = String(req.name).toLowerCase();
      if (!ctx) { unverified.push(`quest ${req.name}`); continue; }
      if (ctx.known && !ctx.known.has(key) && !ctx.quests.has(key)) { unverified.push(`quest ${req.name} (not recorded in 2009Scape saves)`); continue; }
      if (ctx.quests.get(key) !== true) quests.push(req.name);
    } else if (req.type === "unlock") {
      if (!ctx || !ctx.attributes) { unverified.push(req.name); continue; }
      if (!(Number(ctx.attributes[req.attribute] || 0) >= Number(req.min ?? 1))) unlocks.push(req.name);
    } else {
      unverified.push(req.name || "requirement");
    }
  }

  const ready = levelOk && missing.length === 0 && missingTools.length === 0 && quests.length === 0 && unlocks.length === 0;
  return { ready, levelOk, level, need, missing, missingTools, quests, unlocks, unverified };
}

/** Badge text for a result; `label(id)` resolves an item name. */
export function describe(result, label = (id) => `Item ${id}`) {
  const unverified = result.unverified?.length ? ` · can't verify: ${result.unverified.join(", ")}` : "";
  if (result.ready) return { cls: "ready", text: `✓ Ready to make${unverified}` };
  const parts = [];
  if (!result.levelOk) parts.push(`Level ${result.need} needed (you: ${result.level})`);
  if (result.missing.length) parts.push("Missing " + result.missing.map((m) => `${m.need - m.have} × ${label(m.itemId)}`).join(", "));
  if (result.missingTools?.length) parts.push("Missing tool: " + result.missingTools.map((id) => label(id)).join(", "));
  if (result.quests?.length) parts.push("Quest not complete: " + result.quests.join(", "));
  if (result.unlocks?.length) parts.push("Not unlocked: " + result.unlocks.join(", "));
  return { cls: "missing", text: parts.join(" · ") + unverified };
}
