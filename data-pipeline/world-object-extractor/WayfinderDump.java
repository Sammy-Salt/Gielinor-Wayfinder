package rt4;

import java.io.BufferedWriter;
import java.io.File;
import java.lang.reflect.Field;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Gielinor Wayfinder's read-only world-object exporter.
 *
 * Runs inside the 2009Scape RT4 client engine, reusing its cache, XTEA,
 * region and LocType decoders. It never writes to the source cache.
 *
 * Usage: WayfinderDump <2009scape-server-root> <region-x> <region-y> <output.json>
 */
public final class WayfinderDump {
    private static final String[] LAYERS = {
        "wall", "wall-decor", "scenery", "ground-decor"
    };

    private static final List<String> objects = new ArrayList<>();
    private static final Set<String> seen = new HashSet<>();
    private static int[] layerCounts = new int[4];

    public static void main(String[] args) throws Exception {
        if (args.length != 4) {
            throw new IllegalArgumentException(
                "Usage: WayfinderDump <server-root> <region-x> <region-y> <output.json>"
            );
        }

        File serverRoot = new File(args[0]).getCanonicalFile();
        int rx = Integer.parseInt(args[1]);
        int rz = Integer.parseInt(args[2]);
        Path output = new File(args[3]).toPath();

        if (rx < 0 || rx > 255 || rz < 0 || rz > 255) {
            throw new IllegalArgumentException("Region coordinates must be 0..255.");
        }
        if (!serverRoot.isDirectory()) {
            throw new IllegalArgumentException("Server root is not a directory: " + serverRoot);
        }

        System.setProperty("java.awt.headless", "true");
        System.setProperty("editor.server", serverRoot.getAbsolutePath());
        GlRenderer.enabled = false;

        if (!EditorApp.resolveServer(false)) {
            throw new IllegalStateException("Could not discover the server cache and XTEA file.");
        }

        EditorApp.openCache(EditorApp.CACHE_DIR);
        EditorApp.initArchives();
        EditorApp.initTypeLists();
        if (LocTypeList.locsArchive == null) {
            throw new IllegalStateException("LocTypeList did not initialize from cache archives 16/7.");
        }
        if (EditorApp.XTEA_PATH == null || !new File(EditorApp.XTEA_PATH).isFile()) {
            throw new IllegalStateException("xteas.json was not found beside the server cache.");
        }
        EditorApp.xteas = EditorApp.loadXteas(EditorApp.XTEA_PATH);
        if (EditorApp.xteas.isEmpty()) {
            throw new IllegalStateException("No XTEA records were parsed from xteas.json.");
        }

        int regionId = (rx << 8) | rz;
        int mapGroupId = client.js5Archive5.getGroupId(JagString.of("m" + rx + "_" + rz));
        int locGroupId = client.js5Archive5.getGroupId(JagString.of("l" + rx + "_" + rz));
        if (locGroupId < 0) {
            throw new IllegalStateException("No location archive l" + rx + "_" + rz + " in cache index 5.");
        }

        for (int p = 0; p < 4; p++) {
            PathFinder.collisionMaps[p] = new CollisionMap(104, 104);
        }
        PlayerList.self = new Player();
        SceneGraph.dynamicMapRegion = false;
        Player.plane = 0;
        EditorApp.camWorldFineX = (rx * 64 + 32) * 128 + 64;
        EditorApp.camWorldFineZ = (rz * 64 + 32) * 128 + 64;
        EditorApp.recenter();

        boolean locBufferLoaded = false;
        for (int i = 0; i < LoginManager.regionBitPacked.length; i++) {
            if (LoginManager.regionBitPacked[i] == regionId) {
                locBufferLoaded = LoginManager.locationMapFilesBuffer[i] != null;
                break;
            }
        }
        if (!locBufferLoaded) {
            throw new IllegalStateException(
                "Location archive exists but could not be loaded. Check the cache/XTEA pair for region " + regionId + "."
            );
        }

        scanRegion(rx, rz);
        if (objects.isEmpty()) {
            throw new IllegalStateException(
                "No objects decoded in region " + rx + "," + rz + "; refusing to write an empty result."
            );
        }

        StringBuilder json = new StringBuilder(Math.max(4096, objects.size() * 220));
        json.append("{\n")
            .append("  \"schemaVersion\": 1,\n")
            .append("  \"source\": \"2009Scape RT4 cache\",\n")
            .append("  \"region\": {\n")
            .append("    \"regionId\": ").append(regionId).append(",\n")
            .append("    \"x\": ").append(rx).append(",\n")
            .append("    \"y\": ").append(rz).append(",\n")
            .append("    \"mapArchiveId\": ").append(mapGroupId).append(",\n")
            .append("    \"locationArchiveId\": ").append(locGroupId).append(",\n")
            .append("    \"xteaKeyPresent\": ").append(EditorApp.xteas.containsKey(regionId)).append("\n")
            .append("  },\n")
            .append("  \"objectCount\": ").append(objects.size()).append(",\n")
            .append("  \"objects\": [\n");

        for (int i = 0; i < objects.size(); i++) {
            json.append("    ").append(objects.get(i));
            json.append(i + 1 == objects.size() ? "\n" : ",\n");
        }
        json.append("  ]\n}\n");

        Path parent = output.toAbsolutePath().getParent();
        if (parent != null) Files.createDirectories(parent);
        try (BufferedWriter writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
            writer.write(json.toString());
        }

        System.out.println("[WayfinderDump] region=" + rx + "," + rz
            + " id=" + regionId
            + " xtea=" + EditorApp.xteas.containsKey(regionId)
            + " objects=" + objects.size());
        for (int i = 0; i < LAYERS.length; i++) {
            System.out.println("[WayfinderDump] " + LAYERS[i] + "=" + layerCounts[i]);
        }
        System.out.println("[WayfinderDump] wrote " + output.toAbsolutePath());
    }

