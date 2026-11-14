# PASS31.82 – Native offline Android app

Replaces the web-wrapper (TWA) APK with a Capacitor app that bundles `site/`; see ADR-0007 and `docs/development/ANDROID_APK.md`.

- Added `android-app/` (Capacitor config, override script, emulator smoke test, sideload key) and `.github/workflows/build-android-app.yml` (build, sign, inspect, emulator test, publish release).
- Removed the TWA workflow, `android/twa-manifest.json` and `site/.well-known/assetlinks.json`.
- `platform.js`: in the app, no service worker and the status line says "Offline app".
- `test_pass31_81.py` no longer checks the TWA manifest; `test_pass31_82.py` guards the new setup.
