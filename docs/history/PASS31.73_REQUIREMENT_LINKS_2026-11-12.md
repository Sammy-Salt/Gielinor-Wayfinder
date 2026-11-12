# PASS31.73 – Quest requirements and crafting shortfalls linked

- Quest detail: every requirement is a link. Skill → Skill Calculator opened on that skill with the required level as target; quest → that quest; quest points → Quest Tracker; combat → Combat calculator. Skills without a calculator entry (e.g. Sailing) stay plain text.
- Crafting: the "Missing …" badge links each missing material/tool to its item page, "Quest not complete" to the quest, and "Level N needed" to the Skill Calculator for that skill with N as target.
- Skill Calculator accepts `?skill=<name>&target=<level>`; current level comes from the linked save.
- `describe()` in `recipe-ready.js` keeps its `text` output and adds an escaped `html` field built through an optional link callback.
