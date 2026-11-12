#!/usr/bin/env python3
"""Generate site/data/minigames.json (minigame reward shops and rules) from the 2009Scape server source.

Minigame logic is embedded in code, so each minigame has its own parser with rule-literal assertions that fail loudly
if the source changes. Currently modelled: Pest Control (Void Knight commendation shop and xp conversion),
Pyramid Plunder (rooms, xp, artifact and sceptre rates), Barrows (reward chest), the Mage Training Arena shop, the Blast Furnace
the Castle Wars ticket exchange, Fishing Trawler (loot table, xp) and the Gnome Restaurant delivery jobs. Item ids are verified against the item catalog.

Usage: generate_minigames.py --source-root <upstream repo root> --source-commit <sha> [--output site/data/minigames.json]
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MG = "Server/src/main/content/minigame/"
PC = MG + "pestcontrol/reward/PCRewardInterface.java"
PP_UTILS = MG + "pyramidplunder/PlunderUtils.kt"
PP_DATA = MG + "pyramidplunder/PlunderData.kt"
BR = MG + "barrows/RewardChest.kt"
MTA = MG + "mta/MTAShop.java"
BF = MG + "blastfurnace/BlastFurnace.kt"
BFC = MG + "blastfurnace/BlastConsts.kt"
BAR = "Server/src/main/content/global/skill/smithing/smelting/Bar.java"
CW = MG + "castlewars/CastleWars.kt"
SHOPS = "Server/data/configs/shops.json"
FT = MG + "fishingtrawler/"
FISH = "Server/src/main/content/global/skill/fishing/Fish.kt"
GC = MG + "gnomecooking/GnomeCookingJob.kt"


class GeneratorError(Exception):
    pass


def read(root, rel):
    p = Path(root) / rel
    if not p.exists():
        raise GeneratorError(f"missing source file {rel}")
    return p.read_text(errors="ignore")


def prov(rel, commit, **kw):
    return {"source": "2009Scape", "file": rel, "commit": commit, **kw}


def need(text, literals, where):
    for s in literals:
        if s not in text:
            raise GeneratorError(f"rule literal not in {where}: {s}")


def key(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def herb_ids(root):
    text = read(root, "Server/src/main/content/global/skill/herblore/Herbs.java")
    return {n: int(i) for n, i in re.findall(r"\b([A-Z_]+)\(new Item\((\d+)\),", text)}


def pest_control(root, commit):
    text = read(root, PC)
    herbs = herb_ids(root)
    need(text, ["SKILL_POINTS = new int[] { 1, 10, 100 }", "CHARM_POINTS = new int[] { 2, 28, 56 }", "CHARM_AMOUNTS = new int[] { 1, 14, 28 }",
                "(int) ((double) (level * level) / 600) * N", "bonus = 1.1", "bonus = 1.01", "points >= 100", "points >= 10",
                "N = 18", "N = 32", "N = 35", "MIN_BUILD = 13", "MAX_BUILD = 18", "< 25", "!= Skills.PRAYER ? 42 : 22"], PC)
    body = text.split("public enum Reward {", 1)[1]
    rewards = []
    for skill in re.findall(r"\b([A-Z]+)\(Skills\.([A-Z]+),\s*new int\[\]", body):
        rewards.append(OrderedDict(id=f"2009scape-pestcontrol-xp-{key(skill[1])}", kind="xp", name=("Ranged" if skill[1] == "RANGE" else skill[1].capitalize()) + " experience",
                                   skill="Ranged" if skill[1] == "RANGE" else skill[1].capitalize(), pointOptions=[1, 10, 100],
                                   note="xp per point = floor(level² ÷ 600) × N (Prayer 18, Magic/Ranged 32, Attack/Strength/Defence/Hitpoints 35), ×1.01 from 10 points, ×1.1 from 100"))
    for k, name, cost, items in re.findall(r"\b([A-Z_]+)\(\"([^\"]+)\",\s*(\d+),\s*new Item\[\]\s*\{(.*?)\},\s*new int\[\]", body, re.S):
        ids = [int(i) for i in re.findall(r"new Item\((\d+)\)", items)]
        for h in re.findall(r"Herbs\.([A-Z_]+)\.getHerb\(\)", items):
            if h not in herbs:
                raise GeneratorError(f"unknown herb {h}")
            ids.append(herbs[h])
        if not ids:
            raise GeneratorError(f"reward without items: {k}")
        row = OrderedDict(id=f"2009scape-pestcontrol-{key(k)}", kind="pack" if k.endswith("PACK") else "item", name=name, points=int(cost), itemIds=ids)
        if k in ("HERB_PACK", "MINERAL_PACK", "SEED_PACK"):
            skill = {"HERB_PACK": "Herblore", "MINERAL_PACK": "Mining", "SEED_PACK": "Farming"}[k]
            row["requirements"] = [{"skill": skill, "level": 25}]
            row["note"] = "a pack is a random build of 13-18 items (seed/herb packs) or 38-43 (mineral pack); herbs and ore come noted"
        elif k.startswith("VOID_") and k != "VOID_KNIGHT_SEAL":
            row["requirements"] = [{"skill": s, "level": 42} for s in ("Hitpoints", "Attack", "Defence", "Strength", "Ranged", "Magic")] + [{"skill": "Prayer", "level": 22}]
        rewards.append(row)
    for k, name, item in re.findall(r"\b([A-Z_]+_CHARM)\(\"([^\"]+)\",\s*new Item\((\d+)\)", body):
        rewards.append(OrderedDict(id=f"2009scape-pestcontrol-{key(k)}", kind="charm", name=name, itemIds=[int(item)],
                                   options=[OrderedDict(points=p, quantity=q) for p, q in ((2, 1), (28, 14), (56, 28))]))
    for r in rewards:
        r["provenance"] = prov(PC, commit)
    return OrderedDict(
        id="2009scape-minigame-pest-control", name="Pest Control", currency="Void Knight commendation points",
        xpRule=OrderedDict(formula="points × floor(level² ÷ 600) × N × bonus", N=OrderedDict(Prayer=18, Magic=32, Ranged=32, Attack=35, Strength=35, Defence=35, Hitpoints=35),
                           bonus=OrderedDict(under10Points=1.0, from10Points=1.01, from100Points=1.1), pointOptions=[1, 10, 100],
                           note="the shop shows 'Must reach level 25 first' under 25; the divide happens in integer arithmetic before multiplying by N"),
        rewards=rewards, provenance=prov(PC, commit))


def pyramid_plunder(root, commit):
    util = read(root, PP_UTILS)
    data = read(root, PP_DATA)
    need(util, ["11 + (10 * getRoom(player)!!.room)", "* 0.66", "reward /= 2.0", "val divisor = (room * 2) * (tier * 35)", "divisor / 650.0", "divisor / 250.0",
                "1 -> 1500", "2 -> 1350", "3 -> 1250", "4 -> 1150", "else -> 1000", "(room * if(charmed) 2 else 4)", "60000 * 15"], PP_UTILS)
    urn_check = [20.0, 30.0, 50.0, 70.0, 100.0, 150.0, 225.0, 275.0]
    urn_open = [60.0, 90.0, 150.0, 215.0, 300.0, 450.0, 675.0, 825.0]
    for i, v in enumerate(urn_check, 1):
        need(util, [f"{i} -> {v}"], PP_UTILS)
    for i, v in enumerate(urn_open, 1):
        need(util, [f"{i} -> {v}"], PP_UTILS)
    rooms = re.findall(r"PlunderRoom\((\d+),\s*Location\.create\((\d+), (\d+), (\d+)\),\s*Location\.create\((\d+), (\d+), (\d+)\),\s*Direction\.(\w+)\)", data)
    if len(rooms) != 8:
        raise GeneratorError(f"expected 8 plunder rooms, parsed {len(rooms)}")
    sceptre = {1: 1500, 2: 1350, 3: 1250, 4: 1150}
    rows = []
    for n, ex, ey, ez, mx, my, mz, d in rooms:
        n = int(n)
        rows.append(OrderedDict(
            id=f"2009scape-pyramidplunder-room-{n}", kind="room", room=n, name=f"Room {n}", requirements=[{"skill": "Thieving", "level": 11 + 10 * n}],
            urnCheckXp=urn_check[n - 1], urnOpenXp=urn_open[n - 1], sarcophagusXp=urn_check[n - 1],
            chestXp=round(urn_open[n - 1] * 0.66, 2), doorXp=round(urn_open[n - 1] * 0.66, 2), lockpickDoorXp=round(urn_open[n - 1] * 0.66 / 2, 2),
            sceptreOneIn=sceptre.get(n, 1000), spearDirection=d.lower(),
            entrance=OrderedDict(x=int(ex), y=int(ey), plane=int(ez)), mummy=OrderedDict(x=int(mx), y=int(my), plane=int(mz)),
            provenance=prov(PP_UTILS, commit)))
    arts = re.search(r"val artifacts = arrayOf\((.*?)\n    \)", data, re.S).group(1)
    tiers = [[int(i) for i in re.findall(r"_(\d+)\b", g)] for g in re.findall(r"arrayOf\(([^)]*)\)", arts)]
    if [len(t) for t in tiers] != [3, 3, 3]:
        raise GeneratorError(f"artifact tiers not parsed: {tiers}")
    return OrderedDict(
        id="2009scape-minigame-pyramid-plunder", name="Pyramid Plunder", rooms=rows,
        artifacts=OrderedDict(common=tiers[0], stone=tiers[1], gold=tiers[2],
                              rule="per search of tier t (urn 1, sarcophagus 2, chest 3) in room r: divisor = r×2×t×35; gold if divisor÷650 beats the roll, else stone if divisor÷250 does, else common"),
        sceptre=OrderedDict(itemId=9050, oneInByRoom=sceptre | {"5-8": 1000}),
        rules=OrderedDict(entranceRotationMinutes=15, urnSuccess="random(thieving level) > room × 4 (room × 2 when charmed)", timeLimitTicks=500,
                          note="chest and door xp are 66% of the listed open xp; lockpicked doors give half"),
        provenance=[prov(PP_UTILS, commit), prov(PP_DATA, commit)])


def barrows(root, commit):
    text = read(root, BR)
    need(text, ["nKilled = barrowsRewardsIDs.size / 4", "for (i in 0 until nKilled+1)", "RandomFunction.roll(450 - 58 * nKilled)", "REGULAR_DROPS.roll(null, 1)"], BR)
    body = text.split("REGULAR_DROPS = WeightBasedTable.create(", 1)[1].split("\n    )", 1)[0]
    drops = [(int(i), int(lo), int(hi), float(w)) for i, lo, hi, w in re.findall(r"WeightedItem\(Items\.[A-Z_]+_(\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)", body)]
    if len(drops) != 9:
        raise GeneratorError(f"expected 9 barrows drops, parsed {len(drops)}")
    total = sum(d[3] for d in drops)
    table = [OrderedDict(id=f"2009scape-barrows-drop-{i}", kind="drop", itemIds=[i], min=lo, max=hi, weight=w, chancePercent=round(w / total * 100, 3), provenance=prov(BR, commit))
             for i, lo, hi, w in sorted(drops, key=lambda d: (-d[3], d[0]))]
    names = ["Ahrim", "Dharok", "Guthan", "Karil", "Torag", "Verac"]
    sets = re.findall(r"private val ([A-Z]+)\s*=\s*arrayOf\(([\d, ]+)\)", text)
    if [n.capitalize() for n, _ in sets] != names:
        raise GeneratorError(f"barrows sets not parsed: {[n for n, _ in sets]}")
    brothers = [OrderedDict(id=f"2009scape-barrows-brother-{n.lower()}", kind="brother", name=n, index=i, npcId=2025 + i, itemIds=[int(x) for x in ids.split(",")],
                            provenance=prov(BR, commit)) for i, (n, (_, ids)) in enumerate(zip(names, sets))]
    return OrderedDict(
        id="2009scape-minigame-barrows", name="Barrows", brothers=brothers, table=table, totalWeight=total,
        rules=OrderedDict(rolls="killed brothers + 1 rolls (killed = brother items ÷ 4)",
                          brotherItemChance="each roll: 1 in (450 − 58 × brothers killed) to award one random remaining item from the killed brothers' sets, otherwise one roll on the regular table; repeated ids merge",
                          npcIdRule="brother NPC id = 2025 + brother index"),
        provenance=prov(BR, commit))


def mta_shop(root, commit):
    text = read(root, MTA)
    items = [int(i) for i, q in re.findall(r"new Item\((\d+), (\d+)\)", re.search(r"ITEMS = new Item\[\] \{(.*?)\};", text, re.S).group(1))]
    prices = [[int(n) for n in g.split(",")] for g in re.findall(r"\{\s*([\d, ]+?)\s*\}", re.search(r"PRICES = new int\[\]\[\] \{(.*?)\};", text, re.S).group(1))]
    if len(items) != 24 or len(prices) != 24 or any(len(p) != 4 for p in prices):
        raise GeneratorError(f"MTA shop shape: {len(items)} items, {len(prices)} prices")
    need(text, ["item.getAmount() < 100", "isBonesToPeaches()", "slot >= 1 && slot <= 3", "ITEMS[slot - 1]"], MTA)
    rows = [OrderedDict(id=f"2009scape-mta-shop-{i}-{n}", kind="shop", slot=n, itemIds=[i],
                        pizazzPoints=OrderedDict(telekinetic=p[0], alchemist=p[1], enchantment=p[2], graveyard=p[3]), provenance=prov(MTA, commit))
            for n, (i, p) in enumerate(zip(items, prices))]
    return OrderedDict(
        id="2009scape-minigame-mage-training-arena", name="Mage Training Arena", currency="Pizazz points (Telekinetic, Alchemist, Enchantment, Graveyard)", shop=rows,
        rules=OrderedDict(stock="each item stocks 100", costRule="an item needs every listed pizazz-point type at once, and each is spent",
                          wandUpgrades="slots 1-3 (the wand upgrades) consume the previous slot's wand (or require the slot-3 wand)", bonesToPeaches="the Bones to Peaches spell (item 6926) is a one-time unlock"),
        provenance=prov(MTA, commit))


def blast_furnace(root, commit):
    cons, bf, bar = read(root, BFC), read(root, BF), read(root, BAR)
    need(bf, ["state.furnaceTemp !in 51..66", "rewardXP(player, Skills.SMITHING, totalProcessed.toDouble())", "coalAmount >= 1 && level >= Bar.STEEL.level", "coalAmount /= 2",
              "if (smithLevel >= BlastConsts.SMITH_REQ) return 0", "BlastConsts.ENTRANCE_FEE / 2"], BF)
    const = {n: v for n, v in re.findall(r"(?:const )?val ([A-Z_]+)(?::\s*Int)?\s*=\s*(\d+)", cons)}
    for n, v in (("SMITH_REQ", "60"), ("ENTRANCE_FEE", "2500"), ("FEE_ENTRANCE_DURATION", "1000"), ("COAL_LIMIT", "226"), ("ORE_LIMIT", "28"), ("BAR_LIMIT", "28"), ("COKE_LIMIT", "15")):
        if const.get(n) != v:
            raise GeneratorError(f"BlastConsts {n}: {const.get(n)} != {v}")
    rows = []
    for name, lvl, xp, product, ores in re.findall(r"\t([A-Z]+)\((\d+), ([\d.]+), new Item\((\d+), 1\),\s*(.*?)\)[,;]\s*\n", bar):
        pairs = [(int(i), int(q) if q else 1) for i, q in re.findall(r"new Item\((\d+)(?:,\s*(\d+))?\)", ores)]
        coal = next((q for i, q in pairs if i == 453), 0) if len(pairs) > 1 else 0
        rows.append(OrderedDict(id=f"2009scape-blastfurnace-bar-{key(name)}", kind="bar", name=name.capitalize() + " bar", level=int(lvl), smithingXp=float(xp),
                                barItemId=int(product), oreItemIds=[i for i, q in pairs if i != 453], coalPerBar=coal // 2 if coal > 1 else coal,
                                provenance=prov(BAR, commit, enum=name)))
    if len(rows) != 9:
        raise GeneratorError(f"expected 9 bars, parsed {len(rows)}")
    return OrderedDict(
        id="2009scape-minigame-blast-furnace", name="Blast Furnace", bars=rows,
        rules=OrderedDict(smithingRequired=60, entranceFeeCoins=2500, charosEntranceFee=1250, feeFreeAtSmithing=60, feeDurationTicks=1000,
                          limits=OrderedDict(coal=226, ore=28, bar=28, coke=15), pumpStrengthXp=4.0, pedalAgilityXp=2.0, smithingXpPerBarProcessed="1 per bar smelted, shared by everyone in the area when the furnace temperature is 51-66",
                          steel="iron ore becomes steel when coal is present and Smithing is at least 30", coalNote="the furnace needs half the normal coal per bar",
                          entrance=OrderedDict(x=1940, y=4958, plane=0), exit=OrderedDict(x=2931, y=10197, plane=0)),
        provenance=[prov(BF, commit), prov(BFC, commit), prov(BAR, commit)])


def castle_wars(root, commit):
    text = read(root, CW)
    need(text, ["gameTimeMinutes = 20", "gameCooldownMinutes = 5", "CASTLE_WARS_TICKET_4067"], CW)
    shops = json.loads(read(root, SHOPS))
    shop = next((s for s in shops if s.get("title") == "Castle Wars Ticket Exchange"), None)
    if not shop or shop["currency"] != "4067":
        raise GeneratorError("Castle Wars Ticket Exchange shop not found")
    ids = [int(i) for i in re.findall(r"\{(\d+),\d+,\d+\}", shop["stock"])]
    if len(ids) != 19:
        raise GeneratorError(f"expected 19 exchange items, parsed {len(ids)}")
    supplies = list(dict.fromkeys(int(i) for i in re.findall(r"Scenery\.TABLE_\d+ to Items\.[A-Z_]+_(\d+)", text)))
    if len(supplies) != 7:
        raise GeneratorError(f"expected 7 supply items, parsed {supplies}")
    rows = [OrderedDict(id=f"2009scape-castlewars-exchange-{i}", kind="exchange", itemIds=[i], currencyItemId=4067, provenance=prov(SHOPS, commit, shop="255")) for i in ids]
    return OrderedDict(
        id="2009scape-minigame-castle-wars", name="Castle Wars", currency="Castle Wars tickets", exchange=rows,
        rules=OrderedDict(gameMinutes=20, cooldownMinutes=5, ticketsWin=2, ticketsDraw=1, supplyTableItemIds=supplies,
                          note="ticket prices are not stored in the shop config (price comes from the item's value); winners get 2 tickets, a draw 1 (Lanthus dialogue)"),
        provenance=[prov(CW, commit), prov(SHOPS, commit)])


def npc_name(nid):
    p = ROOT / "site/data/npcs" / f"{nid}.json"
    return json.loads(p.read_text()).get("name") if p.exists() else None


def fishing_trawler(root, commit):
    loot, handler, session = read(root, FT + "TrawlerLoot.kt"), read(root, FT + "FishingTrawlerInteractionHandler.kt"), read(root, FT + "FishingTrawlerSession.kt")
    need(loot, ["val lo = 0.6133", "val hi = 0.7852", "(fishLevel.toDouble() - 15.0)*((hi - lo) / (99.0 - 15.0)) + lo", "if(f.level > fishLevel)"], FT + "TrawlerLoot.kt")
    need(handler, ["(((0.015 * player.skills.getLevel(Skills.FISHING))) * player.skills.getLevel(Skills.FISHING)) * rolls", "getLevel(Skills.FISHING) < 15", "1 -> TrawlerLoot.addLootAndMessage(player, level, rolls, true)"], FT + "FishingTrawlerInteractionHandler.kt")
    need(session, ["ceil(session.fishAmount / session.players.size.toDouble())", "session.fishAmount += 3"], FT + "FishingTrawlerSession.kt")
    body = loot.split("private val lootTable = arrayOf(", 1)[1]
    rows = []
    entries = re.findall(r"WeightedChanceItem\((?:Items\.[A-Z_]+_(\d+)|(0)),\s*1,\s*(\d+)\)", body)
    if len(entries) != 15:
        raise GeneratorError(f"expected 15 trawler loot entries, parsed {len(entries)}")
    total = sum(int(w) for _, _, w in entries)
    junk = set(int(i) for i in re.findall(r"_(\d+)\b", re.search(r"val junkItems = arrayOf\((.*?)\)\n", loot).group(1)))
    for item, zero, w in entries:
        iid = int(item) if item else 0
        kind = "fish" if iid == 0 else "junk" if iid in junk else "misc"
        rows.append(OrderedDict(id=f"2009scape-fishingtrawler-loot-{iid or 'fish'}", kind=kind, itemIds=[iid] if iid else [], weight=int(w), chancePercent=round(int(w) / total * 100, 3), provenance=prov(FT + "TrawlerLoot.kt", commit)))
    fish = []
    ftext = read(root, FISH)
    for n in re.findall(r"Items\.[A-Z_]+_(\d+)", re.search(r"val trawlerFishIds = arrayOf\((.*?)\)\n", loot).group(1) if "val trawlerFishIds" in loot else re.search(r"private val trawlerFishIds = arrayOf\((.*?)\)\n", loot).group(1)):
        m = re.search(r"\(Items\.[A-Z_]+_" + n + r", (\d+), ", ftext)
        if not m:
            raise GeneratorError(f"trawler fish {n} not in Fish.kt")
        fish.append(OrderedDict(itemId=int(n), level=int(m.group(1))))
    fish.sort(key=lambda f: f["level"])
    return OrderedDict(
        id="2009scape-minigame-fishing-trawler", name="Fishing Trawler", requirements=[{"skill": "Fishing", "level": 15}], loot=rows, totalWeight=total, fish=fish,
        rules=OrderedDict(rolls="rolls per player = ceil(fish caught by the ship ÷ players aboard); each caught fish adds 3 to the ship's fish",
                          fishRoll="when the table gives 'fish', every fish you meet the level for is tried best-first with chance (level − 15) × (0.7852 − 0.6133) ÷ 84 + 0.6133; the roll repeats until one succeeds",
                          xp="Fishing xp = 0.015 × level² × rolls", skipJunk="the reward interface offers an option that drops junk rolls", delivery="loot goes to the bank; Ultimate ironmen, or a full bank, get it in the inventory (fish noted) or on the floor"),
        provenance=[prov(FT + "TrawlerLoot.kt", commit), prov(FT + "FishingTrawlerInteractionHandler.kt", commit), prov(FT + "FishingTrawlerSession.kt", commit)])


def gnome_restaurant(root, commit):
    text = read(root, GC)
    jobs = re.findall(r"^\s{4}([A-Z_]+)\(GnomeTipper\.LEVEL\.(EASY|HARD),\s*(\d+),\s*\"([^\"]*)\"\)", text, re.M)
    if len(jobs) != 15 or [j[1] for j in jobs].count("EASY") != 8:
        raise GeneratorError(f"gnome restaurant jobs: {len(jobs)}")
    rows = [OrderedDict(id=f"2009scape-gnomerestaurant-job-{key(n)}", kind="job", difficulty=lvl.lower(), name=npc_name(int(nid)) or n.replace("_", " ").title(), npcId=int(nid),
                        location=tip.rstrip("."), provenance=prov(GC, commit, enum=n)) for n, lvl, nid, tip in jobs]
    return OrderedDict(id="2009scape-minigame-gnome-restaurant", name="Gnome Restaurant", jobs=rows,
                       rules=OrderedDict(note="delivery jobs are split into 8 easy and 7 hard customers; tip tables are not modelled"), provenance=prov(GC, commit))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--output", default=str(ROOT / "site/data/minigames.json"))
    a = ap.parse_args()
    c = a.source_commit
    games = [pest_control(a.source_root, c), pyramid_plunder(a.source_root, c), barrows(a.source_root, c), mta_shop(a.source_root, c),
             blast_furnace(a.source_root, c), castle_wars(a.source_root, c), fishing_trawler(a.source_root, c), gnome_restaurant(a.source_root, c)]
    have = {p.stem for p in (ROOT / "site/data/items").glob("*.json")}
    used = []
    for g in games:
        for r in g.get("rewards", []):
            used += r.get("itemIds", [])
        for k in ("brothers", "table", "shop", "exchange", "loot"):
            for r in g.get(k, []):
                used += r.get("itemIds", [])
        used += [f["itemId"] for f in g.get("fish", [])]
        for r in g.get("bars", []):
            used += [r["barItemId"]] + r["oreItemIds"]
        if "artifacts" in g:
            used += g["artifacts"]["common"] + g["artifacts"]["stone"] + g["artifacts"]["gold"] + [g["sceptre"]["itemId"]]
    missing = sorted({i for i in used if str(i) not in have})
    if missing:
        raise GeneratorError(f"item ids missing from the catalog: {missing}")
    doc = OrderedDict(formatVersion=1, source="2009Scape", sourceCommit=c,
                      counts={"minigames": len(games), "rows": sum(len(g.get(k, [])) for g in games for k in ("rewards", "rooms", "brothers", "table", "shop", "bars", "exchange", "loot", "jobs"))}, minigames=games)
    Path(a.output).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
