# World-object cache extractor (PASS31.48)

This is a **development-time, read-only** extractor. It uses the same 2009Scape RT4 client engine and cache path as Gielinor Forge, rather than implementing a second JS5/XTEA decoder.

It does not modify the PWA map, the 2009Scape cache, player saves, XTEA keys, or server configuration.

## Why the Forge engine

Gielinor Forge's loader already:
- opens the JS5 cache and index 5;
- reads the server's `xteas.json` format (each `keys` value is a comma-separated string of four integers);
- resolves `mX_Y` and `lX_Y` map groups;
- decrypts location groups and invokes the RT4 region-location decoder;
- initializes `LocTypeList`, which resolves object IDs to names and map-function/map-scene metadata.

References:
- Gielinor Forge: https://github.com/CodeEviction/Gielinor-Forge-2009scape
- RT4 client: https://gitlab.com/2009scape/rt4-client
- Forge source loader: `src/rt4/EditorApp.java` (`openCache`, `initArchives`, `recenter`, `loadXteas`)

## 1. Build the exporter

Use JDK 11+ in proot Ubuntu. Clone the two source repositories once:

```sh
git clone https://github.com/CodeEviction/Gielinor-Forge-2009scape.git ~/Gielinor-Forge-2009scape
git clone https://gitlab.com/2009scape/rt4-client.git ~/rt4-client
```

From the Gielinor Wayfinder repository:

```sh
bash data-pipeline/world-object-extractor/build.sh \
  "$HOME/Gielinor-Forge-2009scape" "$HOME/rt4-client"
```

The build script copies Forge's `EditorApp.java` and this export class into the RT4 client source tree, adds a dedicated fat-jar task, and builds:

`~/rt4-client/client/build/libs/wayfinder-world-dump.jar`

It changes only the local RT4 client clone.

## 2. Export one known region first

Lumbridge is region `50,50` (region ID `12850`):

```sh
java -Djava.awt.headless=true -jar \
  "$HOME/rt4-client/client/build/libs/wayfinder-world-dump.jar" \
  "$HOME/2009scape" 50 50 \
  /storage/emulated/0/Download/wayfinder-lumbridge-50-50.json
```

The exporter refuses to write a result if the location group cannot be found, the target location buffer fails to load, or no placements decode. It reports whether the target region has an XTEA record; absence alone is not treated as failure because some location groups are unencrypted.

The output contains object IDs, decoded names, world coordinates, plane, placement shape, orientation, scene layer, object dimensions, actions, map-function ID, and map-scene ID. No XTEA values are written.

## 3. Validate the result

```sh
python3 data-pipeline/world-object-extractor/validate_world_objects.py \
  /storage/emulated/0/Download/wayfinder-lumbridge-50-50.json
```

Run the validator's unit tests:

```sh
python3 -m unittest discover -s data-pipeline/world-object-extractor -p 'test_*.py'
```

## Important scope

This first pass deliberately exports **one 64×64-tile region**. Validate its object count and several known objects against Gielinor Forge before enabling whole-world extraction. Do not import this diagnostic file into `site/data/map/locations.js` yet.

Scenery placements are emitted from their recorded origin tile, not once per occupied footprint tile. Walls, wall decorations, ground decorations, and scenery remain separate layers.

The RT4 client and Gielinor Forge are AGPL-licensed projects. Keep their required source and license notices available when redistributing a built tool.
