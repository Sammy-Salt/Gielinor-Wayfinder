#!/usr/bin/env bash
set -euo pipefail

FORGE_ROOT="${1:?Usage: bash build.sh <Gielinor-Forge-root> <rt4-client-root>}"
RT4_ROOT="${2:?Usage: bash build.sh <Gielinor-Forge-root> <rt4-client-root>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
CLIENT="$RT4_ROOT/client"
DEST="$CLIENT/src/main/java/rt4"

test -f "$FORGE_ROOT/src/rt4/EditorApp.java" || { echo "Missing Forge src/rt4/EditorApp.java"; exit 1; }
test -f "$CLIENT/build.gradle" || { echo "Missing rt4-client/client/build.gradle"; exit 1; }
test -x "$RT4_ROOT/gradlew" || { echo "Missing executable rt4-client/gradlew"; exit 1; }

mkdir -p "$DEST"
cp "$FORGE_ROOT/src/rt4/EditorApp.java" "$DEST/EditorApp.java"
cp "$HERE/WayfinderDump.java" "$DEST/WayfinderDump.java"

python3 - "$CLIENT/build.gradle" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text()
if "wayfinderDumpJar" not in s:
    s += """
\n// Gielinor Wayfinder read-only region object exporter.
task wayfinderDumpJar(type: Jar) {
    dependsOn classes
    archiveBaseName = 'wayfinder-world-dump'
    from sourceSets.main.output
    from { configurations.compileClasspath.collect { it.isDirectory() ? it : zipTree(it) } }
    manifest { attributes 'Main-Class': 'rt4.WayfinderDump' }
    duplicatesStrategy = DuplicatesStrategy.INCLUDE
}
"""
    p.write_text(s)
PY

cd "$RT4_ROOT"
./gradlew :client:wayfinderDumpJar
echo
echo "Built: $CLIENT/build/libs/wayfinder-world-dump.jar"
echo "This modifies only the RT4 client clone, not your 2009Scape server/cache or PWA."
