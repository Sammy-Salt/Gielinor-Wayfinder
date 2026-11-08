# PASS31.41 — Recipe relationships and non-recipe cleanup

- Dropped the 32 wiki-secondary rows that had no inputs (11 Thieving, 4 Prayer, 3 Fishing, 3 Mining, 2 Construction, 2 Smithing, 2 Strength, and one each Crafting, Defence, Farming, Fletching, Woodcutting). They describe gathering or skill-activity outputs, not recipes. `recipes.json` is now 743 rows.
- Item pages gain a **Recipes** card with *Made by* and *Used in*, computed in the browser by `site/js/services/recipe-service.js` from `recipes.json`. No new data shards were added, so the offline footprint is unchanged and the later slim-down is not complicated. The card is hidden for items with no recipes.
- Release bumped to PASS31.41; `tests/test_pass31_41.py` added; earlier gates widened.
