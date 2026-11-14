# ADR-0007: Native offline Android app replaces the web-wrapper APK

- Status: accepted (PASS31.82)
- Supersedes: the Trusted Web Activity (TWA) APK described in earlier `ANDROID_APK.md`

## Context

The first APK was a thin Trusted Web Activity that opened the GitHub Pages site in Chrome. It needed a connection to load, depended on Chrome and the browser service worker for offline use, and showed browser install behaviour. The owner asked for a real app named Gielinor Wayfinder that works fully offline, with no browser PWA behaviour and no live connection.

## Decision

- The Android app is a **Capacitor 6 shell** (`android-app/`) whose web directory is `site/`. The whole site, including all data and map tiles, is copied into the APK's assets and served by the app's built-in local server at `https://localhost`.
- The app **declares no network permission** (the generated `INTERNET` permission is removed) and has no `server.url`, so it cannot load anything remotely.
- Inside the app the service worker is never registered, no install prompt appears and the status line reads "Offline app" (`platform.js` detects `Capacitor.isNativePlatform()`).
- `sw.js`, `release-manifest.json` and `.well-known/` are removed from the bundle; they exist only for the browser deployment.
- The app is built by `.github/workflows/build-android-app.yml`: build, align, sign, inspect with `aapt2` (package, name, version, no INTERNET, tiles and index bundled), then **install and launch on an Android 34 emulator**; only a passing smoke test may publish a GitHub Release containing the APK.
- Signing: the committed **sideload key** `android-app/signing/wayfinder-sideload.keystore` is used unless the repository secrets `ANDROID_KEYSTORE_B64`, `ANDROID_KEYSTORE_PASSWORD` and `ANDROID_KEY_ALIAS` are set. A fixed key lets each release update the previous install in place. The key is public, which is acceptable for a sideloaded hobby app (an attacker cannot push an update onto a phone that did not install their APK) but means it is not suitable for a store listing.
- The TWA workflow, `android/twa-manifest.json` and `assetlinks.json` are deleted.
- GitHub Pages deployment of `site/` is unchanged and independent of the app.

## Consequences

- The APK is large (the site is about 200 MB) and its first install takes a moment; there is no update channel inside the app, so a new release is a new APK installed over the old one.
- Capacitor 6 is used on purpose: it targets Android SDK 34, so the app is not forced into edge-to-edge drawing that SDK 35 would impose.
- Site changes still follow the PASS process; every app release must be cut from a PASS-validated commit.
