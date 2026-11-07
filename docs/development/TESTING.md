# Testing

Testing is part of the implementation contract. Historical PASS tests remain to protect regressions discovered during development.

## Required checks

Every release-level change should cover the applicable subset of:

- JSON syntax and structural contracts;
- entity/detail-file integrity;
- relationship endpoint integrity, including `scripts/validate_drop_relationships.py` for exact drop fractions;
- source precedence and provenance;
- JavaScript syntax;
- service-worker/release metadata consistency;
- protected map-boundary integrity;
- no retired-source production references;
- ZIP integrity and fresh extraction;
- representative navigation and invalid-ID behavior;
- target-runtime Firefox/Android smoke testing when runtime behavior is involved.

## Continuous validation

`.github/workflows/ci.yml` runs the project verifier, the complete pytest regression suite, JSON parsing for every shipped JSON file, and Node.js syntax checks for every shipped JavaScript file on every push and pull request. Local validation remains required before a PASS commit; CI provides the shared remote gate rather than replacing release-specific fresh-extraction or runtime smoke testing.

## Shared-shell invariants

Every normal shell page must have exactly one static `#site-nav`, one static `#app-tools-host`, and one static `#app-tools`. Character and Crafting each appear once in the canonical navigation.

Runtime JavaScript may enhance these elements but must not create, replace, remove, or reparent the canonical navigation. `app-enhancer.js` must not depend on navigation layout.

## Service worker

The service worker must expose the current release build ID, use the current cache namespace, include versioned loader/bootstrap assets, and accept `SKIP_WAITING`. Production loader behavior must handle waiting-worker activation before release-selected bootstrap execution.

## Fresh extraction

Do not validate only the working tree. A release archive must be extracted into a clean directory and validated again. This catches missing files, stale manifests, path mistakes, and accidental inclusion of generated artifacts.
