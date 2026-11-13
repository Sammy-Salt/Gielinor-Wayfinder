# PASS31.79 – Tap any icon, drop a pin

**Tap an icon.** The icons drawn into the tiles (bank, altar, anvil, ...) cannot be clicked, so invisible round hit areas now sit over them (zoom 7 and closer, current floor only). Tapping one opens a popup with its name, what it is for and its coordinates; the pointer changes on desktop. Two sources:
- `data-pipeline/generate_map_icons.py` reads object placements from the 2009Scape cache (RS #530) and writes `site/data/map/icons.js`: Bank (booths, chests), Deposit box, Altar, Chaos altar, Anvil, Furnace, Cooking range, Spinning wheel, Potter's wheel, Pottery oven, Loom. Objects of one kind within 9 tiles on one floor become one spot at their centre (the booths of one bank). 268 spots. The cache's object definitions carry no map-icon ids, so spots come from object names, not from icon ids.
- Every shop in `shops.js` (name, shop type, owner).
Spots can sit a tile or two from the picture baked into the tile; hit areas are 15px wide to cover that. Icon kinds not listed above (mining sites, quest starts and so on) are not tappable yet.

**Drop a pin.** Tapping or clicking empty map drops a pin on that tile and opens a card with `x`, `y` and the floor, plus Copy and Remove. One pin at a time; a tap that only closes an open popup does not drop a pin. The live coordinate readout stays bottom left.

Map-boundary hashes re-baselined for `map.html`, `map.js` and `map.css`.
