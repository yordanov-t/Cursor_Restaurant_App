# Quick Reference: Build Android APK

## One-Command Build

```powershell
.\build_android.ps1
```

## Output

```
dist/apk/latest/app-release.apk
```

## Install

```bash
adb install -r dist/apk/latest/app-release.apk
```

## Black Screen? Capture Logs

```bash
adb logcat -c
adb logcat | grep -E "python|flet|crash"
```

## The Fix (What Was Wrong)

**You used:** `--module-name main_app` ❌  
**Correct:**   `--module-name main` ✅

**Why:**
- `main_app.py` = Desktop development only
- `main.py` = Android entry point (has bootstrap logic)

## Full Documentation

See: **`building the app.md`**

## Common Commands

```bash
# Build APK
.\build_android.ps1

# Clean build
.\build_android.ps1 -Clean

# Install on device
adb install -r dist/apk/latest/app-release.apk

# Capture crash logs
adb logcat | grep "python"

# Pull crash.log from device
adb pull /data/data/com.flet.hushove_restaurant_app/files/flet/app/crash.log

# Accept Android licenses (first time)
flutter doctor --android-licenses
```

## Build Parameters (if running manually)

```bash
flet build apk \
  --module-name main \
  --project hushove-restaurant-app \
  --icon resources/restaurant_app_icon.png \
  --no-rich-output \
  build_src
```

## Files Created

1. **`build_android.ps1`** — Automated build pipeline
2. **`building the app.md`** — Complete documentation
3. **`ANDROID_BUILD_FIX_SUMMARY.md`** — What we fixed
4. **`QUICK_REFERENCE.md`** — This file
