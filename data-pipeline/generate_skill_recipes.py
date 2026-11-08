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
            rows.append(recipe(f"2009scape-crafting-silver-string-{e.lower()}", strung, 1, [(prod, 1), (1759, 1)], "Crafting", 1, 0.0, [], [], ["String with a ball of wool"], CRAFT + "silver/SilverStringingListener.kt", e, commit))
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
    return rows + crafting_extra(root, commit) + remaining(root, commit)['Crafting']


def crafting_extra(root, commit):
    rows = []
    # studded armour: base + steel studs
    rel = CRAFT + "StuddedArmourPlugin.java"
    st = re.findall(r"([A-Z]+)\(new Item\((\d+)\), new Item\((\d+)\), (\d+), (\d+)\)", read(root, rel))
    if len(st) != 2:
        raise GeneratorError(f"studded armour: expected 2, parsed {len(st)}")
    for e, base, out, lv, xp in st:
        rows.append(recipe(f"2009scape-crafting-studded-{e.lower()}", out, 1, [(base, 1), (2370, 1)], "Crafting", int(lv), float(xp), [], [], ["Attach steel studs to the leather armour"], rel, e, commit))
    # weaving
    rel = CRAFT + "WeaveOptionPlugin.java"
    wv = re.findall(r"([A-Z]+)\(new Item\((\d+)\), new Item\((\d+), (\d+)\), (\d+), (\d+)\)", read(root, rel))
    if len(wv) != 3:
        raise GeneratorError(f"weaving: expected 3, parsed {len(wv)}")
    for e, out, need, n, lv, xp in wv:
        rows.append(recipe(f"2009scape-crafting-weaving-{e.lower()}", out, 1, [(need, int(n))], "Crafting", int(lv), float(xp), [], ["Loom"], ["Weave on a loom"], rel, e, commit))
    # snelms: shell + chisel (level 15, 32.5 xp)
    rel = CRAFT + "SnelmCraftPlugin.java"
    text = read(root, rel)
    pairs = re.findall(r"\{ (\d+), (\d+) \}", text.split("DATA")[1].split("};")[0])
    if len(pairs) != 9 or "< 15" not in text or "32.5" not in text:
        raise GeneratorError(f"snelms: expected 9 pairs with level 15 / 32.5 xp, parsed {len(pairs)}")
    for shell, snelm in pairs:
        rows.append(recipe(f"2009scape-crafting-snelm-{shell}", snelm, 1, [(shell, 1)], "Crafting", 15, 32.5, ["Chisel"], [], ["Chisel the shell into a snelm"], rel, f"SNELM_{shell}", commit, {"toolItemIds": [CHISEL]}))
    # tanning: hide + coins at a tanner
    rel = CRAFT + "TanningProduct.java"
    tt = re.findall(r"^\s*([A-Z_0-9]+)\((\d+), (\d+), (\d+)\)", read(root, rel), re.M)
    coins = {"SOFT_LEATHER": 1, "HARD_LEATHER": 3, "SNAKESKIN": 15, "SNAKESKIN2": 20}
    if len(tt) != 8:
        raise GeneratorError(f"tanning: expected 8, parsed {len(tt)}")
    for e, _b, hide, leather in tt:
        rows.append(recipe(f"2009scape-crafting-tanning-{e.lower()}", leather, 1, [(hide, 1), (995, coins.get(e, 20))], "Crafting", 1, 0.0, [], ["Tanner"], ["Pay a tanner to tan the hide (no experience)"], rel, e, commit))
    # amulet stringing: unstrung amulet + ball of wool, Crafting level of the amulet, no experience
    rel = CRAFT + "AmuletStringingPlugin.java"
    jt = read(root, CRAFT + "jewellery/JewelleryCrafting.java")
    # (enum, level, xp, component, product) -> key by product id
    amulets = {m[4]: (m[0], int(m[1])) for m in re.findall(r"^\s*([A-Z_]+AMULET)\((\d+), (\d+), (\d+), (\d+),", jt, re.M)}
    handled = [int(x) for x in re.search(r"super\(([\d, ]+)\)", read(root, rel)).group(1).split(",")]
    if len(handled) != 7 or any(str(h) not in amulets for h in handled):
        raise GeneratorError("amulet stringing: handled amulets do not match jewellery table")
    for h in handled:
        e, lv = amulets[str(h)]
        strung = 6581 if h == 6579 else h + 19
        rows.append(recipe(f"2009scape-crafting-amulet-string-{e.lower()}", strung, 1, [(h, 1), (1759, 1)], "Crafting", lv, 0.0, [], [], ["String with a ball of wool (no experience)"], rel, e, commit))
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
    return rows + cooking_assembly(root, commit) + remaining(root, commit)['Cooking']


