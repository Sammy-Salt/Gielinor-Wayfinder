# PASS31.66 — Map search, Map Key and marker size (2026-11-12)

Reported: the map's search and buttons "don't really do anything". Investigation (browser run against the shipped data):

- **Search** only looked at the 34 hand-listed places in `locations.js`, so shops, NPCs and monsters (266 / 4,384 / 8,950 records, the bulk of the map) could never be found.
- **Map Key** listed 99 categories copied from the OSRS wiki map key; 66 of them (all 18 Tutors, all 24 Training, 20 of 21 Main/World) match nothing in the 2009Scape data, so tapping them showed "0 locations found". Four shop categories were empty too.
- Tapping a result or marker opened the tools drawer, which covers the map, instead of showing the place.

Changes (map code hashes re-baselined again on purpose; data files untouched):
- Search covers places, shops, NPCs and monsters, ranks exact > prefix > contains > description, groups same-named spawns ("Man · 37 locations") and flies to the one nearest the map centre (switching floor when needed). A "no match" message replaces a silent empty list.
- Map Key only lists categories that have data, with counts ("Bank (2)"), and gains a "Places" section built from the data's own place types. Empty categories and sections are not shown.
- Details open as a popup on the map; on phones the drawer closes after picking a result or key item so the map is visible.
- Markers are smaller: spawn icons 22px (was 28), clusters 22/28px (was 28/34).

Browser-checked at phone size: "general" finds the general stores, "hans" opens a popup at Hans with the drawer closed, nonsense shows the empty message, the key shows 43 items in 3 sections, no console errors.

Not done: the key still has no OSRS-style icons; NPC/monster results show their kind but not a combat level; "Quest start", "Dungeon", "Altar" and similar would need new location data.

Gate: `tests/test_pass31_66.py`.
