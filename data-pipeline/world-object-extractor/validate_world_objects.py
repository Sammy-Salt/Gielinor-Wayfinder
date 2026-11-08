#!/usr/bin/env python3
"""Validate one-region JSON output from WayfinderDump."""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

LAYERS = {"wall", "wall-decor", "scenery", "ground-decor"}


def validate(data: dict) -> list[str]:
    errors = []
    if data.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1")
    region = data.get("region")
    if not isinstance(region, dict):
        return errors + ["region metadata is missing"]
    try:
        rx, ry = int(region["x"]), int(region["y"])
        rid = int(region["regionId"])
        if not (0 <= rx <= 255 and 0 <= ry <= 255):
            errors.append("region coordinates must be in 0..255")
        if rid != ((rx << 8) | ry):
            errors.append("regionId does not match region x/y")
    except (KeyError, TypeError, ValueError):
        return errors + ["region x, y, or regionId is invalid"]

    rows = data.get("objects")
    if not isinstance(rows, list):
        return errors + ["objects must be a list"]
    if data.get("objectCount") != len(rows):
        errors.append("objectCount does not match objects length")

    seen = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"objects[{i}] is not an object")
            continue
        try:
            object_id = int(row["objectId"])
            x, y, plane = int(row["x"]), int(row["y"]), int(row["plane"])
            shape, orientation = int(row["shape"]), int(row["orientation"])
            layer, name = row["layer"], row["name"]
        except (KeyError, TypeError, ValueError):
            errors.append(f"objects[{i}] is missing valid required fields")
            continue
        if object_id < 0:
            errors.append(f"objects[{i}] has a negative objectId")
        if (x >> 6, y >> 6) != (rx, ry):
            errors.append(f"objects[{i}] is outside the declared region")
        if not 0 <= plane <= 3:
            errors.append(f"objects[{i}] plane is outside 0..3")
        if not 0 <= shape <= 31:
            errors.append(f"objects[{i}] shape is outside 0..31")
        if not 0 <= orientation <= 3:
            errors.append(f"objects[{i}] orientation is outside 0..3")
        if layer not in LAYERS:
            errors.append(f"objects[{i}] has an unknown layer")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"objects[{i}] has no usable name")
        signature = (object_id, x, y, plane, shape, orientation, layer)
        if signature in seen:
            errors.append(f"objects[{i}] duplicates an earlier placement")
        seen.add(signature)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    data = json.loads(args.file.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    counts = Counter(row["layer"] for row in data["objects"])
    print(f"VALID region={data['region']['x']},{data['region']['y']} objects={len(data['objects'])}")
    for layer in sorted(LAYERS):
        print(f"  {layer}: {counts[layer]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
