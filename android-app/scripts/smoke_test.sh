#!/usr/bin/env bash
# Install the built APK on a running emulator, start it, and check that the site renders from the bundled files.
set -uo pipefail
APK="$1"; PKG=com.sammysalt.gielinorwayfinder
fail() { echo "SMOKE FAIL: $*"; adb logcat -d -s chromium:E AndroidRuntime:E Capacitor:V Capacitor/Console:V 2>/dev/null | tail -60; exit 1; }

adb install -r -g "$APK" || fail "install failed"
adb shell pm list packages | grep -q "$PKG" || fail "package not installed"
echo "network permission requested: $(adb shell dumpsys package "$PKG" | grep -c 'android.permission.INTERNET')"
[ "$(adb shell dumpsys package "$PKG" | grep -c 'android.permission.INTERNET')" = "0" ] || fail "app requests INTERNET"

adb logcat -c
adb shell monkey -p "$PKG" -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
for i in $(seq 1 12); do
  sleep 5
  adb shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1
  adb pull /sdcard/ui.xml ui.xml >/dev/null 2>&1
  if grep -q "Total level" ui.xml 2>/dev/null; then echo "Home page rendered after $((i*5))s"; break; fi
done
grep -q "Total level" ui.xml 2>/dev/null || { grep -o 'text="[^"]*"' ui.xml | head -30; fail "home page text not found"; }
adb logcat -d | grep -q "FATAL EXCEPTION" && fail "app crashed"
adb exec-out screencap -p > screen.png || true
echo "SMOKE OK"
