# Map Data Wiring Change Report — 2026-11-06

## Scope

This change fixes the runtime loading and rendering wiring for NPCs, monsters, and shops on `site/map.html`. The goal was to ensure all three entity types are loaded before the map page initializes, indexed by plane, rendered in their own Leaflet layer, and refreshed correctly when the user switches planes.

The change does **not** replace the current OSRS/Explv tile base, change map coordinate conversion, rebuild shop data, or add marker clustering. Those remain separate map-data and map-base tasks.

## Files changed

### `site/map.html`

Added the two missing data scripts before the map runtime:

```html
<script src="data/map/npcs.js?v=2"></script>
<script src="data/map/monsters.js?v=2"></script>
```

The resulting load order is:

1. Leaflet.
2. Curated locations.
3. NPC marker data.
4. Monster spawn data.
5. Shop data.
6. Shared utilities.
7. `js/pages/map.js`.
8. Shared shell behavior.

This ensures the datasets exist before `map.js` reads them.

### `site/js/pages/map.js`

Added a dedicated `monsterLayer` alongside the existing location, NPC, and shop layers.

Added compatible monster data loading:

```javascript
const monsterRecords =
    window.OSRS_MAP_MONSTERS ||
    (typeof monsters !== "undefined" ? monsters : []);
```

The first branch supports a future `window.OSRS_MAP_MONSTERS` export. The second branch supports the current `monsters.js`, which declares a classic-script global named `monsters` rather than a `window` property.

Added a monster marker icon using the crossed-swords symbol and updated `markerIcon()` to select explicit marker types while retaining the NPC fallback.

Added a `monsterByPlane` index and passed monster records through the same plane-indexing function used by locations, NPCs, and shops.

Added monster marker rendering. Each monster marker:

- Uses its `x`, `y`, and `plane` values.
- Appears only when its plane matches the selected plane.
- Uses the monster icon.
- Opens the existing information panel when clicked.
- Displays the monster name and available description/examine text.
- Includes the monster ID and coordinates in the location payload.

Updated `addInteractiveMarkers()` so every refresh clears and rebuilds:

- NPC markers.
- Monster markers.
- Shop markers.

This applies both on initial load and after plane switching.

### `audit/map-boundary.sha256`

Updated the protected hashes for the intentionally changed files:

- `site/map.html`
- `site/js/pages/map.js`

The hashes for the unchanged map CSS and generated NPC, monster, and shop data files were preserved.

### `docs/features/MAPS.md`

No feature-contract changes were required for the implementation itself. The protected map boundary and the existing plane-aware marker model remain the governing behavior. This report records the implementation details and validation evidence.

## Data compatibility notes

The current generated datasets have these formats:

- `npcs.js` exposes `window.OSRS_MAP_NPCS`.
- `shops.js` exposes `window.OSRS_MAP_SHOPS`.
- `monsters.js` currently declares `const monsters = [...]`.

The map code now supports the current formats without requiring a separate regeneration of the monster dataset. The fallback is deliberately isolated in `map.js` so a future generator can switch monsters to `window.OSRS_MAP_MONSTERS` without another map-rendering change.

All entity arrays are indexed by numeric `plane`, defaulting missing plane values to `0`. Plane switching clears and rebuilds the interactive layers, so stale markers from a previous plane are not retained.

## Validation performed

### JavaScript syntax

Passed:

```text
node --check site/js/pages/map.js
node --check site/data/map/npcs.js
node --check site/data/map/monsters.js
node --check site/data/map/shops.js
```

### Script-load ordering

Passed a structural check confirming that `npcs.js`, `monsters.js`, and `shops.js` appear before `map.js` in `site/map.html`.

### Project verifier

Passed:

```text
PROJECT VERIFY: PASS
shellPages=21
JS=78
JSON=47819
Ragger=0
metadata=PASS31.30
git=present
```

### Regression scripts

The environment does not have the `pytest` executable installed, so the repository's historical regression scripts were run directly with Python. Every available script passed:

```text
PASS31.18 tests: errors=0
PASS31.19 tests: errors=0
PASS31.20 regression tests: errors=0
PASS31.21 regression gate: adapted to PASS31.30 canonical lazy drop shards
PASS31.22 compatibility regression: superseded-nav remnants=0 js=syntax-ok
PASS31.23 compatibility nav tests: pages=21 oneNav=all staticLinks=character+crafting noDynamicNav=1 js=syntax-ok
PASS31.24 nav/search isolation tests: pages=21 oneNav=all staticToolsHost=all character+crafting=all navCoupling=0 swUpdate=1 js=syntax-ok
PASS31.27 regression gate: updated for PASS31.30 canonical drop shards
PASS31.28 drop tests: relationships=52194 tertiary=100 authoritativeRates=52194 wikiFallback=0 monolithic=0 gzip=PASS sourceHash=PASS js/json=valid ragger=0
PASS31.30 drop display tests: exactDisplaysChecked=103920 format=1/X canonical=PASS runtime=PASS syntax=PASS
```

### Diff and boundary checks

Passed:

```text
git diff --check
```

The protected map boundary manifest was regenerated only for the two files intentionally changed by this pass.

## Remaining map work

This wiring fix makes the existing NPC, monster, and shop datasets reachable by the map runtime. It does not solve the remaining data-quality and performance issues:

- The tile background is still the OSRS/Explv map rather than a rendered 2009Scape map.
- Shop records remain the existing generated dataset and still need replacement from authoritative `shops.json`.
- Marker clustering or viewport-based loading is still needed for mobile performance.
- The current monster data file should eventually be regenerated as a `window.OSRS_MAP_MONSTERS` export instead of relying on the compatibility fallback.
- Curated map locations remain limited.
- Offline tile caching remains a separate task.
