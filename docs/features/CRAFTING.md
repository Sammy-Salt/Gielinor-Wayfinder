# Crafting & Production — PASS31.19

PASS31.19 adds an offline recipe browser backed by the existing PASS31.9 Wiki recipe snapshot plus 157 authoritative 2009Scape Smithing recipes. The 2009Scape records cover the metal bars and products defined by the uploaded `Bars.java`, `SmithingType.java`, and `BarType.java` sources, including Bronze equipment. Ragger is excluded.

The page supports search, skill filtering, character skill checks, bank-material checks, item links, and truthful unknown/incomplete recipe fields. Recipe item names are resolved through the shared `Catalog.list("items")` index, with `Catalog.get("items", id)` detail lookup as a fallback. Recipe loading normalizes singular/plural output fields and validates every input/output reference before rendering, so a catalog lookup failure is visible in the summary instead of silently dropping a recipe name.
