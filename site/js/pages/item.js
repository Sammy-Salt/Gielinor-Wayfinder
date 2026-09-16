import { enhanceAppShell } from "../components/app-enhancer.js";
enhanceAppShell();
function esc(value){
    return String(value ?? "").replace(/[&<>\"']/g, char => ({
        "&":"&amp;", "<":"&lt;", ">":"&gt;",
        "\"":"&quot;", "'":"&#39;"
    }[char]));
}

function setHTML(element, html){
    if(!element) return;
    const doc = new DOMParser().parseFromString(String(html ?? ""), "text/html");
    for(const node of [...doc.body.querySelectorAll("script,style,iframe,object,embed,form")]) node.remove();
    element.replaceChildren(...doc.body.childNodes);
}

const params = new URLSearchParams(location.search);
const id = params.get("id");
let itemData = null;


function row(label,value){

    if(value === undefined || value === null || value === "")
        return "";

    return `
        <div class="row">
            <span class="label">${esc(label)}</span>
            <span class="value">${esc(value)}</span>
        </div>
    `;
}

function yesNo(value){
    if(value === undefined || value === null || value === "") return "Unknown";
    if(value === true || value === "true" || value === 1 || value === "1") return "Yes";
    if(value === false || value === "false" || value === 0 || value === "0") return "No";
    return "Unknown";
}

async function loadItem(){
    const content=document.getElementById("content");
    if(!id || !/^\d+$/.test(id)){ setHTML(content,'<div class="card"><h1>Invalid Item</h1></div>'); return; }
    try {
        const response = await fetch(`data/items/${encodeURIComponent(id)}.json`, {cache:"no-store"});
        if(!response.ok) throw new Error(`Item data request failed: HTTP ${response.status}`);
        itemData = await response.json();
        render();
    } catch(error) {
        console.error("[OSRS Guide] item load failed", error);
        setHTML(content, `
            <div class="card">
                <h1>Item Not Found</h1>
                <div class="muted">${esc(error?.message || `No item data exists for ID ${id}.`)}</div>
            </div>
        `);
    }
}

