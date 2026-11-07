# Relationships

Relationships are first-class data.

### Monster drops
`monsterId -> itemId` with optional quantity and exact probability evidence.

### Shops
`shopId -> itemId` with shop/location/stock information when supplied by 2009Scape.

### Recipes
`materials -> output` with resolved endpoints and source provenance.

### Ground spawns
Ground-spawn information is shown only when a trusted source is available. Missing trusted ground-spawn data is reported as unknown rather than inferred.

## Monster-drop canonical dataset

`site/data/relationships/index.json` is the runtime index for canonical monster→item drop relationships. It points to gzip-compressed per-monster and per-item shards under `site/data/relationships/monsters/` and `site/data/relationships/items/`.

The generator is `data-pipeline/generate_drop_relationships.py`. It consumes the pinned 2009Scape source payload and calculates exact weighted probabilities. The upstream roll rules, including separate charm and tertiary rolls and the sentinel ids that are not real items, are in `docs/data/DROP_ROLL_MECHANICS.md`. `scripts/validate_drop_relationships.py` checks the shards without regenerating them.

The source currently expands to **52,557 unique relationships**:

- 45,575 main
- 2,097 default/guaranteed
- 4,804 charm
- 100 tertiary

`id: 0` is the roll-table "nothing" outcome. It is included in weighted totals but excluded from item relationships.

The runtime service loads only the monster or item shard needed by the current page. The shared data layer caches decompressed shards and the service worker caches successful shard fetches.
