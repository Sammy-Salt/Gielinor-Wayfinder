# PASS31.55 — Treasure Trail data (2026-11-11)

Adds `site/data/clues.json` (131 clues, 362 reward rows) via `data-pipeline/generate_clues.py` (2009Scape commit 4082f9d).

- **Reward tables** (`Server/data/configs/clue_rewards.json`): easy 125 / medium 104 / hard 115 / rare 18 rows, each with min/max amount, raw weight and `chancePercent` (weight ÷ table total). One reward slot is one roll on the table. Rolls per casket: random(1, 6) slots (Hard: the larger of that and random(4, 6)); Hard also has a single extra rare-table roll when `random(100) == 50` (`ClueLevel.java`). Casket ids and step ranges (Easy 1–5, Medium 1–6, Hard 1–8) are checked against the source.
- **Coordinate clues** (57): sextant text and dig location. **Map clues** (25): dig/search location, search object and zone where the source has one. **Emote clues** (49): emote (plus commence emote when the clue needs one), equipment as groups of acceptable item ids, empty-slot requirements, area and the in-game text.

Source facts kept as found: the server uses the key `bandit-camp-coord` for two different Hard clues (items 2845 and 3505), so their display names carry coordinates; two coordinate clues commented out in the source (Gorad and East Karamja) are excluded; the Emote file also has commented-out emote lines (Cry, Jump for joy, Laugh), which are emote selectors rather than clues; display names come from the source keys (for example `ardgoune-mill-clap` keeps the source spelling, the clue text has the correct one); `area` is `[x1, y1, x2, y2]` with an optional plane as the fifth value.

Not shipped yet: puzzle boxes, riddle/anagram-style clues (none exist in this source), clue-scroll NPC fights (wizards, Uri), and any UI reading this file.

Gate: `tests/test_pass31_55.py`.
