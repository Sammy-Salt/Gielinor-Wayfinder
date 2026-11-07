# 2009Scape drop roll mechanics

**Status: traced from upstream `master` on 2026-11-07. No generator change.**

This is the rule set `data-pipeline/generate_drop_relationships.py` must follow. The read-only checker is `scripts/validate_drop_relationships.py`. It does not rewrite `site/`.

Sources, all on `https://gitlab.com/2009scape/2009scape` branch `master`:

- `Server/src/main/core/game/system/config/DropTableParser.kt`
- `Server/src/main/core/api/utils/NPCDropTable.kt`
- `Server/src/main/core/api/utils/WeightBasedTable.kt`
- `Server/src/main/core/api/utils/WeightedItem.kt`
- `Server/src/main/core/game/node/entity/npc/drop/NPCDropTables.java`
- `Server/src/main/content/data/tables/RareDropTable.kt`
- `Server/src/main/core/tools/RandomFunction.java`

The pinned payload is `site/data/sources/2009scape/drop_tables.json` (444 tables, SHA-256 recorded in `drop_tables.manifest.json` and `site/data/relationships/index.json`).

## What actually runs on death

`NPC.handleDrops` calls `NPCDropTables.drop`, which calls `table.roll(looter, 1)` once. The legacy `DROP_RATES = {750, 150, 15, 5}` array and `modRate` are not used by that path.

`DropTableParser` builds one `NPCDropTable` per JSON object and assigns it to every NPC id in `ids`. A later JSON object that repeats an NPC id replaces the whole table. The pinned file has **no NPC id on more than one table**, so last-wins and merge currently describe the same NPCs. The generator still merges by summing weights and keeping the first table's total; that is a latent bug, not a current numerical error.

`NPCDropTable.roll` always performs three independent rolls:

1. charm table, one weighted roll
2. tertiary table, one weighted roll
3. main table, every default entry, then one weighted roll

Charms are not in the main pool. Tertiary entries are not independent extra rolls. Each tertiary table contributes at most one selected row per kill.

## Weight roll

`WeightBasedTable.add` keeps guaranteed rows out of `totalWeight`. Everyone else is `weight / totalWeight`, using `RandomFunction.randomDouble(totalWeight)`, which is `[0, totalWeight)`.

`id: 0` is the explicit "nothing" row (`DWARF_REMAINS_0`). It counts toward the category total and is then discarded, both by `convertWeightedItems` and by `NPCDropTables.createDrop`. The generator does the same: include it in the denominator, do not emit a relationship.

A zero-weight row has probability 0. It can be chosen only if the draw is exactly 0 and that row is first; the draw is continuous, so that chance is zero. The pinned file has 10 zero-weight rows, all charms. They expand to charm relationships whose stored probability is 0 and whose display is `Rate unavailable`. Keep them. Do not delete them to tidy the table.

## Category rules

| JSON key | Where it goes | Chance of that row |
|---|---|---|
| `main` | weighted main table | row weight / sum of main weights |
| `charm` | separate weighted table | row weight / sum of charm weights |
| `tertiary` | separate weighted table, still one roll | row weight / sum of tertiary weights |
| `default` | guaranteed list on the main table | always, once. Weight is ignored and does not dilute `main` |

If the same item id is on more than one of those rolls, the kill drops it if any roll hits it:

`1 - product(1 - p_category)`.

That is what the generator stores on `rate`. Per-category fractions stay on `categories[]`.

## Sentinel ids are not items

`WeightBasedTable.convertWeightedItems` replaces these ids before the item is spawned. The generator currently emits them as ordinary items. That is the open fidelity gap. Do not "fix" it by deleting the rows until the subtables are expanded on purpose.

| Id | Constant | Real outcome |
|---|---|---|
| 31 | `SLOT_RDT` / `TINDERBOX_31` | one roll on the rare drop table |
| 1 | `SLOT_CLUE_EASY` / `TOOLKIT_1` | easy clue scroll |
| 5733 | `SLOT_CLUE_MEDIUM` | medium clue scroll |
| 12070 | `SLOT_CLUE_HARD` | hard clue scroll |
| 799 | `SLOT_CELEDT` | CEL minor table |
| 14422 | `SLOT_USDT` | uncommon seed table |
| 14424 | `SLOT_HDT` | herb table |
| 14426 | `SLOT_GDT` | gem table |
| 14428 | `SLOT_RSDT` | rare seed table |
| 14430 | `SLOT_ASDT` | allotment seed table |

The rare drop table is XML (`RareDropTable.kt`), not a key in `drop_tables.json`. Access chance is the weight of id 31 on whichever category holds it, divided by that category total. The official 1/14.25 style figures are conditional on already having hit the RDT slot. `shouldRemoveNothings` (ring of wealth) subtracts the weight of id 0 from the RDT total only. It does not change the chance to reach the slot.

On the pinned payload the sentinels above occur on `main`, plus one guaranteed gem row and one guaranteed CEL row on `default`.

## Quantity bound

`WeightedItem.getItem` uses `RandomFunction.random(min, max)`. When `min == max` the amount is that number. When they differ, `random(max - min)` is `[0, max - min)`, so the configured `maxAmount` is **not rolled**. The shipped shards store the JSON min and max unchanged. That display is the configured range, not the inclusive range the server rolls.

## What was checked without regenerating

`scripts/validate_drop_relationships.py` recalculates every shipped relationship from the pinned JSON and compares exact fractions to the gzip shards. A fraction mismatch fails the script. Sentinel rows, rounded `1/X` text with `approximate: false`, and exclusive maximums are printed as findings and left in place.

`site/release.json` stays `PASS31.36`. This note does not publish a new data build.