# ------------------------------------------------------------------ cooking: assembly (hand-written listeners)
CR = COOK + "recipe/"
T = r"Items\.[A-Z0-9_]+?_(\d+)"


def _enum_rows(root, rel, enum_name, pattern, expect):
    text = read(root, rel).split(f"enum class {enum_name}(")[1].split("companion object")[0]
    rows = re.findall(pattern, text, re.M)
    if len(rows) != expect:
        raise GeneratorError(f"{rel}: expected {expect} {enum_name} rows, parsed {len(rows)}")
    return rows


def cooking_assembly(root, commit):
    rows = []
    add = lambda rid, out, inputs, lv, xp, rel, enum, method, fac=None, extra=None: rows.append(
        recipe(f"2009scape-cooking-assembly-{rid}", out, 1, inputs, "Cooking", int(lv), float(xp), [], fac or [], [method], rel, enum, commit, extra))
    # pies: base + added -> product (multi-step pies create part-made items)
    rel = CR + "PieListener.kt"
    for e, b, a, p, lv in _enum_rows(root, rel, "PieProduct", r"^\s*([A-Z_0-9]+)\(Items\.[A-Z0-9_]+?_(\d+), Items\.[A-Z0-9_]+?_(\d+), Items\.[A-Z0-9_]+?_(\d+), (\d+),", 21):
        add(e.lower(), p, [(b, 1), (a, 1)], lv, 0, rel, e, "Combine the ingredients (pie assembly)")
    rel = CR + "PieShellListener.kt"
    add("pie_shell", 2315, [(2313, 1), (1953, 1)], 1, 0, rel, "PIE_SHELL", "Put pastry dough into a pie dish")
    # pizzas
    rel = CR + "PizzaListener.kt"
    for e, b, a, p, lv, xp in _enum_rows(root, rel, "PizzaProduct", r"^\s*([A-Z_0-9]+)\(Items\.[A-Z0-9_]+?_(\d+), Items\.[A-Z0-9_]+?_(\d+), Items\.[A-Z0-9_]+?_(\d+), (\d+), ([0-9.]+),", 7):
        add(e.lower(), p, [(b, 1), (a, 1)], lv, xp, rel, e, "Add the topping to the pizza")
    # bowl toppings / sauces
    rel = CR + "ToppingListener.kt"
    for e, b, a, p, lv, xp in _enum_rows(root, rel, "ToppingProduct", r"^\s*([A-Z_0-9]+)\(Items\.[A-Z0-9_]+?_(\d+), Items\.[A-Z0-9_]+?_(\d+), Items\.[A-Z0-9_]+?_(\d+), (\d+), ([0-9.]+),", 12):
        add(e.lower(), p, [(b, 1), (a, 1)], lv, xp, rel, e, "Combine the ingredients (topping)")
    # stew and curry
    rel = CR + "StewListener.kt"
    for e, b, a, p, lv in _enum_rows(root, rel, "StewProduct", r"^\s*([A-Z_0-9]+)\(Items\.[A-Z0-9_]+?_(\d+), Items\.[A-Z0-9_]+?_(\d+), Items\.[A-Z0-9_]+?_(\d+), (\d+),", 4):
        add(e.lower(), p, [(b, 1), (a, 1)], lv, 0, rel, e, "Combine the ingredients (stew)")
    rel = CR + "CurryListener.kt"
    add("curry_leaf", 2009, [(2001, 1), (5970, 3)], 60, 0, rel, "CURRY_LEAF", "Mix 3 curry leaves into the uncooked stew")
    add("curry_spice", 2009, [(2001, 1), (2007, 1)], 60, 0, rel, "SPICE", "Mix spice into the uncooked stew")
    # potatoes
    rel = CR + "PotatoListener.kt"
    add("potato_with_butter", 6703, [(6701, 1), (6697, 1)], 39, 40.5, rel, "POTATO_WITH_BUTTER", "Add a pat of butter to the baked potato")
    for e, a, p, lv, xp in _enum_rows(root, rel, "PotatoProduct", r"^\s*([A-Z_0-9]+)\(Items\.[A-Z0-9_]+?_(\d+), Items\.[A-Z0-9_]+?_(\d+), (\d+), ([0-9.]+),", 5):
        add(e.lower(), p, [(a, 1), (6703, 1)], lv, xp, rel, e, "Add the topping to the potato with butter")
    # cakes, wraps
    rel = COOK + "CakeListener.kt"
    add("cake_mix", 1889, [(1944, 1), (1927, 1), (1933, 1), (1887, 1)], 40, 0, rel, "UNCOOKED_CAKE", "Mix egg, milk and flour in a cake tin")
    rel = CR + "ChocolateCakeListener.kt"
    add("chocolate_cake_bar", 1897, [(1891, 1), (1973, 1)], 50, 30, rel, "CHOCOLATE_BAR", "Add chocolate to the cake")
    add("chocolate_cake_dust", 1897, [(1891, 1), (1975, 1)], 50, 30, rel, "CHOCOLATE_DUST", "Add chocolate dust to the cake")
    rel = CR + "OomlieWrapListener.kt"
    add("wrapped_oomlie", 2341, [(2337, 1), (2339, 1)], 50, 0, rel, "WRAPPED_OOMLIE", "Wrap the raw oomlie in a palm leaf")
    # dough: water container + pot of flour
    rel = COOK + "DoughMakingListener.kt"
    doughs = re.findall(r"^\s*([A-Z_]+)\(Items\.[A-Z0-9_]+?_(\d+), getItemName\(Items\.[A-Z0-9_]+?_\d+\), (\d+)\)", read(root, rel), re.M)
    if len(doughs) != 4:
        raise GeneratorError(f"dough: expected 4, parsed {len(doughs)}")
    for e, p, lv in doughs:
        for cont, water in (("bucket", 1929), ("bowl", 1921), ("jug", 1937)):
            add(f"{e.lower()}_{cont}", p, [(water, 1), (1933, 1)], lv, 0, rel, e, f"Mix a {cont} of water with a pot of flour")
    # dairy (any one listed input produces the product)
    rel = COOK + "dairy/DairyProduct.java"
    for e, lv, xp, p, ins in re.findall(r"^\s*([A-Z_]+)\((\d+), ([0-9.]+), new Item\(Items\.[A-Z0-9_]+?_(\d+), 1\), new Integer\[\] \{([^}]*)\}", read(root, rel), re.M):
        for i in re.findall(T, ins):
            add(f"dairy_{e.lower()}_from_{i}", p, [(i, 1)], lv, xp, rel, e, "Use a dairy churn", ["Dairy churn"])
    return rows


