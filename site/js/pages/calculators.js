const app = document.querySelector("main,.osrs-content,.container,.content");
if (app) {
  const links = [
    ["combat-stats.html", "⚔ Combat Stats", "Combat accuracy, damage and DPS estimates."],
    ["skill-stats.html", "📈 Skill Stats", "XP, actions and time-to-level estimates."],
    ["drop-stats.html", "📊 Drop Statistics", "Probability and expected-kill calculations."],
    ["drop-time.html", "🎯 Drop Time", "Estimate time required for target drops."]
  ];
  const wrap = document.createElement("section");
  wrap.className = "card";
  const h = document.createElement("h1");
  h.textContent = "🧮 Calculators";
  const grid = document.createElement("div");
  grid.className = "grid grid-auto";
  for (const [href, title, desc] of links) {
    const a = document.createElement("a");
    a.className = "osrs-card osrs-card-link";
    a.href = href;
    const t = document.createElement("h2");
    t.textContent = title;
    const p = document.createElement("span");
    p.textContent = desc;
    a.append(t, p);
    grid.appendChild(a);
  }
  wrap.append(h, grid);
  app.replaceChildren(wrap);
}
