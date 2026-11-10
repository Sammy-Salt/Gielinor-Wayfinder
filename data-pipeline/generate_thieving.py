#!/usr/bin/env python3
"""Generate site/data/thieving.json (pickpocket targets, stalls, chests) from the 2009Scape server source.

Parsed with regex plus shape assertions (row counts, literals) so a source change fails loudly. Item ids are verified
against the item catalog. Pickpocket loot follows WeightBasedTable: guaranteed rows always drop, plus exactly one
weighted roll per success, so chancePercent = weight / sum(non-guaranteed weights) * 100.

Usage: generate_thieving.py --source-root <upstream repo root> --source-commit <sha> [--output site/data/thieving.json]
"""
import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "Server/src/main/content/global/skill/thieving/"
PICK, STALL, CHEST = BASE + "Pickpockets.kt", BASE + "Stall.java", BASE + "ThievableChestPlugin.java"
EXPECTED = {"pickpockets": 18, "stalls": 18, "chests": 6}


class GeneratorError(Exception):
    pass


def read(root, rel):
    p = Path(root) / rel
    if not p.exists():
        raise GeneratorError(f"missing source file {rel}")
    return p.read_text(errors="ignore")


NAMES = {"KNIGHT_OF_ADROUGNE": "Knight of Ardougne"}  # the server enum misspells Ardougne


def title(name):
    return NAMES.get(name) or name.replace("_", " ").capitalize()


def prov(rel, enum, commit):
    return {"source": "2009Scape", "file": rel, "enum": enum, "commit": commit}


def numbers(expr):
    """Ids in an expression: literals, `X_<id>` constants and IntStream.rangeClosed(a, b)."""
    out = []
    for a, b in re.findall(r"rangeClosed\((\d+),\s*(\d+)\)", expr):
        out.extend(range(int(a), int(b) + 1))
    expr = re.sub(r"IntStream\.rangeClosed\([^)]*\)", "", expr)
    for tok in re.findall(r"[A-Za-z_]*?_?(\d+)\b", expr):
        out.append(int(tok))
    seen, uniq = set(), []
    for n in out:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    return uniq


def pickpockets(root, commit):
    text = read(root, PICK)
    body = text.split("enum class Pickpockets", 1)[1].split("companion object", 1)[0]
    body = body.split("{", 1)[1]  # drop the constructor parameter list
    parts = re.split(r"\n    ([A-Z][A-Z_]+)\(", body)
    rows = []
    for name, block in zip(parts[1::2], parts[2::2]):
        h = re.match(r"(.*?),\s*(\d+),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*(\d+),\s*(\d+),\s*(\d+),\s*WeightBasedTable\.create\(", block, re.S)
        if not h:
            raise GeneratorError(f"pickpocket header not parsed: {name}")
        npcs = numbers(re.sub(r"^intArrayOf\(|\)$", "", h.group(1).strip()))
        level, low, high, xp, smin, smax, stun = int(h.group(2)), float(h.group(3)), float(h.group(4)), float(h.group(5)), int(h.group(6)), int(h.group(7)), int(h.group(8))
        loot = []
        for iid, mn, mx, w, g in re.findall(r"WeightedItem\(Items\.[A-Z0-9_]+?_(\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)(,\s*true)?\)", block):
            loot.append(OrderedDict(itemId=int(iid), min=int(mn), max=int(mx), weight=float(w), guaranteed=bool(g)))
        clues = re.findall(r"\.insert(\w+?)Clue\(([\d.]+)\)", block)
        other = set(re.findall(r"\.(insert\w+)\(", block)) - {"insertEasyClue"}
        if other:
            raise GeneratorError(f"unmodelled table insert in {name}: {sorted(other)}")
        total = sum(l["weight"] for l in loot if not l["guaranteed"]) + sum(float(w) for _, w in clues)
        for l in loot:
            l["chancePercent"] = 100.0 if l["guaranteed"] else round(l["weight"] / total * 100, 3)
        for kind, w in clues:
            loot.append(OrderedDict(clue=kind.lower(), weight=float(w), guaranteed=False, chancePercent=round(float(w) / total * 100, 3)))
        if not npcs or not loot:
            raise GeneratorError(f"empty pickpocket row: {name}")
        rows.append(OrderedDict(
            id=f"2009scape-thieving-pickpocket-{name.lower().replace('_', '-')}", skill="Thieving", kind="pickpocket",
            name=title(name), level=level, xp=xp, npcIds=npcs, successLow=low, successHigh=high,
            stunDamage=[smin, smax], stunTicks=stun, loot=loot, provenance=prov(PICK, name, commit)))
    return rows


