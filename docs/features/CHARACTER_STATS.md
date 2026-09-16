# Character / Stats — PASS31.20

PASS31.20 implements a read-only character view against the normalized 2009Scape save snapshot. Confirmed save domains include skills/XP, inventory, equipment, bank, location, quest stages/points, spellbook, energy, prayer/lifepoints, slayer state, achievement diaries, pouches, appearance, and named character statistics. Raw unmapped variables remain outside the UI.

The PWA consumes `site/data/player-sync.json` through `OSRSSync`; the raw 2009Scape format is treated as an external source contract.
