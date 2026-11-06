# Smithing Recipe Primary Import — 2026-11-06

## Scope

Replace the sparse Wiki-only smithing coverage with a full 2009Scape-primary smithing recipe set (smelting + anvil), while retaining non-conflicting secondary Wiki recipes for other skills.

## Source

Extracted from the 2009Scape server tree:

- `Server/src/main/content/global/skill/smithing/Bars.java`
- `Server/src/main/content/global/skill/smithing/SmithingType.java`
- `Server/src/main/content/global/skill/smithing/BarType.java`
- `Server/src/main/content/global/skill/smithing/smelting/Bar.java`
- `Server/data/configs/item_configs.json` (display names)

## Counts

| Set | Count |
|-----|------:|
| 2009Scape smelting | 9 |
| 2009Scape anvil | 158 |
| 2009Scape smithing total | 167 |
| Wiki secondary retained | 202 |
| **Merged total** | **369** |

Three Wiki smithing rows that duplicated primary product IDs (blurite bar / bolts / limbs) were superseded.

## Files

- `site/data/recipes.json` — merged catalog (`snapshot: PASS31.33-smithing-primary`)
- `data-pipeline/generate_smithing_recipes.py` — reproducible generator
- `docs/features/CRAFTING.md` — feature contract update
- `docs/history/SMITHING_RECIPES_2009SCAPE_2026-11-06.md` — this report

## Validation

- Every 2009Scape recipe has non-empty inputs, numeric level, and numeric XP
- Every input/output item ID resolves in `item_configs.json` names
- Bronze line includes dagger through platebody with correct bar counts and XP (platebody: 5 bars × 12.5 = 62.5 XP)
- JSON parses cleanly

## Non-changes

- Crafting page JS wiring (already catalog-based) was not modified
- Item detail stats / acquisition were not modified in this pass
- Map and other skill catalogs were not modified
