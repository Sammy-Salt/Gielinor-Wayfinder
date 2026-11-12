# PASS31.58 — Minigames part 3: Fishing Trawler and Gnome Restaurant (2026-11-11)

Extends `site/data/minigames.json` (now 8 minigames, 126 rows) via `data-pipeline/generate_minigames.py` (2009Scape commit 4082f9d).

- **Fishing Trawler** (`TrawlerLoot.kt`, `FishingTrawlerInteractionHandler.kt`, `FishingTrawlerSession.kt`): requires 15 Fishing. The 15-row weighted loot table (total weight 2078: "fish" 1430, nine junk items, the two half-keys at 7, casket 60, pirate's hat and lucky cutlass at 2 — the source marks the last group as inauthentic), the nine trawler fish with Fishing levels, and the rules: rolls = ceil(ship fish ÷ players) with 3 fish added per catch, a "fish" result tries every fish you have the level for with chance (level − 15) × (0.7852 − 0.6133) ÷ 84 + 0.6133, Fishing xp = 0.015 × level² × rolls, and loot goes to the bank.
- **Gnome Restaurant** (`GnomeCookingJob.kt`): the 15 delivery customers (8 easy, 7 hard) with NPC ids and locations. Tip tables are not modelled: their weighted-item argument order is ambiguous in source and nothing is guessed.

Not modelled: Shades of Mort'ton, Barbarian Assault, Trouble Brewing and Puro-Puro have almost no reward data in the server source (area/dialogue code only); Sorceress's Garden, Vinesweeper, Fist of Guthix, Bounty Hunter, Duel/Clan Wars, Great Orb Project, All Fired Up, Barrows crypt mechanics and MTA enchant-spell data remain candidates.

Gate: `tests/test_pass31_58.py`.
