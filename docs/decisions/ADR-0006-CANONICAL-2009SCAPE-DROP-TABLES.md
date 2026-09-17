# ADR-0006: Canonical 2009Scape Drop Tables and Lazy Relationship Shards

**Status:** Accepted

## Context

PASS31.27 treated the local 2009Scape-derived relationship graph as authoritative for relationship existence but had no primary 2009Scape weighted-drop payload in the PWA. Consequently the calculator could not derive authoritative probabilities and depended on OSRS Wiki secondary rates for a small subset.

The canonical 2009Scape `drop_tables.json` payload is now available and is complete enough to calculate the weighted probabilities for every shipped monster→item relationship.

The previous runtime dataset was a single approximately 50 MB JSON file. Loading it for one monster or one item was wasteful and created avoidable browser memory and startup costs.

## Decision

1. Ship the exact canonical 2009Scape `drop_tables.json` payload with a SHA-256 content pin.
2. Generate monster→item relationships directly from that source.
3. Treat `default` as guaranteed.
4. Calculate `main`, `charm`, and `tertiary` probabilities from the complete roll-table weight, including `id: 0` "nothing" weight.
5. Exclude `id: 0` from emitted item relationships.
6. Combine probabilities exactly across independent categories when a pair appears in more than one category.
7. Emit gzip-compressed per-monster and per-item relationship shards plus a small runtime index.
8. Load and decompress only the requested shard through the shared `Data` service.
9. Keep OSRS Wiki as secondary evidence only when primary source data cannot calculate a rate.
10. Keep Ragger excluded.

## Consequences

- The shipped relationship model is directly reproducible from a pinned primary source.
- PASS31.28 contains 52,194 unique monster→item relationships and 0 unresolved primary rates.
- The runtime no longer loads a 50+ MB relationship JSON merely to display one monster or item.
- The PWA can cache relationship shards as they are fetched.
- The supplied source payload does not identify an upstream commit, so the project pins exact content by SHA-256 rather than inventing a revision.
