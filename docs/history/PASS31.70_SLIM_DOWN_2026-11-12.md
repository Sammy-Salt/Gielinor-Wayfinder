# PASS31.70 – Slim-down release (unused data removed)

Removed, because nothing in the app (pages, service worker, scripts, tests) references them:
- `site/data/wiki/pass31.8/` (67 MB) and `pass31.9/` (46 MB): superseded generated wiki snapshots.
- `site/data/wiki/pass31.13/review/` (12 MB): review/triage files; the app reads only `entities/`, `relationships/`, `manifest.json`, `summary.json`.
- `site/data/map/assets-osrswikimaps-staging/` (5.6 MB): staging tiles.

Result: site 343 MB → about 215 MB, 54,283 → about 36,600 files. All remain in git history.
Kept deliberately: `wiki/pass31.13/entities` (OSRS Wiki fallback per source policy), item data, map tiles, relationships, monsters.
Not changed: `release-manifest.json` copies (generated, checked by verify), git history size.