def items_of(expr):
    return [OrderedDict(itemId=int(i), quantity=int(q or 1)) for i, q in re.findall(r"new Item\([A-Za-z_]*?_?(\d+)(?:,\s*(\d+))?\)", expr)]


def stalls(root, commit):
    text = "\n".join(l for l in read(root, STALL).splitlines() if not l.strip().startswith("//"))
    rows = []
    for m in re.finditer(r"^\s*([A-Z_]+)\(new Integer\[\]\s*\{(.*?)\},\s*new Integer\[\]\s*\{(.*?)\},\s*(\d+),\s*new Item\[\]\s*\{(.*)\},\s*([\d.]+),\s*(\d+),\s*\"([^\"]*)\"\)", text, re.M):
        name, full, empty, level, loot, xp, delay, msg = m.groups()
        objs, empties = numbers(full), numbers(empty)
        if not objs or not empties:
            raise GeneratorError(f"stall full/empty id mismatch: {name}")
        rows.append(OrderedDict(
            id=f"2009scape-thieving-stall-{name.lower().replace('_', '-')}", skill="Thieving", kind="stall",
            name=title(name), level=int(level), xp=float(xp), objectIds=objs, emptyObjectIds=empties,
            respawnTicks=int(delay), loot=items_of(loot), lootMessage=msg, provenance=prov(STALL, name, commit)))
    return rows


def chests(root, commit):
    text = read(root, CHEST)
    body = text.split("enum Chest", 1)[1].split(";", 1)[0] if "enum Chest" in text else ""
    rows = []
    for name, oid, level, xp, loot, respawn in re.findall(r"([A-Z_]+)\((\d+),\s*(\d+),\s*([\d.]+),\s*new Item\[\]\s*\{(.*?)\},\s*(\d+)\)", body, re.S):
        rows.append(OrderedDict(
            id=f"2009scape-thieving-chest-{name.lower().replace('_', '-')}", skill="Thieving", kind="chest",
            name=title(name), level=int(level), xp=float(xp), objectIds=[int(oid)], respawnTicks=int(respawn),
            loot=items_of(loot), provenance=prov(CHEST, name, commit)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--output", default=str(ROOT / "site/data/thieving.json"))
    a = ap.parse_args()
    groups = OrderedDict(pickpockets=pickpockets(a.source_root, a.source_commit),
                         stalls=stalls(a.source_root, a.source_commit),
                         chests=chests(a.source_root, a.source_commit))
    for k, want in EXPECTED.items():
        if len(groups[k]) != want:
            raise GeneratorError(f"{k}: expected {want} rows, parsed {len(groups[k])}")
    for k in groups:
        groups[k].sort(key=lambda r: (r["level"], r["id"]))
    ids = {p.stem for p in (ROOT / "site/data/items").glob("*.json")}
    used = {(r["id"], str(l["itemId"])) for rows in groups.values() for r in rows for l in r["loot"] if "itemId" in l}
    missing = sorted(x for x in used if x[1] not in ids)
    if missing:
        raise GeneratorError(f"item ids missing from the catalog: {missing[:10]}")
    doc = OrderedDict(formatVersion=1, source="2009Scape", sourceCommit=a.source_commit,
                      counts={k: len(v) for k, v in groups.items()} | {"total": sum(len(v) for v in groups.values())}, **groups)
    Path(a.output).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    try:
        main()
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
