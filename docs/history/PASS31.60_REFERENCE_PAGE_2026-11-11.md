# PASS31.60 — Reference page: Slayer, clue rewards, minigames (2026-11-11)

New offline page `site/reference.html` (Encyclopedia menu → "📘 Reference") reading `slayer.json`, `clues.json` and `minigames.json`.

- **Slayer:** choose a master to see every assignable task with Slayer/combat requirement, chance (weight ÷ total), amount range and quest gate, plus reward costs and the point/assignment rules.
- **Clue rewards:** easy/medium/hard/rare tables with item names, quantities and chance per roll, plus steps-per-trail and the roll rules.
- **Minigames:** all 8 modelled minigames, each with its reward/shop/loot/room/bar tables and the rules extracted from source.
- Item names come from the item catalog (name index first, then per-item files); the three data files and the page are in the service-worker shell. Verifier page count is now 23. The Reference link is in every page's menu except `map.html`, which is frozen by `audit/map-boundary.sha256`; reach it from any other page.

Not done: item links to the item pages, per-slot clue step lists, minigame tables for unmodelled games.

Gate: `tests/test_pass31_60.py`.
