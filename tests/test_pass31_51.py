#!/usr/bin/env python3
"""PASS31.51 gate: Agility courses and shortcuts come from the 2009Scape server source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site/data/agility.json").read_text())
assert doc["formatVersion"] == 1 and doc["source"] == "2009Scape" and doc["sourceCommit"]
assert doc["counts"] == {"courses": 3, "shortcuts": 45, "total": 48}
rows = doc["courses"] + doc["shortcuts"]
ids = [r["id"] for r in rows]
assert len(ids) == len(set(ids)), "duplicate row ids"
for r in rows:
    assert r["skill"] == "Agility"
    assert r["provenance"]["source"] == "2009Scape" and r["provenance"]["file"].startswith("Server/src/main/content/global/skill/agility/")
c = {r["id"].split("course-")[1]: r for r in doc["courses"]}
assert c["gnome-stronghold"]["completionXp"] == 39.0 and len(c["gnome-stronghold"]["obstacles"]) == 7 and c["gnome-stronghold"]["obstacleXp"] == 47.5
assert c["barbarian-outpost"]["completionXp"] == 46.2 and c["barbarian-outpost"]["obstacleXp"] == 106.0  # three low walls counted
assert c["wilderness"]["completionXp"] == 499.0 and c["wilderness"]["level"] == 52
assert c["gnome-stronghold"]["level"] is None  # the server has no level gate; never guessed
s = {}
for r in doc["shortcuts"]:
    s.setdefault(r["name"], []).append(r)
pipes = {r["objectIds"][0]: r for r in s["Pipe"]}
assert (pipes[2290]["level"], pipes[2290]["xp"]) == (49, 0.0) and (pipes[9293]["level"], pipes[9293]["xp"]) == (70, 10.0)
assert [r["level"] for r in s["Strange floor"]] == [80] and s["Monkey bar"][-1]["level"] == 57 and s["Monkey bar"][-1]["xp"] == 20.0
grapples = [r for r in doc["shortcuts"] if r["kind"] == "grapple"]
assert len(grapples) == 7
karamja = [r for r in grapples if r["name"] == "Karamja grapple"][0]
assert karamja["requirements"] == [{"skill": "Agility", "level": 53}, {"skill": "Ranged", "level": 42}, {"skill": "Strength", "level": 21}]
assert sum(1 for r in doc["shortcuts"] if r["kind"] == "shortcut" and r["name"] == "Basalt rock") == 10
print("PASS31.51 agility data gate: 3 courses, 45 shortcuts, errors=0")
