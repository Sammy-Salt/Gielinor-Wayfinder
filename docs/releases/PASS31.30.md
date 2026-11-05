# PASS31.30 — Gielinor Wayfinder Identity and Continuous Validation

## Purpose

Establish **Gielinor Wayfinder** as the consistent product identity across the shipped PWA, manifests, runtime diagnostics, backup metadata, release metadata, and regression expectations. Add a GitHub Actions validation gate so every push and pull request runs the repository integrity checks.

## Changes

- Replaced user-facing `OSRS Guide` and `OSRS Companion` branding with `Gielinor Wayfinder` across the static PWA shell, page titles, offline page, manifest, runtime messages, logs, and backup metadata.
- Preserved legitimate `OSRS Wiki` references because they describe the approved secondary data source rather than the product name.
- Bumped the release to `PASS31.30`, build `pass31.30-20261105-1`, and loader version `42`.
- Changed the service-worker cache namespace to `gielinor-wayfinder-pass31.30-20261105-1` so existing clients receive the identity update instead of retaining the prior cache.
- Updated catalog metadata, verifier expectations, and historical regression gates to validate the current PASS31.30 release contract.
- Added `.github/workflows/ci.yml` for push and pull-request validation:
  - project verifier;
  - complete pytest regression suite;
  - all shipped JSON validation;
  - all shipped JavaScript syntax checks.
- Kept the existing IndexedDB database name stable as an internal compatibility namespace so existing local player data is not silently orphaned by a branding-only release.
- Regenerated both release integrity manifests after the shipped-file changes.

## Validation gate

The repository must finish with a clean Git checkpoint and passing project verification, the complete pytest suite, JSON parsing, JavaScript syntax checks, release metadata consistency, and fresh archive validation when a release archive is produced.
