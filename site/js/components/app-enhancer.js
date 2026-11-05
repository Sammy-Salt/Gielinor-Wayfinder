import { UniversalSearch } from "../services/universal-search.js";
import { OfflineStore } from "../core/offline-store.js";
import { PlayerBackup } from "../core/backup.js";

export function enhanceAppShell() {
  const tools = document.getElementById("app-tools");
  const host = document.getElementById("app-tools-host");
  if (!tools || !host) return;
  if (tools.parentElement !== host) host.appendChild(tools);

  const input = document.getElementById("globalSearch");
  const searchButton = tools.querySelector(".global-search-submit");
  const results = document.getElementById("globalSearchResults");
  if (!input || !searchButton || !results || tools.dataset.bound === "true") return;
  tools.dataset.bound = "true";

  const install = document.getElementById("installApp");
  const status = document.getElementById("offlineStatus");
  const exportBtn = tools.querySelector("[data-action=export-player]");
  const importInput = tools.querySelector("input[type=file]");

  const runSearch = async () => {
    const query = input.value.trim();
    results.replaceChildren();
    results.classList.remove("is-open");
    if (!query) return;
    results.textContent = "Searching…";
    results.classList.add("is-open");
    try {
      const rows = await UniversalSearch.search(query, { limit: 16 });
      results.replaceChildren();
      if (!rows.length) { results.textContent = "No matches."; return; }
      for (const row of rows) {
        const link = document.createElement("a");
        link.className = "global-search-result";
        link.href = `${row.path}?id=${encodeURIComponent(row.id)}`;
        const strong = document.createElement("strong");
        strong.textContent = row.name;
        const span = document.createElement("span");
        span.textContent = row.label;
        link.append(strong, span);
        results.appendChild(link);
      }
    } catch (error) {
      results.replaceChildren();
      results.classList.add("is-open");
      const message = document.createElement("span");
      message.className = "search-error";
      message.textContent = "Search unavailable. Try again or check offline data.";
      results.appendChild(message);
      console.warn("[Gielinor Wayfinder] global search failed", error);
    }
  };

  let timer;
  input.addEventListener("focus", () => UniversalSearch.warm().catch(() => {}));
  input.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(runSearch, 150); });
  input.addEventListener("change", runSearch);
  input.addEventListener("keydown", event => { if (event.key === "Enter") { event.preventDefault(); clearTimeout(timer); runSearch(); } });
  searchButton.addEventListener("click", () => { clearTimeout(timer); runSearch(); });

  let installEvent = null;
  window.addEventListener("beforeinstallprompt", event => { event.preventDefault(); installEvent = event; if (install) install.hidden = false; });
  install?.addEventListener("click", async () => { if (!installEvent) return; await installEvent.prompt(); installEvent = null; install.hidden = true; });
  exportBtn?.addEventListener("click", () => PlayerBackup.export());
  importInput?.addEventListener("change", async () => {
    if (!importInput.files?.[0]) return;
    try { await PlayerBackup.import(importInput.files[0]); location.reload(); }
    catch (error) { alert("Player backup could not be imported: " + error.message); }
  });

  const updateOfflineStatus = () => { if (status) status.textContent = navigator.onLine ? "🟢 Online · offline cache ready" : "🟡 Offline mode"; };
  window.addEventListener("online", updateOfflineStatus);
  window.addEventListener("offline", updateOfflineStatus);
  updateOfflineStatus();
  OfflineStore.set("app:lastSeen", Date.now()).catch(() => {});
}
