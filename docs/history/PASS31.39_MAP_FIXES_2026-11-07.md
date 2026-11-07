# PASS31.39 — Map fixes (2026-11-07)

Decision: keep the Leaflet/OSRS tile base map; a custom 2009 render was prototyped (`data-pipeline/mapgen/`, not shipped) and rejected as too heavy.

## Fixed
- **Marker coordinates**: `osrsToLatLng` projected at `map.getMaxZoom()`, which became 8 when the tile pyramid was capped, so every NPC/monster/shop latlng clamped to the map edge and no marker could ever be in view. It now projects at zoom 11, matching `mapToOSRS`.
- **Clustering**: ~14,000 spawn markers are bucketed into 56 px screen cells below zoom 8 (blue NPC, red monster, gold shop), only the visible area is drawn, and clicking a cluster zooms into it. At zoom 8+ markers are individual.
- **Script errors**: `map.html` loaded ES-module files (`utils.js`, `shell.js`) as classic scripts (`export` syntax errors) and `map.js` called an undefined `escapeHtml`. The page now loads the shared `bootstrap.js` module and `map.js` defines `escapeHtml`.
- **Navigation**: `map.html` now has the shared nav and search bar; overlays are positioned from the map's real top edge.
- **Tiles**: 22,798 solid-black tiles (planes 1–3 and outside the world) removed by `scripts/prune_blank_map_tiles.py`: 29,422 → 6,624 files, 164 MB → 75 MB on disk. The map background is black and tile layers use a transparent `errorTileUrl`, so it looks identical.
- Map-boundary hashes updated; release PASS31.39; shell page count 21 → 22.

## Not done
- The base tiles are still OSRS (Explv), not 2009.
- Zoom 8+ can draw several hundred markers at once in dense towns.
- `site/data/map/assets-osrswikimaps-staging` (5.5 MB) is still present for the final slim-down.
