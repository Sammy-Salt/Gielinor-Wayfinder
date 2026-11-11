# PASS31.54 — Slayer data (2026-11-11)

Adds `site/data/slayer.json` (93 tasks, 6 masters, 10 rewards, plus rules) via `data-pipeline/generate_slayer.py` (2009Scape commit 4082f9d).

- **Tasks** (`Tasks.java`): minimum combat level, Slayer level, NPC ids, undead/dragon flags, quest gate (display name from `Quests.kt`), the in-game tip, and which masters can assign it. `ordinal` follows the server enum order, because the server save stores the current task as its ordinal (useful for save import).
- **Masters** (`Master.java`): Turael, Mazchna, Vannaka, Chaeldar, Sumona, Duradel — combat/Slayer requirements, default amount range, completion points (every task / 10th / 50th streak), and each weighted task list with per-task amount overrides.
- **Rewards** (`SlayerRewardPlugin.java`): learn/buy/service costs, with every cost and item literal checked against the source.
- **Rules** (`SlayerManager.kt`, `SlayerUtils.kt`): no points for the first four tasks, Turael awards none, 64,000 point cap, Slayer xp = NPC max life points, dragon slayer gloves ×1.15, block limit 4 gated by quest points 50/100/150/200, and the assignment filter (combat level, Slayer level, not blocked, quest done; weighted pick).

Source facts kept as found: nine tasks are defined but never assigned (commented out of every master: Fever spiders, Molanisks, Mutated zygomites, Scabarites, Sea snakes, Shadow warriors, Wall beasts, Warped terror birds, Warped tortoises) and stay flagged with an empty `assignedBy`; Red dragons has `dragon: false` in the source; Sumona's name comes from the enum when the NPC catalog lacks it.

Not shipped yet: task-location/dungeon tables (`dungeon/*.java`), monster-specific kill requirements (items/equipment), and any UI reading this file.

Gate: `tests/test_pass31_54.py`.
