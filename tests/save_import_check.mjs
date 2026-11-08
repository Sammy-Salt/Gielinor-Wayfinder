// Executed by tests/test_pass31_45.py. Exercises the real save-import parser under Node with a synthetic save.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
globalThis.window = globalThis;
globalThis.localStorage = { _d: {}, getItem(k) { return this._d[k] ?? null; }, setItem(k, v) { this._d[k] = String(v); }, removeItem(k) { delete this._d[k]; } };
const { normalizeSave } = await import(path.join(root, 'site/js/services/save-import.js'));
const raw = JSON.parse(readFileSync(path.join(root, 'tests/fixtures/save_core_data.synthetic.json'), 'utf8'));
const fail = (m) => { console.error('FAIL: ' + m); process.exit(1); };
const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) fail(`${m}: got ${JSON.stringify(a)} expected ${JSON.stringify(b)}`); };

const s = normalizeSave(raw, { fileName: 'fixture_player.json' });
eq(s.formatVersion, 2, 'formatVersion');
eq(s.player.name, 'fixture_player', 'name');
eq(s.source.importMode, 'raw-2009scape', 'importMode');
eq(s.location, { x: 3222, y: 3218, plane: 0 }, 'location x,y,plane');
const sk = Object.fromEntries(s.skills.map(x => [x.name, x]));
eq([sk.Attack.level, sk.Attack.dynamicLevel, sk.Attack.xp], [60, 58, 273742], 'Attack');
eq([sk.Hitpoints.level, sk.Hitpoints.dynamicLevel], [62, 55], 'Hitpoints static/dynamic');
eq(sk.Cooking.level, 40, 'Cooking id 7');
eq(sk.Crafting.level, 55, 'Crafting id 12');
eq(sk.Herblore.level, 30, 'Herblore id 15');
eq(sk.Runecrafting.level, 20, 'Runecrafting id 20');
eq(s.inventory.map(i => [i.id, i.amount]), [[995, 12500], [1755, 1], [1733, 1]], 'inventory (string numbers)');
eq(s.bank.map(i => [i.id, i.amount]), [[1741, 250], [1734, 100]], 'bank');
eq(s.equipment.map(i => i.id), [1277], 'equipment');
eq(s.quests.questPoints, 7, 'quest points');
eq(s.quests.items.filter(q => q.completed).map(q => q.name), ['Sheep Shearer', 'Vampire Slayer'], 'completed quests');
eq(s.quests.items.find(q => q.id === 14).completed, false, 'Rune Mysteries in progress');
eq(s.player.totalXP, raw.skills.reduce((n, x) => n + Number(x.experience), 0), 'totalXP sums skills');

// normalized snapshots pass through untouched
const again = normalizeSave(s, { fileName: 'x.json' });
eq(again.skills.length, s.skills.length, 'normalized passthrough');
eq(again.source.importMode, 'normalized', 'passthrough mode');

// rejections
for (const [bad, label] of [[[], 'array'], [{ hello: 1 }, 'unrecognized'], [{ version: 4, skills: [], core_data: {} }, 'no skills']]) {
  let threw = false;
  try { normalizeSave(bad); } catch { threw = true; }
  if (!threw) fail(`${label} should be rejected`);
}
console.log('save-import check: OK');
