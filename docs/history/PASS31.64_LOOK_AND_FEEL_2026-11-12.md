# PASS31.64 — Look and feel: a flatter, calmer journal (2026-11-12)

Screenshot review (phone and desktop) found a competent but heavy theme: every element was a bordered, gradient-filled, shadowed box nested inside another box, with gold on every heading, button-shaped navigation and a bright white search bar.

Direction: keep the dark leather-and-gold identity of the game, but make surfaces flat and let gold mean "title, link, current page".

- Surfaces: one flat panel colour with a hairline; no gradients, shadows or inner highlights; the grid texture overlay is gone; page headers are unboxed.
- Type: system UI sans for text (was Arial), Georgia kept for the page title and the numbers; section headings are quiet bone-coloured instead of gold; stat numbers are larger with tabular figures.
- Navigation: text tabs with a gold underline on the current page instead of button pills; dropdowns unboxed.
- Controls: dark search field (was white), rounded buttons and inputs, gold checkbox accent; checkbox rows no longer stretch.
- Quests: status is a coloured left edge and a line of text, not a second boxed banner; the developer line "Quest DB: LOADED" is hidden.
- Fixed: Progress skill cards had no padding; crafting recipe cards now match the other panels.

CSS only, appended to `site/site.css` and scoped with `body:not([data-page="map"])`; the map boundary hashes are unchanged and focus outlines are untouched.

Not done: emoji in headings are still in the markup, copy such as "Trusted acquisition relationships from the project's canonical data model" is still developer-voice, the Monsters list shows a stray lighter strip behind its rows, and crafting has a tall gap under its header.

Gate: `tests/test_pass31_64.py`.
