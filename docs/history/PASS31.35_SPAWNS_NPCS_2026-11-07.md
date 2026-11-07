# PASS31.35 — NPC catalog, spawns and ground spawns from 2009Scape (2026-11-07)

Source: 2009Scape `4082f9d`, `npc_configs.json`, `npc_spawns.json`, `ground_spawns.json`. Policy: 2009Scape → OSRS Wiki → unknown.

## What changed
- **NPC catalog rebuilt in 2009Scape ids**: 1,646 NPCs (every named upstream NPC with a spawn that is not already a monster). The old 6,804-record catalog was OSRS-Wiki data in a different id space and is removed.
- **Spawns**: monsters now take locations from `npc_spawns.json` (1,409 monsters, 8,950 spawns); NPCs have 4,384 spawns. Every spawn carries its **plane**, so upper-floor and dungeon markers no longer collapse onto plane 0.
- **Field fix**: spawn tokens are `{x,y,plane,walks,direction}` (NPCSpawner.kt). The shipped fields `face`/`walk` were these last two tokens under wrong names; they are now `walks` (bool) and `direction`.
- **Ground spawns**: 173 items (713 points) go from unknown to known; the item page lists coordinates, plane, amount and respawn ticks. Items with no upstream ground spawn stay unknown. Four upstream ground-spawn item ids (357, 2408, 4615, 5008) are not in the item catalog.
- **Map data**: `map/npcs.js` and `map/monsters.js` regenerated from the catalogs; `audit/map-boundary.sha256` updated for those two files. No map code changed.
- NPC and monster pages group spawns by floor and show the plane. Derived indexes, search index, graph and counts regenerated. Release PASS31.35.

## Known gaps / next
- NPC `aliases`, `options` (interaction menu) and `shops` links were wiki data and are dropped/empty; options need cache parsing, shops come in Pass C.
- Monsters without a spawn upstream keep their previous locations.
- Map: marker clustering and the `map.html` module/classic-script errors are still open.
