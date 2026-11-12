#!/usr/bin/env python3
"""Generate site/data/slayer.json (tasks, masters, rewards, rules) from the 2009Scape server source.

`Tasks.java` is the assignment table (combat check, NPC ids, Slayer level, quest gate, undead/dragon flags), `Master.java`
the masters and their weighted task lists, `SlayerRewardPlugin.java` the reward costs, `SlayerManager.kt`/`SlayerUtils.kt`
the point and assignment rules. Shape assertions (row counts) and rule-literal checks make source changes fail loudly.
`ordinal` is kept because the server save stores the current task as its enum ordinal.

Usage: generate_slayer.py --source-root <upstream repo root> --source-commit <sha> [--output site/data/slayer.json]
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "Server/src/main/content/global/skill/slayer/"
QUESTS = "Server/src/main/content/data/Quests.kt"
EXPECTED = {"tasks": 93, "masters": 6}


class GeneratorError(Exception):
    pass


def read(root, rel):
    p = Path(root) / rel
    if not p.exists():
        raise GeneratorError(f"missing source file {rel}")
    return p.read_text(errors="ignore")


def prov(rel, commit, **kw):
    return {"source": "2009Scape", "file": rel, "commit": commit, **kw}


def key(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def npc_name(nid):
    p = ROOT / "site/data/npcs" / f"{nid}.json"
    return json.loads(p.read_text()).get("name") if p.exists() else None


def life_points(nid):
    p = ROOT / "site/data/monsters" / f"{nid}.json"
    return json.loads(p.read_text()).get("lifepoints") if p.exists() else None


def quest_names(root):
    text = read(root, QUESTS)
    return dict(re.findall(r"^\s{4}([A-Z0-9_]+)\(\"([^\"]+)\"", text, re.M))


def xp_range(npc_ids):
    """Slayer xp per kill is the NPC's maximum life points (SlayerManager.kt); None when no listed NPC has catalog life points."""
    lp = [int(v) for v in (life_points(i) for i in npc_ids) if v]
    return OrderedDict(min=min(lp), max=max(lp)) if lp else None


def tasks(root, commit, qnames):
    rel = BASE + "Tasks.java"
    text = read(root, rel)
    body = text.split("public enum Tasks", 1)[1].split("\n    ;", 1)[0]
    body = "\n".join(l for l in body.splitlines() if not l.strip().startswith("//"))
    parts = re.split(r"\n    ([A-Z][A-Z_]+)\s?\(", "\n" + body.split("{", 1)[1])
    rows = []
    for ordinal, (name, block) in enumerate(zip(parts[1::2], parts[2::2])):
        m = re.match(r"\s*(\d+),\s*new int\[\]\s*\{(.*?)\},\s*new String\[\]\s*\{(.*?)\}\s*,\s*(\d+)\s*,\s*(.*?)\)\s*,?\s*$", block.strip(), re.S)
        if not m:
            raise GeneratorError(f"task not parsed: {name}")
        combat, ids, info, slayer, tail = m.groups()
        npc_ids = []
        for n in re.findall(r"(?:[A-Za-z_]+_)?(\d+)", ids):
            if int(n) not in npc_ids:
                npc_ids.append(int(n))
        flags = re.match(r"(true|false)\s*,\s*(true|false)$", tail.strip())
        quest = re.match(r"Quests\.([A-Z0-9_]+)$", tail.strip())
        if not (flags or quest):
            raise GeneratorError(f"task tail not parsed: {name}: {tail!r}")
        if quest and quest.group(1) not in qnames:
            raise GeneratorError(f"unknown quest {quest.group(1)}")
        tip = " ".join(s.strip() for s in re.findall(r"\"((?:[^\"\\]|\\.)*)\"", info))
        rows.append(OrderedDict(
            id=f"2009scape-slayer-task-{key(name)}", skill="Slayer", kind="task", ordinal=ordinal, key=name,
            name=npc_name(npc_ids[0]) or name.replace("_", " ").capitalize(), minCombatLevel=int(combat), level=int(slayer),
            undead=bool(flags and flags.group(1) == "true"), dragon=bool(flags and flags.group(2) == "true"),
            quest=qnames[quest.group(1)] if quest else None, npcIds=npc_ids, xpPerKill=xp_range(npc_ids), tip=tip, provenance=prov(rel, commit, enum=name)))
    return rows


def masters(root, commit, task_rows):
    rel = BASE + "Master.java"
    text = read(root, rel)
    by_key = {t["key"]: t for t in task_rows}
    rows = []
    for m in re.finditer(r"\n\t([A-Z]+)\((\d+),\s*(\d+),\s*(\d+),\s*new int\[\]\{(\d+),\s*(\d+)\},\s*new int\[\]\{(\d+),\s*(\d+),\s*(\d+)\},(.*?)(?=\n\t[A-Z]+\(\d+,|\n\tprivate static final HashMap)", text, re.S):
        name, npc, combat, slayer, lo, hi, p1, p2, p3, body = m.groups()
        body = "\n".join(l for l in body.splitlines() if not l.strip().startswith("//"))
        entries = []
        for mm in re.finditer(r"new Task\(Tasks\.([A-Z_]+),\s*(\d+)(?:,\s*new Integer\[\]\{(\d+),\s*(\d+)\})?\)", body):
            t, w, a, b = mm.groups()
            if t not in by_key:
                raise GeneratorError(f"{name}: unknown task {t}")
            entries.append(OrderedDict(taskId=by_key[t]["id"], weight=int(w), amountRange=[int(a), int(b)] if a else None))
        if not entries:
            raise GeneratorError(f"master without tasks: {name}")
        rows.append(OrderedDict(
            id=f"2009scape-slayer-master-{key(name)}", skill="Slayer", kind="master", key=name, name=npc_name(int(npc)) or name.capitalize(),
            npcId=int(npc), minCombatLevel=int(combat), level=int(slayer), defaultAmountRange=[int(lo), int(hi)],
            completionPoints=OrderedDict(every=int(p1), tenth=int(p2), fiftieth=int(p3)), totalWeight=sum(e["weight"] for e in entries),
            tasks=entries, provenance=prov(rel, commit, enum=name)))
    return rows


