# PASS31.19 — Character Intelligence Foundation

## Scope
- 2009Scape save-backed character model
- Character/Stats page
- Inventory, equipment, bank, quests, location, diaries and statistics display
- Crafting & Production recipe browser
- Character-aware bank/skill availability checks
- Documentation and release metadata

## Source policy
2009Scape primary; OSRS Wiki secondary; Ragger retired and absent.

## Data note
The supplied `sam.json` was used to map the normalized character snapshot. The ZIP does not contain the raw save file; only normalized app data is packaged.

## Deliberate limitations
- Quest stage semantics are only labeled complete when the supplied stage is 100; other stages remain numeric.
- Recipe records are Wiki secondary data and may lack XP/level/materials where the source snapshot did not provide a resolvable value.
- Unmapped varps/attributes/global flags are retained out of the character UI until their meanings are verified.
