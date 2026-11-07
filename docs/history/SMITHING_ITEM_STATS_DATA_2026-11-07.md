# Smithing and Item Stats Data Pass — 2026-11-07

## Scope

This pass adds authoritative 2009Scape Smithing production data and makes compound item combat fields usable without discarding the original upstream strings. It proceeds from the current `main` branch and uses the uploaded 2009Scape source snapshot as the primary source.

## Files added

### `data-pipeline/generate_smithing_recipes.py`

Added a deterministic parser and merger for the upstream Smithing enums:

- `Bars.java` supplies every Smithing product, bar material, product ID, and Smithing level.
- `SmithingType.java` supplies required bar quantities and product quantities.
- `BarType.java` supplies bar item IDs and Smithing XP per bar.

The generator parses 157 authoritative Smithing entries and merges them into the existing recipe envelope without duplicating equivalent input/output recipes. Equivalent secondary records are replaced by the authoritative record so provenance is not lost. Each generated recipe includes Hammer and Anvil metadata plus 2009Scape provenance.

### `data-pipeline/normalize_item_catalog.py`

Added a non-destructive normalizer for the shipped per-item catalog. It preserves existing acquisition data and raw upstream values while adding:

- `bonusesRaw` — the original 15-value comma-separated string;
- `bonusStats` — labeled combat/stat fields;
- `requirementsRaw` — the original requirement string;
- `requirementsParsed` — numeric `{typeId, level}` pairs.

The bonus ordering follows the 2009Scape combat implementation: five attack values, five defence values, summoning, strength, prayer, magic strength, and ranged strength.

### `data-pipeline/extract_authoritative_catalogs.py`

Updated the authoritative extractor to emit the same structured item fields in generated catalogs. This keeps fresh extraction output consistent with the shipped normalized catalog.

### `tests/test_pass31_33.py`

Added a regression gate covering:

- all 157 authoritative Smithing recipes;
- Bronze sword, platebody, platelegs, full helm, dagger, and scimitar outputs;
- output-item resolution;
- Blurite bolt ranged-strength parsing;
- requirement pair parsing;
- normalized bonus-key coverage across the item catalog.

## Shipped data changes

- Recipe count increased from 205 to 360.
- 157 authoritative 2009Scape Smithing recipes are now available.
- Equivalent secondary Smithing recipes were upgraded to authoritative provenance rather than duplicated.
- 2,969 item records now include labeled `bonusStats`.
- 1,882 item records now include parsed numeric requirements.
- Existing `_acquisition` records remain present.

Examples now available through the crafting catalog include Bronze sword (1277), Bronze platebody (1117), Bronze platelegs (1075), Bronze full helm (1155), Bronze dagger (1205), and Bronze scimitar (1321).

## Validation

```text
PASS31.33 data gate: recipes=360 authoritativeSmithing=157 normalizedBonusItems=2969 outputsChecked=6
```

The scripts were compile-checked and run against the uploaded source. The item normalizer was run against all 11,978 shipped item detail files.

## Deliberate non-changes

Requirement `typeId` values remain numeric because the uploaded item config does not provide a verified universal name mapping for every pair. The raw value is retained so a later mapping pass can be added without data loss. The item detail UI is not changed in this data-only pass; the structured fields are ready for the next presentation update.
