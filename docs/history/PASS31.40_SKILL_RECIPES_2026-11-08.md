# PASS31.40 — Herblore, Crafting, Cooking and Runecrafting recipes from 2009Scape

Source policy: 2009Scape first. Every new row is parsed from the server source (commit 4082f9d) by `data-pipeline/generate_skill_recipes.py`; no wiki values are used. Smithing (PASS31.33) and Fletching/staffs (PASS31.37) are untouched, and the four `2009scape-crafting-battlestaff-*` rows are explicitly preserved.

| Skill | Rows | Source files |
| --- | --- | --- |
| Herblore | 146 | `Herbs.java`, `UnfinishedPotion.kt`, `FinishedPotion.kt`, `Tars.java`, `BarbarianPotion.kt`, `GrindingItem.java` |
| Crafting | 102 | gems, pottery (shape + fire), spinning, glass (incl. molten glass), silver (+ stringing), jewellery, dragonhide, soft/hard leather, snakeskin |
| Cooking | 61 | `CookableItems.java` |
| Runecrafting | 20 | `Rune.java` (14 runes), `CombinationRune.java` (6) |

`recipes.json` now holds 775 recipes. Two wiki Cooking rows with the same output/inputs were replaced by the 2009Scape rows; no other existing row changed.

## Deliberate exclusions
- `ROOT5` spinning (input 6053 is not in the item catalog) and `UGTHANKI` cooking (identical ids to CHICKEN; the server keeps CHICKEN) are listed in `SKIP_ENUMS`.
- Cooking omits seaweed, barley, oomlie raw, sinew drying and nettle tea (not cooking-skill recipes). Burnt results are not modelled because burnt items are not in the catalog.
- Dough, pie/pizza/cake assembly, stews, wine fermenting, amulet stringing of gold jewellery, studded armour, tanning, weaving and snelms remain unextracted. The 7 non-2009 wiki Herblore rows (waking sleep vial, chemical compound, serum 208, dream potion) are left as wiki-secondary.
- Combination runes record pure essence plus the second rune; the talisman/imbue and the 1-in-3 chance per essence are in the method text.

## Also in this pass
- Refreshed `audit/map-boundary.sha256` after the collapsible map-tools changes by other contributors had left it stale (pytest was failing on main).
- Release bumped to PASS31.40; `tests/test_pass31_40.py` added; earlier pass gates widened to accept PASS31.40.
