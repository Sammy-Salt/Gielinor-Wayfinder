import { OSRS } from "../core/osrs.js";
import { escapeHTML as esc } from "../core/utils.js";
import { Catalog } from "../services/catalog-service.js";
import { shopsHTML } from "../services/shop-service.js";

const params = new URLSearchParams(location.search);
const id = Number(params.get("id"));

let meta = null;

const app = document.getElementById("app");

function prettyKey(k){
    return k
        .replace(/_/g," ")
        .replace(/\b\w/g,c=>c.toUpperCase());
}

function formatValue(v){
    if(v === null || v === undefined || v === "")
        return '<span class="muted">—</span>';

    if(typeof v === "boolean")
        return v ? "Yes" : "No";

    if(Array.isArray(v)){
        if(!v.length) return '<span class="muted">—</span>';

        if(v.every(x => typeof x !== "object"))
            return v.map(x=>`<span class="badge">${esc(x)}</span>`).join("");

        return `<pre>${esc(JSON.stringify(v,null,2))}</pre>`;
    }

    if(typeof v === "object")
        return `<pre>${esc(JSON.stringify(v,null,2))}</pre>`;

    return esc(v);
}

function stat(key,value){
    return `
        <div class="stat">
            <div class="label">${esc(prettyKey(key))}</div>
            <div class="value">${formatValue(value)}</div>
        </div>
    `;
}

function section(title, keys, monster){
    const present = keys.filter(k =>
        Object.prototype.hasOwnProperty.call(monster,k) &&
        monster[k] !== null &&
        monster[k] !== undefined &&
        monster[k] !== ""
    );

    if(!present.length) return "";

    return `
        <div class="card">
            <h2>${esc(title)}</h2>
            <div class="grid">
                ${present.map(k=>stat(k,monster[k])).join("")}
            </div>
        </div>
    `;
}

(async function(){
    try {
        meta = (await OSRS.Data.list("monsters")).find(x => Number(x.id) === id) || null;
        if(!meta){ OSRS.setHTML(app,'<div class="card">Monster not found.</div>'); return; }
        const monster = await Catalog.get("monsters", id);
        const itemNameIndex = await OSRS.Data.itemNameIndex();

        document.title = monster.name || meta.name || "Monster";

        const combatKeys = [
            "combat_level",
            "lifepoints",
            "hitpoints",
            "attack_level",
            "strength_level",
            "defence_level",
            "magic_level",
            "range_level",
            "ranged_level",
            "max_hit",
            "attack_speed",
            "attack_style",
            "combat_style",
            "aggressive",
            "attack_bonus",
            "strength_bonus",
            "magic_attack",
            "magic_strength",
            "ranged_attack",
            "ranged_strength",
            "defensive_stab",
            "defensive_slash",
            "defensive_crush",
            "defensive_magic",
            "defensive_light_ranged",
            "defensive_standard_ranged",
            "defensive_heavy_ranged"
        ];

        const slayerKeys = [
            "slayer_category",
            "slayer_xp",
            "slayer_assigned_by"
        ];

        const specialKeys = [
            "weakness",
            "poisonous",
            "poison_immune",
            "can_tolerate",
            "aggressive",
            "movement_radius",
            "respawn_delay",
            "safespot",
            "projectile",
            "protect_style",
            "prj_height",
            "start_gfx",
            "end_gfx",
            "start_height",
            "end_height",
            "water_npc",
            "force_talk",
            "facing_booth",
            "clue_level",
            "elemental_weakness_type",
            "elemental_weakness_percent",
            "immunities",
            "attributes",
            "size",
            "respawn",
            "members"
        ];

        const locations = monster.locations || [];
        const locationGroups = {};

        locations.forEach(loc => {
            const name = loc.location || loc.name || (Number(loc.plane) ? `Floor ${loc.plane}` : "Ground floor");
            if (!locationGroups[name]) locationGroups[name] = [];
            locationGroups[name].push(loc);
        });

        let locationHTML = "";

        if (Object.keys(locationGroups).length) {
            locationHTML = Object.entries(locationGroups).map(([name, spawns], i) => `
                <details class="location">
                    <summary>
                        <strong>${esc(name)}</strong>
                        <span class="muted">${spawns.length.toLocaleString()} spawn${spawns.length === 1 ? "" : "s"}</span>
                    </summary>
                    <div class="coords">
                        ${spawns.map(loc => `
                            <div>
                                X: ${esc(loc.x ?? "—")}
                                &nbsp;&nbsp;
                                Y: ${esc(loc.y ?? "—")}
                                &nbsp;&nbsp;
                                Plane: ${esc(loc.plane ?? 0)}
                            </div>
                        `).join("")}
                    </div>
                </details>
            `).join("");
        } else {
            locationHTML =
                '<div class="muted">No spawn locations available.</div>';
        }

        OSRS.setHTML(app, `

            <h1>${esc(monster.name || meta.name)}</h1>

            <div class="sub">
                NPC ID: ${esc(monster.id ?? id)}
                ${monster.boss ? " · Boss" : ""}
            </div>

            <div class="muted small">Primary source: 2009Scape · Wiki used only as a secondary fallback where available</div>

            ${section("Combat",combatKeys,monster)}

            ${section("Slayer",slayerKeys,monster)}
${section("Special Properties",specialKeys,monster)}

            <details>
                <summary>
                    📍 Locations — ${locations.length.toLocaleString()} spawns ▸
                </summary>

                <div>
                    ${locationHTML}
                </div>
            </details>

            ${await shopsHTML(monster.id ?? id)}

            ${await (async()=>{
                const rows = await OSRS.Relationships.monsterDrops(monster.id ?? id);
                if(!rows.length) return "";
                return `
                <details>
                    <summary>
                        💰 Known Drops — ${rows.length.toLocaleString()} ▸
                    </summary>
                    <div class="drop-table">
                        <div class="drop-row drop-header"><div>Item</div><div>Source</div></div>
                        ${rows.map(d=>`<div class="drop-row"><div class="drop-item"><a href="item.html?id=${encodeURIComponent(d.itemId)}">${esc(d.itemName || d.name || "Unknown")}</a></div><div class="drop-quantity">${esc(d.rateDisplay || (d.rateStatus === "conflict" ? "Rate unresolved" : "Rate unavailable"))}</div></div>`).join("")}
                    </div>
                </details>`;
            })()}

        `);

    } catch (error) {
        OSRS.setHTML(app, '<div class="card">Monster detail data could not be loaded.</div>');
        console.error(error);
    }
})();
