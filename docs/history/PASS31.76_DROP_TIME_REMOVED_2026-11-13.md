# PASS31.76 – Remove Drop & Kill Time

Drop & Kill Time repeated Drop Statistics (same monster/drop pickers, same exact-rate source, same chance milestones). The only thing it added was kills per hour, so that moved into Drop Statistics as one optional input that adds "Expected time", "Drops per hour" and a time under each chance milestone.

Removed: `drop-time.html`, `js/pages/drop-time.js`, `css/pages/drop-time.css`, its nav, Calculators and Home links, route and service-worker entries. Tests 20, 21, 27 and 29 now check `drop-stats.js`.
