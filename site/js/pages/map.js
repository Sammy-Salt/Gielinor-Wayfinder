/*
 * World map (PASS31.77 rewrite).
 *
 * Plain Leaflet 1.9.4 with a simple pixel CRS. Tiles are Explv's OSRS tile set
 * (plane/{z}/{x}/{y}.png, TMS rows). Game coordinates map straight to the map:
 *
 *   lng = gameX - ORIGIN_X        lat = gameY - ORIGIN_Y
 *   one game tile = 2^(zoom - 6) pixels, so zoom 8 is 4px per tile and a 256px
 *   tile covers 64 game tiles. Tile (tx, ty) starts at game (960 + 64*tx, 1216 + 64*ty) at zoom 8.
 *
 * Everything else (search, "show" list, deep links, popups) works on plain arrays
 * of {name, x, y, plane}. There is no clustering, no custom projection and no
 * per-zoom special casing.
 */
(function () {
  "use strict";

  const ORIGIN_X = 960;
  const ORIGIN_Y = 1216;
  const NATIVE_MAX_ZOOM = 8;
  const MAX_PLOTTED = 400;
  const WORLD = L.latLngBounds([0, 0], [145 * 64, 49 * 64]);
  // The surface world is the framed rectangle x 1016-3974, y 2106-4168. Everything else in the
  // tile set is underground (dungeons, Zanaris, Dorgesh-Kaan, instances) and only opens up when
  // something you plotted is down there.
  const SURFACE = L.latLngBounds([2106 - 1216, 1016 - 960], [4169 - 1216, 3975 - 960]);

  const $ = id => document.getElementById(id);
  const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* ---------- map ---------- */

  const CRS = L.extend({}, L.CRS.Simple, {
    scale: z => Math.pow(2, z - 6),
    zoom: s => Math.log(s) / Math.LN2 + 6
  });

  const toLatLng = (x, y) => L.latLng(y - ORIGIN_Y + 0.5, x - ORIGIN_X + 0.5);
  const toGame = ll => ({ x: Math.floor(ll.lng + ORIGIN_X), y: Math.floor(ll.lat + ORIGIN_Y) });

  const BLANK = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
  const Tiles = L.TileLayer.extend({
    getTileUrl(c) {
      return `data/map/assets/${this.options.floor}/${c.z}/${c.x}/${-c.y - 1}.png`;
    }
  });
  let area = SURFACE;
  const tilesFor = floor => new Tiles("", {
    floor, minZoom: 4, maxZoom: 10, maxNativeZoom: NATIVE_MAX_ZOOM,
    bounds: area, errorTileUrl: BLANK, keepBuffer: 2, updateWhenIdle: true,
    attribution: "OSRS map tiles © Explv"
  });

  const map = L.map("map", {
    crs: CRS, minZoom: 4, maxZoom: 10, zoomSnap: 0.5,
    maxBounds: SURFACE.pad(0.02), maxBoundsViscosity: 0.9,
    preferCanvas: true
  });
  map.zoomControl.setPosition("bottomright");

  let floor = 0;
  let tiles = tilesFor(floor).addTo(map);
  const layer = L.layerGroup().addTo(map);
  const surfaceZoom = () => Math.max(4, map.getBoundsZoom(SURFACE, true));
  map.setMinZoom(surfaceZoom());
  map.setView(toLatLng(3222, 3218), 7);

  function setArea(wide) {
    const next = wide ? WORLD : SURFACE;
    if (next === area) return;
    area = next;
    map.setMaxBounds(area.pad(0.02));
    map.setMinZoom(wide ? 4 : surfaceZoom());
    tiles.options.bounds = area;
    tiles.redraw();
  }
  map.on("resize", () => { if (area === SURFACE) map.setMinZoom(surfaceZoom()); });

  const readout = L.control({ position: "bottomleft" });
  readout.onAdd = () => L.DomUtil.create("div", "map-readout");
  readout.addTo(map);
  const showCoords = ll => {
    const g = toGame(ll);
    readout.getContainer().textContent = `x ${g.x}, y ${g.y}, floor ${floor}`;
  };
  map.on("mousemove click", e => showCoords(e.latlng));

  /* ---------- data ---------- */

  const list = v => (Array.isArray(v) ? v : []);
  const places = list(window.OSRS_MAP_LOCATIONS).map(r => ({ ...r, kind: "Place", group: "Places" }));
  const shops = list(window.OSRS_MAP_SHOPS).map(r => ({ ...r, kind: "Shop", group: "Shops" }));
  const points = list(window.OSRS_MAP_POINTS).map(r => ({ ...r, kind: "Point", group: r.legend }));
  const spawns = [
    ...list(typeof monsters !== "undefined" ? monsters : window.OSRS_MAP_MONSTERS),
    ...list(window.OSRS_MAP_NPCS)
  ];

  // Spawns grouped by name so "Man" is one search result with all its spawn points.
  const spawnGroups = new Map();
  for (const r of spawns) {
    const key = `${r.type}:${String(r.name).toLowerCase()}`;
    if (!spawnGroups.has(key)) spawnGroups.set(key, { name: r.name, kind: r.type, recs: [] });
    spawnGroups.get(key).recs.push(r);
  }

  const fixed = [...places, ...shops, ...points];
  const categories = new Map();
  for (const r of fixed) {
    if (!categories.has(r.group)) categories.set(r.group, []);
    categories.get(r.group).push(r);
  }

  /* ---------- plotting ---------- */

  const GLYPH = {
    "Fairy ring": "🍄", "Teleport destination": "✨", "Shooting star": "⭐", "Clue dig spot": "⛏",
    "Bank": "🏦", "Dungeon": "🕳", "Fishing spot": "🎣", "Slayer Master": "💀", "Shops": "🏪", "Places": "📍"
  };
  const badge = group => L.divIcon({
    className: "map-badge", html: `<span>${GLYPH[group] || "📍"}</span>`,
    iconSize: [24, 24], iconAnchor: [12, 12], popupAnchor: [0, -12]
  });

  function popup(r) {
    const bits = [`<strong>${esc(r.name)}</strong>`];
    const sub = r.shopType ? `${r.shopType}${r.owner ? ` · run by ${r.owner}` : ""}` : (r.description || r.type || "");
    if (sub && r.kind !== "Monster" && r.kind !== "NPC") bits.push(`<span>${esc(sub)}</span>`);
    if (r.kind === "Monster" || r.kind === "NPC") {
      const page = r.kind === "Monster" ? "monster" : "npc";
      bits.push(`<span>${esc(r.kind)} · <a href="${page}.html?id=${encodeURIComponent(r.id)}">Open ${esc(r.kind.toLowerCase())} page</a></span>`);
    }
    bits.push(`<span class="muted">x ${r.x}, y ${r.y}, floor ${r.plane || 0}</span>`);
    return bits.join("");
  }

  function marker(r) {
    const ll = toLatLng(r.x, r.y);
    const m = (r.kind === "Monster" || r.kind === "NPC")
      ? L.circleMarker(ll, { radius: 5, weight: 1.5, color: "#111", fillColor: r.kind === "Monster" ? "#e08b78" : "#8fb6e8", fillOpacity: 0.95 })
      : L.marker(ll, { icon: badge(r.group) });
    return m.bindPopup(popup(r));
  }

  let current = null; // { recs, title } so changing floor can redraw

  function setStatus(text) {
    $("mapStatus").textContent = text || "";
  }

  function setFloor(n) {
    n = Number(n) || 0;
    $("mapFloor").value = String(n);
    if (n === floor) return;
    floor = n;
    map.removeLayer(tiles);
    tiles = tilesFor(floor).addTo(map);
    tiles.bringToBack();
  }

  function render(fit) {
    layer.clearLayers();
    if (!current) { setArea(false); setStatus(""); return; }
    const here = current.recs.filter(r => (Number(r.plane) || 0) === floor);
    const onSurface = here.filter(r => SURFACE.contains(toLatLng(r.x, r.y)));
    // Mixed lists stay on the surface map; the underground tiles only open when everything plotted is down there.
    const shown = onSurface.length ? onSurface : here;
    const drawn = shown.slice(0, MAX_PLOTTED);
    setArea(!onSurface.length && drawn.length > 0);
    drawn.forEach(r => marker(r).addTo(layer));
    const other = current.recs.length - here.length;
    let text = `${current.title}: ${shown.length} on this floor`;
    if (other) text += `, ${other} on other floors`;
    if (onSurface.length && here.length > onSurface.length) text += `, ${here.length - onSurface.length} underground not shown`;
    if (area === WORLD) text += " (underground view)";
    if (shown.length > MAX_PLOTTED) text += ` (showing ${MAX_PLOTTED})`;
    setStatus(text);
    if (!fit || !drawn.length) return;
    if (drawn.length === 1) {
      map.setView(toLatLng(drawn[0].x, drawn[0].y), 8);
      layer.eachLayer(l => l.openPopup());
    } else {
      map.fitBounds(L.latLngBounds(drawn.map(r => toLatLng(r.x, r.y))).pad(0.3), { maxZoom: 8 });
    }
  }

  function plot(recs, title) {
    current = { recs, title };
    if (recs.length && !recs.some(r => (Number(r.plane) || 0) === floor)) setFloor(Number(recs[0].plane) || 0);
    render(true);
  }

  $("mapFloor").addEventListener("change", e => { setFloor(e.target.value); render(false); });

  /* ---------- "show on map" list ---------- */

  const show = $("mapShow");
  for (const [name, recs] of categories) {
    const o = document.createElement("option");
    o.value = name;
    o.textContent = `${name} (${recs.length})`;
    show.appendChild(o);
  }
  show.addEventListener("change", () => {
    clearResults();
    if (!show.value) { current = null; render(false); return; }
    plot(categories.get(show.value) || [], show.value);
  });

  /* ---------- search ---------- */

  const box = $("mapSearch"), results = $("mapResults");
  function clearResults() { results.hidden = true; results.replaceChildren(); }

  function find(q) {
    q = q.trim().toLowerCase();
    if (q.length < 2) return [];
    const rank = n => { n = String(n).toLowerCase(); return n === q ? 0 : n.startsWith(q) ? 1 : n.includes(q) ? 2 : 9; };
    const hits = [];
    for (const r of fixed) { const k = rank(r.name); if (k < 9) hits.push({ k, name: r.name, kind: r.kind === "Point" ? r.group : r.kind, recs: [r] }); }
    for (const g of spawnGroups.values()) { const k = rank(g.name); if (k < 9) hits.push({ k: k + 0.5, name: g.name, kind: g.kind, recs: g.recs }); }
    return hits.sort((a, b) => a.k - b.k || a.name.localeCompare(b.name)).slice(0, 25);
  }

  function choose(hit) {
    clearResults();
    box.value = hit.name;
    show.value = "";
    plot(hit.recs, hit.name);
  }

  box.addEventListener("input", () => {
    const hits = find(box.value);
    results.replaceChildren();
    if (!hits.length) { results.hidden = box.value.trim().length < 2; if (!results.hidden) results.innerHTML = '<p class="empty">No matches.</p>'; return; }
    for (const h of hits) {
      const b = document.createElement("button");
      b.type = "button";
      b.setAttribute("role", "option");
      const count = h.recs.length > 1 ? ` · ${h.recs.length} spawns` : "";
      b.innerHTML = `${esc(h.name)} <small>${esc(h.kind)}${count}</small>`;
      b.addEventListener("click", () => choose(h));
      results.appendChild(b);
    }
    results.hidden = false;
  });
  box.addEventListener("keydown", e => {
    if (e.key === "Enter") { const first = find(box.value)[0]; if (first) { e.preventDefault(); choose(first); } }
    if (e.key === "Escape") clearResults();
  });
  map.on("click", clearResults);

  /* ---------- deep links: ?q=name  ?legend=Category  ?npc=id,id ---------- */

  (function deepLink() {
    let params;
    try { params = new URLSearchParams(location.search); } catch { return; }
    const npcIds = (params.get("npc") || "").split(",").filter(Boolean).map(Number).filter(Number.isFinite);
    const legend = params.get("legend");
    const q = (params.get("q") || "").trim();
    if (npcIds.length) {
      const ids = new Set(npcIds);
      const recs = spawns.filter(r => ids.has(Number(r.id)));
      if (recs.length) { box.value = recs[0].name; plot(recs, recs[0].name); }
    } else if (legend && categories.has(legend)) {
      show.value = legend;
      plot(categories.get(legend), legend);
    } else if (q.length >= 2) {
      const first = find(q)[0];
      if (first) choose(first); else { box.value = q; box.dispatchEvent(new Event("input")); }
    }
  })();
})();
