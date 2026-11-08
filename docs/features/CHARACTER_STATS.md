# Character / Stats — PASS31.43

PASS31.20 implemented a read-only character view against the normalized 2009Scape save snapshot. Confirmed save domains include skills/XP, inventory, equipment, bank, location, quest stages/points, spellbook, energy, prayer/lifepoints, slayer state, achievement diaries, pouches, appearance, and named character statistics. Raw unmapped variables remain outside the UI.

PASS31.43 adds **local save import** on the Character page:

- Pick a 2009Scape player `.json` (or a normalized `player-sync` snapshot).
- The app stores the normalized result and, when possible, a File System Access handle.
- On later opens, `OSRSSync.load` tries to re-read the remembered file; otherwise it reuses the cached snapshot so skills, bank, inventory, equipment, and quests stay available offline.
- Clear linked save returns to the bundled `site/data/player-sync.json` sample.

Typical desktop private-server path: `Server/data/players/<username>.json`.
