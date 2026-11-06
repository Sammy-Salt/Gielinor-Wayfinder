# Crafting & Production — PASS31.19

PASS31.19 adds an offline recipe browser backed by the existing PASS31.9 Wiki recipe snapshot. 2009Scape remains the primary source policy; no 2009Scape recipe catalog was present in the PASS31.18 site export, so these recipe records are explicitly marked as OSRS Wiki secondary data. Ragger is excluded.

The page supports search, skill filtering, character skill checks, bank-material checks, item links, and truthful unknown/incomplete recipe fields. Recipe item names are resolved through the shared `Catalog.list("items")` index, with `Catalog.get("items", id)` detail lookup as a fallback. Recipe loading normalizes singular/plural output fields and validates every input/output reference before rendering, so a catalog lookup failure is visible in the summary instead of silently dropping a recipe name.
