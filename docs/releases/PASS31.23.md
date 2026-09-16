# PASS31.23 — Canonical Navigation Architecture

## Purpose

Replace the competing static/runtime navigation model that caused Firefox/Android to show one navigation and later replace it with another.

## Implementation

- `site/js/core/shell.js` now enhances the existing static `#site-nav` instead of deleting and rebuilding it.
- `site/js/components/app-enhancer.js` appends search controls to the existing navigation and no longer creates `.nav-primary`.
- Obsolete `.nav-primary` CSS and PASS31.22 layout overrides were removed.
- Static Character and Crafting links remain first-class shared navigation links.
- Duplicate Crafting inside the calculator menu was removed.
- Historical and current navigation behavior is documented in ARCHITECTURE, RUNTIME, PWA, ADR-0004, and ADR-0005.
- PASS31.23 regression coverage verifies one navigation, no dynamic navigation creation, no obsolete wrapper, unique Character/Crafting links, and JS syntax.

## Validation gate

Release packaging is not considered complete until the automated suite, fresh extraction, release-manifest integrity, and Firefox/Android smoke test pass. The 96% confidence requirement remains mandatory.
