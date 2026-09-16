# PASS31.22 — Deterministic Navigation Layout

## Purpose

Resolve the Firefox/Android navigation regression where Character and Crafting links appeared initially but disappeared when the runtime global search row was inserted.

## Change

The navigation is now explicitly two rows at the layout level:

1. `.nav-primary` is a full-width, non-shrinking row containing the brand and primary navigation links.
2. `.app-tools` is a separate full-width, non-shrinking row containing global search.

This removes flex competition between navigation links and the search row. The runtime enhancer still owns creation of the search UI, while CSS guarantees that adding it cannot compress or hide primary navigation.

## Compatibility

The existing navigation HTML and shared `app-enhancer.js` remain in use. No page-specific navigation implementation is introduced.

## Validation

- PASS31.18–PASS31.21 regression suites retained.
- PASS31.22 navigation regression checks added.
- JavaScript syntax checked across production scripts.
- Fresh archive extraction and manifest validation required.
- Firefox/Android target-runtime verification remains required before final release confidence.

## Documentation/Git

The navigation layout decision is recorded here as the implementation-level release record. ADR-0004 remains the architectural source for the separation of primary navigation and search; PASS31.22 makes that separation deterministic at the CSS container level.
