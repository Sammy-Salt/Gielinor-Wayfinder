# PASS31.67 – Map location data (2009Scape source)

## What changed
- New generator `data-pipeline/generate_map_points.py` writes `site/data/map/points.js` (247 points, provenance in `OSRS_MAP_POINTS_META`, 2009Scape commit 4082f9d).
- The Map Key now offers real data for: Fairy ring (35), Teleport destination (24, enchanted jewellery), Shooting star (42), Clue dig spot (82, from clues.json), Bank (30 clusters of banker spawns), Dungeon (10 entrances, SpecialLadders), Fishing spot (18 spot groups, centroid), Slayer Master (6).
- `map.html` loads `points.js`; `map.js` merges points into the legend and plots them as markers with popups.
- `audit/map-boundary.sha256` re-baselined for map.html/map.js; npcs/monsters/shops data files are unchanged.

## Source policy
Every point comes from the 2009Scape server source. No OSRS Wiki or invented data.

## Honest limits
- The server repo has no scenery spawns (altars, anvils, ranges, furnaces, trees, rocks), so those categories stay unmapped.
- Banks are derived from banker NPC spawns, grouped by proximity; they are not booth objects. Fishing spots are group centroids.
- Hunter, Farming and Agility have no coordinates in the data and are not mapped.
- `points.js` is cached offline on first map visit (network-first for .js, same as other map data).

## Validation
`tests/test_pass31_67.py`, all pass31 gates, `scripts/verify_project.py`, pytest.