    private static void scanRegion(int rx, int rz) {
        for (int p = 0; p < 4; p++) {
            for (int x = 0; x < 104; x++) {
                for (int z = 0; z < 104; z++) {
                    int worldX = Camera.originX + x;
                    int worldY = Camera.originZ + z;
                    if ((worldX >> 6) != rx || (worldY >> 6) != rz) continue;

                    add(SceneGraph.getWallKey(p, x, z), 0, worldX, worldY, p);
                    add(SceneGraph.getWallDecorKey(p, x, z), 1, worldX, worldY, p);
                    add(SceneGraph.getGroundDecorKey(p, x, z), 3, worldX, worldY, p);

                    Tile tile = SceneGraph.tiles[p][x][z];
                    if (tile != null) {
                        for (int i = 0; i < tile.sceneryLen; i++) {
                            Scenery scenery = tile.scenery[i];
                            if (scenery == null) continue;
                            int sx = intField(scenery, "xMin");
                            int sz = intField(scenery, "zMin", "yMin");
                            int sp = intField(scenery, "level");
                            if (sx == x && sz == z && sp == p) {
                                add(scenery.key, 2, worldX, worldY, p);
                            }
                        }
                    }
                }
            }
        }
    }

    private static int intField(Object value, String... names) {
        for (String name : names) {
            try {
                Field field = value.getClass().getField(name);
                return field.getInt(value);
            } catch (ReflectiveOperationException ignored) { }
        }
        return Integer.MIN_VALUE;
    }

    private static void add(long key, int layer, int x, int y, int plane) {
        if (key == 0L) return;

        int id = (int) (key >>> 32) & Integer.MAX_VALUE;
        int shape = (int) (key >> 14) & 0x1F;
        int orientation = (int) (key >> 20) & 0x3;
        String signature = plane + ":" + x + ":" + y + ":" + id + ":" + shape + ":" + orientation + ":" + layer;
        if (!seen.add(signature)) return;

        LocType type = LocTypeList.get(id);
        String name = type == null || type.name == null ? "Unknown object " + id : type.name.toString();
        int mapFunction = type == null ? -1 : type.mapfunction;
        int mapScene = type == null ? -1 : type.mapscene;
        int width = type == null ? 1 : type.width;
        int length = type == null ? 1 : type.length;

        StringBuilder row = new StringBuilder(256);
        row.append("{\"objectId\":").append(id)
            .append(",\"name\":").append(quote(name))
            .append(",\"x\":").append(x)
            .append(",\"y\":").append(y)
            .append(",\"plane\":").append(plane)
            .append(",\"shape\":").append(shape)
            .append(",\"orientation\":").append(orientation)
            .append(",\"layer\":").append(quote(LAYERS[layer]))
            .append(",\"mapFunction\":").append(mapFunction)
            .append(",\"mapScene\":").append(mapScene)
            .append(",\"width\":").append(width)
            .append(",\"length\":").append(length)
            .append(",\"actions\":[");
        boolean first = true;
        if (type != null && type.ops != null) {
            for (JagString action : type.ops) {
                if (action == null) continue;
                if (!first) row.append(',');
                row.append(quote(action.toString()));
                first = false;
            }
        }
        row.append("]}");
        objects.add(row.toString());
        layerCounts[layer]++;
    }

    private static String quote(String value) {
        StringBuilder out = new StringBuilder(value.length() + 2);
        out.append('"');
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            switch (c) {
                case '"': out.append("\\\""); break;
                case '\\': out.append("\\\\"); break;
                case '\n': out.append("\\n"); break;
                case '\r': out.append("\\r"); break;
                case '\t': out.append("\\t"); break;
                default:
                    if (c < 0x20) out.append(String.format("\\u%04x", (int) c));
                    else out.append(c);
            }
        }
        return out.append('"').toString();
    }

    private WayfinderDump() { }
}
