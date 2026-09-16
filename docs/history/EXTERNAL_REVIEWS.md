# Consolidated External Review Findings

The PASS31.17 reviews consistently supported the following durable conclusions:

- The item file catalog is structurally healthy: indexed IDs have matching detail files.
- The standalone item page is a valid stabilization technique and was confirmed to execute against real item JSON.
- The standalone rewrite caused a user-visible acquisition-data regression because source arrays were left empty.
- The project needs typed canonical contracts, first-class relationships, provenance, reproducible generation, automated integrity tests, and consistent release metadata.
- The service worker should explicitly precache page modules needed for first-use offline behavior.
- Duplicate names are not safe identities; stable IDs and conservative deterministic resolution are required.

Obsolete recommendations that conflict with the current project source policy are intentionally not carried forward.

## PASS31.22 — Claude patch review

A Claude-produced `OSRS_Guide_PASS31_21_crafting_fix.zip` was reviewed as an external candidate patch. Its useful changes were limited to Character/Crafting presentation and a small Crafting HTML-escaping correction. It did not resolve the navigation regression. The navigation regression was traced to flex-layout competition between the runtime primary-navigation wrapper and the full-width search row, so the project implementation uses a deterministic two-row layout instead of adopting the external patch wholesale.
