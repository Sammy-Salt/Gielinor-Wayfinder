# ADR-0005: Canonical Static Navigation

**Status:** Accepted — current

## Context

The project previously had competing static and runtime navigation implementations. PASS31.23 removed the second navigation and established the static `<nav id="site-nav">` as canonical. Firefox/Android testing then showed that Character and Crafting could still disappear while the search enhancement initialized. The remaining coupling was that `app-enhancer.js` appended its application-tools container directly inside the navigation flex container.

## Decision

Keep the static `<nav id="site-nav">` as the sole navigation owner, and place asynchronous application tools in a separate static `<div id="app-tools-host">` immediately after the navigation.

- `shell.js` may enhance the existing navigation but may not create, replace, or remove it.
- `app-enhancer.js` mounts only into `#app-tools-host`.
- Search initialization must never mutate the navigation's child list.
- Character and Crafting remain static first-class navigation links.
- Crafting is not duplicated inside the calculator menu.
- The established navigation visual system remains unchanged.
- The service worker and loader use release-specific versioning and explicit waiting-worker activation to reduce stale-runtime failures.

## Consequences

Navigation and search have separate DOM ownership and layout responsibility. Delayed search initialization cannot alter navigation flex layout or remove navigation links. The page remains useful before JavaScript finishes.

## Validation

PASS31.23–PASS31.25 progressively validated one navigation, static tools isolation, no dynamic navigation ownership, unique Character/Crafting links, release-versioned loader URLs, waiting-worker activation, static shell parity, and JavaScript syntax across production scripts.

## PASS31.25 clarification — static shell components
The canonical shell boundary includes both navigation and the application-tools host. Application tools are shipped as static markup and enhanced in place. Runtime JavaScript must not create, replace, or remove the canonical navigation or application-tools component. This removes a class of timing-sensitive DOM replacement bugs and keeps all pages structurally equivalent, including standalone detail pages.

## Governance

This ADR is a durable architectural contract. Future agents must read it before modifying the shell, navigation, global search, or application-tools host.
