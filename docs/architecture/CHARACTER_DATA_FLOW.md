# Character Data Flow — PASS31.19

2009Scape player save → normalized `player-sync.json` snapshot → `OSRSSync` → Character page / Progress / Crafting.

The normalized snapshot is read-only and intentionally excludes arbitrary unmapped varps/attributes from presentation. Inventory, equipment and bank remain item-ID based and resolve through the existing local item catalog.
