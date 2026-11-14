#!/usr/bin/env python3
"""Customise the generated Capacitor Android project (run after `npx cap add android`, before `npx cap sync`).

- no INTERNET permission: the app never talks to a network;
- name, version, colours, launcher icon and splash screen;
- Gradle heap sized for ~35,000 bundled asset files.
Environment: VERSION_NAME, VERSION_CODE.
"""
import os, re, sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent.parent
ANDROID = HERE / "android"
APP = ANDROID / "app"
RES = APP / "src/main/res"
ICON = Image.open(HERE.parent / "site/icons/icon-512.png").convert("RGBA")
BG = (23, 19, 14, 255)          # edge colour of the shipped icon
BAR = "#111111"                 # status / navigation bar, same as the site theme


def edit(path, fn):
    p = Path(path); t = p.read_text(encoding="utf-8"); n = fn(t)
    if n == t: print("  (unchanged)", p.relative_to(ANDROID))
    p.write_text(n, encoding="utf-8")


# --- manifest: drop every network permission -------------------------------------------------
manifest = APP / "src/main/AndroidManifest.xml"
edit(manifest, lambda t: re.sub(r'\s*<uses-permission android:name="android\.permission\.(INTERNET|ACCESS_NETWORK_STATE)"\s*/>', "", t))
assert "permission.INTERNET" not in manifest.read_text(encoding="utf-8")

# --- strings / colours / theme -----------------------------------------------------------------
strings = RES / "values/strings.xml"
edit(strings, lambda t: re.sub(r"(<string name=\"(?:app_name|title_activity_main)\">)[^<]*(</string>)", r"\1Gielinor Wayfinder\2", t))
bgxml = RES / "values/ic_launcher_background.xml"
if bgxml.exists():
    bgxml.write_text('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">#17130E</color>\n</resources>\n', encoding="utf-8")
styles = RES / "values/styles.xml"
def theme(t):
    bars = f'        <item name="android:statusBarColor">{BAR}</item>\n        <item name="android:navigationBarColor">{BAR}</item>\n        <item name="android:windowBackground">{BAR}</item>\n'
    def add(m):
        block = m.group(0)
        return block if "statusBarColor" in block else block.replace("</style>", bars + "    </style>")
    return re.sub(r'<style name="AppTheme\.NoActionBar"[^>]*>.*?</style>', add, t, flags=re.S)
edit(styles, theme)

# --- launcher icons and splash: regenerate every PNG at its existing size ------------------------
def render(size, kind):
    if kind == "foreground":                      # adaptive icon: art inside the central 66 %
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        art = ICON.resize((round(size * 0.66),) * 2, Image.LANCZOS)
        im.paste(art, ((size - art.width) // 2,) * 2, art); return im
    im = ICON.resize((size, size), Image.LANCZOS)
    if kind == "round":
        mask = Image.new("L", (size * 4,) * 2, 0); ImageDraw.Draw(mask).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0)); out.paste(im, mask=mask.resize((size, size), Image.LANCZOS)); return out
    return im

count = 0
for png in RES.rglob("*.png"):
    name = png.name
    kind = {"ic_launcher.png": "square", "ic_launcher_round.png": "round", "ic_launcher_foreground.png": "foreground"}.get(name)
    if kind:
        size = Image.open(png).size[0]; render(size, kind).save(png); count += 1
    elif name == "splash.png":
        w, h = Image.open(png).size
        im = Image.new("RGBA", (w, h), BG); side = round(min(w, h) * 0.32)
        art = ICON.resize((side, side), Image.LANCZOS); im.paste(art, ((w - side) // 2, (h - side) // 2), art); im.save(png); count += 1
print(f"  regenerated {count} icon/splash images")
assert count >= 15, "expected launcher and splash images in the generated project"

# --- version + Gradle memory ----------------------------------------------------------------------
gradle = APP / "build.gradle"
vn, vc = os.environ.get("VERSION_NAME", "1.0.0"), os.environ.get("VERSION_CODE", "1")
edit(gradle, lambda t: re.sub(r"versionName\s+\"[^\"]*\"", f'versionName "{vn}"', re.sub(r"versionCode\s+\d+", f"versionCode {vc}", t)))
props = ANDROID / "gradle.properties"
t = props.read_text(encoding="utf-8")
t = re.sub(r"(?m)^org\.gradle\.jvmargs=.*$", "org.gradle.jvmargs=-Xmx4g -Dfile.encoding=UTF-8", t) if "org.gradle.jvmargs" in t else t + "\norg.gradle.jvmargs=-Xmx4g -Dfile.encoding=UTF-8\n"
props.write_text(t, encoding="utf-8")
print(f"app version {vn} ({vc})")
