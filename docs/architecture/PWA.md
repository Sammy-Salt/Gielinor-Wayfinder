# PWA Runtime

The application is designed for offline use after its local assets and data have been cached. Firefox on Android is a target runtime, while Termux is the development/test environment.

All normal pages expose the same static navigation before runtime JavaScript executes. Runtime enhancement preserves that navigation rather than replacing it.

Global search and application tools are deliberately mounted outside `#site-nav` in the static `#app-tools-host`. This keeps navigation layout independent from asynchronous search initialization.

The service worker uses a release-specific cache namespace and the loader performs an update check before bootstrap on non-local origins. Release asset URLs are versioned so an older cached loader cannot silently satisfy a newer HTML page request when the browser has access to the new release.
