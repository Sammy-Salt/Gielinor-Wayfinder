# PASS31.27 — Project Polish & Data Integrity

## Purpose
Stabilize the project-wide architecture before the final Maps pass.

## Changes
- Standardized page data access through the shared `Data`/`Catalog` services for Item, Character, and Crafting pages.
- Made `monster-drops.json` the single canonical runtime relationship source for both monster and item drop views.
- Added `relationshipsByItem` for efficient item-side lookup.
- Removed the obsolete runtime relationship component after eliminating duplicate detail-page rendering.
- Unified Drop Time and Drop Statistics around the structured canonical probability record.
- Exact-rate drops are sorted first and calculators distinguish unavailable/conflicting rates from valid rates.
- Removed obsolete production test CSS from `site/`; retained it under `audit/map-tests/`.
- Standardized bootstrap asset versioning at `v39`.
- Updated release/service-worker metadata to PASS31.27.

## Data policy
2009Scape remains primary. OSRS Wiki remains secondary. Missing or conflicting evidence remains unknown. No Ragger data is restored.

## Validation
The PASS31.18–PASS31.26 regression suite remains required, plus the PASS31.27 architecture/data-integrity tests and fresh archive extraction.
