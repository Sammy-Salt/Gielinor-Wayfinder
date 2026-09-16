const detailPages = {
  "monster.html": "monsters",
  "item.html": "items",
  "npc.html": "npcs",
  "boss.html": "bosses"
};

export function initShell() {
  const page = (location.pathname.split("/").pop() || "index.html").toLowerCase();
  const nav = document.getElementById("site-nav");
  const active = detailPages[page] || page.replace(/\.html$/, "");

  document.documentElement.dataset.page = active;
  document.body.dataset.page = active;

  if (!document.querySelector(".osrs-skip-link")) {
    const skip = document.createElement("a");
    skip.className = "osrs-skip-link";
    skip.href = "#main-content";
    skip.textContent = "Skip to main content";
    document.body.prepend(skip);
  }

  const main = document.querySelector("main,.osrs-content,.container,.content");
  if (main && !main.id) main.id = "main-content";

  if (!nav) return;

  nav.querySelectorAll("a[href]").forEach((link) => {
    link.removeAttribute("aria-current");
    const href = link.getAttribute("href")?.split("?")[0]?.split("#")[0];
    if (href === page || (detailPages[page] && href === `${detailPages[page]}.html`)) {
      link.setAttribute("aria-current", "page");
    }
  });

  nav.querySelectorAll("details[open]").forEach((menu) => menu.removeAttribute("open"));
  if (!nav.dataset.shellBound) {
    nav.dataset.shellBound = "true";
    document.addEventListener("click", (event) => {
      nav.querySelectorAll("details[open]").forEach((menu) => {
        if (!menu.contains(event.target)) menu.removeAttribute("open");
      });
    }, { passive: true });
  }
}
