#!/usr/bin/env python3
"""Generate authoritative 2009Scape recipes for Herblore, Crafting, Cooking and Runecrafting.

  generate_skill_recipes.py --source-root <2009scape>/Server --recipes site/data/recipes.json \
      --output site/data/recipes.json --source-commit <sha> [--skills herblore,crafting,cooking,runecrafting]

Every row is parsed from the server source (no wiki values). Item ids come from `Items.NAME_<id>` constants or
numeric literals. Rows whose (skill, output, inputs) key matches an existing row replace it; everything else is added.
Smithing (PASS31.33) and Fletching/staffs (PASS31.37) are produced by their own generators and are left untouched.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

BASE = "Server/src/main/content/global/skill/"
SKILL_DIR = BASE
ITEM = r"Items\.[A-Z0-9_]+?_(\d+)"


class GeneratorError(RuntimeError):
    pass


def read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def recipe(rid, out, qty, inputs, skill, level, xp, tools, facilities, method, rel, enum, commit, extra=None):
    v = {"id": rid, "output": {"itemId": int(out), "quantity": qty},
         "inputs": [{"itemId": int(i), "quantity": q} for i, q in inputs],
         "skill": skill, "skills": [skill], "level": level, "xp": xp, "tools": tools, "facilities": facilities,
         "requirements": [], "method": method,
         "provenance": [{"source": "2009Scape", "file": rel, "commit": commit, "enum": enum}]}
    if extra:
        v.update(extra)
    return v


# ------------------------------------------------------------------ herblore
HERBLORE = BASE + "herblore/"
VIAL_OF_WATER, PESTLE, SWAMP_TAR, ROE, CAVIAR = 227, 233, 1939, 11324, 11326
QUEST = {"ZOGRE_FLESH_EATERS": "Zogre Flesh Eaters", "SHADES_OF_MORTTON": "Shades of Mort'ton", "HEROES_QUEST": "Heroes' Quest",
         "KENNITHS_CONCERNS": "Kenneth's Concerns", "GRIM_TALES": "Grim Tales", "FAIRYTALE_II_CURE_A_QUEEN": "Fairytale II - Cure a Queen",
         "IN_AID_OF_THE_MYREQUE": "In Aid of the Myreque"}


def parse_herbs(root):
    text = read(root, HERBLORE + "Herbs.java")
    pat = r"([A-Z_]+)\(new Item\((\d+)\),\s*([0-9.]+),\s*(\d+),\s*new Item\((\d+)\)\)"
    return {m[0]: dict(herb=int(m[1]), xp=float(m[2]), level=int(m[3]), product=int(m[4])) for m in re.findall(pat, text)}


def parse_grinding(root):
    text = read(root, HERBLORE + "GrindingItem.java")
    pat = r"^\s*([A-Z_]+)\(new Item\[\]\s*\{\s*new Item\(" + ITEM + r"\)\s*\},\s*new Item\(" + ITEM + r"\)\)"
    return {m[0]: (int(m[1]), int(m[2])) for m in re.findall(pat, text, re.M)}


def parse_unfinished(root, herbs):
    rel = HERBLORE + "UnfinishedPotion.kt"
    text = read(root, rel)
    pat = r"^\s*([A-Z_]+)\(Item\(" + ITEM + r"\),\s*(Herbs\.([A-Z_]+)\.product|Item\(" + ITEM + r"\)),\s*(\d+),\s*Item\(" + ITEM + r"\)\)"
    out = {}
    for enum, base, _, herb, ing, level, potion in re.findall(pat, text, re.M):
        ingredient = herbs[herb]["product"] if herb else int(ing)
        out[enum] = dict(base=int(base), ingredient=ingredient, level=int(level), potion=int(potion))
    if len(out) != 21:
        raise GeneratorError(f"expected 21 unfinished potions, parsed {len(out)}")
    return rel, out


def parse_finished(root, herbs, grind, unf):
    rel = HERBLORE + "FinishedPotion.kt"
    text = read(root, rel).split("enum class FinishedPotion(")[1].split("fun canMake")[0]
    starts = [m for m in re.finditer(r"^    ([A-Z][A-Z0-9_]+)\(", text, re.M)]
    produced: dict[str, int] = {}
    rows = []
    for i, m in enumerate(starts):
        block = text[m.start(): starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        enum = m.group(1)
        head = re.match(r"\s*[A-Z0-9_]+\(\s*(.+?),\s*(Item\(Items\.[A-Z0-9_]+?_\d+\)|GrindingItem\.[A-Z_]+\.product|Herbs\.[A-Z_]+\.product),\s*(\d+),\s*([0-9.]+),\s*Item\(" + ITEM + r"\)", block, re.S)
        if not head:
            raise GeneratorError(f"cannot parse FinishedPotion {enum}")
        first, second, level, xp, product = head.groups()
        def resolve(tok):
            if (mm := re.fullmatch(r"UnfinishedPotion\.([A-Z_]+)\.potion", tok)): return unf[mm.group(1)]["potion"]
            if (mm := re.fullmatch(r"Item\(" + ITEM + r"\)", tok)): return int(mm.group(1))
            if (mm := re.fullmatch(r"Herbs\.([A-Z_]+)\.product", tok)): return herbs[mm.group(1)]["product"]
            if (mm := re.fullmatch(r"GrindingItem\.([A-Z_]+)\.product", tok)): return grind[mm.group(1)][1]
            if tok in produced: return produced[tok]
            if (mm := re.fullmatch(r"([A-Z0-9_]+)\.potion", tok)) and mm.group(1) in produced: return produced[mm.group(1)]
            raise GeneratorError(f"unresolved token {tok!r} in {enum}")
        a, b = resolve(first.strip()), resolve(second.strip())
        produced[enum] = int(product)
        quests = [QUEST.get(q, q) for q in re.findall(r"Quests\.([A-Z_]+)", block.split(")", 1)[1] if False else block[head.end():])]
        rows.append((enum, a, b, int(level), float(xp), int(product), quests))
    return rel, rows


def parse_tars(root, herbs):
    rel = HERBLORE + "Tars.java"
    text = read(root, rel)
    pat = r"^\s*([A-Z_]+)\((Herbs\.([A-Z_]+)\.getProduct\(\)|new Item\(Items\.[A-Z0-9_]+?_(\d+)\)),\s*(\d+),\s*([0-9.]+),\s*new Item\((\d+)\)\)"
    out = []
    for enum, _, herb, lit, level, xp, tar in re.findall(pat, text, re.M):
        out.append((enum, herbs[herb]["product"] if herb else int(lit), int(level), float(xp), int(tar)))
    return rel, out


def parse_barbarian(root):
    rel = HERBLORE + "BarbarianPotion.kt"
    text = read(root, rel)
    pat = r"([A-Z_]+)\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+),\s*(true|false)\)"
    return rel, re.findall(pat, text)


def herblore(root, commit):
    herbs = parse_herbs(root)
    grind = parse_grinding(root)
    rows = []
    hrel = HERBLORE + "Herbs.java"
    for enum, h in herbs.items():
        rows.append(recipe(f"2009scape-herblore-clean-{enum.lower()}", h["product"], 1, [(h["herb"], 1)], "Herblore", h["level"], h["xp"], [], [], ["Clean a grimy herb"], hrel, enum, commit))
    urel, unf = parse_unfinished(root, herbs)
    for enum, u in unf.items():
        rows.append(recipe(f"2009scape-herblore-unfinished-{enum.lower()}", u["potion"], 1, [(u["base"], 1), (u["ingredient"], 1)], "Herblore", u["level"], 0.0, [], [], ["Add the herb to a vial of water (or coconut milk) to make an unfinished potion"], urel, enum, commit))
    frel, fin = parse_finished(root, herbs, grind, unf)
    for enum, a, b, level, xp, product, quests in fin:
        extra = {"requirements": [{"type": "quest", "name": q} for q in quests]} if quests else None
        rows.append(recipe(f"2009scape-herblore-potion-{enum.lower()}", product, 1, [(a, 1), (b, 1)], "Herblore", level, xp, [], [], ["Add the secondary ingredient to the unfinished potion"], frel, enum, commit, extra))
    trel, tars = parse_tars(root, herbs)
    for enum, ing, level, xp, tar in tars:
        rows.append(recipe(f"2009scape-herblore-tar-{enum.lower()}", tar, 15, [(SWAMP_TAR, 15), (ing, 1)], "Herblore", level, xp, [], [], ["Combine swamp tar with a herb"], trel, enum, commit))
    brel, bar = parse_barbarian(root)
    for enum, potion, level, product, xp, both in bar:
        for egg, label in ((ROE, "roe"), (CAVIAR, "caviar")):
            if egg == ROE and both != "true":
                continue
            rows.append(recipe(f"2009scape-herblore-barbarian-{label}-{enum.lower()}", int(product), 1, [(int(potion), 1), (egg, 1)], "Herblore", int(level), float(xp), [], [], [f"Barbarian mix: add {label} to the potion"], brel, enum, commit,
                               {"requirements": [{"type": "other", "name": "Barbarian Herblore training (Otto Godblessed)"}]}))
    grel = HERBLORE + "GrindingItem.java"
    for enum, (src, prod) in grind.items():
        rows.append(recipe(f"2009scape-herblore-grind-{enum.lower()}", prod, 1, [(src, 1)], "Herblore", 1, 0.0, ["Pestle and mortar"], [], ["Grind with a pestle and mortar (no experience)"], grel, enum, commit))
    return rows


# ------------------------------------------------------------------ crafting
CRAFT = BASE + "crafting/"
CHISEL, NEEDLE, THREAD, SOFT_CLAY, GLASS_PIPE = 1755, 1733, 1734, 1761, 1785
SODA_ASH, SAND, BUCKET, MOLTEN, SILVER_BAR, GOLD_BAR, LEATHER, HARD_LEATHER, SNAKE = 1781, 1783, 1925, 1775, 2355, 2357, 1741, 1743, 6289
MOULD = {"ring": 1592, "necklace": 1597, "amulet": 1595, "bracelet": 11065}


def crafting(root, commit):
    rows = []
    # gems
    rel = CRAFT + "gem/Gems.java"
    pat = r"^\s*([A-Z_]+)\(new Item\((\d+)\), new Item\((\d+)\), (\d+), new Animation\(\d+\), ([0-9.]+)\)"
    gems = re.findall(pat, read(root, rel), re.M)
    if len(gems) != 9:
        raise GeneratorError(f"gems: expected 9, parsed {len(gems)}")
    for e, unc, cut, lv, xp in gems:
        rows.append(recipe(f"2009scape-crafting-gem-{e.lower()}", cut, 1, [(unc, 1)], "Crafting", int(lv), float(xp), ["Chisel"], [], ["Cut the uncut gem with a chisel"], rel, e, commit))
    # pottery (shape soft clay, then fire)
    rel = CRAFT + "pottery/PotteryItem.java"
    pat = r"([A-Z]+)\(new Item\((\d+)\), new Item\((\d+)\), (\d+), ([0-9.]+), ([0-9.]+)\)"
    pots = re.findall(pat, read(root, rel))
    if len(pots) != 5:
        raise GeneratorError(f"pottery: expected 5, parsed {len(pots)}")
    for e, unf, prod, lv, xp, fxp in pots:
        rows.append(recipe(f"2009scape-crafting-pottery-shape-{e.lower()}", unf, 1, [(SOFT_CLAY, 1)], "Crafting", int(lv), float(xp), [], ["Pottery wheel"], ["Mould soft clay on a pottery wheel"], rel, e, commit))
        rows.append(recipe(f"2009scape-crafting-pottery-fire-{e.lower()}", prod, 1, [(unf, 1)], "Crafting", int(lv), float(fxp), [], ["Pottery oven"], ["Fire the unfired item in a pottery oven"], rel, e, commit))
    # spinning
    rel = CRAFT + "spinning/SpinningItem.java"
    pat = r"([A-Z_0-9]+)\((\d+), (\d+), (\d+), (\d+), ([0-9.]+)\)"
    spin = re.findall(pat, read(root, rel))
    if len(spin) != 11:
        raise GeneratorError(f"spinning: expected 11, parsed {len(spin)}")
    for e, _b, need, prod, lv, xp in spin:
        rows.append(recipe(f"2009scape-crafting-spinning-{e.lower()}", prod, 1, [(need, 1)], "Crafting", int(lv), float(xp), [], ["Spinning wheel"], ["Spin on a spinning wheel"], rel, e, commit))
    # glass
    rel = CRAFT + "glass/GlassProduct.kt"
    pat = r"^\s*([A-Z_]+)\((\d+), (\d+), (\d+), (\d+), ([0-9.]+)\)"
    glass = re.findall(pat, read(root, rel), re.M)
    if len(glass) != 8:
        raise GeneratorError(f"glass: expected 8, parsed {len(glass)}")
    for e, _b, prod, qty, lv, xp in glass:
        rows.append(recipe(f"2009scape-crafting-glass-{e.lower()}", prod, int(qty), [(MOLTEN, 1)], "Crafting", int(lv), float(xp), ["Glassblowing pipe"], [], ["Blow molten glass with a glassblowing pipe"], rel, e, commit))
    rows.append(recipe("2009scape-crafting-glass-molten-glass", MOLTEN, 1, [(SODA_ASH, 1), (SAND, 1)], "Crafting", 1, 20.0, [], ["Furnace"], ["Smelt soda ash and a bucket of sand in a furnace (returns the bucket)"], CRAFT + "glass/GlassMakePulse.kt", "MOLTEN_GLASS", commit, {"byproducts": [{"itemId": BUCKET, "quantity": 1}]}))
    # silver
    rel = CRAFT + "silver/SilverProduct.kt"
    pat = r"^\s*([A-Z_]+)\(BUTTON_[A-Z_]+, " + ITEM + r", " + ITEM + r", (\d+), (\d+), ([0-9.]+), (?:" + ITEM + r"|-1)\)"
    silver = re.findall(pat, read(root, rel), re.M)
    if len(silver) != 8:
        raise GeneratorError(f"silver: expected 8, parsed {len(silver)}")
    for e, mould, prod, qty, lv, xp, strung in silver:
        rows.append(recipe(f"2009scape-crafting-silver-{e.lower()}", prod, int(qty), [(SILVER_BAR, 1)], "Crafting", int(lv), float(xp), [f"Mould {mould}"], ["Furnace"], ["Pour a silver bar into the matching mould at a furnace"], rel, e, commit, {"toolItemIds": [int(mould)]}))
        if strung:
            rows.append(recipe(f"2009scape-crafting-silver-string-{e.lower()}", strung, 1, [(prod, 1), (1759, 1)], "Crafting", 1, 4.0, [], [], ["String with a ball of wool"], CRAFT + "silver/SilverStringingListener.kt", e, commit))
    # jewellery
    rel = CRAFT + "jewellery/JewelleryCrafting.java"
    pat = r"^\s*([A-Z_]+)\((\d+), (\d+), (\d+), (\d+), ([A-Z0-9_, ]+)\),?;?\s*$"
    jew = re.findall(pat, read(root, rel), re.M)
    if len(jew) != 29:
        raise GeneratorError(f"jewellery: expected 29, parsed {len(jew)}")
    names = {"GOLD_BAR": GOLD_BAR, "SAPPHIRE": 1607, "EMERALD": 1605, "RUBY": 1603, "DIAMOND": 1601, "DRAGONSTONE": 1615, "ONYX": 6573}
    for e, lv, xp, comp, prod, items in jew:
        ids = [names[x.strip()] if not x.strip().isdigit() else int(x) for x in items.split(",")]
        comp = int(comp)
        kind = "ring" if comp < 41 else "necklace" if comp < 60 else "amulet" if comp < 79 else "bracelet"
        rows.append(recipe(f"2009scape-crafting-jewellery-{e.lower()}", prod, 1, [(i, 1) for i in ids], "Crafting", int(lv), float(xp), [f"{kind.title()} mould"], ["Furnace"], [f"Make at a furnace with a {kind} mould"], rel, e, commit, {"toolItemIds": [MOULD[kind]]}))
    # leather
    lrel = CRAFT + "armour/LeatherCrafting.java"
    ltext = read(root, lrel)
    dh = re.findall(r"^\s*([A-Z_]+D_HIDE_[A-Z]+)\((\d+), (\d+), (\d+), (\d+), (\d+)\)", ltext, re.M)
    if len(dh) != 12:
        raise GeneratorError(f"dragonhide: expected 12, parsed {len(dh)}")
    for e, leather, amt, prod, lv, xp in dh:
        rows.append(recipe(f"2009scape-crafting-dragonhide-{e.lower()}", prod, 1, [(leather, int(amt)), (THREAD, 1)], "Crafting", int(lv), float(xp), ["Needle"], [], ["Sew dragonhide with a needle and thread"], lrel, e, commit, {"toolItemIds": [NEEDLE]}))
    sl = re.findall(r"^\s*([A-Z]+)\((\d+), (\d+), ([0-9.]+), new Item\((\d+)\)\)", ltext, re.M)
    if len(sl) != 7:
        raise GeneratorError(f"soft leather: expected 7, parsed {len(sl)}")
    for e, _b, lv, xp, prod in sl:
        rows.append(recipe(f"2009scape-crafting-leather-{e.lower()}", prod, 1, [(LEATHER, 1), (THREAD, 1)], "Crafting", int(lv), float(xp), ["Needle"], [], ["Sew leather with a needle and thread"], lrel, e, commit, {"toolItemIds": [NEEDLE]}))
    hrel = CRAFT + "armour/HardCraftPulse.java"
    hb = re.search(r"HARD_LEATHER, 1\)", read(root, hrel))
    if not hb:
        raise GeneratorError("hard leather body: pattern not found")
    rows.append(recipe("2009scape-crafting-leather-hard-body", 1131, 1, [(HARD_LEATHER, 1), (THREAD, 1)], "Crafting", 28, 35.0, ["Needle"], [], ["Sew hard leather with a needle and thread"], hrel, "HARD_LEATHER_BODY", commit, {"toolItemIds": [NEEDLE]}))
    srel = CRAFT + "armour/SnakeSkin.java"
    sn = re.findall(r"([A-Z_]+)\(new Item\((\d+)\), (\d+), (\d+), (\d+)\)", read(root, srel))
    if len(sn) != 5:
        raise GeneratorError(f"snakeskin: expected 5, parsed {len(sn)}")
    for e, prod, lv, xp, amt in sn:
        rows.append(recipe(f"2009scape-crafting-snakeskin-{e.lower()}", prod, 1, [(SNAKE, int(amt)), (THREAD, 1)], "Crafting", int(lv), float(xp), ["Needle"], [], ["Sew snakeskin with a needle and thread"], srel, e, commit, {"toolItemIds": [NEEDLE]}))
    return rows


# ------------------------------------------------------------------ cooking
COOK = BASE + "cooking/"
NUM = r"(?:(\d+)|Items\.[A-Z0-9_]+?_(\d+))"


def cooking(root, commit):
    rel = COOK + "CookableItems.java"
    text = read(root, rel).split("public enum CookableItems")[1].split("public final static")[0]
    pat = r"^\s*([A-Z_]+)\(" + (NUM + r",\s*") * 3 + r"(\d+),\s*([0-9.]+),"
    rows = []
    for m in re.finditer(pat, text, re.M):
        e = m.group(1)
        cooked, raw, burnt = (int(m.group(2 + 2 * i) or m.group(3 + 2 * i)) for i in range(3))
        level, xp = int(m.group(8)), float(m.group(9))
        if raw == 0 or e in {"SINEW", "BOWL_NETTLE"}:
            continue  # seaweed/barley/oomlie processing, sinew drying and nettle tea are not cooking recipes
        facility = ["Fire or range"]
        rows.append(recipe(f"2009scape-cooking-{e.lower()}", cooked, 1, [(raw, 1)], "Cooking", level, xp, [], facility, ["Cook on a fire or range (may burn)"], rel, e, commit))
    if len(rows) < 60:
        raise GeneratorError(f"cooking: parsed only {len(rows)} rows")
    return rows


# ------------------------------------------------------------------ runecrafting
RC = BASE + "runecrafting/"
RUNE_ESSENCE, PURE_ESSENCE = 1436, 7936


def runecrafting(root, commit):
    ids = dict(re.findall(r"([A-Z]+)_RUNE\((\d+)\)", read(root, "Server/src/main/core/game/node/entity/combat/spell/Runes.java")))
    rel = RC + "Rune.java"
    pat = r"^\s*([A-Z]+)\(Runes\.[A-Z]+_RUNE\.transform\(\), (\d+), ([0-9.]+)(?:, new int\[\] \{([^}]*)\})?\)"
    rows = []
    normal = {"AIR", "MIND", "WATER", "EARTH", "FIRE", "BODY"}
    for e, lv, xp, mult in re.findall(pat, read(root, rel), re.M):
        ess = [(RUNE_ESSENCE if e in normal else PURE_ESSENCE, 1)]
        steps = [int(x) for x in mult.replace(" ", "").split(",") if x] or []
        note = "Bind essence at the altar" + (f"; extra runes per essence at levels {', '.join(map(str, steps[1:]))}" if len(steps) > 1 else "")
        rows.append(recipe(f"2009scape-runecrafting-{e.lower()}", ids[e], 1, ess, "Runecrafting", int(lv), float(xp), [], [f"{e.title()} altar"], [note + " (per essence)"], rel, e, commit))
    if len(rows) != 14:
        raise GeneratorError(f"runecrafting: expected 14 runes, parsed {len(rows)}")
    crel = RC + "CombinationRune.java"
    pat = r"^\s*([A-Z]+)\(new Item\((\d+)\), (\d+), ([0-9.]+), new Altar\[\] \{ Altar\.([A-Z]+), Altar\.([A-Z]+) \}, Rune\.([A-Z]+), Rune\.([A-Z]+)\)"
    combos = re.findall(pat, read(root, crel), re.M)
    if len(combos) != 6:
        raise GeneratorError(f"combination runes: expected 6, parsed {len(combos)}")
    for e, rid, lv, xp, a1, a2, r1, r2 in combos:
        rows.append(recipe(f"2009scape-runecrafting-combination-{e.lower()}", rid, 1, [(PURE_ESSENCE, 1), (ids[r1] if a1 == r2 else ids[r2], 1)], "Runecrafting", int(lv), float(xp), [], [f"{a1.title()} altar", f"{a2.title()} altar"],
                           [f"Use the matching talisman (or imbue) on the altar; each essence has a 1 in 3 chance to become a {e.lower()} rune unless a binding necklace is worn"], crel, e, commit))
    return rows


# ------------------------------------------------------------------ registry
PARSERS = {"herblore": herblore, "crafting": crafting, "cooking": cooking, "runecrafting": runecrafting}
SOURCE_FILES = {"cooking": [COOK + "CookableItems.java"], "runecrafting": [RC + "Rune.java", RC + "CombinationRune.java"], "crafting": [CRAFT + f for f in ("gem/Gems.java", "pottery/PotteryItem.java", "spinning/SpinningItem.java", "glass/GlassProduct.kt", "glass/GlassMakePulse.kt", "silver/SilverProduct.kt", "jewellery/JewelleryCrafting.java", "armour/LeatherCrafting.java", "armour/HardCraftPulse.java", "armour/SnakeSkin.java")], "herblore": [HERBLORE + f for f in ("Herbs.java", "UnfinishedPotion.kt", "FinishedPotion.kt", "Tars.java", "BarbarianPotion.kt", "GrindingItem.java")]}
SKILL_NAME = {"herblore": "Herblore", "crafting": "Crafting", "cooking": "Cooking", "runecrafting": "Runecrafting"}


PRESERVE = ("2009scape-crafting-battlestaff-",)  # produced by the Fletching/staff generator (PASS31.37)
# Source rows whose item id has no catalog entry (the server defines the enum, the cache has no such item).
SKIP_ENUMS = {"UGTHANKI": "same raw/cooked ids as CHICKEN; cookingMap.putIfAbsent keeps CHICKEN, so it is never used",
             "ROOT5": "spinning input 6053 is not an item in the catalog"}


def key(r):
    return (r.get("skill"), (r.get("output") or {}).get("itemId"), tuple(sorted((x.get("itemId"), x.get("quantity")) for x in r.get("inputs", []))))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source-root", type=Path, required=True)
    p.add_argument("--recipes", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--source-commit", default="unknown")
    p.add_argument("--skills", default=",".join(PARSERS))
    p.add_argument("--snapshot", default=None)
    a = p.parse_args()
    root = a.source_root.resolve()
    skills = [s for s in a.skills.split(",") if s]
    payload = json.loads(a.recipes.read_text(encoding="utf-8"))
    existing = payload["recipes"]
    summary = {}
    for s in skills:
        generated = [r for r in PARSERS[s](root, a.source_commit) if r["provenance"][0]["enum"] not in SKIP_ENUMS]
        if not generated:
            raise GeneratorError(f"{s}: nothing parsed")
        ids = [r["id"] for r in generated]
        if len(ids) != len(set(ids)):
            raise GeneratorError(f"{s}: duplicate recipe ids")
        gkeys = {key(r): r for r in generated}
        dropped = {r["id"] for r in existing if r["id"].startswith(f"2009scape-{s}-") and not r["id"].startswith(PRESERVE)}
        replaced = sum(1 for r in existing if key(r) in gkeys and r["id"] not in dropped)
        existing = [r for r in existing if r["id"] not in dropped]
        merged = [gkeys.pop(key(r), r) for r in existing]
        added = list(gkeys.values())
        existing = merged + added
        payload.setdefault("generation", {})[s] = {"provider": "2009Scape", "sourceFiles": SOURCE_FILES[s], "commit": a.source_commit,
                                                    "generated": len(generated), "added": len(added), "replacedWikiRows": replaced}
        payload.setdefault("counts", {})[f"from2009Scape{SKILL_NAME[s]}"] = sum(1 for r in existing if r["id"].startswith(f"2009scape-{s}-") and not r["id"].startswith(PRESERVE))
        summary[s] = {"generated": len(generated), "added": len(added), "replacedWikiRows": replaced}
    payload["recipes"] = sorted(existing, key=lambda r: (str(r.get("skill", "")), int(r.get("level") or 0), str(r.get("id", ""))))
    payload["counts"]["total"] = len(payload["recipes"])
    if a.snapshot:
        payload["snapshot"] = a.snapshot
    a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "total": len(payload["recipes"])}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        raise SystemExit(f"error: {e}")
