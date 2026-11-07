# Items

The item list navigates by numeric item ID. The item detail page must load core item data independently enough to remain resilient in Firefox.

The **Where to Get It** section may display:

- 2009Scape shop relationships
- OSRS Wiki fallback monster-drop relationships when safely resolved
- trusted ground spawns when available

Secondary-source entries are visibly marked with `*`. Unknown data is not presented as a negative fact.

Item records preserve raw 2009Scape compound fields and expose normalized data when the source shape is valid. A 15-value `bonuses` string is retained as `bonusesRaw` and expanded into labeled `bonusStats`; numeric requirement pairs are retained as `requirementsRaw` and expanded into `requirementsParsed` with `typeId` and `level`.
