import { OSRSSync } from "../services/player-sync.js";
import { OSRS } from "../core/osrs.js";

const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
}[char]));

let data = [];
let names = new Map();
let bank = new Map();
let levels = new Map();
let catalogSize = 0;
let unresolvedItemIds = new Set();

function numberOrNull(value) {
    if (value === null || value === undefined || value === "") return null;
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
}

function itemReference(value, context) {
    const itemId = numberOrNull(value?.itemId ?? value?.id ?? value);
    if (itemId === null || !Number.isInteger(itemId) || itemId < 0) {
        throw new Error(`Invalid item reference in ${context}`);
    }
    const quantity = numberOrNull(value?.quantity ?? value?.qty ?? 1);
    if (quantity === null || quantity <= 0) {
        throw new Error(`Invalid item quantity for ${itemId} in ${context}`);
    }
    return {
        itemId,
        quantity,
        name: value?.name
    };
}

function recipeOutputs(recipe, index) {
    const values = Array.isArray(recipe.outputs)
        ? recipe.outputs
        : recipe.output == null ? [] : [recipe.output];
    if (!values.length) {
        throw new Error(`Recipe ${recipe.id || index} has no output`);
    }
    return values.map((value) => itemReference(value, `recipe ${recipe.id || index} output`));
}

function normalizeRecipe(recipe, index) {
    if (!recipe || typeof recipe !== "object") {
        throw new Error(`Recipe ${index} is not an object`);
    }
    const inputs = Array.isArray(recipe.inputs)
        ? recipe.inputs.map((value) => itemReference(value, `recipe ${recipe.id || index} input`))
        : [];
    const outputs = recipeOutputs(recipe, index);
    const skills = Array.isArray(recipe.skills)
        ? recipe.skills.filter(Boolean).map(String)
        : recipe.skill ? [String(recipe.skill)] : [];
    const skill = String(recipe.skill || skills[0] || "Unknown");
    const level = numberOrNull(recipe.level);
    const xp = numberOrNull(recipe.xp);
    return {
        ...recipe,
        id: String(recipe.id || `${skill.toLowerCase()}:${outputs[0].itemId}:${index}`),
        skill,
        skills: skills.length ? skills : [skill],
        level,
        xp,
        inputs,
        outputs,
        output: outputs[0]
    };
}

function quantity(map, id) {
    return Number(map.get(Number(id)) || 0);
}

function canMake(recipe) {
    const level = Number(levels.get(recipe.skill.toLowerCase()) || 1);
    return level >= Number(recipe.level || 0) && recipe.inputs.every(
        (item) => quantity(bank, item.itemId) >= Number(item.quantity || 1)
    );
}

function sourceLabel(recipe) {
    const provenance = Array.isArray(recipe.provenance) ? recipe.provenance[0] : null;
    return provenance?.source || recipe.source?.provider || recipe.source || "Unknown source";
}

function itemLabel(id, fallback) {
    return names.get(Number(id)) || fallback || `Item ${id}`;
}

function recipeMatches(recipe, query) {
    if (!query) return true;
    const outputText = recipe.outputs
        .map((item) => itemLabel(item.itemId, item.name).toLowerCase())
        .join(" ");
    const inputText = recipe.inputs
        .map((item) => itemLabel(item.itemId, item.name).toLowerCase())
        .join(" ");
    return outputText.includes(query) || inputText.includes(query) ||
        recipe.skill.toLowerCase().includes(query);
}

function renderItemLinks(items) {
    return items.map((item) => {
        const label = itemLabel(item.itemId, item.name);
        return `<a href="item.html?id=${encodeURIComponent(item.itemId)}">${esc(label)} × ${esc(item.quantity)}</a>`;
    }).join("");
}

