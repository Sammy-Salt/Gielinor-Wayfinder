# PASS31.62 — Slayer in the Skill Calculator (2026-11-11)

- `generate_slayer.py` now adds `xpPerKill {min,max}` to each Slayer task: the server awards Slayer xp equal to the NPC's maximum life points (`SlayerManager.kt`), taken from the monster catalog for each listed NPC id (min/max because variants differ, e.g. Ankou 60–66, Bats 8–32). All 93 tasks resolve; nothing else in `slayer.json` changed.
- The Skill Calculator's training-methods table now has Slayer: one row per task (per kill), Slayer level requirement, highest xp shown, with combat requirement, quest gate and the variant range in the note. `slayer.json` is already in the service-worker shell.

Gates: `tests/test_pass31_54.py` (xpPerKill), `tests/test_pass31_59.py` (Slayer wired).
