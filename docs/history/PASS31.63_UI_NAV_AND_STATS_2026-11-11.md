# PASS31.63 — UI pass: compact navigation and stat cards (2026-11-11)

Found by screenshotting pages at phone (Pixel 7) and 1280px desktop widths:

- Phone: the wrapped navigation took ~27% of the first screen. It is now a single swipeable row (44px targets kept); dropdown panels open full width under it and were checked in a browser.
- Desktop: the menu wrapped to a second line; tighter padding now fits it on one line.
- Phone: stat cards stacked one per row; they now stay side by side (Home, Skill Calculator result).

CSS only (`site.css`, `css/pages/index.css`, `css/pages/skill-stats.css`). The map page keeps its own navigation: every new rule is scoped with `body:not([data-page="map"])` and the map boundary hashes are unchanged.

Not done: the desktop dropdown buttons sit ~2px higher than the plain links; other pages (quests, monsters, items, character) were not yet reviewed at phone width.

Gate: `tests/test_pass31_63.py`.
