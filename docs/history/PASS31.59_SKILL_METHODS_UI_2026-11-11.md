# PASS31.59 — Skill Calculator training methods (2026-11-11)

First UI use of the 2009Scape-derived data. `site/skill-stats.html` / `js/pages/skill-stats.js` gain a "training methods" table for Woodcutting, Mining, Fishing, Firemaking (`gathering.json`), Thieving, Agility, Hunter and Farming.

- Rows are built at runtime from the offline JSON (name, level, xp, note). Fishing/Firemaking rows have no name in the data, so the item catalog supplies it.
- Rows above the entered current level are greyed; tapping a row copies its xp into "XP per action" and recalculates. The current level starts from the saved character when one exists.
- Farming xp is planting + one harvest; Agility courses show xp per lap; shortcut rows show their xp.
- Offline: the five data files and `items/name-index.json` are added to the service-worker shell. No new page, so navigation and verifier page counts are unchanged.

Not done: Slayer, Cooking/Smithing methods, multi-harvest farming totals, and per-method actions-per-hour (the calculator's existing field stays manual).

Gate: `tests/test_pass31_59.py`.
