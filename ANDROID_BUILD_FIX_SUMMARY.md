# Android Build Fix - Changes Summary

## Problem
User built with `flet build apk --module-name main_app` and got a black screen on Android.

## Root Cause
**Wrong entry point module:** Used `main_app` instead of `main` as the module name.
- `main_app.py` is for **desktop development** only
- `main.py` is the **Android entry point** with special bootstrap logic for Android packaging

## Solution Applied

### 1. Created Automated Build Pipeline
**File:** `build_android.ps1`

**What it does:**
- Automates the entire APK build process
- Runs environment checks (Python, Flet, icon file)
- Executes `prepare_build.py` to create staging folder
- Verifies staging folder contents
- Builds APK with correct parameters
- Copies APK to timestamped dist folder

**Usage:**
```powershell
.\build_android.ps1           # Normal build
.\build_android.ps1 -Clean    # Clean build (removes old artifacts)
```

**Key improvements:**
- Fail-fast validation at each step
- Colored output for easy debugging
- Timestamped APK copies for archiving
- Clear error messages with troubleshooting hints

### 2. Created Comprehensive Documentation
**File:** `building the app.md`

**Sections:**
1. **Prerequisites** — Required software and setup
2. **Quick Start** — One-command build instructions
3. **Build Process Details** — Step-by-step explanation
4. **Troubleshooting Black Screen** — Debug guide with adb logcat commands
5. **Code Changes for Android** — What we changed and why
6. **Manual Build Steps** — Fallback if script doesn't work
7. **Common Commands Reference** — Quick reference for adb/build commands

**Key troubleshooting content:**
- How to capture crash logs with `adb logcat`
- Common black screen causes and fixes
- Module import debugging steps
- Database path issues on Android
- Startup code crash detection

### 3. Verified Existing Code (No Changes Needed)

**Files already correct:**
- ✅ `main.py` — Android entry point with bootstrap logic
- ✅ `prepare_build.py` — Creates POSIX-compatible app.zip
- ✅ `core/storage.py` — Cross-platform storage paths
- ✅ `pyproject.toml` — Includes resources folder
- ✅ All core and ui_flet modules included

**Key existing features:**
- Windows backslash path fix in `main.py`
- Crash logging to `crash.log`
- FLET_APP_STORAGE_DATA detection for Android
- Bootstrap import logic for zip-packaged code

## Correct Build Command

```bash
flet build apk \
  --module-name main \
  --project hushove-restaurant-app \
  --icon resources/restaurant_app_icon.png \
  --no-rich-output \
  build_src
```

**Critical parameters:**
- `--module-name main` ✅ (NOT `main_app` ❌)
- `--project hushove-restaurant-app` — Sets Android package name
- `--icon resources/restaurant_app_icon.png` — App launcher icon
- `build_src` — Staging directory with app.zip

## Files Changed

### New Files Created
1. **`build_android.ps1`** — Automated PowerShell build pipeline
2. **`building the app.md`** — Complete build documentation

### Files Already Correct (No Changes)
- `main.py` — Android entry point (already implemented)
- `prepare_build.py` — Staging folder preparation (already implemented)
- `core/storage.py` — Cross-platform paths (already implemented)
- `pyproject.toml` — Project config (already correct)

## How to Use

### Quick Build
```powershell
.\build_android.ps1
```

### Output Location
```
dist/apk/latest/app-release.apk  (always latest)
dist/apk/YYYY-MM-DD_HH-mm-ss/app-release.apk  (archived)
```

### Install on Device
```bash
adb install -r dist/apk/latest/app-release.apk
```

### If Black Screen Occurs
```bash
# Capture logs
adb logcat -c
adb logcat | grep -E "python|flet|crash"

# Pull crash log
adb pull /data/data/com.flet.hushove_restaurant_app/files/flet/app/crash.log
```

## Why the Black Screen Happened

1. **Wrong module name** — Used `main_app` which doesn't have Android bootstrap logic
2. **Missing app icon flag** — Icon wasn't applied (minor, doesn't cause crash)

**Fix applied:**
- Use `--module-name main` (correct entry point)
- Use `--icon resources/restaurant_app_icon.png` (applies icon)

## Previous Fixes (Already in Codebase)

These were implemented earlier and are documented here for reference:

### 1. Windows Backslash Path Fix
**Problem:** Windows creates zip entries with backslashes (`core\__init__.py`). On Android, these extract as flat files with backslash in filename.

**Fix:** `prepare_build.py` explicitly uses forward slashes:
```python
arcname = f"{pkg_name}/{py_file.name}"  # Force forward slash!
```

### 2. Bootstrap Import Logic
**Problem:** Android packages app in `app.zip`, Python needs correct path in `sys.path`.

**Fix:** `main.py` has `_bootstrap_imports()` function that:
- Detects Android via `FLET_APP_STORAGE_DATA` env var
- Finds `app.zip` location
- Adds to `sys.path[0]`
- Fixes Windows backslash paths if needed

### 3. Cross-Platform Storage
**Problem:** Android can't write to app directory, needs app storage.

**Fix:** `core/storage.py` checks `FLET_APP_STORAGE_DATA`:
```python
flet_data_dir = os.environ.get("FLET_APP_STORAGE_DATA")
if flet_data_dir:
    return Path(flet_data_dir)  # Android
return Path.cwd()  # Desktop
```

### 4. Crash Logging
**Problem:** Hard to debug crashes on Android without logcat.

**Fix:** `main.py` writes exceptions to `crash.log`:
```python
def _write_crash_log(error_msg, tb_str):
    crash_file = _get_app_dir() / "crash.log"
    with open(crash_file, "w") as f:
        f.write(f"=== CRASH LOG ===\n")
        f.write(f"Error: {error_msg}\n\n")
        f.write(f"Traceback:\n{tb_str}\n")
```

## Testing Checklist

After building:
- [ ] APK exists at `dist/apk/latest/app-release.apk`
- [ ] APK size is reasonable (15-30 MB typical)
- [ ] Install: `adb install -r dist/apk/latest/app-release.apk`
- [ ] Launch app on device
- [ ] App shows UI (not black screen)
- [ ] App icon displays correctly in launcher
- [ ] Can create/view reservations
- [ ] Can navigate between tabs
- [ ] Database persists after closing app

## Next Steps for User

1. Run the automated build:
   ```powershell
   .\build_android.ps1
   ```

2. If first build, accept Android licenses when prompted:
   ```bash
   flutter doctor --android-licenses
   ```

3. Install and test:
   ```bash
   adb install -r dist/apk/latest/app-release.apk
   ```

4. If any issues, check the documentation in `building the app.md`

## Summary

**Problem:** Black screen on Android due to wrong module name (`main_app` instead of `main`)

**Solution:** 
- Created automated build script (`build_android.ps1`)
- Created comprehensive documentation (`building the app.md`)
- Verified all code is correct (no changes needed)
- Correct build command uses `--module-name main`

**Result:** User can now build working Android APK with one command: `.\build_android.ps1`
