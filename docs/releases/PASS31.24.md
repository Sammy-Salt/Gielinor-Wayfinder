# PASS31.24 — Navigation/Search Isolation & Service-Worker Hardening

## Purpose

Resolve the remaining Firefox/Android symptom where Character and Crafting could disappear after the application search UI initialized, while preserving the established navigation appearance.

## Implementation

- Added one static `#app-tools-host` immediately after `#site-nav` on every shipped page.
- Moved global search/application tools out of the navigation DOM.
- `app-enhancer.js` now owns only the tools host and never mutates navigation children.
- Removed obsolete navigation-coupled search CSS.
- Preserved the existing static Character and Crafting links and established navigation styling.
- Versioned every page's `local-loader.js` reference to loader version 38.
- Hardened service-worker updates with `SKIP_WAITING` handling and explicit waiting-worker activation.
- Added core shell and app-enhancer assets to the service-worker shell list.
- Updated release/catalog metadata and documentation.
- Added PASS31.24 regression coverage for DOM ownership, static links, search isolation, and service-worker update behavior.

## Validation gate

Release packaging is not considered complete until the automated suite, fresh extraction, release-manifest integrity, map-boundary integrity, no-Ragger scan, and Firefox/Android smoke test pass. The 96% confidence requirement remains mandatory.
