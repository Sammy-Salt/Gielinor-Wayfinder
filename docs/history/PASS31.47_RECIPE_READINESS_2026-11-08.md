# PASS31.47 — "Can I make this?" from the imported save

- New `site/js/services/recipe-ready.js` (pure, no imports): `buildHoldings` (inventory + bank + equipment summed per item id), `buildLevels` (static skill levels), `assess` (level and materials) and `describe` (badge text with reasons, e.g. `Level 60 needed (you: 55) · Missing 2 × Thread`).
- **Crafting page:** replaces the old bank-only check. Shows the specific reason on each recipe, counts "N you can make now" for the loaded character, and the *Ready* filter uses the same logic.
- **Item pages:** every "Made by / Used in" entry carries the same badge.
- The character comes from whichever save is loaded: an imported 2009Scape save (PASS31.43/44) when present, otherwise the bundled `player-sync.json`. The card and summary name the character.
- `tests/recipe_ready_check.mjs` runs the logic under Node against the synthetic save and the shipped recipes; `tests/test_pass31_47.py` wraps it. A Playwright pass confirmed the import → crafting page → item page flow with no JS errors.

## Limits
- Tools are not checked (many recipe rows list tool names without item ids). They remain visible in each entry.
- Quest and unlock requirements are not modelled; readiness is level + materials only.
- Levels are static (not boosted) levels from the save.
