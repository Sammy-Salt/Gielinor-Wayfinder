# PASS31.65 — Map page once-over (2026-11-12)

The map is protected by `audit/map-boundary.sha256` so it is not rewritten casually. The owner asked for this work explicitly, so the three map code files (`map.html`, `js/pages/map.js`, `css/pages/map.css`) were changed on purpose and their hashes **re-baselined in this pass**. The three large data files (`data/map/npcs.js`, `monsters.js`, `shops.js`) are unchanged and still match their original hashes (asserted in `tests/test_pass31_65.py`).

Findings (phone and desktop screenshots): the header took about a third of a phone screen, and ~200 large saturated cluster bubbles at the default zoom hid the map itself.

Changes:
- Navigation on the map page is the same compact one-row menu as the rest of the app (the nav rules from PASS31.63/64 no longer exclude the map); the Reference link is now in the map's menu too. The global search bar is hidden on phones (the map has its own search in Map tools), so the map gets ~93% of a phone screen instead of ~65%.
- Marker clusters are smaller (28/34px instead of 34/40), translucent, with a thinner outline, and group in 64px cells instead of 56px, so fewer bubbles cover the map.
- New "Show on map" switches (Shops, NPCs, Monsters) in the Map tools drawer. The choice is remembered per device (`localStorage`, guarded) and defaults to all on. Browser-checked: turning NPCs and Monsters off removed their 182 clusters, kept the shops, and survived a reload.
- The tools drawer now opens below the Map tools button instead of underneath it (it hid the floor selector).

Not done: the map still uses the OSRS tile set; the zoom control is partly covered by the open drawer on phones; spawn data completeness was not reviewed.

Gate: `tests/test_pass31_65.py`.
