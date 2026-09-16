# Runtime Loading Rules

The runtime uses the HTML page as the stable shell. Bootstrap initializes shared behavior without replacing the page's canonical navigation.

## Navigation ownership

Each shipped page contains one static `#site-nav`. It is the only navigation owner and is usable before JavaScript runs.

- `shell.js` sets page state, active links, skip-link behavior, and menu interaction.
- `app-enhancer.js` never creates, removes, replaces, or appends children to `#site-nav`.
- Global search and application tools mount into the static `#app-tools-host` immediately after `#site-nav`.
- Character and Crafting are permanent static navigation links and cannot be removed by search initialization.

## Service-worker update order

`local-loader.js` is versioned in the HTML and loads the release-selected bootstrap version. On non-local origins it requests a service-worker update before importing bootstrap. If a worker is waiting, the loader sends `SKIP_WAITING`; the worker handles that message and activates immediately. This reduces the chance that an older cached runtime controls a newly released page.

On localhost, runtime registrations and caches are cleared for deterministic development testing.

## Standalone pages

Standalone item detail pages retain their deliberately small loading path but use the same static navigation and application-tools host. They must not create a second shell.

## Invariant

Future changes must preserve one DOM owner for navigation, one visual navigation system, one static navigation element, and an application-tools host outside that navigation.
