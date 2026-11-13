# PASS31.75 – Redesign: black, white, grey and soft yellow, light/dark mode

Approved from the mockup canvas ("Wayfinder redesign mockup").

- **Tokens** (`site.css`, end of file): `--ui-*` colours for dark (`#111` ground, `#e8d48a` yellow) and light (`#f7f7f5`, `#7a5f0a` link yellow, `#c9a93a` bars). The old `--osrs-*`, `--leather`, `--gold` names point at them so page CSS keeps working. The PASS31.64 block was edited in place to drop its brown hex values and 10–12px radii.
- **Theme**: dark by default; light follows the system setting; the sun/moon button at the end of the nav overrides it and is remembered (`wayfinder.theme`). `js/theme-init.js` runs in `<head>` on all 23 pages and is precached.
- **Look**: flat sections separated by thin lines, 6px radius, one sans font, text tabs with a yellow underline for the current page, thin yellow bars, stats as a plain row, map overlays and "Map tools" follow the theme. Map tiles unchanged.
- **Emoji removed** from nav, headings, status text and cards (map marker badges keep theirs). Brand is now "Wayfinder".
- **Home** rebuilt to match the mockup: stats, quest progress (n of total), Ready to start, goals, Tools, Encyclopedia. Home now loads the player save like Progress does.
- **Back links**: removed the last ones ("← Bosses", "← Back to Bosses" on boss pages).
- Tests that asserted emoji labels were updated (`test_pass31_20`).
