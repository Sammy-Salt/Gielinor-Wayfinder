# PASS31.42 — Cooking assembly and remaining Crafting recipes (2009Scape)

Extends `data-pipeline/generate_skill_recipes.py` (source commit 4082f9d). `recipes.json` is now 847 recipes.

## Added
- **Cooking +75** (`2009scape-cooking-assembly-*`): pie shells and every pie stage, pizzas, bowl toppings and sauces, stews, curry, baked-potato toppings, cake mix, chocolate cake, wrapped oomlie, dough (bread, pastry, pizza base, pitta × bucket/bowl/jug of water), and dairy (cream, butter, cheese; one row per accepted input, since the churn uses whichever listed input is in the inventory).
- **Crafting +29**: studded armour (2), weaving (3), snelms (9), tanning (8, hide plus coins, no xp), and amulet stringing (7, level of the amulet, no xp).

## Correction
PASS31.40 gave silver symbol/emblem stringing 4 xp. `SilverStringingListener.kt` awards none and has no level check; those two rows now read 0 xp.

## Still not extracted
Spiky vambraces, lantern assembly, limestone chiselling, heraldic shields, wine and brewing, tea, skewered foods and kebabs, chocolate cutting, coconut and watermelon handling, and runecrafting talisman enchanting. Multi-step recipes with many variants (barbarian fishing, gnome cooking) are also absent.

## Notes
- Container returns (empty bucket/bowl/pot) are not modelled as outputs.
- Pre-existing wiki Fletching rows that duplicate 2009Scape Fletching outputs (from PASS31.37) are untouched.
- Release bumped to PASS31.42; `tests/test_pass31_42.py` added; earlier gates widened.