def rewards(root, commit):
    rel = BASE + "SlayerRewardPlugin.java"
    text = read(root, rel)
    must = ["purchase(player, 300)", "purchase(player, 400)", "purchase(player, 75)", "purchase(player, 35)", "purchase(player, 30)", "purchase(player, 100)",
            "addExperience(Skills.SLAYER, 10000", "new Item(13281)", "new Item(558, 1000)", "new Item(560, 250)", "new Item(13280, 250)", "new Item(4172, 250)",
            "qp < 50", "qp < 100", "qp < 150", "qp < 200"]
    for s in must:
        if s not in text:
            raise GeneratorError(f"reward literal not in source: {s}")
    p = prov(rel, commit)
    return [
        OrderedDict(name="Learn: Broad arrows", kind="unlock", cost=300),
        OrderedDict(name="Learn: Slayer ring", kind="unlock", cost=300),
        OrderedDict(name="Learn: Slayer helm", kind="unlock", cost=400),
        OrderedDict(name="10,000 Slayer experience", kind="buy", cost=400, xp=10000),
        OrderedDict(name="Ring of slaying", kind="buy", cost=75, items=[OrderedDict(itemId=13281, quantity=1)]),
        OrderedDict(name="Mind and death runes", kind="buy", cost=35, items=[OrderedDict(itemId=558, quantity=1000), OrderedDict(itemId=560, quantity=250)]),
        OrderedDict(name="Broad-tipped bolts", kind="buy", cost=35, items=[OrderedDict(itemId=13280, quantity=250)]),
        OrderedDict(name="Broad arrows", kind="buy", cost=35, items=[OrderedDict(itemId=4172, quantity=250)]),
        OrderedDict(name="Cancel current task", kind="service", cost=30),
        OrderedDict(name="Block current task", kind="service", cost=100, note="needs 50/100/150/200 quest points for the 1st/2nd/3rd/4th blocked task; at most 4"),
    ], p


def rules(root, commit):
    mgr = read(root, BASE + "SlayerManager.kt")
    for s in ["completedTasks > 4", "taskStreak % 50 == 0", "taskStreak % 10 == 0", "getPoints() < 64000", "maximumLifepoints.toDouble()", "xp *= 1.15"]:
        if s not in mgr:
            raise GeneratorError(f"rule literal not in SlayerManager.kt: {s}")
    util = read(root, BASE + "SlayerUtils.kt")
    for s in ["task.task.combatCheck <= player.properties.currentCombatLevel", "getLevel(Skills.SLAYER) >= task.levelReq"]:
        if s not in util:
            raise GeneratorError(f"rule literal not in SlayerUtils.kt: {s}")
    return OrderedDict(
        pointsStartAfterTasks=4, turaelAwardsPoints=False, pointCap=64000, streakBonusEvery=[10, 50],
        experiencePerKill="the NPC's maximum life points", dragonSlayerGlovesMultiplier=1.15,
        assignment="a master offers only tasks whose minimum combat level and Slayer level you meet, that are not blocked, and whose quest is complete; one is picked by weight",
        maxBlockedTasks=4, saveNote="the server save stores the current task as its enum ordinal (see task ordinal)",
        provenance=[prov(BASE + "SlayerManager.kt", commit), prov(BASE + "SlayerUtils.kt", commit)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--output", default=str(ROOT / "site/data/slayer.json"))
    a = ap.parse_args()
    c = a.source_commit
    t = tasks(a.source_root, c, quest_names(a.source_root))
    m = masters(a.source_root, c, t)
    for k, rows in (("tasks", t), ("masters", m)):
        if len(rows) != EXPECTED[k]:
            raise GeneratorError(f"{k}: expected {EXPECTED[k]} rows, parsed {len(rows)}")
    ids = [r["id"] for r in t + m]
    if len(ids) != len(set(ids)):
        raise GeneratorError("duplicate row ids")
    used = {tk for mm in m for e in mm["tasks"] for tk in [e["taskId"]]}
    for r in t:
        r["assignedBy"] = [mm["name"] for mm in m if any(e["taskId"] == r["id"] for e in mm["tasks"])]
    rw, rprov = rewards(a.source_root, c)
    for r in rw:
        r["provenance"] = rprov
    have = {p.stem for p in (ROOT / "site/data/items").glob("*.json")}
    for r in rw:
        for i in r.get("items", []):
            if str(i["itemId"]) not in have:
                raise GeneratorError(f"reward item missing from catalog: {i['itemId']}")
    doc = OrderedDict(formatVersion=1, source="2009Scape", sourceCommit=c,
                      counts={"tasks": len(t), "masters": len(m), "rewards": len(rw), "total": len(t) + len(m) + len(rw)},
                      rules=rules(a.source_root, c), rewards=rw, masters=m, tasks=t)
    Path(a.output).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