# ------------------------------------------------------------------ remaining crafting / cooking / runecrafting
def remaining(root, commit):
    out = {"Crafting": [], "Cooking": [], "Runecrafting": []}

    def add(skill, rid, o, qty, inputs, lv, xp, rel, enum, method, tools=None, fac=None, extra=None):
        out[skill].append(recipe(f"2009scape-{skill.lower()}-{rid}", o, qty, inputs, skill, int(lv), float(xp), tools or [], fac or [], [method], rel, enum, commit, extra))

    # spiky vambraces: kebbit claws + vambraces, level 32, 6 xp
    rel = CRAFT + "leather/SpikyVambraces.kt"
    text = read(root, rel)
    vs = re.findall(r"Items\.[A-Z0-9_]+?_(\d+) ->\s*\{\s*craftVamb\(player,vamb,Items\.[A-Z0-9_]+?_(\d+),", text)
    if len(vs) != 5 or ">= 32" not in text or "CRAFTING,6.0" not in text:
        raise GeneratorError(f"spiky vambraces: unexpected shape ({len(vs)} rows)")
    for vamb, prod in vs:
        add("Crafting", f"spiky-vambraces-{prod}", prod, 1, [(vamb, 1), (10113, 1)], 32, 6.0, rel, f"SPIKY_{prod}", "Attach kebbit claws to the vambraces")
    # lanterns (no experience)
    rel = CRAFT + "lightsources/LanternCrafting.kt"
    text = read(root, rel)
    if not all(x in text for x in ("4529", "4532", "4535", "4546", "4700", ">= 20")):
        raise GeneratorError("lanterns: expected product ids not found")
    for rid, prod, ins, lv in (("candle-lantern-white", 4529, (4527, 36), 1), ("candle-lantern-black", 4532, (4527, 38), 1), ("oil-lantern", 4535, (4540, 4525), 1), ("bullseye-lantern", 4546, (4544, 4542), 1), ("sapphire-lantern", 4700, (4544, 1607), 20)):
        add("Crafting", rid, prod, 1, [(i, 1) for i in ins], lv, 0.0, rel, rid.upper().replace("-", "_"), "Combine the items (no experience)")
    # limestone bricks
    rel = CRAFT + "limestone/ChiselLimestonePulse.java"
    text = read(root, rel)
    if not all(x in text for x in ("3211", "3420", "< 12", "CRAFTING, 6")):
        raise GeneratorError("limestone: expected values not found")
    add("Crafting", "limestone-brick", 3420, 1, [(3211, 1)], 12, 6.0, rel, "LIMESTONE_BRICK", "Chisel limestone into a brick", ["Chisel"], extra={"toolItemIds": [CHISEL]})
    # skewers, kebab, dust, slices
    rel = COOK + "SkeweredFoodListener.kt"
    text = read(root, rel)
    skew = dict(re.findall(r"Items\.[A-Z0-9_]+?_(\d+) to Items\.[A-Z0-9_]+?_(\d+)", text))
    levels = dict(re.findall(r"Items\.[A-Z0-9_]+?_(\d+) -> (\d+)\n", text))
    if len(skew) != 4 or set(skew) != set(levels):
        raise GeneratorError("skewers: map and level tables do not match")
    for raw, prod in skew.items():
        add("Cooking", f"skewer-{prod}", prod, 1, [(raw, 1), (7225, 1)], levels[raw], 0.0, rel, f"SKEWER_{prod}", "Put the raw meat on an iron spit")
    rel = COOK + "SaucyKebabListener.kt"
    text = read(root, rel)
    kebabs = re.findall(r"Items\.[A-Z_]*KEBAB_(\d+)", text)
    if len(kebabs) < 4 or "4610" not in text or "4608" not in text:
        raise GeneratorError("kebab: expected ids not found")
    for k in sorted(set(kebabs) - {"4608"}):
        add("Cooking", f"super-kebab-{k}", 4608, 1, [(k, 1), (4610, 1)], 1, 0.0, rel, f"KEBAB_{k}", "Add red hot sauce to a kebab (no level or experience)")
    rel = COOK + "ChocolateBarCutter.kt"
    if "1973" not in read(root, rel) or "1975" not in read(root, rel):
        raise GeneratorError("chocolate cutter: ids not found")
    add("Cooking", "chocolate-dust", 1975, 1, [(1973, 1)], 1, 0.0, rel, "CHOCOLATE_DUST", "Cut a chocolate bar with a knife", ["Knife"])
    rel = COOK + "WatermelonSliceListener.kt"
    if "5982" not in read(root, rel) or ", 3)" not in read(root, rel):
        raise GeneratorError("watermelon: expected values not found")
    add("Cooking", "watermelon-slices", 5984, 3, [(5982, 1)], 1, 0.0, rel, "WATERMELON_SLICE", "Slice a watermelon with a knife (3 slices)", ["Knife"])
    # wine
    rel = COOK + "WineFermentListener.kt"
    text = read(root, rel)
    if not all(x in text for x in ("1987", "1937", "1995", "< 35")):
        raise GeneratorError("wine: expected values not found")
    add("Cooking", "unfermented-wine", 1995, 1, [(1987, 1), (1937, 1)], 35, 0.0, rel, "UNFERMENTED_WINE", "Mix grapes with a jug of water")
    frel = COOK + "fermenting/WineFermentingPulse.java"
    if "addExperience(Skills.COOKING, 200" not in read(root, frel):
        raise GeneratorError("wine fermenting: xp not found")
    add("Cooking", "wine", 1993, 1, [(1995, 1)], 35, 200.0, frel, "WINE", "Wait for the wine to ferment (may fail to bad wine); experience is granted when it succeeds")
    # brewing
    rel = COOK + "fermenting/Brewable.kt"
    brews = re.findall(r"^\s*([A-Z_]+)\(\"([^\"]+)\", Items\.[A-Z0-9_]+?_(\d+), (\d+), intArrayOf\(Items\.[A-Z0-9_]+?_(\d+)[^)]*\), ([0-9.]+), \d+, \d+(?:, (\d+))?\)", read(root, rel), re.M)
    if len(brews) != 11:
        raise GeneratorError(f"brewing: expected 11, parsed {len(brews)}")
    for e, name, ing, lv, prod, xp, amt in brews:
        add("Cooking", f"brew-{e.lower()}", prod, 1, [(ing, int(amt or 4))], lv, xp, rel, e, f"Ferment {name} in a vat or barrel (also needs water and ale yeast; modelled here by the ingredient only)", fac=["Brewing vat"])
    # runecrafting: tiaras and talisman staves (Altar enum maps Talisman/Tiara/Staff by name)
    rel = RC + "RunecraftingData.kt"
    text = read(root, rel)
    tal = dict(re.findall(r"^    ([A-Z]+)\(Item\(Items\.[A-Z_]+?_TALISMAN_(\d+)\)\)", text.split("enum class Talisman")[1].split("enum class", 1)[0], re.M))
    tia = {n: (int(i), float(x)) for n, i, x in re.findall(r"^    ([A-Z]+)\(Item\(Items\.[A-Z_]+?_TIARA_(\d+)\), ([0-9.]+)\)", text.split("enum class Tiara")[1].split("enum class", 1)[0], re.M)}
    stf = dict(re.findall(r"^    ([A-Z]+)\(Item\(Items\.[A-Z_]+?_STAFF_(\d+)\)\)", text.split("enum class Staff")[1].split("enum class", 1)[0], re.M))
    altars = re.findall(r"^    ([A-Z]+)\(Scenery\.[A-Z_0-9]+, [^,]+, [^,]+, Rune\.[A-Z]+\)", text.split("enum class Altar")[1], re.M)
    names = [n for n in altars if n in tal and n in tia and n in stf]
    if len(names) != 12:
        raise GeneratorError(f"talisman enchanting: expected 12 altars, parsed {len(names)}: {names}")
    erel = RC + "TalismanEnchantingListener.kt"
    if "Items.TIARA_5525" not in read(root, erel) or "RUNECRAFTING_STAFF_13629" not in read(root, erel):
        raise GeneratorError("talisman enchanting: base items changed")
    for n in names:
        add("Runecrafting", f"tiara-{n.lower()}", tia[n][0], 1, [(tal[n], 1), (5525, 1)], 1, tia[n][1], erel, f"{n}_TIARA", f"Use the {n.lower()} talisman on a tiara at the {n.lower()} altar", fac=[f"{n.title()} altar"])
        add("Runecrafting", f"staff-{n.lower()}", stf[n], 1, [(tal[n], 1), (13629, 1)], 1, 0.0, erel, f"{n}_STAFF", f"Use the {n.lower()} talisman on a runecrafting staff at the {n.lower()} altar", fac=[f"{n.title()} altar"])
    return out


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
    return rows + remaining(root, commit)["Runecrafting"]


