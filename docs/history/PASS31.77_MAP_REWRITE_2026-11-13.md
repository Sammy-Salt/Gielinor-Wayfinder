# PASS31.77 – Map rewrite

**Why.** The old `map.js` (912 lines) used an Earth-style projection with a zoom-11 pixel conversion, a +quarter-tile offset, TMS flags, clustering, a drawer, a legend accordion and a `--map-top` position hack. Fixes kept breaking other parts, and markers and tiles could disagree.

**What is documented and standard here.** Leaflet 1.9.4 plus Explv's OSRS tile set (already shipped). The other GitHub projects checked were not a fit: `dennisdev/rs-map-viewer` (3D cache viewer, needs cache downloads), `JoeGandy/RSMap` (Next.js server, no licence, 1–3 h tile build), `collisionlab/osrs-tiles` (hosted, Jagex imagery, licence unclear), `Explv/osrs_map_tiles` (the tiles themselves, Docker generator).

**New design (about 240 lines).**
- `L.CRS.Simple` with `lat = y - 1216`, `lng = x - 960`, one game tile = `2^(zoom-6)` px. At zoom 8 a tile is 64 game tiles; tile (tx, ty) starts at game (960 + 64·tx, 1216 + 64·ty). Tile URL row is `-leafletY - 1` (TMS) with no CRS bounds tricks.
- Markers sit on the tile centre (+0.5), no hand-tuned offsets.
- One control bar above the map: search, "Show on map" list (places, shops, 8 point categories), floor select, status line. Results are a plain list. No drawer, legend accordion, clustering or `--map-top` maths.
- Search covers places, shops, points, NPC and monster names (spawns grouped by name). Deep links `?q=`, `?legend=`, `?npc=` unchanged.
- Spawns are only plotted when searched for or linked, capped at 400.
- Data files (`npcs.js`, `monsters.js`, `shops.js`, `points.js`, `locations.js`) and tiles are unchanged. Map-boundary hashes re-baselined for `map.html`, `map.js`, `map.css`.
- Old map-only rules removed from `site.css`. Tests 39, 65, 66, 67, 69, 72 updated to the new structure.
