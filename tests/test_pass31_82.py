#!/usr/bin/env python3
"""PASS31.82 gate: native offline Android app setup (ADR-0007)."""
import json, py_compile
from pathlib import Path
R = Path(__file__).resolve().parents[1]
for gone in ("android/twa-manifest.json", ".github/workflows/build-apk.yml", "site/.well-known/assetlinks.json"):
    assert not (R / gone).exists(), gone
cfg = json.loads((R / "android-app/capacitor.config.json").read_text())
assert cfg["appId"] == "com.sammysalt.gielinorwayfinder" and cfg["appName"] == "Gielinor Wayfinder" and cfg["webDir"] == "../site"
assert "url" not in cfg.get("server", {}), "a server.url would make the app load live"
pkg = json.loads((R / "android-app/package.json").read_text())
assert all(k.startswith("@capacitor/") for k in {**pkg["dependencies"], **pkg["devDependencies"]})
py_compile.compile(str(R / "android-app/scripts/apply_android_overrides.py"), doraise=True)
ov = (R / "android-app/scripts/apply_android_overrides.py").read_text()
assert "permission.INTERNET" in ov and "assert" in ov
assert (R / "android-app/signing/wayfinder-sideload.keystore").stat().st_size > 1000
wf = (R / ".github/workflows/build-android-app.yml").read_text()
for n in ("npx cap add android", "apply_android_overrides.py", "apksigner", "dump badging", "INTERNET", "android-emulator-runner", "smoke_test.sh", "gh release create", "needs: [build, smoke]"):
    assert n in wf, n
assert "Offline app" in (R / "site/js/core/platform.js").read_text(encoding="utf-8")
for d in ("docs/decisions/ADR-0007-OFFLINE-ANDROID-APP.md", "docs/development/ANDROID_APK.md", "docs/history/PASS31.82_OFFLINE_ANDROID_APP_2026-11-13.md"):
    assert (R / d).exists(), d
print("PASS31.82 gate: offline Android app setup, no TWA leftovers, errors=0")
