# PASS31.61 — Reference page item links (2026-11-11)

Item names on the Reference page (clue reward tables, and Barrows, Mage Training Arena, Castle Wars and Fishing Trawler tables) now link to `item.html?id=<id>`. Table cells accept plain text or a list of item links; ids are URL-encoded and names HTML-escaped. Rows with more than four items show the first four then "…". Browser-checked: 125 links on the easy clue table, Barrows armour links resolve to the item page.

Gate: `tests/test_pass31_60.py` (extended with the link assertions).