function render() {
    const query = String($("search").value || "").toLowerCase().trim();
    const skill = $("skill").value;
    const ready = $("ready").checked;
    const rows = data.filter((recipe) =>
        (!skill || recipe.skills.includes(skill) || recipe.skill === skill) &&
        recipeMatches(recipe, query) &&
        (!ready || canMake(recipe))
    );

    const unresolved = unresolvedItemIds.size
        ? ` · ${unresolvedItemIds.size.toLocaleString()} catalog references unresolved`
        : "";
    $("summary").textContent = `${rows.length.toLocaleString()} recipes shown · ${data.length.toLocaleString()} indexed · ${catalogSize.toLocaleString()} items available${unresolved}`;

    const container = $("recipes");
    container.replaceChildren();
    for (const recipe of rows) {
        const readyToMake = canMake(recipe);
        const card = document.createElement("article");
        card.className = "recipe";
        card.innerHTML = `
            <h3>${recipe.outputs.map((item) =>
                `<a href="item.html?id=${encodeURIComponent(item.itemId)}">${esc(itemLabel(item.itemId, item.name))}</a>`
            ).join(" · ")}</h3>
            <div class="recipe-meta">
                <span>${esc(recipe.skill)}</span>
                <span>Level ${recipe.level ?? "unknown"}</span>
                <span>XP ${recipe.xp ?? "unknown"}</span>
                <span>${esc(sourceLabel(recipe))}</span>
                <span class="${readyToMake ? "ready" : "missing"}">${readyToMake ? "✓ Available" : "Missing level/materials"}</span>
            </div>
            <div class="materials">${recipe.inputs.length
                ? renderItemLinks(recipe.inputs)
                : "<span class=\"muted\">No resolved materials</span>"}</div>`;
        container.append(card);
    }
}

async function loadItemNames(itemIds) {
    const catalog = await OSRS.Catalog.list("items");
    if (!Array.isArray(catalog)) {
        throw new Error("Item catalog index is not an array");
    }
    catalogSize = catalog.length;
    for (const item of catalog) {
        const id = numberOrNull(item?.id);
        if (id !== null && item?.name) names.set(id, String(item.name));
    }

    const missingFromIndex = [...itemIds].filter((id) => !names.has(id));
    await Promise.all(missingFromIndex.map(async (id) => {
        try {
            const item = await OSRS.Catalog.get("items", id);
            if (item?.name) names.set(id, String(item.name));
        } catch (error) {
            unresolvedItemIds.add(id);
        }
    }));

    for (const id of itemIds) {
        if (!names.has(id)) unresolvedItemIds.add(id);
    }
}

async function loadRecipes() {
    const payload = await OSRS.Data.get("recipes.json");
    const rawRecipes = Array.isArray(payload) ? payload : payload?.recipes;
    if (!Array.isArray(rawRecipes)) {
        throw new Error("Recipe catalog does not contain a recipes array");
    }
    data = rawRecipes.map(normalizeRecipe);

    const itemIds = new Set();
    for (const recipe of data) {
        for (const item of [...recipe.inputs, ...recipe.outputs]) itemIds.add(item.itemId);
    }
    await loadItemNames(itemIds);
    return payload;
}

async function init() {
    try {
        await OSRSSync.load({ force: true });
        const player = OSRSSync.getData();
        for (const skill of player.skills || []) {
            levels.set(String(skill.name).toLowerCase(), Number(skill.level) || 1);
        }
        for (const item of player.bank || []) {
            bank.set(Number(item.id), quantity(bank, item.id) + Number(item.amount || 0));
        }

        await loadRecipes();
        const skills = [...new Set(data.flatMap((recipe) => recipe.skills))]
            .filter(Boolean)
            .sort((a, b) => a.localeCompare(b));
        $("skill").innerHTML = `<option value="">All skills</option>${skills
            .map((skill) => `<option value="${esc(skill)}">${esc(skill)}</option>`)
            .join("")}`;
        render();
    } catch (error) {
        console.error("Crafting data load failed", error);
        $("summary").textContent = `🔴 Crafting data error: ${error.message}`;
    }
}

$("search").addEventListener("input", render);
$("skill").addEventListener("input", render);
$("ready").addEventListener("input", render);
$("skill").addEventListener("change", render);
$("ready").addEventListener("change", render);
init();
