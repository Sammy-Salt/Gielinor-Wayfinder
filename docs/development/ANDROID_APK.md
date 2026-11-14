# Android app (offline)

Gielinor Wayfinder ships as a native Android app that contains the whole site. It needs no internet, no browser and no install from a web page. See ADR-0007.

## Get the app

1. Open the repository's **Releases** page and download `Gielinor-Wayfinder-<version>.apk` from the newest `app-v…` release.
2. On the phone, allow installs from the browser or file manager when asked, open the file and install.
3. The app appears as **Gielinor Wayfinder**. Later releases install over the top and keep your saved player data.

If an older web-wrapper build (version 1.x TWA) is installed, uninstall it once first: it was signed with a different key.

## Make a new release

1. Land and validate the change on `main` (PASS process).
2. **Actions → Build Android app (offline) → Run workflow.** Set the version name (for example `1.3.0`) and a version code larger than the last one.
3. The workflow builds, signs, checks the APK, runs it on an emulator and, if that passes, publishes the release.

## What the workflow checks

Package name `com.sammysalt.gielinorwayfinder`, app name, version, no `INTERNET` permission, `index.html` and map tiles inside the APK, then install, launch and render of the Home page on an Android 34 emulator.

## Layout

- `android-app/package.json`, `capacitor.config.json` – Capacitor shell, web directory `../site`.
- `android-app/scripts/apply_android_overrides.py` – name, version, icons, splash, bar colours, removes network permission.
- `android-app/scripts/smoke_test.sh` – emulator test.
- `android-app/signing/` – sideload signing key (used unless repository secrets provide another).
- `.github/workflows/build-android-app.yml` – the build.

## Signing

By default the committed sideload key is used so updates install in place. To use a private key, add the secrets `ANDROID_KEYSTORE_B64` (base64 of the keystore), `ANDROID_KEYSTORE_PASSWORD` and `ANDROID_KEY_ALIAS`; phones must then reinstall once.
