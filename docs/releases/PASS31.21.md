# PASS31.21 — Canonical Monster-Drop Relationships

## Purpose

Replace the standalone Drop Time rate fallback with a canonical monster→item relationship dataset shared by Drop Time, Drop Statistics, and monster drop displays.

## Source policy

- 2009Scape-derived local game-data relationships are authoritative for whether a monster drops an item.
- OSRS Wiki is secondary evidence only when an existing relationship has no trusted rate and the Wiki supplies one unambiguous, non-approximate published rate.
- Conflicting or approximate rates remain unavailable.
- Ragger is not read or shipped.

## Data

`site/data/relationships/monster-drops.json` contains the canonical relationship records. Each record preserves relationship source/status and structured rate provenance. The generated dataset contains 52,094 relationships: 348 with exact Wiki secondary rates, 11 with conflicting Wiki rates withheld, and 51,735 with no trusted rate.

## Runtime

`relationship-service.js` reads the canonical relationship dataset. Drop Time and Drop Statistics consume numerator/denominator probabilities from the same records. This avoids maintaining a separate rate database.

## Validation

Required validation includes JSON validation, JavaScript syntax checks, PASS31.18/PASS31.19 regression suites, canonical relationship integrity, probability parsing, fresh extraction, release-manifest verification, and protected map-boundary verification.
