# Provenance

Material source-sensitive values and relationships carry provenance metadata.

## Canonical monster-drop source

- Provider: 2009Scape
- Upstream path: `Server/data/configs/drop_tables.json`
- URL: `https://gitlab.com/2009scape/2009scape/-/blob/master/Server/data/configs/drop_tables.json`
- Pinned content SHA-256: `3f6b1f4d2f49f72d54d71545a8397bc0ca04c44bb4aaa6f58325a27dac59e856`
- Tables: 434
- Expanded unique monster→item relationships: 52,194
- Upstream commit: not embedded in the supplied payload, so no unverified commit is recorded.

The exact source payload is retained at `site/data/sources/2009scape/drop_tables.json` with a companion manifest.

## Relationship provenance

Each emitted relationship records `source=2009Scape`, `status=authoritative`, the applicable roll category, exact weight/total-weight data, and the source content hash.

`id: 0` ("nothing") contributes to weighted-table totals but is not emitted as an item relationship.

## Secondary evidence

OSRS Wiki may enrich a relationship only when the primary source cannot calculate a value and the Wiki evidence is exact and unambiguous. Approximate, conflicting, variable, or unsupported evidence remains unavailable.

The current PASS31.28 canonical source calculates all 52,194 shipped relationship rates, so no Wiki fallback rates are required.

Ragger is retired and must remain absent from production data, code, HTML, CSS, and manifests.
