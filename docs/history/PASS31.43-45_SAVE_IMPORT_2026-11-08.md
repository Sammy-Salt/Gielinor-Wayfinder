# PASS31.43–45 — 2009Scape save import

- **PASS31.43:** Character page can pick a 2009Scape player `.json`, remember it (localStorage snapshot plus a File System Access handle in IndexedDB where supported) and re-read it on the next open. See `docs/features/PLAYER_SYNC.md`.
- **PASS31.44:** parser reads the real v4 layout: containers under `core_data`, location as `"x,y,plane"`, quests as `questStages` plus `points`, string-typed numbers.
- **PASS31.45 (this record):** the missing gate. `tests/save_import_check.mjs` runs the real `normalizeSave` under Node against `tests/fixtures/save_core_data.synthetic.json` and checks skills (static/dynamic/xp, ids 0, 3, 7, 12, 15, 20), inventory/bank/equipment, location, quest completion and points, total XP, normalized-snapshot passthrough, and rejection of arrays, unrecognised objects and saves with no skills. `tests/test_pass31_45.py` wraps it.

## Caveat
The fixture is **synthetic**: it follows the documented layout but is not a real player. If the real server format differs in a field the importer does not read, this test will not notice. Replacing it with an anonymised real save (names and bank trimmed) is the follow-up that closes that gap.

Release bumped to PASS31.45; earlier gates widened.
