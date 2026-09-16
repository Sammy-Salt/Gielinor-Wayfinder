# ADR-0002: Standalone Item Detail Stabilization

**Status:** Accepted temporarily

## Decision

Keep the standalone item detail loader while acquisition relationships are restored and the shared runtime is stabilized.

## Rationale

The standalone path was the first implementation confirmed working in Firefox/Android after the item-loading regression. Reintroducing a broad bootstrap dependency before its failure modes are controlled would risk repeating the original problem.

## Exit condition

A shared repository path must pass the same core item, relationship, offline, and Firefox smoke tests before the standalone path is removed.
