# Android APK (TWA) Setup

This project uses **Option A**: the PWA is hosted on GitHub Pages and wrapped in a Trusted Web Activity (TWA) shell. The APK is a thin native wrapper. All content and updates come from the live site (your existing service worker handles caching and versioned releases).

## Live URL

After the first successful deploy:

**https://sammy-salt.github.io/Gielinor-Wayfinder/**

## One-time setup steps (do these in the GitHub UI)

### 1. Enable GitHub Pages

1. Go to the repository **Settings → Pages**.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
3. The workflow `.github/workflows/deploy-pages.yml` will run on every push to `main` and publish the `site/` folder.

### 2. First deploy

Push any change to `main` (or manually run the **Deploy to GitHub Pages** workflow). Wait until it finishes. The site should then be reachable at the URL above.

### 3. Build the APK

1. Go to the **Actions** tab.
2. Select the **Build APK (TWA)** workflow.
3. Click **Run workflow**.
4. Optionally set version name / version code.
5. After it finishes, download the APK artifact (`gielinor-wayfinder-apk`).

### 4. Install on device

- Enable "Install from unknown sources" / allow the browser or file manager to install APKs.
- Install the downloaded APK.

Because the APK points at the GitHub Pages URL, any future push to `main` that updates `site/` will be available in the app (the PWA service worker will pick up the new release).

## Signing note

The current CI workflow generates a **temporary keystore** on every run. This is fine for testing/sideloading, but each build will have a different signing key, so Android will treat them as different apps (you cannot update an earlier install with a later CI build).

For production / proper updates:

1. Generate a permanent keystore once:
   ```bash
   keytool -genkey -v -keystore android.keystore -alias android -keyalg RSA -keysize 2048 -validity 10000
   ```
2. Store the keystore + passwords as GitHub Actions secrets.
3. Update the build workflow to use those secrets instead of generating a new keystore.
4. Put the SHA-256 fingerprint of that key into `site/.well-known/assetlinks.json` so full TWA verification works.

## Package ID

`com.sammysalt.gielinorwayfinder`

## Related files

- `.github/workflows/deploy-pages.yml` – publishes `site/` to GitHub Pages
- `.github/workflows/build-apk.yml` – builds the TWA APK on demand
- `android/twa-manifest.json` – Bubblewrap / TWA configuration
- `site/.well-known/assetlinks.json` – Digital Asset Links (fill in the SHA-256 fingerprint later)
