# PASS31.36 — Shops rebuilt from 2009Scape (2026-11-07)

Source: 2009Scape `4082f9d` `shops.json`, `npc_spawns.json`. Policy: 2009Scape → OSRS Wiki → unknown.

## What changed
- **New canonical `site/data/shops.json`**: 245 shops, 2,481 stock lines with real item ids, amounts (`-1` = unlimited) and restock rates, currency, general-store and high-alchemy flags, and owning NPC ids.
- **OSRS-only shops removed**: the 405 wiki shops are replaced; 246 of them did not exist in 2009Scape. Item `_acquisition.shops` was rebuilt from the new list: 1,030 items now list the shops that stock them (previously 155, name-matched from wiki data).
- **Map**: `map/shops.js` regenerated with 266 markers placed at each shopkeeper's real spawn (including plane). Boundary hashes updated; no map code changed.
- **NPC/monster pages** show each shopkeeper's shops with linked stock (`js/services/shop-service.js`). 22 shopkeepers missing from the catalog were added as NPC records.
- `shopType` is a PWA classification (not a 2009Scape field): carried over by title from the previous catalog, else "General store" / "Other". 104 shops are "Other".
- Derived indexes, search, graph and counts regenerated. Release PASS31.36.

## Known gaps
- 25 shops have no map marker because no listed shopkeeper has a spawn (stalls, chests, minigame shops): ids 5, 26, 28, 53, 72, 93, 119, 146, 162, 177, 178, 182–185, 198, 200, 201, 226, 241, 251–254, 257.
- Shop prices are not stored; they derive from item value in game. Special-currency shops show the currency item id only.
- `generate_acquisition.py` (wiki-NPC shop path) is obsolete and must not be rerun.
