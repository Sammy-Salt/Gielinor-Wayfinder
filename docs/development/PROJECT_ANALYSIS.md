# Project Deep Analysis — PASS31.27 Baseline

## Purpose

This is the maintained architectural assessment of the current Gielinor Wayfinder repository. It records what the project actually contains at the PASS31.27 baseline, where responsibilities live, what invariants are important, and which areas require special care during future AI-assisted development.

## 1. Product boundary

Gielinor Wayfinder is an offline-first PWA companion for the 2009Scape experience. The deployable application is `site/`. Development infrastructure lives above it.

The repository currently contains:

- 21 normal shell pages with the canonical navigation/tools shell;
- 22 HTML files total, including the root development landing page;
- 73 production JavaScript modules;
- 26 CSS files;
- a large offline JSON data/catalog corpus;
- reproducible data-pipeline scripts;
- PASS regression tests;
- architecture, data, feature, decision, history, and release documentation.

The map assets are intentionally large and protected by a map-boundary audit. A future AI must not rewrite or regenerate them casually.

## 2. Runtime architecture

The runtime has five practical layers:

1. **Static HTML shell** — provides usable navigation and page structure before JavaScript finishes.
2. **Loader/bootstrap** — selects the release runtime and initializes shared behavior.
3. **Core runtime** — routing, shell, state, persistence, storage, player services, and common utilities.
4. **Services/components** — search, relationships, acquisition, progression, player sync, backup, and other reusable domain behavior.
5. **Page modules** — page-specific rendering and interaction.

The service worker provides offline caching and release-versioned runtime assets.

### Ownership rule

The HTML document owns the canonical shell. `shell.js` enhances the existing navigation. `app-enhancer.js` binds existing application tools in `#app-tools-host`. No runtime component should create a competing navigation or replace the canonical shell.

This rule directly addresses the historical PASS31.22–31.25 navigation race and must not be weakened.

## 3. Data architecture

The data model separates entities from relationships.

### Entity identity

Items, monsters, NPCs, and quests use stable numeric identifiers. Names are display/search attributes, not primary identity.

### Relationships

Drops, shops, recipes, and location information are represented as relationships where possible. Runtime pages should consume canonical relationship services rather than reconstructing relationships with ad-hoc string matching.

### Source precedence

The project's data foundation is:

1. 2009Scape primary;
2. OSRS Wiki secondary;
3. unknown if trusted evidence is insufficient.

A secondary Wiki record may enrich a trusted relationship only when identity and evidence are safe. Conflicts, approximate values, and ambiguous matches must remain unresolved rather than being converted into false precision.

### Retired source

Ragger is not a valid production source. Production scans must continue to enforce zero Ragger references.

## 4. Canonical monster-drop path

`site/data/relationships/monster-drops.json` is the canonical runtime dataset for monster→item drop relationships and structured probability provenance.

The relationship generator is `data-pipeline/generate_drop_relationships.py`.

The current dataset records 52,094 monster→item relationships. PASS31.27 retains 348 Wiki-enriched exact rates, 11 conflicting Wiki-rate cases withheld from calculation, and 51,735 relationships without a trusted exact rate. No external third-party drop table is substituted for missing 2009Scape evidence.

The important architectural property is that Drop Statistics (which also estimates time from kills per hour) uses the canonical relationship source. A standalone duplicate rate database must not become the hidden source of truth again.

## 5. Item acquisition path

Item acquisition is a related but distinct domain because it includes shop relationships, monster drops, and the explicit unknown state for ground spawns. The item detail page is intentionally resilient as a standalone page in Firefox and must retain the shared static shell.

The acquisition generator is `data-pipeline/generate_acquisition.py`.

## 6. Character/player path

The character feature consumes a normalized offline player snapshot rather than exposing arbitrary raw save variables directly to the UI.

The established save contract includes skills/XP, inventory, equipment, bank, location, quest progress, energy/prayer/lifepoints, spellbook, slayer state, achievement diaries, pouches, appearance, and selected named statistics. Unverified raw variables remain unmapped.

The sync format is versioned. A format-version mismatch is a compatibility error, not a reason to silently reinterpret the save.

## 7. Crafting path

Crafting is an offline recipe browser with filtering, requirement checks, bank-material checks, and item links. Its current recipe source is a secondary Wiki snapshot because the relevant 2009Scape recipe catalog was not present in the established site export. This is explicitly documented rather than disguised as primary game data.

## 8. PWA/update architecture

`site/js/local-loader.js` is the canonical production entrypoint. It handles deterministic local development behavior and release update sequencing. The service worker uses a release-specific cache namespace and exposes `SKIP_WAITING` handling.

Release metadata, loader versions, bootstrap versions, and service-worker asset references must remain synchronized.

## 9. Testing architecture

PASS tests are incremental regression gates, not disposable scripts. Historical PASS tests remain in the repository to protect regressions discovered during development. Current-release compatibility ranges may be updated when the architecture intentionally advances, but the semantic regression checks must not be deleted merely because the PASS number changed.

