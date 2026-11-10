# PASS31.51 — Agility data (2026-11-10)

Adds `site/data/agility.json` (3 courses, 45 shortcuts) via `data-pipeline/generate_agility.py` (2009Scape commit 4082f9d).

- **Shortcuts** are parsed from `agility/shortcuts/`: object ids, level, xp and options from each registration, plus the source's location comments (e.g. "Yanille Dungeon"). Shape assertions pin the counts per parser (28 configured, 8 singleton, 2 stepping-stone, 7 grapple).
- **Grapple shortcuts** carry their three-skill requirements (Agility/Ranged/Strength) and start/end tiles.
- **Courses** (Gnome Stronghold, Barbarian Outpost, Wilderness): the server passes obstacle xp inside procedural handlers, so obstacle tables are transcribed in the generator and every object id and xp literal is checked to occur in the named source file. Completion xp comes from the `AgilityCourse(player, size, completionXp)` constructor.

Source facts kept as found: the Gnome and Barbarian courses have no level gate in the server (level is `null`, not guessed); the Wilderness gate needs Agility 52 and its pipe 49; the Barbarian low-wall obstacle appears three times.

Not modelled yet: Brimhaven Agility Arena, Agility Pyramid, the stile shortcut (12 object ids, no level), the rope swing shortcut (object 2327 with item 954, 22 xp), success-rate rules, and any UI reading this file. Stepping-stone xp is `null` because the source does not state it.

Gate: `tests/test_pass31_51.py`.
