# PASS31.71 – Back links removed, Goals margins, total-level fix

- Removed the old "← Dashboard" link from Goals and Quest Tracker, and "← Quest Tracker" from quest detail pages.
- Goals page content is wrapped in `<main class="osrs-content">` so it has side margins like other pages.
- Total level was inconsistent across pages (Home 393, Character 394, Progress 379). Progress looked up "Range" so Ranged counted as level 1; it now also tries "Ranged". Home skipped Summoning. All three now show 394 for the bundled save.
