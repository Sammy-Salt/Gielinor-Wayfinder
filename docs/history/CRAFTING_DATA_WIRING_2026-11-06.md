# Crafting Data Wiring Change Report — 2026-11-06

## Scope

This change fixes the crafting page's runtime data wiring so recipe rows resolve their item names through the shared generated item catalog instead of issuing one independent item request per recipe reference. It also makes recipe loading more tolerant of catalog/schema evolution and makes unresolved references visible rather than silently hiding lookup failures.

The current shipped recipe source remains the existing PASS31.9 OSRS Wiki snapshot. This pass does not claim that the recipe definitions themselves have been replaced with 2009Scape definitions. It wires those recipe records to the canonical generated item catalog already shipped under `site/data/items/`.

## Files changed

### `site/js/pages/crafting.js`

Replaced the previous compact loader and renderer with an explicit data-loading pipeline.

#### Shared catalog loading

The page now loads the item index through the shared catalog service:

```javascript
const catalog = await OSRS.Catalog.list("items");
```

This uses the existing offline-capable `Data.list("items")` path and the generated `site/data/items/index.json` catalog rather than reconstructing item names through ad-hoc requests.

If a recipe reference is absent from the index, the page attempts the canonical detail endpoint through:

```javascript
await OSRS.Catalog.get("items", id);
```

This preserves compatibility with catalogs where a detail record exists but the compact index is incomplete.

The loader records any remaining unresolved IDs in `unresolvedItemIds`. The recipe list still renders, but the summary reports the unresolved count so the failure is visible instead of silently replacing names without explanation.

#### Recipe normalization

Added normalization for recipe records before rendering:

- Validates that every recipe is an object.
- Accepts the existing singular `output` field.
- Accepts a future/generated plural `outputs` array.
- Normalizes output and input item references from `itemId`, `id`, or scalar IDs.
- Validates positive quantities.
- Normalizes `skill` and `skills` into a consistent skills array.
- Normalizes missing IDs using a deterministic fallback recipe ID.
- Preserves level, XP, provenance, tools, facilities, and other source fields.

The normalized recipe always exposes:

```javascript
{
    inputs: [...],
    outputs: [...],
    output: outputs[0],
    skill,
    skills
}
```

This keeps the current UI compatible while allowing generated recipe records to contain multiple outputs.

#### Rendering changes

The renderer now:

- Searches across all output names, input names, and skill names.
- Renders all normalized outputs as item links.
- Uses canonical catalog names first and source-provided names as fallback.
- Shows XP when available instead of omitting it.
- Escapes item names, skills, source labels, quantities, and links.
- Keeps the existing skill filter and bank-material readiness check.
- Displays recipe count, indexed count, catalog size, and unresolved catalog-reference count in the summary.

The bank check continues to use the player's current bank and the normalized input item IDs. Character skill levels continue to come from `OSRSSync`.

#### Error handling

The page now reports explicit errors for:

- Missing or malformed recipe arrays.
- Recipes without outputs.
- Invalid input/output item references.
- Invalid item quantities.
- A malformed item catalog index.

The existing page-level error summary remains in place for unrecoverable catalog or recipe failures.

### `docs/features/CRAFTING.md`

Updated the permanent crafting feature documentation to record that recipe item names are resolved through the shared item catalog index with detail-file fallback, and that singular/plural recipe output fields are normalized before rendering.

The documentation continues to identify the current recipe snapshot as OSRS Wiki secondary data, consistent with the repository source policy.

### `tests/test_pass31_32.py`

Added a focused regression gate that verifies:

- Every shipped recipe has an output item ID.
- Every input has an item ID.
- Every recipe input/output ID exists in `site/data/items/index.json`.
- Every referenced item has a corresponding detail JSON file.
- `crafting.js` uses the shared catalog index and detail fallback.
- Recipe normalization and unresolved-reference reporting remain present.
- The rewritten module passes Node syntax validation.

### `release-manifest.json` and `site/release-manifest.json`

Regenerated both integrity manifests after the shipped `crafting.js` change. The site manifest now records the rewritten crafting module at 8,313 bytes, and the root manifest also includes this report, the feature-document update, and the new regression script.

### `docs/history/CRAFTING_DATA_WIRING_2026-11-06.md`

Added this detailed implementation and validation report.

## Current data coverage verified

Against the live repository data:

```text
Recipes:                 205
Unique referenced items: 194
Generated catalog items: 11,978
Missing catalog IDs:     0
Missing detail files:    0
```

The current 205 recipe records therefore have complete item endpoint coverage in the shipped generated item catalog.

## Validation performed

### JavaScript syntax

Passed:

```text
node --check site/js/pages/crafting.js
```

### Recipe/catalog reference validation

Passed with:

```text
recipes=205
uniqueRefs=194
missing=0
catalog=11978
```

### Crafting regression gate

The new direct regression script passes:

```text
PASS31.32 crafting catalog gate: recipes=205 referencedItems=194 catalogItems=11978 missingIndex=0 missingDetails=0 errors=0
```

### Release manifests

Both release manifests were regenerated successfully and retain the existing `PASS31.30` release/build metadata.

### Remaining validation

The repository environment does not provide the `pytest` executable. The new regression script is executable directly with Python, and the repository's existing direct regression scripts can be run the same way. The full project verifier and historical regression suite should be run before any release packaging.

## Deliberate non-changes

This pass does not:

- Change the current 205-row recipe source.
- Claim that 2009Scape crafting definitions are now authoritative in production.
- Duplicate the separate 2009Scape extraction workspace into the live site.
- Change the shared catalog schema.
- Change player persistence, bank data, or skill data.
- Change item detail pages or item URLs.
