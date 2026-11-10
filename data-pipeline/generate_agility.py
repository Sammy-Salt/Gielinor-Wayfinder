#!/usr/bin/env python3
"""Generate site/data/agility.json (basic courses and shortcuts) from the 2009Scape server source.

Shortcuts are parsed from the source (registrations with object ids, level and xp; grapple requirements and
locations) with shape assertions. The three basic courses are procedural in the server (xp is passed inside
handler code), so their obstacle tables are transcribed below and every object id and xp literal is checked
to occur in the named source file; a source change then fails loudly. Brimhaven and the Agility Pyramid are
not modelled yet.

Usage: generate_agility.py --source-root <upstream repo root> --source-commit <sha> [--output site/data/agility.json]
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "Server/src/main/content/global/skill/agility/"
SHORT = BASE + "shortcuts/"
EXPECTED_SHORTCUTS = {"configured": 28, "singleton": 8, "stepping-stone": 2, "grapple": 7}  # verified against the source below


class GeneratorError(Exception):
    pass


def read(root, rel):
    p = Path(root) / rel
    if not p.exists():
        raise GeneratorError(f"missing source file {rel}")
    return p.read_text(errors="ignore")


def prov(rel, commit, **kw):
    return {"source": "2009Scape", "file": rel, "commit": commit, **kw}


def ids_of(s):
    return [int(x) for x in re.findall(r"\d+", s)]


def label(cls):
    s = re.sub(r"Shortcut$", "", cls)
    return re.sub(r"(?<!^)(?=[A-Z])", " ", s).strip().capitalize()


# (name, objectIds, xp, failChance, source literals that must appear in the source file)
COURSES = [
    dict(key="gnome-stronghold", name="Gnome Stronghold Agility Course", file=BASE + "GnomeStrongholdCourse.kt",
         completionXp=39.0, level=None, entryNote="no level check in the server source",
         obstacles=[("Log balance", [2295], 7.5, None), ("Obstacle net", [2285], 7.5, None), ("Tree branch (up)", [35970], 5.0, None),
                    ("Balancing rope", [2312], 7.5, None), ("Tree branch (down)", [2314, 2315], 5.0, None),
                    ("Obstacle net", [2286], 7.5, None), ("Obstacle pipe", [4058, 154], 7.5, None)]),
    dict(key="barbarian-outpost", name="Barbarian Outpost Agility Course", file=BASE + "BarbarianOutpostCourse.kt",
         completionXp=46.2, level=None, entryNote="no level check in the server source; entry needs the Barcrawl completed",
         obstacles=[("Rope swing", [2282], 22.0, 0.1), ("Log balance", [2294], 13.5, 0.5), ("Obstacle net", [20211], 8.0, None),
                    ("Ledge balance", [2302], 22.0, 0.3), ("Low wall", [1948], 13.5, None)]),
    dict(key="wilderness", name="Wilderness Agility Course", file=BASE + "WildernessCourse.kt",
         completionXp=499.0, level=52, entryNote="entry gate needs Agility 52 (the obstacle pipe checks 49)",
         obstacles=[("Ridge entrance", [2307, 2308], 15.0, 0.3), ("Obstacle pipe", [2288], 12.5, None), ("Rope swing", [2283], 20.0, 0.1),
                    ("Stepping stones", [37704], 20.0, 0.3), ("Log balance", [2297], 20.0, 0.5), ("Rock climb", [2328], 0.0, None)]),
]
LOW_WALL_COUNT = 3  # the Barbarian course has three separate low walls (flags 4, 5, 6)


def courses(root, commit):
    out = []
    for c in COURSES:
        text = read(root, c["file"])
        if f"{c['completionXp']}" not in text:
            raise GeneratorError(f"{c['key']}: completion xp {c['completionXp']} not in source")
        obs = []
        for name, oids, xp, fail in c["obstacles"]:
            for oid in oids:
                if not re.search(rf"\b{oid}\b", text):
                    raise GeneratorError(f"{c['key']}: object {oid} not in source")
            if xp and not re.search(rf"(?<![\d.]){re.escape(str(xp))}(?!\d)|(?<![\d.]){int(xp)}(?![\d.])", text):
                raise GeneratorError(f"{c['key']}: xp {xp} not in source")
            o = OrderedDict(name=name, objectIds=oids, xp=xp)
            if fail is not None:
                o["failChance"] = fail
            if name == "Low wall":
                o["count"] = LOW_WALL_COUNT
            obs.append(o)
        out.append(OrderedDict(id=f"2009scape-agility-course-{c['key']}", skill="Agility", kind="course", name=c["name"],
                               level=c["level"], levelNote=c["entryNote"], completionXp=c["completionXp"],
                               obstacleXp=round(sum(o["xp"] * o.get("count", 1) for o in obs), 2), obstacles=obs,
                               provenance=prov(c["file"], commit)))
    return out


def shortcuts(root, commit):
    rows, kinds = [], {k: 0 for k in EXPECTED_SHORTCUTS}
    files = sorted((Path(root) / SHORT).glob("*.*"))
    for f in files:
        rel = SHORT + f.name
        text = f.read_text(errors="ignore")
        cls = f.stem
        # configure(new X(new int[]{ids}, level, xp[, ...]))  /  configure(X(intArrayOf(ids), level, xp, "opt")) //note
        for m in re.finditer(r"configure\(\s*(?:new\s+)?(\w+)\((?:new int\[\]\s*\{|intArrayOf\()([^})]*)[})]\s*,\s*(\d+),\s*([\d.]+)([^\n]*)", text):
            kind, ids, level, xp, rest = m.groups()
            opt = re.findall(r'"([^"]+)"', rest)
            note = re.search(r"//\s*(.+)$", rest)
            rows.append(OrderedDict(kind="shortcut", cls=kind, ids=ids_of(ids), level=int(level), xp=float(xp), options=opt,
                                    note=note.group(1).strip() if note else None, rel=rel))
            kinds["configured"] += 1
        # super(new int[]{ids}, level, xp, "option")  /  AgilityShortcut(intArrayOf(ids), level, xp, "option")
        for m in re.finditer(r"(?:super|AgilityShortcut)\((?:new int\[\]\s*\{|intArrayOf\()([^})]*)[})]\s*,\s*(\d+),\s*([\d.]+),\s*\"([^\"]+)\"", text):
            ids, level, xp, opt = m.groups()
            if not ids_of(ids):
                continue
            rows.append(OrderedDict(kind="shortcut", cls=cls, ids=ids_of(ids), level=int(level), xp=float(xp), options=[opt], note=None, rel=rel))
            kinds["singleton"] += 1
        # SteppingStoneShortcut: configure(intArrayOf(ids), Location(a), Location(b), "option", level)
        for m in re.finditer(r'configure\(intArrayOf\(([^)]*)\),\s*Location\.create\(([^)]*)\),\s*Location\.create\(([^)]*)\),\s*"([^"]+)",\s*(\d+)\)', text):
            ids, a, b, opt, level = m.groups()
            rows.append(OrderedDict(kind="shortcut", cls="SteppingStone", ids=ids_of(ids), level=int(level), xp=None, options=[opt],
                                    note=f"between {tuple(ids_of(a)[:3])} and {tuple(ids_of(b)[:3])}", rel=rel))
            kinds["stepping-stone"] += 1
    # grapples: each class has REQUIREMENTS + start/end locations
    for f in sorted((Path(root) / SHORT / "grapple").glob("*.kt")):
        text = f.read_text(errors="ignore")
        for m in re.finditer(r"hashMapOf\(Skills\.AGILITY to (\d+), Skills\.RANGE to (\d+), Skills\.STRENGTH to (\d+)\)(.*?)(?=override val REQUIREMENTS|\Z)", text, re.S):
            ag, rg, st, tail = m.groups()
            s = re.search(r"grappleStartLocation[^=]*=\s*Location(?:\.create)?\(([^)]*)\)", tail)
            e = re.search(r"grappleEndLocation[^=]*=\s*Location(?:\.create)?\(([^)]*)\)", tail)
            cls = re.findall(r"class\s+(\w+)", text[:m.start()])
            if not (s and e and cls):
                raise GeneratorError(f"grapple not parsed in {f.name}")
            rows.append(OrderedDict(kind="grapple", cls=cls[-1], ids=[], level=int(ag), xp=None, options=["grapple"],
                                    requirements=[{"skill": "Agility", "level": int(ag)}, {"skill": "Ranged", "level": int(rg)}, {"skill": "Strength", "level": int(st)}],
                                    note=f"from {tuple(ids_of(s.group(1)))} to {tuple(ids_of(e.group(1)))}", rel=SHORT + "grapple/" + f.name))
            kinds["grapple"] += 1
    if kinds != EXPECTED_SHORTCUTS:
        raise GeneratorError(f"shortcut shape changed: {kinds} != {EXPECTED_SHORTCUTS}")
    out = []
    for i, r in enumerate(rows):
        key = f"{r['cls']}-{r['ids'][0] if r['ids'] else r['note']}"
        key = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
        row = OrderedDict(id=f"2009scape-agility-shortcut-{key}", skill="Agility", kind=r["kind"], name=label(r["cls"]), level=r["level"],
                          xp=r["xp"], objectIds=r["ids"], options=r["options"])
        if r.get("requirements"):
            row["requirements"] = r["requirements"]
        if r.get("note"):
            row["note"] = r["note"]
        row["provenance"] = prov(r["rel"], commit, enum=r["cls"])
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--output", default=str(ROOT / "site/data/agility.json"))
    a = ap.parse_args()
    cs, ss = courses(a.source_root, a.source_commit), shortcuts(a.source_root, a.source_commit)
    seen = {}
    for r in ss:
        if r["id"] in seen:
            seen[r["id"]] += 1
            r["id"] += f"-{seen[r['id']]}"
        else:
            seen[r["id"]] = 1
    ss.sort(key=lambda r: (r["level"], r["id"]))
    doc = OrderedDict(formatVersion=1, source="2009Scape", sourceCommit=a.source_commit,
                      counts={"courses": len(cs), "shortcuts": len(ss), "total": len(cs) + len(ss)}, courses=cs, shortcuts=ss)
    Path(a.output).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
