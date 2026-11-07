# PASS31.38 — drop roll mechanics, read-only check

No shipped drop rows, monster pages, or `site/release.json` changed. The published build remains `PASS31.36`.

Traced 2009Scape `master` `DropTableParser`, `NPCDropTable`, `WeightBasedTable`, and `RareDropTable`. The rules are in `docs/data/DROP_ROLL_MECHANICS.md`.

`scripts/validate_drop_relationships.py` recalculates every pinned relationship and compares the exact fractions to the gzip shards. It does not regenerate data. Sentinel ids (rare drop table, clues, herb/seed/gem tables) are reported and left as the generator emits them.

## Verification

`python3 scripts/validate_drop_relationships.py`

`python3 tests/test_pass31_38.py`
