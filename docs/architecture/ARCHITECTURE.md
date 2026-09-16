# Architecture

Gielinor Wayfinder is an offline-first static PWA. `site/` is the deployable application; development tooling lives outside `site/`.

## Runtime layers

1. Static HTML pages and shell
2. `local-loader.js` and shared bootstrap
3. Core runtime services in `site/js/core/`
4. Shared components/services in `site/js/components/` and `site/js/services/`
5. Page modules in `site/js/pages/`
6. Offline JSON catalogs and relationship datasets
7. Service worker/cache lifecycle

## Ownership boundaries

Each shipped shell page contains exactly one static `<nav id="site-nav">` and one static `#app-tools-host`. The HTML shell is the canonical owner.

- `site/js/core/shell.js` enhances the existing navigation: active-page state, skip-link setup, and menu behavior.
- `site/js/components/app-enhancer.js` binds the existing search/application tools inside `#app-tools-host`.
- Neither runtime component may create, replace, remove, or reparent the canonical navigation.
- Search initialization must not mutate the navigation child list.
- Character and Crafting are first-class static navigation links.

This ownership model prevents competing navigation implementations, timing-sensitive DOM replacement, and Firefox/Android shell regressions.

## Data rule

Canonical production values are selected from trusted source data during generation. UI code should consume canonical services/data and should not perform source arbitration or identity resolution ad hoc.

## Project governance

Git history, permanent documentation, ADRs, PASS records, and automated validation are part of the architecture. See `AGENTS.md` and `docs/development/AI_CHANGE_PROTOCOL.md`.
