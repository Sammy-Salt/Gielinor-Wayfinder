#!/usr/bin/env python3
"""Regenerate the release integrity manifests.

Writes ``release-manifest.json`` (whole project) and ``site/release-manifest.json``
(deployable PWA). Each manifest lists every file with its SHA-256 and byte size,
sorted by path. The manifest being written is excluded from itself; the root
manifest does include ``site/release-manifest.json``.

Usage: scripts/generate_release_manifest.py [--check]
  --check  do not write; exit 1 if the manifests on disk are out of date.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def walk(base: Path):
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(base).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        yield path


def build(base: Path, release: dict, own_name: str) -> dict:
    files = {}
    for path in walk(base):
        rel = path.relative_to(base).as_posix()
        if rel == own_name:
            continue
        data = path.read_bytes()
        files[rel] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    return {
        "formatVersion": 1,
        "release": release["release"],
        "buildId": release["buildId"],
        "manifestExcludes": [own_name] if base == SITE else [own_name, ".git"],
        "files": files,
    }


def render(manifest: dict) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    check = "--check" in sys.argv[1:]
    release = json.loads((SITE / "release.json").read_text())
    # Site manifest first: the root manifest hashes it.
    outputs = [
        (SITE / "release-manifest.json", build(SITE, release, "release-manifest.json")),
    ]
    stale = []
    for path, manifest in outputs:
        text = render(manifest)
        if check:
            if not path.exists() or path.read_text() != text:
                stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.write_text(text)
    root_manifest = build(ROOT, release, "release-manifest.json")
    root_path = ROOT / "release-manifest.json"
    text = render(root_manifest)
    if check:
        if not root_path.exists() or root_path.read_text() != text:
            stale.append("release-manifest.json")
        if stale:
            print("RELEASE MANIFEST: STALE " + ", ".join(stale))
            return 1
        print("RELEASE MANIFEST: PASS")
        return 0
    root_path.write_text(text)
    print(
        f"RELEASE MANIFEST: written | root={len(root_manifest['files'])} files "
        f"site={len(outputs[0][1]['files'])} files | {release['release']} {release['buildId']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
