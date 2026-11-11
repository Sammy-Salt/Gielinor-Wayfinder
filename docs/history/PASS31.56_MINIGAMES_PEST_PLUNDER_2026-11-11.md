# PASS31.56 — Minigames part 1: Pest Control and Pyramid Plunder (2026-11-11)

Adds `site/data/minigames.json` via `data-pipeline/generate_minigames.py` (2009Scape commit 4082f9d). The server's minigame logic lives in code, so each minigame has its own parser with rule-literal assertions; more minigames are added by extending the same generator and file.

- **Pest Control** (`PCRewardInterface.java`): the Void Knight commendation shop — 7 experience conversions, Herb/Mineral/Seed packs (25 Herblore/Mining/Farming), Void Knight top/robes/mace/gloves/3 helms (42 in all combat stats and Magic/Ranged, 22 Prayer) and the seal, and the Spinner/Ravager/Torcher charms (2/28/56 points for 1/14/28). The xp rule is `points × floor(level² ÷ 600) × N × bonus`: N is Prayer 18, Magic/Ranged 32, Attack/Strength/Defence/Hitpoints 35; bonus 1.01 from 10 points and 1.1 from 100.
- **Pyramid Plunder** (`PlunderUtils.kt`, `PlunderData.kt`): 8 rooms with Thieving requirement (11 + 10 × room), urn/sarcophagus/chest/door xp, spear direction, entrance and mummy tiles; artifact tiers (common/stone/gold) and the roll rule; Pharaoh's sceptre odds by room (1-in-1500/1350/1250/1150, then 1-in-1000).

Source facts kept as found: the xp-per-point division is integer arithmetic before the multiply by N; the shop text says "Must reach level 25 first" for xp but the confirm path does not enforce it (only displayed); chest and door xp are 66% of the open xp, and lockpicked doors give half.

Not modelled yet (next passes extend this file): Barrows, Mage Training Arena, Castle Wars, Blast Furnace, Fishing Trawler, Shades of Mort'ton, Barbarian Assault, Trouble Brewing, Gnome Restaurant, Puro-Puro, Sorceress's Garden, Vinesweeper, Fist of Guthix, Bounty Hunter, Duel/Clan Wars, Great Orb Project, All Fired Up.

Gate: `tests/test_pass31_56.py`.
