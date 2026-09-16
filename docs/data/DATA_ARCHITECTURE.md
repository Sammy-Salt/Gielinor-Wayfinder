# Data Architecture

Production data is generated into simple offline-friendly JSON catalogs.

## Entity data

Items, monsters, NPCs, quests, and other catalogs use stable numeric IDs. IDs, not names, are the navigation identity.

## Relationship data

Drops, recipes, shops, and locations are relationships with typed endpoints. UI pages must not reconstruct them from ad-hoc string matching at runtime.

## Unknown vs empty

- `[]` means a validated relationship list is present and contains no entries.
- `status: unknown` means the trusted pipeline does not currently have enough evidence.
- `status: unresolved` means a candidate exists but identity/evidence was not safe enough to publish.
