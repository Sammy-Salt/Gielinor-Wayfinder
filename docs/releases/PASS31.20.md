# PASS31.20 — Navigation, Character Runtime, and Drop-Rate Stabilization

## Reported regressions addressed
- Primary navigation is isolated from the full-width search row so Character and other navigation controls remain visible.
- Item detail pages initialize the shared navigation search without sacrificing their standalone data-loading path.
- Crafting is directly reachable from the primary navigation on every normal page.
- Character snapshot format version 2 is accepted; the 2009Scape save-backed page can render the normalized snapshot.
- Character sections are real collapsible controls and open by default.
- Drop Time now receives exact rate strings from a compact trusted OSRS Wiki fallback index when the 2009Scape relationship does not carry a rate.

## Source policy
2009Scape primary; OSRS Wiki secondary; Ragger absent. The Wiki drop-rate index is fallback evidence only and never replaces a 2009Scape relationship.

## Validation
- Full JavaScript syntax check
- Full JSON parse check
- PASS31.20 regression suite
- Existing PASS31.18/31.19 regression suites updated to recognize the current release
- Service-worker build/cache metadata updated
- Protected map data unchanged
