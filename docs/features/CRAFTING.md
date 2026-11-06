# Crafting & Production — PASS31.33

Offline recipe browser for production skills. Source policy is **2009Scape primary → OSRS Wiki secondary → unknown**.

## Recipe catalog

`site/data/recipes.json` currently contains:

- **167** 2009Scape-primary **Smithing** recipes extracted from the server implementation:
  - 9 smelting recipes (ore → bar) from `smelting/Bar.java`
  - 158 anvil recipes (bar → equipment/components) from `Bars.java` + `SmithingType.java` + `BarType.java`
  - Includes full bronze through rune lines, plus blurite and precious-metal bars
  - XP, level, bar counts, and output quantities are taken from the server enums
- **202** non-conflicting OSRS Wiki secondary recipes retained from the PASS31.9 snapshot (Fletching, Crafting, Cooking, etc.)

Wiki smithing rows that duplicated a 2009Scape product ID were replaced by the primary records.

Provenance on each 2009Scape recipe points at the server source symbol (for example `Bars.java:BRONZE_PLATEBODY`).

## Runtime behavior

The page supports search, skill filtering, character skill checks, bank-material checks, item links, and truthful unknown/incomplete recipe fields. Recipe item names are resolved through the shared `Catalog.list("items")` index, with `Catalog.get("items", id)` detail lookup as a fallback. Recipe loading normalizes singular/plural output fields and validates every input/output reference before rendering, so a catalog lookup failure is visible in the summary instead of silently dropping a recipe name.

## Regeneration

Reproducible generator:

```text
data-pipeline/generate_smithing_recipes.py
```

It merges 2009Scape smithing definitions with the previous Wiki secondary snapshot and writes `site/data/recipes.json`.

## Deliberate gaps

- Other production skills (beyond the retained Wiki secondary rows) are not yet fully 2009Scape-primary.
- Silver/gold jewellery moulding and some specialty smithing remain secondary or absent until dedicated server content is extracted.