Release validation also needs fresh extraction because a source tree can pass while an archive is malformed or incomplete.

## 10. Documentation architecture

Permanent knowledge is organized as:

- `docs/architecture/` — how the application is built and loaded;
- `docs/data/` — source, identity, provenance, and relationship contracts;
- `docs/features/` — feature behavior and user-facing contracts;
- `docs/development/` — workflow, AI protocol, testing, Git, and release process;
- `docs/decisions/` — durable architectural decisions;
- `docs/releases/` — PASS history;
- `docs/history/` — consolidated external-review findings.

This structure is intentionally similar to a conventional Android/software project: source is separated from tests, build/data tooling, documentation, and release history.

## 11. Current baseline findings

### Healthy / protected

- Canonical static navigation exists across the 21 shell pages.
- Application tools are static and outside the navigation.
- Character and Crafting are static first-class navigation links.
- Production Ragger scan is clean.
- Monster-drop relationships have a canonical dataset.
- Character sync is versioned.
- Map boundaries are explicitly protected.
- PASS regression tests are retained.

### Governance gaps identified by this analysis

- The project previously had no committed `.git` history in the supplied source archive.
- The existing documentation was organized but many documents were too terse to act as an onboarding contract for an independent AI.
- The root `scripts/` directory existed but was empty.
- Generated Python cache files were present in the source archive even though they are not project source.
- Release metadata is now synchronized at PASS31.27; historical metadata mismatches are retained only in PASS history.
- The previous PASS31.26 governance baseline did not yet cover all runtime data-access duplication found during the PASS31.27 polish audit.

PASS31.27 addresses the remaining architecture/data-integrity inconsistencies while preserving the working shell and map boundary.

## 12. Future-change risk map

High-risk areas requiring extra validation:

- service-worker/loader/cache behavior;
- shared HTML shell/navigation;
- standalone item loading;
- canonical monster-drop probability data;
- player-sync format/schema;
- map assets and map-boundary files;
- generated catalogs and release manifests.

Medium-risk areas:

- universal search;
- acquisition relationships;
- progression/quest services;
- crafting requirements and recipe normalization.

Low-risk changes are still subject to the same documentation and Git rules when they affect project behavior.

## 13. Non-negotiable invariants

1. Offline-first remains the product boundary.
2. 2009Scape is primary.
3. OSRS Wiki is secondary.
4. Unknown is preferable to invented data.
5. Ragger remains absent from production.
6. One canonical navigation exists.
7. Application tools remain outside navigation ownership.
8. Canonical relationships are consumed by their runtime consumers.
9. Map boundaries remain protected unless a map-specific change is authorized.
10. Every completed change is documented, tested, reviewed in Git, and committed.

## 14. PASS31.27 polish findings

- Item, Character, and Crafting pages now use the shared data-access layer instead of page-local `fetch()` calls.
- Item and Monster drop displays consume the canonical monster-drop relationship service instead of the older acquisition/relationship duplication path.
- Drop Statistics uses the structured exact-rate adapter and explicitly distinguish unavailable/conflicting rates from calculable rates.
- The calculator defaults to a monster with an exact trusted rate when one exists, while still preserving unknown relationships as unknown.
- Obsolete map/test CSS was moved out of the shipped PWA into `audit/map-tests/`.
- The obsolete runtime relationship component was removed after its consumers were eliminated; detail pages now own their canonical relationship presentation.


## PASS31.28 canonical drop-data update

PASS31.28 supersedes the PASS31.27 drop relationship runtime with the pinned 2009Scape `drop_tables.json` payload. The source expands to 52,194 unique monster→item relationships, including 100 tertiary relationships. Weighted probabilities are calculated from source weights, and runtime access uses lazy gzip-compressed per-monster/per-item shards. The supplied source payload is pinned by SHA-256 because it does not embed an upstream commit identifier.

## PASS31.29 drop-rate presentation update

PASS31.29 preserves the PASS31.28 canonical probability model and normalizes all player-facing exact drop-rate displays to `1/X`. The shared runtime formatter derives presentation from the exact numerator/denominator fields, while the generator emits the same normalized display into canonical shards.

## PASS31.30 identity and validation update

PASS31.30 establishes Gielinor Wayfinder as the shipped product identity across the PWA shell, page titles, manifest, release metadata, runtime diagnostics, and backup metadata. Legitimate `OSRS Wiki` references remain because they describe the approved secondary source rather than the product name. The service-worker namespace and loader version are bumped so existing clients do not retain the prior product shell.

The repository now includes `.github/workflows/ci.yml`, which runs the project verifier, the complete pytest regression suite, JSON parsing, and JavaScript syntax checks on every push and pull request. The internal IndexedDB name remains stable as a compatibility namespace so the branding-only release does not orphan existing local player data.
