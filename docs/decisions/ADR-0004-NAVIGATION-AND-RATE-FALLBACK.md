# ADR-0004: Navigation Shell and Canonical Drop Relationships

**Status:** Superseded for navigation by ADR-0005. Drop-relationship portions remain accepted.

## Decision

The shipped HTML navigation is canonical. Runtime code enhances the existing `#site-nav` and must not delete or recreate it. Global search is appended to that same navigation. Character and Crafting are first-class top-level links.

For monster drops, the canonical relationship dataset is the single runtime source for the Drop Time and Drop Statistics calculators. The existence of a monster→item relationship is authoritative from the local 2009Scape-derived game-data graph. OSRS Wiki is secondary evidence only for enriching an existing relationship with an unambiguous exact published probability. Conflicting, approximate, variable, or unsupported Wiki rates remain unavailable rather than being guessed. Ragger is excluded.

## Historical navigation rationale

The earlier two-row runtime-wrapper approach was implemented in PASS31.22 but proved architecturally wrong in practice because the project already contained static navigation while `initShell()` also created a second navigation. PASS31.23 removes that competing ownership model. See ADR-0005.

## Drop-rate rationale

The canonical relationship dataset prevents calculator rate data from drifting away from actual monster drop relationships. A probability is represented with its type, numerator/denominator where applicable, and provenance so exact published rates remain distinct from unavailable or uncertain values.
