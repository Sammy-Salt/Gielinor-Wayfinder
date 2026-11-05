# Drops and Drop Calculators

## Canonical model

Monster→item drop relationships are generated directly from the pinned 2009Scape `Server/data/configs/drop_tables.json` payload shipped with the PWA. The source payload is content-pinned by SHA-256:

`3f6b1f4d2f49f72d54d71545a8397bc0ca04c44bb4aaa6f58325a27dac59e856`

The current canonical payload contains 434 drop tables and produces **52,194 unique monster→item relationships** after excluding the `id: 0` "nothing" roll outcome. The 52,194 relationships comprise 45,256 main-table relationships, 2,077 default/guaranteed relationships, 4,780 charm relationships, and 100 tertiary relationships. The category counts overlap where the same item is represented by more than one roll category.

## Probability provenance

2009Scape is primary. Its weighted tables are calculated exactly from the source weights. `default` entries are guaranteed; `main`, `charm`, and `tertiary` probabilities are calculated as entry weight divided by the complete roll-table weight, including the `id: 0` "nothing" weight.

Where a monster/item pair has multiple independent source categories, the relationship probability is combined exactly as:

`1 - product(1 - p_category)`

Rates are represented as exact numerator/denominator values rather than assuming every rate is `1/N`. This supports values such as `9/128` and combined independent rolls without rounding.

The OSRS Wiki remains a secondary source for evidence when a primary source genuinely cannot calculate a value. The current canonical drop-table payload supplies a calculable rate for every shipped relationship, so PASS31.30 has **0 Wiki fallback rates** and **0 unresolved primary rates**.

## Player-facing rate format

All exact drop-rate displays use a consistent reciprocal format: `1/X`. The underlying probability remains the exact numerator/denominator value; only the presentation is normalized. Integer reciprocals remain exact (`1/513`), finite decimal reciprocals are shown without unnecessary trailing zeroes (`1/25.6`), and repeating decimal reciprocals are rounded to at most two decimal places (`1/11.64`). This applies across monster drops, item-side sources, boss drops, Drop Statistics, Drop Time, and secondary-source rates.

The formatter is shared by the runtime drop service, while the canonical relationship generator writes the same normalized display into generated records so offline data and UI consumers remain consistent.

## Runtime consumers

- Monster detail: lazy-loaded canonical drop relationships.
- Item detail: lazy-loaded item-side relationship shards.
- Drop Statistics: canonical relationship + structured probability.
- Drop Time: canonical relationship + structured probability.
- Boss detail: canonical relationship service.
- Item acquisition: existing acquisition pipeline remains separate because it also contains shops and ground-spawn state.

## Lazy loading

The previous 50+ MB monolithic relationship JSON is no longer shipped as a runtime payload. Relationships are emitted as gzip-compressed per-monster and per-item shards with a small index. The shared `Data` service decompresses and caches shards on demand, while the service worker caches fetched shards for offline reuse.

## Source limitations

The supplied source payload did not embed an upstream Git commit/revision. The exact bytes are nevertheless reproducible because the shipped source payload and generated relationship records are pinned by SHA-256. The project does not silently claim a revision it cannot verify.

Ragger remains excluded.
