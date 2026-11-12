# PASS31.72 – Training methods linked to the encyclopedia and map

Skill calculator method tables now have a Links column:
- Slayer: Info → monster page, Map → nearest spawn of the task's NPC ids.
- Thieving pickpockets and Hunter creatures: Info → NPC/monster page, Map → spawn. Stalls and tracking/pit-trap rows link a loot/reward item.
- Woodcutting, Mining, Fishing, Firemaking: Item page; Fishing also links to the Fishing spot layer on the map.
- Farming: Crop and Seed item pages.
- Info link target (npc.html vs monster.html) is chosen by which data file exists, so no dead links.

Map deep links (new): `?npc=id,id`, `?legend=<Map Key category>`, `?q=<name>`.

Not linkable, because the 2009Scape data has no coordinates or pages: rocks, trees, fires, stalls, chests, agility courses/shortcuts, farming patches, Hunter tracking and pit-traps (item link only). Crafting-type skills (Herblore, Smithing, Cooking, etc.) have no method table yet.
`audit/map-boundary.sha256` re-baselined for map.js.
