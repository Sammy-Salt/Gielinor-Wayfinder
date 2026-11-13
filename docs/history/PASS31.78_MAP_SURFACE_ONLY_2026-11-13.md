# PASS31.78 – Map shows the surface world only

The Explv tile set also contains dungeons, Zanaris, Dorgesh-Kaan and instance pieces in a large black region north of (and a few pieces south of) the framed surface map. They appeared as stray tiles when panning north.

- `SURFACE` = x 1016–3974, y 2106–4168 (the framed rectangle, measured from the zoom-5 composite). Panning and zooming are limited to it, and tiles outside are not requested. Minimum zoom fits the surface to the screen.
- If something plotted on the current floor lies outside the surface (about 1,160 NPC spawns, 4,800 monster spawns, 47 shops, 17 fairy rings are underground), the map widens to the whole tile set and the status line says "(underground view)". Clearing the plot or choosing a surface item narrows it again.
- Tiles and data files unchanged.

Follow-up in the same pass: lists that mix surface and underground items (for example Fairy ring) plot only the surface ones and report how many underground items were left out; the underground tiles open only when everything plotted is underground (for example a search for one underground NPC).
