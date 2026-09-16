# Drops and Drop Calculators

## Canonical model

Monster→item drop relationships are generated from the local 2009Scape-derived relationship graph. The relationship itself is authoritative. A relationship may additionally carry a structured probability record.

## Probability provenance

2009Scape is preferred when an authoritative probability is present in the source data. OSRS Wiki can provide secondary evidence only for an already-existing relationship, and only when its published probability is exact and unambiguous. Approximate, conflicting, variable, or unsupported rates remain unknown.

Rates are represented as numerator/denominator rather than assuming every rate is `1/N`. This supports values such as `9/128` correctly.

## Runtime consumers

- Monster detail: canonical drop relationships.
- Drop Statistics: canonical relationship + structured probability.
- Drop Time: canonical relationship + structured probability.
- Item acquisition: existing acquisition pipeline remains separate because it also contains shops and ground-spawn state.

## Unknown data

The UI must say that a rate is unavailable rather than manufacture a probability. This is intentional data integrity behavior.
