# PASS31.52 — Hunter data (2026-11-10)

Adds `site/data/hunter.json` (67 rows plus trap types and impling spawner tiers) via `data-pipeline/generate_hunter.py` (2009Scape commit 4082f9d), with per-section shape assertions.

- **Trap creatures** (`Traps.java`): level, xp, NPC ids, trap-object ids (bird snare/deadfall), reward items, and the pet summoning level for Box/Net catches. Trap types carry the level and the item ids needed to lay them (`TrapSetting` constructors).
- **Butterflies** (`BNetTypes.java`): catch level, bare-hand level, Agility level; `xp` is the first entry of the source's experience array (what the net grants); the other two values are kept raw as `experience` because the source leaves them unlabelled.
- **Implings**: level, xp, Puro-Puro xp, jar item, respawn, and full loot with the source's drop-frequency labels; spawner tiers (`ImplingData.kt`) with their weighted impling mixes.
- **Falconry**, **kebbit tracking** (Polar, Common) and **pitfalls** (Larupia, Graahk, Kyatt corpse-looting xp).

Source facts kept as found: Grenwall grants 0 xp (the server prints a note); the Ferret item (10092) is used by the server but missing from the item catalog (allow-listed, not invented); creature names come from the NPC catalog, with four documented fallbacks recorded in `nameSource` (three from the server source, one — Barb-tailed kebbit — from the OSRS Wiki).

Not shipped yet: catch-rate formulas, trap success rules, Puro-Puro/impling spawn locations, kebbit trail layouts, and any UI reading this file.

Gate: `tests/test_pass31_52.py`.
