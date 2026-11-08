// Executed by tests/test_pass31_47.py. Exercises recipe-ready.js with the synthetic save and the shipped recipes.json.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
globalThis.window = globalThis;
globalThis.localStorage = { _d: {}, getItem(k) { return this._d[k] ?? null; }, setItem(k, v) { this._d[k] = String(v); }, removeItem(k) { delete this._d[k]; } };
const { normalizeSave } = await import(path.join(root, 'site/js/services/save-import.js'));
const { assess, describe, buildHoldings, buildLevels } = await import(path.join(root, 'site/js/services/recipe-ready.js'));
const fail = (m) => { console.error('FAIL: ' + m); process.exit(1); };
const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) fail(`${m}: got ${JSON.stringify(a)} expected ${JSON.stringify(b)}`); };

const snap = normalizeSave(JSON.parse(readFileSync(path.join(root, 'tests/fixtures/save_core_data.synthetic.json'), 'utf8')), { fileName: 'f.json' });
const levels = buildLevels(snap), held = buildHoldings(snap);
eq(levels.get('crafting'), 55, 'crafting level');
eq(held.get(1741), 250, 'bank leather counted');
eq(held.get(1755), 1, 'inventory chisel counted');
eq(held.get(1277), 1, 'equipment counted');

const recipes = Object.fromEntries(JSON.parse(readFileSync(path.join(root, 'site/data/recipes.json'), 'utf8')).recipes.map(r => [r.id, r]));
const label = (id) => ({ 1743: 'Hard leather', 1741: 'Leather' }[id] || `Item ${id}`);

let a = assess(recipes['2009scape-crafting-leather-gloves'], levels, held);
eq([a.ready, a.levelOk, a.missing.length], [true, true, 0], 'gloves ready (leather in bank, thread in bank)');
eq(describe(a, label).text, '✓ Ready to make', 'ready text');

a = assess(recipes['2009scape-crafting-leather-hard-body'], levels, held);
eq([a.ready, a.levelOk, a.missing], [false, true, [{ itemId: 1743, need: 1, have: 0 }]], 'hard body: level fine, hard leather missing');
eq(describe(a, label).text, 'Missing 1 × Hard leather', 'missing text');

a = assess({ ...recipes['2009scape-crafting-leather-coif'], level: 60 }, levels, held);
eq([a.ready, a.levelOk, a.need, a.level], [false, false, 60, 55], 'level-only failure');
eq(describe(a, label).text, 'Level 60 needed (you: 55)', 'level text');

a = assess(recipes['2009scape-crafting-dragonhide-black_d_hide_body'], levels, held);
eq([a.ready, a.levelOk, a.missing.length], [false, false, 1], 'black d-hide body: level and materials');
eq(describe(a, label).text.includes(' · '), true, 'both reasons joined');

// quantities are summed across inventory, bank and equipment
const split = { skills: [{ name: 'Crafting', level: 10 }], inventory: [{ id: 1734, amount: 1 }], bank: [{ id: 1734, amount: 1 }, { id: 1741, amount: 1 }], equipment: [] };
a = assess({ skill: 'Crafting', level: 1, inputs: [{ itemId: 1734, quantity: 2 }, { itemId: 1741, quantity: 1 }] }, buildLevels(split), buildHoldings(split));
eq(a.ready, true, 'inventory + bank summed');

// unknown skill defaults to level 1; Ranged aliases to Range
a = assess({ skill: 'Nothing', level: 2, inputs: [] }, new Map(), new Map());
eq([a.ready, a.level], [false, 1], 'unknown skill is level 1');
a = assess({ skill: 'Ranged', level: 5, inputs: [] }, new Map([['range', 9]]), new Map());
eq(a.ready, true, 'Ranged alias');
console.log('recipe-ready check: OK');
