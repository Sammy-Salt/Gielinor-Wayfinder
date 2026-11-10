# PASS31.53 — Farming data (2026-11-10)

Adds `site/data/farming.json` (61 crops, 13 patch types, 45 patches, plus yield rules) via `data-pipeline/generate_farming.py` (2009Scape commit 4082f9d).

- **Crops** (`Plantable.kt`): level, planting / harvest / check-health xp, seed and harvest item ids, patch type, growth stages, protection payment (items the farmer takes) and protection flower. `growthMinutes = stages × minutes-per-stage` is derived (growth ticks run on 5-minute cycles, so real times can be a few minutes shorter, as the server notes).
- **Patch types** (`PatchType.kt`): minutes per growth stage. **Patches** (`FarmingPatch.kt`): 45 patches with their varbit ids; display names are derived from the enum names (the enum key is authoritative).
- **Rules** (`Patch.kt`): base crop lives 3, compost bonus (Compost +1, Supercompost +2 to harvest amount and lives), per-crop base amounts (limpwurt/woad 3, mushroom 6), and the per-pick life-loss chances for allotments/hops/cactus. Every literal is checked against the source.

Source facts kept as found: the Scarecrow is in the crop enum with stages `-3`, so it is marked `kind: "scarecrow"` with no growth time; the spirit tree payment has three items; the life-loss chances are marked inauthentic averages in the source.

Not shipped yet: disease/death chances, patch coordinates, seed-to-yield calculators, and any UI reading this file.

Gate: `tests/test_pass31_53.py`.
