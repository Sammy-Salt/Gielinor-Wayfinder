# PASS31.57 — Minigames part 2: Barrows, Mage Training Arena, Blast Furnace, Castle Wars (2026-11-11)

Extends `site/data/minigames.json` (now 6 minigames, 96 rows) via `data-pipeline/generate_minigames.py` (2009Scape commit 4082f9d).

- **Barrows** (`RewardChest.kt`): the 9-row regular reward table with weights (coins 380, runes/bolt racks 125 each, half-keys 3 each, dragon med helm 1; total 1012) and the six brothers' 4-piece item sets with NPC ids (2025 + index). Rule: killed brothers + 1 rolls; each roll has a 1-in-(450 − 58 × killed) chance of one random remaining brother item, otherwise one regular-table roll; repeated ids merge.
- **Mage Training Arena** (`MTAShop.java`): 24 shop items with their price in all four pizazz-point types (Telekinetic, Alchemist, Enchantment, Graveyard); an item needs every listed type. The wand upgrade slots consume the previous wand; Bones to Peaches (6926) is a one-time unlock.
- **Blast Furnace** (`BlastFurnace.kt`, `BlastConsts.kt`, `Bar.java`): 9 bars with level, xp, ores and the coal the furnace needs (half the usual: steel 1, mithril 2, adamant 3, runite 4); 60 Smithing needed to skip the 2,500 coin fee (half with Charos' ring, as in source); limits (coal 226, ore/bar 28, coke 15); pump 4.0 Strength xp, pedals 2.0 Agility xp; smithing xp is 1 per bar shared when furnace temperature is 51-66; iron ore becomes steel with coal at Smithing 30.
- **Castle Wars** (`CastleWars.kt`, shop 255 in `shops.json`): the 19-item ticket exchange, the 7 supply-table items, game length 20 min and cooldown 5 min, tickets 2 for a win / 1 for a draw (from the Lanthus dialogue).

Source limits kept honest: Castle Wars ticket prices are not in the shop config (they derive from item values), so none are invented. Not modelled yet: Fishing Trawler, Shades of Mort'ton, Barbarian Assault, Trouble Brewing, Gnome Restaurant, Puro-Puro, Sorceress's Garden, Vinesweeper, Fist of Guthix, Bounty Hunter, Duel/Clan Wars, Great Orb Project, All Fired Up, Barrows crypt/tunnel mechanics, MTA enchant-spell data.

Gate: `tests/test_pass31_57.py`.
