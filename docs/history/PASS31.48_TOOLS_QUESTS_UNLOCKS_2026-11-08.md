# PASS31.48 — Tool, quest and unlock checks, and a quest-name correction

## Correction first: quest names were wrong
The importer (PASS31.43/44) and the bundled `player-sync.json` labelled quests with a hand-written id→name table that does not match the server. A save stores `questId` = `Quest.index` (`PlayerSaver.saveQuests`, `QuestRepository.setStage`). Examples from the server source: 15 is Cook's Assistant, 19 Ernest the Chicken, 27 Rune Mysteries, 28 Sheep Shearer; the old table had 15 as Sheep Shearer, 17 as Vampire Slayer, 27 as Creature of Fenkenstrain.

Independent proof: the bundled save has four completed quests and 7 quest points. Under the source mapping they are Cook's Assistant (1), Ernest the Chicken (4), Rune Mysteries (1) and Sheep Shearer (1) = 7. The old names cannot reach 7.

- `data-pipeline/generate_quest_ids.py` generates `site/js/services/quest-ids.js` (70 quests) from the 2009Scape source (4082f9d); the importer now uses it and the hand-written table is removed.
- `site/data/player-sync.json` quests are relabelled from the same table (stages unchanged; 65 → 70 entries so every real quest is listed).
- The PASS31.45 fixture asserted the old, wrong names; it now uses the real ones. That test could not have caught this: it checked the parser against its own table. `tests/test_pass31_48.py` now ties the bundled save to the table and the quest-point total.

## New checks (`recipe-ready.js`)
- **Tools:** `data-pipeline/annotate_recipe_checks.py` maps tool names to catalog item ids (`toolItemIds`; 336 of 340 tooled recipes fully mapped, ids verified against catalog names). All listed tools are required; none of the 2009Scape rows has interchangeable tools. The four "Costume needle" rows (OSRS-only item) stay unchecked.
- **Quests:** 27 requirements (e.g. Zogre Flesh Eaters, Heroes' Quest). A quest passes only when its stage is 100 in the save. Five quest names appear in the server's `Quests` list with no implementing quest class, so a save can never record them (In Aid of the Myreque, Grim Tales, Shades of Mort'ton, Kenneth's Concerns, Fairytale II); they show as "can't verify".
- **Unlocks:** the 29 Barbarian Herblore mix recipes check the saved attribute `barbtraining:herblore` ≥ 1 (`BarbarianMixListener.kt`; `/save:` prefix stripped by the game). The importer now reads the save's `attributes` array (`PlayerSaver.saveAttributes`: `{type, key, value}`) into `snapshot.attributes`.
- **Cannot decide → "can't verify", not pass or fail:** unknown tools, unimplemented quests, and any save without attributes (the bundled demo). A real raw save with no attributes array means none are set.

## Limits
Still static levels only; other unlock kinds (none exist in the recipe data yet) would need their storage location found in the server code first.
