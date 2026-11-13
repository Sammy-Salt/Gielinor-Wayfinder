# PASS31.81 – Faster map start, CI fixed, APK colours

- **Map startup.** `monsters.js` and `npcs.js` (about 1 MB, only needed for search and `?q=`/`?npc=` links) are no longer in `map.html`. `map.js` loads them the first time the search box gets focus or a link needs them (`ensureSpawns`). With the CPU slowed 4× on a phone profile, DOM ready went from about 800 ms to 430 ms and long tasks from 364 ms to 139 ms. Data files are unchanged.
- **Other map costs checked and left alone.** Tiles load only for the visible area and the surface bounds; markers are only drawn for the selected category or search; canvas rendering is on. Nothing else showed up.
- **CI.** The workflow had failed on every push because the runner lacked Pillow, which `test_pass31_39.py` imports. `ci.yml` now installs `pytest pillow`.
- **APK.** `android/twa-manifest.json` theme, navigation and background colours changed from `#17130e` to `#111111` to match the redesign.
