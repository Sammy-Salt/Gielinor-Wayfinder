# PASS31.28 — Canonical 2009Scape Drop Data & Lazy Loading

## Purpose

Replace the PASS31.27 relationship graph/rate gap with the canonical 2009Scape weighted drop-table payload while removing the 50+ MB monolithic runtime relationship load.

## Changes

- Added the canonical 2009Scape `drop_tables.json` payload and SHA-256 provenance manifest.
- Rebuilt monster→item relationships directly from 434 source tables.
- Added the missing 100 tertiary relationships, producing 52,194 unique relationships.
- Calculated authoritative weighted probabilities for main, charm, tertiary, and guaranteed default drops.
- Included `id: 0` "nothing" in weighted totals without exposing it as an item relationship.
- Replaced the monolithic `monster-drops.json` runtime payload with per-monster and per-item gzip shards plus an index.
- Added gzip JSON loading/decompression and caching to the shared `Data` service.
- Updated relationship consumers to lazy-load only the required shard.
- Updated rate handling so authoritative 2009Scape rates are calculated by the drop calculators.
- Added exact source/category/weight provenance to drop records.
- Added PASS31.28 regression coverage and documentation/ADR updates.

## Validation targets

- 52,194 canonical relationships.
- 2,125 monster shards.
- 1,081 item shards.
- 0 primary-source unknown rates.
- 0 Wiki fallback rates required by the canonical source.
- 0 Ragger production references.
- Canonical source SHA-256: `3f6b1f4d2f49f72d54d71545a8397bc0ca04c44bb4aaa6f58325a27dac59e856`.
- Abyssal whip from Abyssal demon: `1/513`.

## Release gate

The repository must finish with a clean Git checkpoint, a passing full regression suite, fresh archive extraction validation, JSON/JavaScript syntax validation, source-provenance checks, and release-manifest consistency.