function render(){

    const item = itemData;

    if(!item){

        setHTML(document.getElementById("content"), `
            <div class="card">
                <h1>Item Data Unavailable</h1>
            </div>
        `);

        return;
    }

    document.title = item.name || "Item";

    /* The item record contains trusted acquisition relationships generated
       from 2009Scape primary data and OSRS Wiki secondary evidence. */
    const acquisition = item._acquisition || {};
    const drops = Array.isArray(acquisition.monsterDrops) ? acquisition.monsterDrops : [];
    const shops = Array.isArray(acquisition.shops) ? acquisition.shops : [];
    const ground = acquisition.groundSpawns || {status:"unknown"};
    let html = "";

    /* ======================================================
       HEADER
       ====================================================== */

    html += `
        <div class="card">

            <h1>${esc(item.name || "Unknown Item")}</h1>

            ${row("Item ID",item.id)}
            ${row("Members",yesNo(item.members))}
            ${row("Tradeable",yesNo(item.tradeable))}
            ${row("Weight",item.weight)}

        </div>
    `;

    /* ======================================================
       WHERE TO GET IT
       ====================================================== */

    html += `
        <div class="card">

            <h2>📍 Where to Get It</h2>

            <div class="subtitle">
                Known acquisition sources from the 2009Scape game data.
            </div>
    `;

    /* ------------------------------------------------------
       MONSTER DROPS
       ------------------------------------------------------ */

    html += `
        <details>

            <summary>
                ⚔️ Monster Drops
                <span class="count">(${drops.length})</span>
            </summary>

            <div class="source-body">
    `;

    if(!drops.length){

        html += `
            <div class="empty">
                No known monster drops.
            </div>
        `;

    }else{

        /*
         * Group entries by monster.
         */

        const grouped = {};

        drops.forEach(drop=>{

            const key = String(drop.monsterId ?? drop.id);

            if(!grouped[key])
                grouped[key] = [];

            grouped[key].push(drop);

        });

        const groups = Object.keys(grouped);

        groups.sort((a,b)=>{

            const aa = grouped[a][0].name || "";
            const bb = grouped[b][0].name || "";

            return aa.localeCompare(bb);

        });

        groups.forEach(npcId=>{

            const entries = grouped[npcId];

            const monster =
                entries[0].name || ("Monster " + npcId);

            html += `
                <details>

                    <summary>
              ⚔️ <a href="monster.html?id=${encodeURIComponent(npcId)}">${esc(monster)}</a>
            </summary>

                    <div class="source-body">

                        ${row("NPC ID",npcId)}
                        <div class="muted">${entries[0].source === "OSRS Wiki" ? "* Secondary source: OSRS Wiki. Identity was resolved by the trusted Wiki reconciliation layer." : "Primary source: 2009Scape."}</div>
            `;

            html += `
                    </div>
                </details>
            `;

        });

    }

    html += `
            </div>
        </details>
    `;

    /* ------------------------------------------------------
       SHOPS
       ------------------------------------------------------ */
    html += `
        <details>
            <summary>🏪 Shops <span class="count">(${shops.length})</span></summary>
            <div class="source-body">
    `;
    if(!shops.length){
        html += `<div class="empty">No trusted 2009Scape shop relationships.</div>`;
    }else{
        shops.forEach(shop=>{
            html += `
                <div class="source-entry">
                    <strong>${esc(shop.shopName || "Unknown Shop")}</strong>
                    ${row("Shop ID",shop.shopId)}
                    ${row("Location",shop.location)}
                    ${row("Owner",shop.owner)}
                    ${row("Shop Type",shop.shopType)}
                    ${row("Stock",shop.stock)}
                    ${row("Restock",shop.restock)}
                    <div class="muted">Primary source: 2009Scape.</div>
                </div>
            `;
        });
    }
    html += `
            </div>
        </details>
    `;

    /* ------------------------------------------------------
       GROUND SPAWNS
       ------------------------------------------------------ */
    if(ground && ground.status === "unknown"){
        html += `
            <div class="source-entry">
                <strong>🪨 Ground Spawns</strong>
                <div class="muted">Trusted ground-spawn data is currently unavailable. This is intentionally shown as unknown rather than guessed.</div>
            </div>
        `;
    }

    /* ------------------------------------------------------
       NO SOURCES
       ------------------------------------------------------ */

    if(!shops.length && !drops.length && ground && ground.status === "unknown"){

        html += `
            <div class="source-entry">

                <strong>No known acquisition sources.</strong>

                <div class="muted result-note">
                    No trusted acquisition relationship is currently available for this item. Missing information is not treated as proof that the item has no source.
                </div>

            </div>
        `;

    }

    html += `
        </div>
    `;

    /* ======================================================
       BASIC INFORMATION
       ====================================================== */

    html += `
        <div class="card">

            <h2>📖 Basic Information</h2>

            ${row("Examine",item.examine)}
            ${row("Shop Price",item.shop_price)}
            ${row("Grand Exchange Price",item.grand_exchange_price)}
            ${row("GE Buy Limit",item.ge_buy_limit)}

        </div>
    `;

    /* ======================================================
       COMBAT / EQUIPMENT
       ====================================================== */

    if(
        item.equipment_slot !== undefined ||
        item.attack_speed !== undefined ||
        item.two_handed !== undefined ||
        item.bonuses
    ){

        html += `
            <div class="card">

                <h2>⚔️ Combat & Equipment</h2>
        `;

        html += row(
            "Equipment Slot",
            item.equipment_slot
        );

        html += row(
            "Attack Speed",
            item.attack_speed
        );

        html += row(
            "Two-Handed",
            item.two_handed !== undefined
                ? yesNo(item.two_handed)
                : undefined
        );

        if(item.bonuses){

            html += row(
                "Bonuses",
                JSON.stringify(item.bonuses)
            );

        }

        html += `
            </div>
        `;

    }

    /* ======================================================
       BEHAVIOR
       ====================================================== */

    html += `
        <div class="card">

            <h2>⚙️ Properties</h2>
    `;

    html += row("Bankable",
        item.bankable !== undefined
            ? yesNo(item.bankable)
            : undefined
    );

    html += row("Lendable",
        item.lendable !== undefined
            ? yesNo(item.lendable)
            : undefined
    );

    html += row("Alchemizable",
        item.alchemizable !== undefined
            ? yesNo(item.alchemizable)
            : undefined
    );

    html += row("Rare Item",
        item.rare_item !== undefined
            ? yesNo(item.rare_item)
            : undefined
    );

    html += row("Has Special",
        item.has_special !== undefined
            ? yesNo(item.has_special)
            : undefined
    );

    html += `
        </div>
    `;

    /* ======================================================
       RAW DATA
       ====================================================== */

    html += `
        <div class="card">

            <details>

                <summary>
                    🔧 Additional Item Data
                </summary>

                <div class="source-body">

                    <pre>${esc(
                        JSON.stringify(item,null,2)
                    )}</pre>

                </div>

            </details>

        </div>
    `;

    setHTML(document.getElementById("content"), html);

}


loadItem();