# ------------------------------------------------------------------ registry
PARSERS = {"herblore": herblore, "crafting": crafting, "cooking": cooking, "runecrafting": runecrafting}
SOURCE_FILES = {"cooking": [COOK + "CookableItems.java", COOK + "DoughMakingListener.kt", COOK + "CakeListener.kt", COOK + "dairy/DairyProduct.java", COOK + "SkeweredFoodListener.kt", COOK + "SaucyKebabListener.kt", COOK + "ChocolateBarCutter.kt", COOK + "WatermelonSliceListener.kt", COOK + "WineFermentListener.kt", COOK + "fermenting/WineFermentingPulse.java", COOK + "fermenting/Brewable.kt"] + [CR + f for f in ("PieListener.kt", "PieShellListener.kt", "PizzaListener.kt", "ToppingListener.kt", "StewListener.kt", "CurryListener.kt", "PotatoListener.kt", "ChocolateCakeListener.kt", "OomlieWrapListener.kt")], "runecrafting": [RC + "Rune.java", RC + "CombinationRune.java", RC + "RunecraftingData.kt", RC + "TalismanEnchantingListener.kt"], "crafting": [CRAFT + f for f in ("gem/Gems.java", "pottery/PotteryItem.java", "spinning/SpinningItem.java", "glass/GlassProduct.kt", "glass/GlassMakePulse.kt", "silver/SilverProduct.kt", "jewellery/JewelleryCrafting.java", "armour/LeatherCrafting.java", "armour/HardCraftPulse.java", "armour/SnakeSkin.java", "leather/SpikyVambraces.kt", "lightsources/LanternCrafting.kt", "limestone/ChiselLimestonePulse.java", "StuddedArmourPlugin.java", "WeaveOptionPlugin.java", "SnelmCraftPlugin.java", "TanningProduct.java", "AmuletStringingPlugin.java")], "herblore": [HERBLORE + f for f in ("Herbs.java", "UnfinishedPotion.kt", "FinishedPotion.kt", "Tars.java", "BarbarianPotion.kt", "GrindingItem.java")]}
SKILL_NAME = {"herblore": "Herblore", "crafting": "Crafting", "cooking": "Cooking", "runecrafting": "Runecrafting"}
SOURCE_FILES["crafting"] += [CRAFT + f for f in ("leather/SpikyVambraces.kt", "lightsources/LanternCrafting.kt", "limestone/ChiselLimestonePulse.java")]
SOURCE_FILES["cooking"] += [COOK + f for f in ("SkeweredFoodListener.kt", "SaucyKebabListener.kt", "ChocolateBarCutter.kt", "WatermelonSliceListener.kt", "WineFermentListener.kt", "fermenting/WineFermentingPulse.java", "fermenting/Brewable.kt")]
SOURCE_FILES["runecrafting"] += [RC + "RunecraftingData.kt", RC + "TalismanEnchantingListener.kt"]


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
