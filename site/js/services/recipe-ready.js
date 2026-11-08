/**
 * Character-aware recipe check. Pure functions (no imports) so Node tests can run them.
 * A recipe is "ready" when the character's static skill level meets the recipe level and
 * inventory + bank + equipment together hold every input. Tools are not checked: many
 * recipe rows list tool names only, so a tool check would be inconsistent across rows.
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

/** @returns {{ready:boolean, levelOk:boolean, level:number, need:number, missing:{itemId:number, need:number, have:number}[]}} */
export function assess(recipe, levels, held) {
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
  return { ready: levelOk && missing.length === 0, levelOk, level, need, missing };
}

/** Short badge text for a result; `label(id)` resolves an item name. */
export function describe(result, label = (id) => `Item ${id}`) {
  if (result.ready) return { cls: "ready", text: "✓ Ready to make" };
  const parts = [];
  if (!result.levelOk) parts.push(`Level ${result.need} needed (you: ${result.level})`);
  if (result.missing.length) {
    parts.push("Missing " + result.missing.map((m) => `${m.need - m.have} × ${label(m.itemId)}`).join(", "));
  }
  return { cls: "missing", text: parts.join(" · ") };
}
