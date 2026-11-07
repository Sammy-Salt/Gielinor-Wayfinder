# Fletching and Staff Recipes Data Pass — 2026-11-07

## Scope

This pass extends the authoritative 2009Scape recipe pipeline beyond Smithing. It adds deterministic extraction for Fletching production and elemental battlestaff creation while preserving the current Wiki-secondary recipes and the newer 2009Scape Smithing, shop, NPC, spawn, and drop data already on `main`.

## Generator

Added `data-pipeline/generate_fletching_recipes.py`.

The generator reads these authoritative upstream definitions:

- `fletching/log/LogCraftInfo.kt` — arrow shafts, unstrung bows, composite bows, and crossbow stocks;
- `fletching/stringing/StringableCraftInfo.kt` — stringing bows and crossbows;
- `fletching/arrow/ArrowCraftInfo.kt` — tipped arrows;
- `fletching/arrow/HeadlessArrowCraftScript.kt` — headless arrows;
- `fletching/arrow/FlightedOgreArrowCraftScript.kt` — flighted ogre arrows;
- `fletching/bolts/BoltCraftInfo.kt` — feathered bolts;
- `fletching/darts/DartCraftInfo.kt` — feathered darts;
- `fletching/crossbow/UnfinishedCrossbowCraftInfo.kt` — crossbow limb assembly;
- `crafting/BattlestaffListener.kt` — air, water, earth, and fire battlestaves.

Recipes are merged by skill, output item, and normalized input quantities. Equivalent existing secondary records are replaced by the authoritative record instead of duplicated. Repeated generator runs are idempotent and do not duplicate source metadata.

## Coverage

The generated primary records contain:

- 75 Fletching recipes;
- 4 elemental battlestaff recipes;
- 20 unstrung bow, stock, and shaft outputs;
- 13 bow/crossbow stringing outputs;
- 8 tipped arrow outputs plus headless and flighted ogre arrows;
- 9 feathered bolt outputs;
- 7 dart outputs;
- 7 unfinished crossbow outputs;
- 4 battlestaff outputs.

Examples now available include shortbow, longbow, oak through magic bows, bronze through dragon arrows, headless arrows, flighted ogre arrows, crossbows, and elemental battlestaves.

The recipe catalog now contains 448 total records, including the prior 369 records and the 79 new authoritative production records.

## Data semantics

- Arrow shafts produce 15 shafts per log, matching the upstream script.
- Ogre arrow shafts are represented as quantity 4 with an explicit variable-output note because the upstream runtime chooses a random quantity from 2–6.
- Flighted ogre arrows consume one ogre arrow shaft and four feathers.
- Bow stringing uses bow string item 1777; crossbow stringing uses crossbow string item 9438.
- Battlestaves consume one battlestaff and one elemental orb and use the upstream XP values.
- All generated records include source file, enum, provider, and uploaded source commit provenance.

## Regression coverage

Added `tests/test_pass31_37.py`, checking:

- all 75 generated Fletching records;
- all four battlestaff records;
- bow and stringing output coverage;
- bronze through rune/dragon arrow coverage;
- headless and flighted ogre arrow inputs;
- elemental battlestaff inputs and outputs;
- 2009Scape provenance and item-detail resolution.

Validation result:

```text
PASS31.37 data gate: recipes=448 fletching=75 battlestaves=4 outputsChecked=30
```

The repository verifier, existing crafting catalog gate, direct regression scripts, Python compilation, JSON validation, and whitespace checks are run before publishing.
