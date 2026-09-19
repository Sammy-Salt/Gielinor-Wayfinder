# PASS31.29 — Unified 1/X Drop-Rate Presentation

## Purpose

Normalize every player-facing exact drop rate to the requested `1/X` format without changing the canonical probabilities introduced in PASS31.28.

## Changes

- Changed canonical generated `rateDisplay` values from raw reciprocal fractions such as `128/5` or bare integers such as `128` to `1/X` form.
- Added a shared runtime reciprocal formatter so exact authoritative and fallback rates are normalized consistently even if a stale display string exists in a relationship record.
- Applied the formatter to monster drops, item-side monster sources, boss drop rendering, Drop Statistics, and Drop Time.
- Preserved exact numerator/denominator probabilities underneath the display; no probability data is rounded or replaced.
- Finite decimal reciprocals retain useful precision without trailing zeroes; repeating reciprocals are shown to at most two decimal places.
- Bumped the application loader/cache version to force normal browser/service-worker clients onto the PASS31.29 code path.
- Added PASS31.29 regression coverage for representative exact rates and the normalized display contract.

## Examples

- `1/513` remains `1/513`.
- `5/128` displays as `1/25.6`.
- `11/64` displays as `1/5.82`.
- A guaranteed `1/1` probability displays as `1/1`.

## Release gate

The repository must finish with a clean Git checkpoint, passing targeted and historical regression tests, generated-data validation, JSON/JavaScript syntax checks, manifest consistency, and fresh archive extraction validation.
