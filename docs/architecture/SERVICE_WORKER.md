# Service Worker

The service worker owns offline shell caching and runtime caching. Every release gets a unique build/cache identifier. Per-page modules that are required for first-use offline behavior must be represented in the precache list.

Release validation must verify that `site/release.json`, the catalog manifest, service-worker build IDs, and the root release manifest agree.
